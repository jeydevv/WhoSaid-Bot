import string
import numpy as np
import pandas as pd
import tensorflow as tf
from keras import models, layers
from nltk.corpus import stopwords
from gensim.models import Word2Vec
from keras.utils import to_categorical
from nltk.tokenize import word_tokenize
from sklearn.model_selection import train_test_split

server_models = {}
SAMPLE_LENGTH = 30


async def get_model(server_csv):
    print("gotten ", server_models[server_csv])
    return server_models[server_csv]


async def set_model(server_csv, model, w2v, player_dict):
    server_models[server_csv] = [model, w2v, player_dict]


async def train(server_csv):
    # Load the data
    data = pd.read_csv(server_csv)
    unique_classes = data['user'].nunique() + 1

    player_dict = {}

    # give people int ids
    newid = 1
    for user in data['user'].unique():
        data.loc[data["user"] == user, "user"] = newid
        player_dict[newid] = user
        newid += 1

    x_train, x_test, y_train, y_test = train_test_split(data['msg'], data['user'], test_size=0.2, random_state=42)
    stop_words = set(stopwords.words('english'))

    def preprocess(text):
        text = text.lower()
        text = ''.join([word for word in text if word not in string.punctuation])
        tokens = word_tokenize(text)
        tokens = [word for word in tokens if word not in stop_words]
        return ' '.join(tokens)

    x_train = x_train.apply(preprocess)
    x_test = x_test.apply(preprocess)

    sentences = [sentence.split() for sentence in x_train]
    w2v_model = Word2Vec(sentences, vector_size=SAMPLE_LENGTH, window=5, min_count=5, workers=4)

    def vectorize(sentence):
        words = sentence.split()
        words_vecs = [w2v_model.wv[word] for word in words if word in w2v_model.wv]
        if len(words_vecs) == 0:
            return np.zeros(SAMPLE_LENGTH)
        words_vecs = np.array(words_vecs)
        return words_vecs.mean(axis=0)

    x_train = np.array([vectorize(sentence) for sentence in x_train])
    x_test = np.array([vectorize(sentence) for sentence in x_test])

    y_train = to_categorical(y_train)
    y_test = to_categorical(y_test, unique_classes)

    model = models.Sequential()

    model.add(layers.Dense(500, activation="relu", input_shape=(SAMPLE_LENGTH,)))
    model.add(layers.Dense(100, activation="relu"))

    model.add(layers.Dense(unique_classes, activation="softmax"))
    model.summary()

    model.compile(
        optimizer="adam",
        loss="categorical_crossentropy",
        metrics=["accuracy"]
    )

    model.fit(
        x_train, y_train,
        epochs=37,
        batch_size=16,
        validation_data=(x_test, y_test)
    )

    scores = model.evaluate(x_test, y_test, verbose=0)
    print("Accuracy: %.2f%%" % (scores[1] * 100))

    await set_model(server_csv, model, w2v_model, player_dict)


async def predict(msg, server_csv):
    try:
        model_arr = await get_model(server_csv)
    except KeyError:
        return "NEED_TRAIN"

    model = model_arr[0]
    w2v_model = model_arr[1]
    player_dict = model_arr[2]

    stop_words = set(stopwords.words('english'))

    def preprocess(text):
        text = text.lower()
        text = ''.join([word for word in text if word not in string.punctuation])
        tokens = word_tokenize(text)
        tokens = [word for word in tokens if word not in stop_words]
        return ' '.join(tokens)

    def vectorize(sentence):
        words = sentence.split()
        words_vecs = [w2v_model.wv[word] for word in words if word in w2v_model.wv]
        if len(words_vecs) == 0:
            return np.zeros(SAMPLE_LENGTH)
        words_vecs = np.array(words_vecs)
        return words_vecs.mean(axis=0)

    topredict = tf.reshape(vectorize(preprocess(msg)), shape=(1, SAMPLE_LENGTH))

    predictions = model.predict(topredict)
    pred = np.argmax(predictions, axis=1)

    pred_player = player_dict[pred[0]]
    return pred_player
