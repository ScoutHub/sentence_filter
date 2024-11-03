# python3 -m spacy download fr_core_news_md to install french core

import random
import re
import spacy.training
from unidecode import unidecode
import json
import os

# nltk import
import nltk

# spacy import
import spacy
from spacy.lang.fr.stop_words import STOP_WORDS
from spacy.training import Example
from spacy.util import minibatch, compounding

def load_json_data(path: str) -> list[str]:
    with open('assets/data.json', 'r') as file:
        data = json.load(file)
    city_data = [item['COMMUNE'] for item in data]
    return city_data

def prepare_training_data(city_data):
    train_data = []
    pre_sentence = []
    with open('sentence2.txt') as f:
        [pre_sentence.append(line.rstrip()) for line in f.readlines()]
    for city_name in city_data:
        formated_city = unidecode(city_name)
        formated_city = re.sub(r'[^\w\s]', '', formated_city)
        
        random_sentence = pre_sentence[random.randint(0, len(pre_sentence) - 1)]
        sentence = random_sentence.replace("#", formated_city)
        start_idx = sentence.index(formated_city)
        end_idx = start_idx + len(formated_city)

        sentence = unidecode(sentence)
        sentence = re.sub(r'[^\w\s]', '', sentence)
        
        train_data.append((sentence.lower(), {'entities': [(start_idx, end_idx, 'LOC')]}))
    
    return train_data

def install_dependencies():
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('averaged_perceptron_tagger')
    nltk.download('averaged_perceptron_tagger_eng')
    nltk.download('maxent_ne_chunker_tab')
    nltk.download('maxent_ne_chunker')
    nltk.download('words')
    nltk.download('wordnet')

def train_ner_model(train_data, model='fr_core_news_lg', output_dir=None, n_iter=10):
    nlp = None
    if(os.path.isdir('model_ner')):
        nlp = spacy.load('model_ner')
        return nlp
    
    nlp = spacy.load(model)
    ner = nlp.get_pipe('ner')

    for _, annotations in train_data:
        for ent in annotations.get("entities"):
            ner.add_label(ent[2])

    # Deactivate other pipes
    pipe_exceptions = ["ner", "trf_wordpiecer", "trf_tok2vec"]
    unaffected_pipes = [pipe for pipe in nlp.pipe_names if pipe not in pipe_exceptions]

    # Deactivate other pipes while training
    with nlp.disable_pipes(*unaffected_pipes):
        for iteration in range(n_iter):
            print(f"Iteration {iteration + 1} / {n_iter}")
            # Randomize train data
            random.shuffle(train_data)
            losses = {}

            # Batching train data
            batches = minibatch(train_data, size=compounding(4.0, 32.0, 1.001))

            for batch in batches:
                texts, annotations = zip(*batch)
                examples = []

                for text, annot in zip(texts, annotations):
                    doc = nlp.make_doc(text)
                    example = Example.from_dict(doc, annot)
                    examples.append(example)

                nlp.update(
                    examples,
                    drop=0.5,
                    losses=losses,
                )
            print(f"Losses at iteration {iteration + 1}: {losses}")
    
    if output_dir:
        nlp.to_disk(output_dir)
        print(f"Modèle enregistré dans {output_dir}")

    return nlp

def generate_sentence(cities) -> str:
    variations_depart = [
        "Je veux partir de", "Je désire quitter", "Je compte partir de", "J'ai l'intention de quitter", 
        "Je souhaite partir de", "Je rêve de quitter", "Je veux m'envoler de", "Je prévois de partir de", 
        "Je projette de quitter", "Je voudrais partir de"
    ]

    variations_arrivee = [
        "pour aller à", "afin de me rendre à", "vers", "en direction de", "pour rejoindre", 
        "à destination de", "pour visiter", "afin de découvrir", "dans le but d'aller à", "pour explorer"
    ]

    depart = random.choice(cities)
    arrivee = random.choice(cities)
    while depart == arrivee:
        arrivee = random.choice(cities)
    sentence = f"{random.choice(variations_depart)} {depart} {random.choice(variations_arrivee)} {arrivee}."
    return sentence.lower()

