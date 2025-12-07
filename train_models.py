#!/usr/bin/env python3
import os
import django
import sys

# Ensure the project root is in PYTHONPATH
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")
django.setup()

import pandas as pd
import numpy as np
import re, string
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from nltk.corpus import stopwords
import pickle

from text_classifier.models import StoredModel

stopwords_english = stopwords.words('english')

def preprocess(corpus):
    for text in corpus:
        text = text.lower()
        text = re.sub(r'https?://[^\s\n\r]+', '', text)
        text = re.sub('[%s]' % re.escape(string.punctuation), '', text)
        text = re.sub(r'\w*\d\w*', '', text)
        yield ' '.join([word for word in text.split() if word not in stopwords_english])

def probNB(bow, target, cat):
    mask = (target == cat).to_numpy()
    p = np.array(bow[mask].sum(axis=0))
    return np.transpose((p + 1) / (p.sum() + bow.shape[1]))

# ---------------------------
# Load training data
# ---------------------------
train_data = pd.read_csv('train.csv')
clean_comments = list(preprocess(train_data['comment_text']))
vectorizer = TfidfVectorizer(min_df=3, max_df=0.9)
bow = vectorizer.fit_transform(clean_comments)
target = train_data[['toxic','severe_toxic','obscene','threat','insult','identity_hate']]

# ---------------------------
# Train models
# ---------------------------
trained_models = {}
trained_logs = {}

for col in target.columns:
    log = np.log(probNB(bow, target[col], 1) / probNB(bow, target[col], 0))
    m = bow.dot(log)
    model = LogisticRegression(C=0.5, max_iter=500, solver='lbfgs', random_state=42)
    model.fit(m, target[col])
    trained_models[col] = model
    trained_logs[col] = log

# ---------------------------
# Save models to database
# ---------------------------
StoredModel.objects.update_or_create(
    name='vectorizer',
    defaults={'binary_file': pickle.dumps(vectorizer)}
)
StoredModel.objects.update_or_create(
    name='logs',
    defaults={'binary_file': pickle.dumps(trained_logs)}
)
for label, model in trained_models.items():
    StoredModel.objects.update_or_create(
        name=f'model_{label}',
        defaults={'binary_file': pickle.dumps(model)}
    )

print("All models saved successfully to the database!")
