import pandas as pd
from langdetect import detect
import json
import random

def load_json_data(path: str) -> list[str]:
    with open('assets/data.json', 'r') as file:
        data = json.load(file)
    city_data = [item['COMMUNE'] for item in data]
    return city_data

villes = load_json_data("assets/data.json")

phrases_incompletes = [
    "Je voudrais voir mon ami demain", "Quel temps fait-il à Paris ?", "Il pleut à Bordeaux en ce moment",
    "Je me demande où est Albert", "Une phrase sans origine ni destination", "Je vais faire du shopping",
    "Le restaurant est loin", "Il y a une bonne ambiance à la fête", "Je ne sais pas quoi faire ce week-end"
]

phrases_anglais = [
    "Is there any train from Paris to London?", "How do I get from New York to Boston?",
    "Is the train from Los Angeles to San Francisco available?", "Are there buses between Paris and Berlin?",
    "I want to travel from Rome to Florence"
]

def generate_trip_phrase():
    ville_depart = random.choice(villes)
    ville_arrivee = random.choice(villes)

    while ville_arrivee == ville_depart:
        ville_arrivee = random.choice(villes)
    phrases = [
        f"Je veux aller de {ville_depart} à {ville_arrivee}.",
        f"Comment me rendre à {ville_arrivee} depuis {ville_depart} ?",
        f"Y a-t-il des trains de {ville_depart} à {ville_arrivee} ?",
        f"Je prévois de voyager de {ville_depart} à {ville_arrivee} demain.",
        f"J'aimerai aller à {ville_arrivee} depuis {ville_depart}.",
        f"Je veux voyager à {ville_arrivee} de {ville_depart}",
    ]
    return random.choice(phrases), ville_depart, ville_arrivee

def generate_trip_phrase_with_intermediate():
    ville_depart = random.choice(villes)
    ville_arrivee = random.choice(villes)
    
    while ville_arrivee == ville_depart:
        ville_arrivee = random.choice(villes)

    nb_detour = random.randint(1, 5)
    villes_detour = []

    for _ in range(nb_detour):
        random_detour = random.choice(villes)
        while(random == ville_arrivee or random == ville_depart):
            random_detour = random.choice(villes)
        villes_detour.append(random_detour)

    phrases = [
        f"Je veux aller de {ville_depart} à {ville_arrivee} en passant par .",
        f"Comment me rendre à {ville_arrivee} depuis {ville_depart} en passant par ?",
        f"Y a-t-il des trains de {ville_depart} à {ville_arrivee} en passant par ?",
        f"Je prévois de voyager de {ville_depart} à {ville_arrivee} en coupant par .",
        f"J'aimerai aller à {ville_arrivee} depuis {ville_depart} en passant par .",
        f"Je veux voyager à {ville_arrivee} de {ville_depart} en faisant un détour par ",
    ]
    
    random_phrase = random.choice(phrases)
    last_char = random_phrase[len(random_phrase) - 1]
    random_phrase = random_phrase[:-1]

    for i in range(len(villes_detour)):
        if(i == len(villes_detour) - 1):
            random_phrase += f'{villes_detour[i]}{last_char}'
        elif i == len(villes_detour) - 2:
            random_phrase += f'{villes_detour[i]} et '
        else:
            random_phrase += f'{villes_detour[i]}, '

    return random_phrase, ville_depart, ville_arrivee

data = []

for i in range(1, 5001):
    phrase, origine, destination = generate_trip_phrase()
    data.append((i, phrase, origine, destination))

for i in range(5001, 7001):
    phrase = random.choice(phrases_incompletes)
    data.append((i, phrase, "NOT_TRIP", "NOT_TRIP"))

for i in range(7001, 9001):
    phrase = random.choice(phrases_anglais)
    data.append((i, phrase, "NOT_FRENCH", "NOT_FRENCH"))

for i in range(9001, 12001):
    phrase, origine, destination = generate_trip_phrase_with_intermediate()
    data.append((i, phrase, origine, destination))

df = pd.DataFrame(data, columns=['sequence', 'text', 'origin', 'destination'])

def detect_language(text):
    try:
        lang = detect(text)
        return 'NOT_FRENCH' if lang != 'fr' else 'FRENCH'
    except:
        return 'NOT_TRIP'

df['language'] = df['text'].apply(detect_language)

df['origin'] = df.apply(lambda x: 'NOT_FRENCH' if x['language'] == 'NOT_FRENCH' else x['origin'], axis=1)
df['destination'] = df.apply(lambda x: 'NOT_FRENCH' if x['language'] == 'NOT_FRENCH' else x['destination'], axis=1)

df.to_csv("dataset.csv", ";")