# -*- coding: utf-8 -*-
"""
Created on Thu Nov  1 19:23:22 2018

@author: noyana
"""

import metapy
import re
import os

#curr_dir = os.getcwd()
#os.chdir('..')
#def load_textinfo(text_config_file):
txt_fwd_idx = metapy.index.make_forward_index('uiuc-textinfo-config.toml')

# load data

fwd_idx = metapy.index.make_forward_index('config.toml')
inv_idx = metapy.index.make_inverted_index('config.toml')
fwd_idx.num_docs()
fwd_idx.unique_terms()
fwd_idx.metadata(0).get("title")
fwd_idx.metadata(0).get("path")
fwd_idx.metadata(0).get("url")
fwd_idx.metadata(0).get("description")
fwd_idx.metadata(0).get("content")

query = metapy.index.Document()
doc_id = 0
title = txt_fwd_idx.metadata(doc_id).get('title')
description = txt_fwd_idx.metadata(doc_id).get('description')

query_content = re.sub(r'(-|\. | \|)', r' ', title)
query.content(query_content)
#query.content("lagrange multipler")

print(query_content)

# find ranker
bm25 = metapy.index.OkapiBM25()
rocchio = metapy.index.Rocchio(fwd_idx, bm25)
top_docs = rocchio.score(inv_idx, query, num_results=10)

for num, (d_id, score) in enumerate(top_docs):
    content = inv_idx.metadata(d_id).get('description')
    print("{}. {}...\n".format(d_id, content))
    print ("{}. {}..\n".format(inv_idx.label(d_id), score))



dset = metapy.learn.Dataset(txt_fwd_idx)


#alpha	The hyperparameter for the Dirichlet prior over \(\phi\)
#beta	The hyperparameter for the Dirichlet prior over \(\theta\)
#

lda_inf = metapy.topics.LDACollapsedVB(dset, num_topics=2, alpha=1.0, beta=0.01)
lda_inf.run(num_iters=1000)
lda_inf.save('lda-cvb0-textinfo')

model = metapy.topics.TopicModel('lda-cvb0-textinfo')
model.top_k(tid=0)
[(fwd_idx.term_text(pr[0]), pr[1]) for pr in model.top_k(tid=0)]
[(fwd_idx.term_text(pr[0]), pr[1]) for pr in model.top_k(tid=1)]
#[(fwd_idx.term_text(pr[0]), pr[1]) for pr in model.top_k(tid=2)]

scorer = metapy.topics.BLTermScorer(model)
[(fwd_idx.term_text(pr[0]), pr[1]) for pr in model.top_k(tid=0, scorer=scorer)]

[(fwd_idx.term_text(pr[0]), pr[1]) for pr in model.top_k(tid=1, scorer=scorer)]

# use the top ranked term as query




# view fwd idx
fwd_idx.num_docs()
fwd_idx.unique_terms()
#fwd_idx.avg_doc_length()
#fwd_idx.total_corpus_terms()

# try to extract sequences
with open("data/cs-410/02_week-1/02_week-1-lessons/05_lesson-1-5-vector-space-model-basic-idea.en.txt") as f:
    vs = f.readlines()
vs[0].strip()

def extract_sequences(tok):
    sequences = []
    for token in tok:
        if token == '<s>' or len(sequences) == 0:
            sequences.append(metapy.sequence.Sequence())
        elif token != '</s>':
            print ("length",len(sequences))
            sequences[-1].add_symbol(token)            
    return sequences

#tok.set_content(doc.content())
for seq in extract_sequences(vs[0].strip()):
    print(seq)

fwd_idx.metadata(0).get('content')



ana = metapy.analyzers.load("config.toml")
doc = metapy.index.Document()
doc.content("the both querying nad browsing. If you want to know more about")
ana.analyze(doc)


###############
# classification
###############
# get label for each class
dset = metapy.classify.MulticlassDataset(fwd_idx)
labels = set([dset.label(instance) for instance in dset])
labels = list(labels)
label = labels[0]
label = re.sub(r'-', r' ', label)
query = metapy.index.Document()
#query.content(label)
query.content("langrange multiplier")
bm25 = metapy.index.OkapiBM25()
rocchio = metapy.index.Rocchio(fwd_idx, bm25)
top_docs = rocchio.score(inv_idx, query, num_results=5)

for num, (d_id, score) in enumerate(top_docs):
    #content = inv_idx.metadata(d_id).get('content')
    #print("{}. {}...\n".format(num + 1, content[0:250]))
    print ("{}. {}..\n".format(inv_idx.label(d_id), score))
    
###############
# topic model
###############
# load documents into our memory


#alpha = 1.0    # original query weight parameter
#beta = 1.0     # feedback document weight parameter
#k = 10         # number of feedback documents to retrieve
#max-terms = 50 # maximum number of feedback terms to use
#[ranker.feedback]
#method = # whatever ranker method you want to wrap
# other parameters for that ranker
