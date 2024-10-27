import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline

data = pd.read_csv("dataset.csv", delimiter=";")

data['label'] = data.apply(lambda row: f"{row['origin']},{row['destination']}" if row['language'] == "FRENCH" else row['language'], axis=1)

X_train, X_test, y_train, y_test = train_test_split(data['text'], data['label'], test_size=0.2, random_state=42)

pipeline = Pipeline([
    ('tfidf', TfidfVectorizer()),
    ('clf', SVC())
])

pipeline.fit(X_train, y_train)

y_pred = pipeline.predict(X_test)

def predict_trip(text):
    return pipeline.predict([text])[0]

print(predict_trip("Je suis à Marseille et je veux aller à Paris"))
print(predict_trip("Je suis à Marseille et je veux aller à Paris en passant par Metz, Strasbourg et Reims"))
print(predict_trip("Il pleut à Paris."))
print(predict_trip("Is there a train from Nice to Marseille?"))
