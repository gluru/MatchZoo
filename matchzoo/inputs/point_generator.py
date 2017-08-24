# -*- coding: utf-8 -*-

import sys
import random
import numpy as np
from utils.rank_io import *
from layers import DynamicMaxPooling

class PointGenerator(object):
    def __init__(self, config):
        self.__name = 'PointGenerator'
        self.config = config
        self.data1 = config['data1']
        self.data2 = config['data2']
        rel_file = config['relation_file']
        self.rel = read_relation(filename=rel_file)
        self.batch_size = config['batch_size']
        self.data1_maxlen = config['text1_maxlen']
        self.data2_maxlen = config['text2_maxlen']
        self.fill_word = config['fill_word']
        self.is_train = config['phase'] == 'TRAIN'
        self.point = 0
        self.total_rel_num = len(self.rel)
        self.check_list = ['data1', 'data2', 'text1_maxlen', 'text2_maxlen', 'relation_file', 'batch_size', 'fill_word']

    def check(self):
        for e in self.check_list:
            if e not in self.config:
                print '[%s] Error %s not in config' % (self.__name, e)
                return False
        return True

    def get_batch(self, randomly=True):
        X1 = np.zeros((self.batch_size, self.data1_maxlen), dtype=np.int32)
        X1_len = np.zeros((self.batch_size,), dtype=np.int32)
        X2 = np.zeros((self.batch_size, self.data2_maxlen), dtype=np.int32)
        X2_len = np.zeros((self.batch_size,), dtype=np.int32)
        Y = np.zeros((self.batch_size,), dtype=np.int32)

        X1[:] = self.fill_word
        X2[:] = self.fill_word
        for i in range(self.batch_size):
            if randomly:
                label, d1, d2 = random.choice(self.rel)
            else:
                label, d1, d2 = self.rel[self.point]
                self.point += 1
            d1_len = min(self.data1_maxlen, len(self.data1[d1]))
            d2_len = min(self.data2_maxlen, len(self.data2[d2]))
            X1[i, :d1_len], X1_len[i]   = self.data1[d1][:d1_len], d1_len
            X2[i, :d2_len], X2_len[i]   = self.data2[d2][:d2_len], d2_len
        return X1, X1_len, X2, X2_len, Y    

    def get_batch_generator(self):
        if self.is_train:
            while True:
                X1, X1_len, X2, X2_len, Y = self.get_batch()
                yield ({'query': X1, 'query_len': X1_len, 'doc': X2, 'doc_len': X2_len}, Y)
        else:
            while self.point + self.batch_size <= self.total_rel_num:
                X1, X1_len, X2, X2_len, Y = self.get_batch(randomly = False)
                yield ({'query': X1, 'query_len': X1_len, 'doc': X2, 'doc_len': X2_len}, Y)

    def reset(self):
        self.point = 0