import os
import requests
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import joblib

csv_file = "fake_and_real_news_dataset.csv"

data = pd.read_csv(csv_file)
data["text"] = data["title"].fillna("") + " " + data["text"].fillna("")
data["label"] = data["label"].str.upper().replace({"FALSE":"FAKE","TRUE":"REAL"})
data = data.dropna(subset=["text","label"]).drop_duplicates(subset=["text"])

print(f"Number of articles: {len(data)}")
print(data["label"].value_counts())

# Map labels to numbers
label2num = {"FAKE":0, "REAL":1}
num2label = {0:"FAKE",1:"REAL"}
data["label_num"] = data["label"].map(label2num)

X_train, X_test, y_train, y_test = train_test_split(
    data["text"], data["label_num"], test_size=0.2, random_state=42, stratify=data["label_num"]
)

vectorizer = TfidfVectorizer(stop_words="english", max_features=10000)
X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

model = LogisticRegression(max_iter=300)
model.fit(X_train_vec, y_train)

# Save the model and vectorizer
joblib.dump(model, "lr_model.pkl")
joblib.dump(vectorizer, "tfidf.pkl")
print("Model trained and saved")

def predict(text):
    vec = vectorizer.transform([text])
    pred = model.predict(vec)[0]
    return num2label[pred]

# Example usage
example1 = "Breaking: NASA confirms discovery of new planet with intelligent life!"
example2 = "The local school announced a new math curriculum for next year."

print("Example 1 Prediction:", predict(example1))
print("Example 2 Prediction:", predict(example2))