def spacy_process(nlp, sentence):
    sentence = sentence.lower()

    sentence = unidecode(sentence)
    sentence = re.sub(r'[^\w\s]', '', sentence)

    if(nlp == None): 
        nlp = spacy.load('fr_core_news_md')
    
    # Tokenisation, POS tagging, Lemmatisation and NER via spaCy
    doc = nlp(sentence)

    # Deleting stopwords
    filtered_tokens = [token for token in doc if token.text not in STOP_WORDS]

    # Lemmatisation
    lemmatized_tokens = [token.lemma_ if token.pos_ != 'PROPN' else token.text for token in filtered_tokens]

    # POS Tagging
    pos_tags = [(token.text, token.pos_) for token in filtered_tokens]

    # Filtrage incorrect entities
    named_entities = [(ent.text, ent.label_) for ent in doc.ents]

    # Show results
    # print(sentence)
    # print("Tokenisation : ", [token.text for token in doc])
    # print("Tokens filtrés (sans stopwords) : ", [token.text for token in filtered_tokens])
    # print("Lemmatisation : ", lemmatized_tokens)
    # print("POS Tagging : ", pos_tags)
    # print("Reconnaissance des entités nommées : ", named_entities)

    locations = [ent.text for ent in doc.ents if ent.label_ == 'LOC']
    print(f'locations: {locations}')
    
    source, destination = None, None
    for token in doc:
        if token.lemma_ in ['aller', 'partir', 'voyager', 'se rendre']:
            destination = find_next_location(token, doc)
        if token.lemma_ in ['à', 'de', 'depuis']:
            source = find_next_location(token, doc)

    if not source and locations:
        source = locations[0]
    if not destination and locations:
        destination = locations[-1]
    
    # Afficher les résultats
    # print("Phrase:", sentence)
    print("Source:", source)
    print("Destination:", destination)
    return source, destination

def find_next_location(token, doc):
    for next_token in doc[token.i:]:
        if next_token.ent_type_ == 'LOC':
            return next_token.text
    return None

if __name__ == "__main__":
    
    # Delete the comment if install is necessary
    # install_dependencies()
    
    city_data = load_json_data('assets/data.json')
    train_data = prepare_training_data(city_data)
    sentences = [generate_sentence(city_data) for i in range(20)]

    nlp = train_ner_model(train_data, output_dir='model_ner', n_iter=3)

    # sentence = input("Comment puis-je vous aider ?\n")
    # sentence = """Je suis à Lyon, qui est une très belle ville, et je veux aller à Paris"""
    # sentence = """Je voudrais aller à Lyon depuis Paris."""
    # sentence = """En passant par Lille, Nice, et Marseille j'aimerai aller à Paris depuis Strasbourg"""
    
    sentences = [
        {"sentence": "Je suis à Lyon, qui est une très belle ville, et je veux aller à Paris", "source": "Lyon", "dest": "Paris"},
        {"sentence": "Je voudrais aller à Lyon depuis Paris.", "source": "Paris", "dest": "Lyon"},
        {"sentence": "En passant par Lille, Nice, et Marseille j'aimerai aller à Paris depuis Strasbourg", "source": "Strasbourg", "dest": "Paris"},
        {"sentence": "Je voudrais aller à Lyon depuis Paris en passant par Maseille et Strasbourg.", "source": "Paris", "dest": "Lyon"},
    ]

    for sentence in sentences:
        print(f"sentence: {sentence['sentence']}, source: {sentence['source']}, dest: {sentence['dest']}")
        sentence = sentence['sentence'].lower()

        sentence = unidecode(sentence)
        sentence = re.sub(r'[^\w\s]', '', sentence)

        spacy_process(nlp, sentence)
        print('##################')
    
    # sentence = sentence.lower()

    # # Deleting special characters
    # sentence = unidecode(sentence)
    # sentence = re.sub(r'[^\w\s]', '', sentence)

    # spacy_process(nlp, sentence)