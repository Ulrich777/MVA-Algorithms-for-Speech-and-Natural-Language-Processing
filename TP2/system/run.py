#!/usr/bin/env python2

import sys
from OOV import load_obj, OOV
from pcyk import PCYK
import pickle
from helper import GetFile, EvalFile
import time

#import os
#os.chdir("C:/Users/utilisateur/Documents/GITHUB/TP2/code")

#SENT_PATH = 'C:/Users/utilisateur/Documents/GITHUB/TP2/code/sents_test.txt'
#OUTPUT_FILE = 'C:/Users/utilisateur/Documents/GITHUB/TP2/code/my_output.txt'
#GAMMA = 0.3
#WEIGHT = 0.3
#CHOICE = 308


def to_launch(SENT_PATH, OUTPUT_FILE, GAMMA, WEIGHT, LOWER, UPPER):


    unknown = load_obj('C:/Users/utilisateur/Documents/GITHUB/TP2/code/oov_data/', 'unknown')
    known = load_obj('C:/Users/utilisateur/Documents/GITHUB/TP2/code/oov_data/', 'known')
    dists = load_obj('C:/Users/utilisateur/Documents/GITHUB/TP2/code/oov_data/', 'dists')

    with open('C:/Users/utilisateur/Documents/GITHUB/TP2/code/polyglot-fr.pkl', 'rb') as f:
        words, embeddings = pickle.load(f, encoding='latin1') 
 
    lines_train = GetFile('C:/Users/utilisateur/Documents/GITHUB/TP2/code/train.txt')
    oov = OOV(known, unknown, dists, words, embeddings, GAMMA, WEIGHT)
    parser = PCYK(lines_train, fix_spelling_error=False, oov=oov)

    sents = GetFile(SENT_PATH)

    
    if UPPER == 'None':
        UPPER = len(sents) - 1
    else:
        UPPER = int(UPPER)
    if LOWER is None:
        LOWER = 0
    else:
        LOWER = int(LOWER)
     
    print(LOWER, UPPER)
    dt = time.time()
    

    with open(OUTPUT_FILE, 'a',  encoding='utf-8') as f:

        for  choice in range(LOWER, UPPER):
            print(choice)
 
            ans = parser.parse(sents[choice])
            print(ans)
            f.write(ans +'\n')

    dt = time.time() - dt
    print('elapsed time: %.3f'%(dt/60))

if __name__ == "__main__":
    #chmod u+x run.sh
    List = sys.argv
    SENT_PATH = List[1]
    OUTPUT_FILE = List[2]
    GAMMA  = float(List[3])
    WEIGHT = float(List[4])
    LOWER = List[5]
    UPPER = List[6]
    to_launch(SENT_PATH, OUTPUT_FILE, GAMMA, WEIGHT, LOWER, UPPER)
    #time.sleep(20)




