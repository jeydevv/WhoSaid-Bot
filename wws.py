import pandas as pd
from math import ceil


async def savetraindata(df, server_csv):
    user_msgcount = {}
    min_msgs = 0

    for userid in df["user"].unique():
        count = len(df.loc[df["user"] == userid])
        user_msgcount[userid] = count
        min_msgs += count
    min_msgs = ceil((min_msgs / len(df["user"].unique())))

    for userid in df["user"].unique():
        if user_msgcount[userid] < min_msgs:
            df = df[df.user != userid]

    max_msgs = 0
    for i in user_msgcount:
        if user_msgcount[i] > max_msgs:
            max_msgs = user_msgcount[i]

    for user in df['user'].unique():
        new_msg_count = max_msgs - user_msgcount[user] + 1
        user_msgs = df[df.user == user]
        x = 0
        for i in range(1, new_msg_count):
            to_add = user_msgs.iloc[x]
            df = pd.concat([df, to_add], ignore_index=True)
            df.loc[len(df)] = to_add
            x += 1
            if x == len(user_msgs):
                x = 0
    df = df[df['user'].notna()]
    df = df.drop(df.columns[2], axis=1)

    df.to_csv(server_csv, index=False)
    print(server_csv + " saved")

""" Obsolete: old method using N-GRAM and NAIVE BAYES
# Ideal context range found by testing F1 and accuracy of ranges from 1-10
CONTEXT_RANGE = 4

async def predict(msg, server_csv):
    data = pd.read_csv(server_csv)
    x_train, x_test, y_train, y_test = train_test_split(data["msg"], data["user"], test_size=0.2, random_state=42)

    cv = CountVectorizer(analyzer="word", ngram_range=(1, CONTEXT_RANGE), stop_words="english")
    x_train_cv = cv.fit_transform(x_train)

    clf = MultinomialNB()
    clf.fit(x_train_cv, y_train)

    return clf.predict(cv.transform([msg]))
"""
