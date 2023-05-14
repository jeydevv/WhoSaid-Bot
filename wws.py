import pandas as pd
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer

# Ideal context range found by testing F1 and accuracy of ranges from 1-10
context_range = 4


async def predict(msg, server_csv):
    data = pd.read_csv(server_csv)
    x_train, x_test, y_train, y_test = train_test_split(data["msg"], data["user"], test_size=0.2, random_state=42)

    cv = CountVectorizer(analyzer="word", ngram_range=(1, context_range), stop_words="english")
    x_train_cv = cv.fit_transform(x_train)

    clf = MultinomialNB()
    clf.fit(x_train_cv, y_train)

    return clf.predict(cv.transform([msg]))


async def savetraindata(df, server_csv):
    df.to_csv(server_csv, index=False)
    print(server_csv + " saved")
