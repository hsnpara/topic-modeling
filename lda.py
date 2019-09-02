"""
[-]Preprocessing:
    [+]1) Parse files
    [+]2) Tokenization
    [+]3) Remove stopwords, numbers, punctuation
    [-]4) Lemmatization
    [-]5) Stemming
[+]Create BOW, remove the most and least frequent words, keep ~100k words
[+]Apply LDA
[-]Evaluate:
    [+]1) Topic Coherence Metric (CV)
    [-]2) tSNE Visualization
"""
import json
import nltk
nltk.download('punkt')
nltk.download('stopwords')
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from string import punctuation
from gensim.corpora import Dictionary
from gensim.models import LdaMulticore
from gensim.models.coherencemodel import CoherenceModel

def parse(files):
    documents = []
    for file in files:
        with open(file) as json_file:
            data = json.load(json_file)
            for i in data:
                documents.append(i['text'])
    return documents

def preprocess():
    files = ['wikisection_dataset_json/wikisection_en_city_train.json', 'wikisection_dataset_json/wikisection_en_disease_train.json']
    documents = parse(files)

    #tokenize
    tokenized_data = []
    for data in documents:
        tokenized_data.append(i.lower() for i in word_tokenize(data))

    #remove stopwords, numbers and punctuation
    stop_words = set(stopwords.words('english')) 
    filtered_data = []
    for data in tokenized_data:
        filtered_data.append([w for w in data if (w not in stop_words) and (not w.isdigit()) and (w not in punctuation)])

    return filtered_data

def create_bow(data):
    dct = Dictionary(data)
    dct.filter_extremes(no_below=20)
    bow = [dct.doc2bow(doc) for doc in data]
    return dct, bow

data = preprocess()
dct, bow = create_bow(data)
lda_model = LdaMulticore(bow, num_topics=2, id2word=dct, passes=5, workers=2)

#word weights for topics
for idx, topic in lda_model.print_topics(-1):
    print('Topic: {} \nWords: {}'.format(idx, topic))

#Topic Coherence
coherence_model_lda = CoherenceModel(model=lda_model, texts=data, corpus=bow, dictionary=dct, coherence='c_v')
coherence = coherence_model_lda.get_coherence()
print('\nCoherence Score: ', coherence)