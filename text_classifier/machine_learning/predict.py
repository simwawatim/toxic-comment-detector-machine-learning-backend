from text_classifier.models import StoredModel
from django.shortcuts import render
from nltk.corpus import stopwords
import re, string
import numpy as np
import pickle


stopwords_english = stopwords.words('english')

def preprocess(corpus):
    """Clean and preprocess text"""
    for text in corpus:
        text = text.lower()
        text = re.sub(r'https?://[^\s\n\r]+', '', text)  
        text = re.sub('[%s]' % re.escape(string.punctuation), '', text)
        text = re.sub(r'\w*\d\w*', '', text) 
        yield ' '.join([word for word in text.split() if word not in stopwords_english])

def load_models_from_db():
    models = {}
    logs = {}
    vectorizer = None

    stored_objects = StoredModel.objects.all()
    for obj in stored_objects:
        data = pickle.loads(obj.binary_file)
        if obj.name == 'vectorizer':
            vectorizer = data
        elif obj.name == 'logs':
            logs = data
        elif obj.name.startswith('model_'):
            label = obj.name.replace('model_', '')
            models[label] = data

    return vectorizer, logs, models

vectorizer, trained_logs, trained_models = load_models_from_db()
labels = list(trained_models.keys())

def predict_new_text(text):
    cleaned = list(preprocess([text]))
    bow_input = vectorizer.transform(cleaned)

    results = {}
    for label in labels:
        model = trained_models[label]
        log = trained_logs[label]

        x = bow_input.dot(log).reshape(1, -1)
        prediction = model.predict(x)
        results[label] = "Yes" if prediction[0] == 1 else "No"

    return results
