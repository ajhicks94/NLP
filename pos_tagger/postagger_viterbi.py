# Author: Anthony Hicks
# Class : NLP

#!/usr/bin/env python

from __future__ import division
from optparse import OptionParser
from collections import defaultdict

import sys
import os
import logging
import operator
import utils

class HMM:
    def __init__(self, sentences):
        self.unitags = defaultdict(int)
        self.bitags = defaultdict(lambda: defaultdict(int))
        self.wt_count = defaultdict(lambda: defaultdict(int))
        self.wt_prob = defaultdict(lambda: defaultdict(int))
        self.bitag_prob = defaultdict(lambda: defaultdict(int))
        self.tag_list = []

        self.create_model(sentences)

    def count_words_and_tags(self, sentences):
        for sentence in sentences:
            z = len(sentence) - 1

            for i in xrange(z):
                self.unitags[sentence[i].tag] += 1
                self.wt_count[sentence[i].tag][sentence[i].word] += 1

                if i == z:
                    continue

                self.bitags[sentence[i].tag][sentence[i+1].tag] += 1

    def calc_prob(self):
        for x, next_tags in self.bitags.iteritems():
            for y in next_tags:
                self.bitag_prob[x][y] = (self.bitags[x][y] + 1) / (self.unitags[x] + 36)

        for tag, words in self.wt_count.iteritems():
            for word in words:
                self.wt_prob[tag][word] = self.wt_count[tag][word] / self.unitags[tag]

    def create_model(self, sentences):
        self.count_words_and_tags(sentences)
        self.calc_prob()

        for tag in self.unitags:
            self.tag_list.append(tag)

    def viterbi(self, sentence):
        n = len(sentence)
        t = len(self.tag_list)
        
        matrix = [[0.0 for x in xrange(n)] for y in xrange(t)]
        path = [[0 for x in xrange(n)] for y in xrange(t)]
        final_tags = []

        # Iterate top to bottom, left to right
        for j in xrange(n):
            for i in xrange(t):
                if self.wt_prob[self.tag_list[i]][sentence[j].word] == 0:
                    self.wt_prob[self.tag_list[i]][sentence[j].word] = 0.00000005
                if j == 0:
                    matrix[i][j] = self.wt_prob[self.tag_list[i]][sentence[j].word] * self.bitag_prob['<s>'][self.tag_list[i]]
                else:
                    maximum = -sys.maxint - 1
                    max_i = 0

                    for k in xrange(t):
                        temp = matrix[k][j-1] * self.bitag_prob[self.tag_list[k]][self.tag_list[i]]
                        if maximum < temp:
                            maximum = temp
                            max_i = k

                    path[i][j] = max_i
                    matrix[i][j] = self.wt_prob[self.tag_list[i]][sentence[j].word] * maximum

        # Get the max of the last column so we know where to start going back from
        last_col_max = -sys.maxint - 1
        prev_row = 2
        end = n - 1

        for i in xrange(t):
            if last_col_max < matrix[i][end]:
                last_col_max = matrix[i][end]
                prev_row = i

        final_tags.append(self.tag_list[prev_row])

        for j in xrange(end, 1, -1):
            final_tags.append(self.tag_list[path[prev_row][j]])
            prev_row = path[prev_row][j]

        final_tags.append('<s>')
        final_tags.reverse()

        return final_tags

    def predict_tags(self, sentences):
        for sentence in sentences:
            final_tags = []
            final_tags = self.viterbi(sentence)

            for i in xrange(len(sentence)):
                sentence[i].tag = final_tags[i]

        return sentences

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

    model = HMM(training_sents)

    ## read sentences again because predict_tags(...) rewrites the tags
    #sents = utils.read_tokens(training_file)
    #predictions = predict_tags(sents, model)
    #accuracy = utils.calc_accuracy(training_sents, predictions)
    #print "Accuracy in training [%s sentences]: %s" % (len(sents), accuracy)

    sents = utils.read_tokens(test_file)
    predictions = model.predict_tags(sents)
    accuracy = utils.calc_accuracy(test_sents, predictions)
    print "Accuracy in testing [%s sentences]: %s" % (len(sents), accuracy)
