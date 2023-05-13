import pandas as pd
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer

context_range = 3

csv_loc = "wws_train.csv"
data = pd.read_csv(csv_loc)
x_train, x_test, y_train, y_test = train_test_split(data["msg"], data["user"], test_size=0.2, random_state=42)


def predict(msg):
    cv = CountVectorizer(analyzer="word", ngram_range=(1, context_range), stop_words="english")
    x_train_cv = cv.fit_transform(x_train)

    clf = MultinomialNB()
    clf.fit(x_train_cv, y_train)

    return clf.predict(cv.transform([msg]))


def refit():
    global data
    global x_train, x_test, y_train, y_test
    data = pd.read_csv(csv_loc)
    x_train, x_test, y_train, y_test = train_test_split(data['msg'], data['user'], test_size=0.2, random_state=42)


def savetraindata(df):
    df.to_csv(csv_loc, index=False)
    print(csv_loc + " saved")


def wouldsay(user, msg):
    data2 = data
    data2.loc[data["user"] != user, "user"] = "not_user"
    x_spec_train, x_spec_test, y_spec_train, y_spec_test = train_test_split(data['msg'], data['user'], test_size=0.2, random_state=42)

    cv = CountVectorizer(analyzer='word', ngram_range=(1, context_range), stop_words='english')
    x_spec_train_cv = cv.fit_transform(x_spec_train)

    clf = MultinomialNB()
    clf.fit(x_spec_train_cv, y_spec_train)

    return clf.predict(cv.transform([msg]))
