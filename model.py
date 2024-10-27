import pandas as pd

df = pd.read_csv('dataset.csv', delimiter=';')

print(df.head())

from sklearn.feature_extraction.text import TfidfVectorizer

X = df['text']
y_origin = df['origin']
y_destination = df['destination']

vectorizer = TfidfVectorizer(ngram_range=(1, 2))
X_tfidf = vectorizer.fit_transform(X)

from sklearn.preprocessing import LabelEncoder

encoder_origin = LabelEncoder()
encoder_destination = LabelEncoder()

y_origin_encoded = encoder_origin.fit_transform(y_origin)
y_destination_encoded = encoder_destination.fit_transform(y_destination)

from sklearn.model_selection import train_test_split

X_train, X_test, y_origin_train, y_origin_test = train_test_split(X_tfidf, y_origin_encoded, test_size=0.2, random_state=42)
X_train, X_test, y_destination_train, y_destination_test = train_test_split(X_tfidf, y_destination_encoded, test_size=0.2, random_state=42)

from sklearn.svm import LinearSVC
from sklearn.metrics import accuracy_score
from sklearn.ensemble import RandomForestClassifier

model_origin = RandomForestClassifier()
model_origin.fit(X_train, y_origin_train)

model_destination = LinearSVC()
model_destination.fit(X_train, y_destination_train)

y_origin_pred = model_origin.predict(X_test)
y_destination_pred = model_destination.predict(X_test)

accuracy_origin = accuracy_score(y_origin_test, y_origin_pred)
accuracy_destination = accuracy_score(y_destination_test, y_destination_pred)

print(f"Précision pour l'origine: {accuracy_origin:.02f}")
print(f"Précision pour la destination: {accuracy_destination:.02f}")

def predict_trip(text):
    text_tfidf = vectorizer.transform([text])
    predicted_origin = encoder_origin.inverse_transform(model_origin.predict(text_tfidf))
    predicted_destination = encoder_destination.inverse_transform(model_destination.predict(text_tfidf))
    return predicted_origin[0], predicted_destination[0]

text_example = "Je suis à Marseille et je veux aller à Lille"
origin, destination = predict_trip(text_example)
print(f"Origine: {origin}, Destination: {destination}")
