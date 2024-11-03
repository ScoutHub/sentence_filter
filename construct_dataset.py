import pandas as pd
from langdetect import detect
import json
import random

def load_json_data(path: str) -> list[str]:
    with open(path, 'r') as file:
        data = json.load(file)
    city_data = [item['label'] for item in data["cities"]]
    return city_data

villes = load_json_data("assets/cities.json")

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
    ville_depart = random.choice(villes).lower()
    ville_arrivee = random.choice(villes).lower()

    while ville_arrivee == ville_depart:
        ville_arrivee = random.choice(villes).lower()
    phrases = [
        f"Je veux aller de {ville_depart} à {ville_arrivee}.",
        f"Je veux aller à {ville_arrivee} depuis {ville_depart}.",
        f"Je suis à {ville_arrivee} et je veux aller à {ville_depart}.",
        f"Comment me rendre à {ville_arrivee} depuis {ville_depart} ?",
        f"Y a-t-il des trains de {ville_depart} à {ville_arrivee} ?",
        f"Je prévois de voyager de {ville_depart} à {ville_arrivee} demain.",
        f"J'aimerai aller à {ville_arrivee} depuis {ville_depart}.",
        f"Je veux voyager à {ville_arrivee} de {ville_depart}",
        f"Quel est le trajet de {ville_depart} à {ville_arrivee} ?",
        f"Voyage de {ville_depart} jusqu'à {ville_arrivee}",
    ]
    return random.choice(phrases), ville_depart, ville_arrivee

def generate_trip_phrase_with_intermediate():
    ville_depart = random.choice(villes).lower()
    ville_arrivee = random.choice(villes).lower()
    
    while ville_arrivee == ville_depart:
        ville_arrivee = random.choice(villes).lower()

    nb_detour = random.randint(1, 5)
    villes_detour = []

    for _ in range(nb_detour):
        random_detour = random.choice(villes)
        while(random == ville_arrivee or random == ville_depart):
            random_detour = random.choice(villes)
        villes_detour.append(random_detour.lower())

    phrases = [
        f"Je veux aller de {ville_depart} à {ville_arrivee} en passant par #.",
        f"Comment me rendre à {ville_arrivee} depuis {ville_depart} en passant par #?",
        f"Y a-t-il des trains de {ville_depart} à {ville_arrivee} en passant par # ?",
        f"Je prévois de voyager de {ville_depart} à {ville_arrivee} en coupant par #",
        f"J'aimerai aller à {ville_arrivee} depuis {ville_depart} en passant par #",
        f"Je veux voyager à {ville_arrivee} de {ville_depart} en faisant un détour par #",
        f"Je veux aller à {ville_arrivee} depuis {ville_depart} en passant par #.",
        f"Je suis à {ville_arrivee} et je veux aller à {ville_depart} en passant par #.",
        f"En passant par #, je veux aller de {ville_depart} à {ville_arrivee}.",
        f"En passant par #, comment me rendre à {ville_arrivee} depuis {ville_depart} ?",
        f"En passant par #, y a-t-il des trains de {ville_depart} à {ville_arrivee} ?",
        f"En passant par #, je prévois de voyager de {ville_depart} à {ville_arrivee}.",
        f"En passant par #, j'aimerai aller à {ville_arrivee} depuis {ville_depart}.",
        f"En faisant un détour par #, je veux voyager à {ville_arrivee} de {ville_depart}.",
        f"En passant par #, je veux aller à {ville_arrivee} depuis {ville_depart}.",
    ]
    
    random_phrase = random.choice(phrases)

    last_index = random_phrase.find("#")
    begin = random_phrase[:last_index]
    end = random_phrase[last_index:].replace("#", "")

    for i in range(len(villes_detour)):
        if(i == len(villes_detour) - 1):
            begin += f'{villes_detour[i]}'
        elif(i == len(villes_detour) - 2):
            begin += f'{villes_detour[i]} et '
        else:
            begin += f'{villes_detour[i]}, '

    detours = ','.join(villes_detour)

    random_phrase = begin + end
    return random_phrase, ville_depart, ville_arrivee, detours

data = []

for _ in range(10000):
    phrase, origine, destination = generate_trip_phrase()
    data.append((phrase, origine, destination))

for _ in range(3000):
    phrase = random.choice(phrases_incompletes)
    data.append((phrase, "NOT_TRIP", "NOT_TRIP"))

for i in range(7000):
    phrase, origine, destination, detours = generate_trip_phrase_with_intermediate()
    data.append((phrase, origine, destination, detours))

df = pd.DataFrame(data, columns=['text', 'origin', 'destination', 'detours'])

def detect_language(text):
    try:
        lang = detect(text)
        return 'NOT_FRENCH' if lang != 'fr' else 'FRENCH'
    except:
        return 'NOT_TRIP'

# df['language'] = df['text'].apply(detect_language)

# df['origin'] = df.apply(lambda x: 'NOT_FRENCH' if x['language'] == 'NOT_FRENCH' else x['origin'], axis=1)
# df['destination'] = df.apply(lambda x: 'NOT_FRENCH' if x['language'] == 'NOT_FRENCH' else x['destination'], axis=1)

df.to_csv("dataset.csv", ";")