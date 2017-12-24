# Author: Anthony Hicks
# Class : NLP
# Instr : Eduardo Blanco
# Date  : Too close to the due date

#!/usr/bin/env python

from __future__ import division
from optparse import OptionParser
from collections import defaultdict

import sys
import os
import logging
import math
import operator
import utils

class V:
    def __init__(self, prob, prev):
        self.prob = prob
        self.prev = prev

def count_words_and_tags(sentences):

    unitags = defaultdict(int)
    bitags = defaultdict(lambda: defaultdict(int))
    wt_count = defaultdict(lambda: defaultdict(int))

    for sentence in sentences:

        for i, token in enumerate(sentence, start=0):

            unitags[token.tag] += 1
            wt_count[token.tag][token.word] += 1

            if i == len(sentence) - 1:
                continue
            else:
                bitags[token.tag][sentence[i+1].tag] += 1

    return wt_count, unitags, bitags

def calc_prob(wt_count, unitags, bitags):

    wt_prob = defaultdict(lambda: defaultdict(int))
    bitag_prob = defaultdict(lambda: defaultdict(int))

    # Smooth and log probabilities (I was using log prob, but for some reason it was making my accuracy go down...I'm not sure why)
    for x, next_tags in bitags.iteritems():
        for y in next_tags:
            bitag_prob[x][y] = ((bitags[x][y] + 1) / (unitags[x] + 36))

    for tag, words in wt_count.iteritems():
        for word in words:
            wt_prob[tag][word] = ((wt_count[tag][word]) / (unitags[tag]))

    return wt_prob, bitag_prob

def create_model(sentences):

    counts = count_words_and_tags(sentences)

    probs = calc_prob(counts[0], counts[1], counts[2])

    wt_prob = probs[0]
    bitag_prob = probs[1]

    tag_list = []

    # Populate tag list for matrix bounds
    for tag in counts[1]:
        tag_list.append(tag)

    print "Count of ./.= ", counts[0]['.']['.']
    print "Prob. of ./.= ", wt_prob['.']['.']
    print "Count of ./UH=", counts[0]['.']['UH']
    print "Prob. of ./UH=", counts[0]['.']['UH']
    
    return wt_prob, bitag_prob, counts[1], tag_list, counts[0]

def viterbi_populate(sentence, wt_prob, bitag_prob, tag_list):
    matrix = [[0.0 for x in range(len(sentence))] for y in range(len(tag_list))]

    backtrack = []

    for j in range(len(sentence)):

        if j > 0:
            temp_m = -sys.maxint - 1
            max_prob_index = ()
            for k in range(len(tag_list)):
                if temp_m < matrix[k][j-1]:
                        max_prob_index = (k,j-1)
                        temp_m = matrix[k][j-1]

            backtrack.append(max_prob_index)

        for i in range(len(tag_list)):
            if j == 0:
                matrix[i][j] = wt_prob[tag_list[i]][sentence[j]] * bitag_prob['<s>'][tag_list[i]]
            else:
                maximum = 0.0

                for k in range(len(tag_list)):
                    maximum = max(maximum, matrix[k][j-1] * bitag_prob[tag_list[k]][tag_list[i]])
                matrix[i][j] = wt_prob[tag_list[i]][sentence[j]] * maximum

    #backtrack.reverse()

    final_tags = ['<s>']

    for tu in backtrack:
        final_tags.append(tag_list[tu[0]])

    return final_tags

def predict_tags(sentences, model):
    # Create a matrix per sentence
    #counter = 0
    for sentence in sentences:
        final_tags = viterbi_populate(sentence, model[0], model[1], model[3])

        for j, token in enumerate(sentence):
            token.tag = final_tags[j]
    return sentences
                #else:
                #    maximum = 0
                #    back = 0
                    # argmax()
                #    for k, t in enumerate(model[3]):
                #        temp = (matrix[k][j-1].prob * model[1][t][tags])
                #        if(temp > maximum):
                #            maximum = temp
                #            back = k
                #    # Fill the cell
                #    matrix[i][j].prob = model[0][token.word][tags] * maximum
                #    matrix[i][j].prev = back

        # Find the cell in V matrix to start with
       # y = len(sentence) - 1
       # tag_sequence = []
# THIS IS PART OF THE PROBLEM
       # last_tag_index = 1
       # print "y= ", y
       # for i, tags in enumerate(model[3]):
       #     if matrix[i][y].prob > maximum:
       #         print "last_tag_index now = ", i
       #         last_tag_index = i
       # tag_sequence.insert(0, model[3][i])
       # print "Starting at [", last_tag_index, "][", y, "]"
        #print "Sentence: ",
        #for words in sentence:
        #    print words.word, " ",

       # print "\nExpected tags: ",
       # for words in sentence:
       #     print words.tag, " ",
        # Going R->L in Viterbi matrix while also adding the tags to the main sequence
       # for j in xrange(len(sentence) - 1, 0, -1):
       #     print "[", last_tag_index, "][", y, "] points back to: ", model[3][matrix[last_tag_index][j].prev]
       #     if j == 0:
       #         break
       #     tag_sequence.insert(0, model[3][matrix[last_tag_index][j].prev])
       #     
       #     last_tag_index = matrix[last_tag_index][j].prev

        # Change tags
       # print "\nAssigned tags: ",
        #if counter == 2:
        #    break
       # counter += 1
    #return sentences

if __name__ == "__main__":
    usage = "usage: %prog [options] GOLD TEST"
    parser = OptionParser(usage=usage)

    parser.add_option("-d", "--debug", action="store_true",
                      help="turn on debug mode")

    (options, args) = parser.parse_args()
    if len(args) != 2:
        parser.error("Please provide required arguments")

    if options.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.CRITICAL)

    training_file = args[0]
    training_sents = utils.read_tokens(training_file)
    test_file = args[1]
    test_sents = utils.read_tokens(test_file)

    model = create_model(training_sents)
    ## read sentences again because predict_tags(...) rewrites the tags
    #sents = utils.read_tokens(training_file)
    #predictions = predict_tags(sents, model)
    #accuracy = utils.calc_accuracy(training_sents, predictions)
    #print "Accuracy in training [%s sentences]: %s" % (len(sents), accuracy)

    ## read sentences again because predict_tags(...) rewrites the tags
    sents = utils.read_tokens(test_file)
    predictions = predict_tags(sents, model)
    accuracy = utils.calc_accuracy(test_sents, predictions)
    print "Accuracy in testing [%s sentences]: %s" % (len(sents), accuracy)
