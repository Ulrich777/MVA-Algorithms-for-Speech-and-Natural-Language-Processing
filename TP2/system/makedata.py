import os
os.chdir("C:/Users/utilisateur/Desktop/LAST_YEAR/NLP/TP2/code")

from helper import GetFile, GetSentence#, CreateFile
from pcyk import PCYK, GetPostTag
from OOV import OOV, load_obj
import pickle
import numpy as np
import sys
import pandas as pd
import time
import matplotlib.pyplot as plt



def score(true_parse, proposed_parse):
    try:
        sc = (np.array(GetPostTag(true_parse, ajust=True))==np.array(GetPostTag(proposed_parse))).mean()
    except:
        sc = 0
    return sc

lines_train = GetFile('C:/Users/utilisateur/Desktop/LAST_YEAR/NLP/TP2/code/train.txt')
lines_val = GetFile('C:/Users/utilisateur/Desktop/LAST_YEAR/NLP/TP2/code/val.txt')
lines_test = GetFile('C:/Users/utilisateur/Desktop/LAST_YEAR/NLP/TP2/code/test.txt')



sents_val = [GetSentence(sent) for sent in lines_val]

unknown = load_obj('C:/Users/utilisateur/Desktop/LAST_YEAR/NLP/TP2/code/oov_data/', 'unknown')
known = load_obj('C:/Users/utilisateur/Desktop/LAST_YEAR/NLP/TP2/code/oov_data/', 'known')
dists = load_obj('C:/Users/utilisateur/Desktop/LAST_YEAR/NLP/TP2/code/oov_data/', 'dists')

with open('C:/Users/utilisateur/Desktop/LAST_YEAR/NLP/TP2/code/polyglot-fr.pkl', 'rb') as f:
    words, embeddings = pickle.load(f, encoding='latin1') 
    

def HyperEval(bet, weight):
    oov = OOV(known, unknown, dists, words, embeddings, bet, weight)
    parser = PCYK(lines_train, fix_spelling_error=False, oov=oov)
    
    n = len(sents_val)
    scores = []
    
    for i in range(n):
        ans = parser.OOVParse(sents_val[i])
        scores.append(score(lines_val[i], ans))
        
    scores_arr = np.array(scores)
    return scores_arr.mean()
 

MAKE_REPORT = False

if MAKE_REPORT:

    bets = [0.1 *i for i in range(11)]
    weights = [0.1*i for i in range(11)]  

    n1 = len(bets)
    n2 = len(weights)

    BET, W, S = [], [], []

    dt = time.time()
    for i, bet in enumerate(bets):
        for j, weight in enumerate(weights):
        
            BET.append(bet)
            W.append(weight)
        
            sys.stderr.write('\rcase: %d/%d -- bet=%.2f -- weight=%.2f' % (n2*i+j+1, n1*n2, bet, weight))
            sys.stderr.flush()
            S.append(HyperEval(bet, weight))
 
    dt = time.time() - dt
    print('Duration: %.3f'%(dt/60))

    df = pd.DataFrame({'bet':BET, 'weight':W, 'score':S})
    df.to_csv('C:/Users/utilisateur/Desktop/LAST_YEAR/NLP/TP2/code/scores_val.csv', index=False)
    
else:
    df = pd.read_csv('C:/Users/utilisateur/Desktop/LAST_YEAR/NLP/TP2/code/scores_val.csv')

plt.hist(df.score)

##
i_opt = df.score.argmax()
bet_best = df.bet[i_opt]
weight_best = df.weight[i_opt]
print(bet_best, weight_best, df.score[i_opt])

oov = OOV(known, unknown, dists, words, embeddings, bet_best, weight_best)
parser = PCYK(lines_train, fix_spelling_error=False, oov=oov)

ii = 12
print(sents_val[ii])
ans = parser.parse(sents_val[ii])
ans_ = parser.OOVParse(sents_val[ii])
score(lines_val[ii], ans)



