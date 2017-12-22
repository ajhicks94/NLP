## Author: Anthony Hicks
## Class : CSCE 4930 - NLP
## Instr : Eduardo Blanco
## Descr : Creates a language model using trigrams and returns whether a text is more likely to be written in english or spanish

#!/usr/bin/env python

from __future__ import division
from optparse import OptionParser
from collections import defaultdict
from math import log10
import os, logging, re

def preprocess(line):
    ## get rid of the stuff at the end of the line
    line = line.rstrip()
    ## lower case
    line = line.lower()
    ## remove everything except characters and white space
    line = re.sub("[^a-z ]", '', line)

    tokens = line.split()
    tokens = ['$$'+token+'$$' for token in tokens]
    
    return tokens

def calc_prob(text, model):
    prob = 0.0
    f = open(text, 'r')
    smooth_const = 26*26

    ## Loop through each line
    for l in f.readlines():
        tokens = preprocess(l)
        if len(tokens) == 0:
           continue

        ## Loop through each token
        for token in tokens:
            ## Loop through each character
            for i, c in enumerate(token):
                if i >= (len(token) - 2):
                    continue
                else:
                    ## If we haven't seen this particular trigram
                    if(model[0][c][token[i+1]][token[i+2]] == 0):
                        prob += log10((1 / (model[1][c][token[i+1]] + smooth_const)))
                    else:
                        prob += model[0][c][token[i+1]][token[i+2]]

    return prob

def create_model(path):
    bigrams = defaultdict(lambda: defaultdict(int))
    trigrams = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    trigram_prob = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))

    f = open(path, 'r')
    ## You shouldn't visit a token more than once
    for l in f.readlines():
        tokens = preprocess(l)

        if len(tokens) == 0:
            continue

        for token in tokens:
            ## Loop through each character in the token, and update the counts
            for i, c in enumerate(token):
                ## If we're at the end of the token
                if i == (len(token) - 1):
                    continue
                if i == (len(token) - 2):
                    bigrams[c][token[i+1]] += 1
                else:
                    bigrams[c][token[i+1]] += 1
                    trigrams[c][token[i+1]][token[i+2]] += 1

    ## Calculate initial probabilities
    initial_prob(trigram_prob, trigrams, bigrams)

    return trigram_prob, bigrams

def initial_prob(tri_prob, tri, bi):
    smooth_const = 26*26

    ## Prob(xyz) = Count(xyz) / Count(xy)
    for x, second_chars in tri.iteritems():
        for y, third_chars in second_chars.iteritems():
            for z in third_chars:
                tri_prob[x][y][z] = log10(((tri[x][y][z] + 1) / (bi[x][y] + smooth_const)))

def predict(file, model_en, model_es):
    prob_en = calc_prob(file, model_en)
    prob_es = calc_prob(file, model_es)
    prediction = "English" if (prob_en > prob_es) else "Spanish"
    
    return prediction

def main(en_tr, es_tr, folder_te):

    ## Create a model for English with the english training documents
    model_en = create_model(en_tr)

    ## Create a model for Spanish with the spanish trainingn documents
    model_es = create_model(es_tr)

    ## STEP 3: loop through all the files in folder_te and print prediction
    folder = os.path.join(folder_te, "en")
    print "Prediction for English documents in test:"
    for f in os.listdir(folder):
        f_path =  os.path.join(folder, f)
        print "%s\t%s" % (f, predict(f_path, model_en, model_es))
    
    folder = os.path.join(folder_te, "es")
    print "\nPrediction for Spanish documents in test:"
    for f in os.listdir(folder):
        f_path =  os.path.join(folder, f)
        print "%s\t%s" % (f, predict(f_path, model_en, model_es))

if __name__ == "__main__":
    ## DO NOT CHANGE THIS CODE

    usage = "usage: %prog [options] EN_TR ES_TR FOLDER_TE"
    parser = OptionParser(usage=usage)

    parser.add_option("-d", "--debug", action="store_true",
                      help="turn on debug mode")

    (options, args) = parser.parse_args()
    if len(args) != 3:
        parser.error("Please provide required arguments")

    if options.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.CRITICAL)

    main(args[0], args[1], args[2])
