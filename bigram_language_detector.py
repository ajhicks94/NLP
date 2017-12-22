## Author: Anthony Hicks
## Class : CSCE 4930 - NLP
## Instr : Eduardo Blanco
## Descr : Creates a language model using bigrams and calculates the probablility of a text being in english and spanish, and returns the higher of the two

#!/usr/bin/env python

from __future__ import division
from optparse import OptionParser
import os, logging, re, math
import collections


def preprocess(line):
    ## get rid of the stuff at the end of the line
    line = line.rstrip()
    ## lower case
    line = line.lower()
    ## remove everything except characters and white space
    line = re.sub("[^a-z ]", '', line)

    tokens = line.split()
    tokens = ['$'+token+'$' for token in tokens]
    
    return tokens

def calc_prob(text, model):
    prob = 0.0
    f = open(text, 'r')

    for l in f.readlines():
        tokens = preprocess(l)
        if len(tokens) == 0:
           continue

        for token in tokens:
            for i, char in enumerate(token):
                if i == (len(token) - 1):
                    continue
                else:
                    if(model[0][char][token[i+1]] == 0):
                        prob += math.log10((1 / (model[1][char] + 26)))
                    else:
                        prob += model[0][char][token[i+1]]

    return prob

def create_model(path):
    unigrams = collections.defaultdict(int)
    bigrams = collections.defaultdict(lambda: collections.defaultdict(int))
    bigram_prob = collections.defaultdict(lambda: collections.defaultdict(int))

    f = open(path, 'r')
    ## For each line in the file
    for l in f.readlines():
        ## Preprocess the line
        tokens = preprocess(l)

        if len(tokens) == 0:
            continue

        ## Loop through each token
        for token in tokens:

            ## Loop through each character and update the counts
            for i, char in enumerate(token):
                ## If we're at the end of the token
                if i == (len(token) - 1):
                    unigrams[char] += 1
                else:
                    unigrams[char] += 1
                    bigrams[char][token[i+1]] += 1

    for prev_char, next_chars in bigrams.iteritems():
        for next_char in next_chars:
            bigram_prob[prev_char][next_char] = math.log10(((bigrams[prev_char][next_char] + 1) / (unigrams[prev_char] + 26)))

    return bigram_prob, unigrams

def predict(file, model_en, model_es):
    prob_en = calc_prob(file, model_en)
    prob_es = calc_prob(file, model_es)

    prediction = "English" if (prob_en > prob_es) else "Spanish"
    
    return prediction

def main(en_tr, es_tr, folder_te):
    ## DO NOT CHANGE THIS METHOD

    ## STEP 1: create a model for English with en_tr
    model_en = create_model(en_tr)
    ## STEP 2: create a model for Spanish with es_tr
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
