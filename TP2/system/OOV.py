import pickle
import numpy as np

def save_obj(path, name, obj ):
    with open(path + name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(path, name ):
    with open(path + name + '.pkl', 'rb') as f:
        return pickle.load(f)

#unknown = load_obj('C:/Users/utilisateur/Documents/GITHUB/TP2/code/oov_data/', 'unknown')
#known = load_obj('C:/Users/utilisateur/Documents/GITHUB/TP2/code/oov_data/', 'known')
#dists = load_obj('C:/Users/utilisateur/Documents/GITHUB/TP2/code/oov_data/', 'dists')

with open('polyglot-fr.pkl', 'rb') as f:
    words, embeddings = pickle.load(f, encoding='latin1') 


def getdetails():
    id2un = load_obj('C:/Users/utilisateur/Documents/GITHUB/TP2/code/oov_data/', 'id2un')
    un2id = load_obj('C:/Users/utilisateur/Documents/GITHUB/TP2/code/oov_data/', 'un2id')
    id2kn = load_obj('C:/Users/utilisateur/Documents/GITHUB/TP2/code/oov_data/', 'id2kn')
    kn2id = load_obj('C:/Users/utilisateur/Documents/GITHUB/TP2/code/oov_data/', 'kn2id')
    fe_un  = load_obj('C:/Users/utilisateur/Documents/GITHUB/TP2/code/oov_data/', 'fe_un')
    fe_kn = load_obj('C:/Users/utilisateur/Documents/GITHUB/TP2/code/oov_data/', 'fe_kn')
    sim = load_obj('C:/Users/utilisateur/Documents/GITHUB/TP2/code/oov_data/', 'sim') 
    return id2un, un2id, id2kn, kn2id, fe_un, fe_kn, sim

class OOV():
    
    def __init__(self, known, unknown, dists, words, embeddings, bet, weight):
        self.id2known = {i:w for i,w in enumerate(known)}
        self.known2id = {w:i for i,w in enumerate(known)}
        self.id2unknown = {i:w for i,w in enumerate(unknown)}
        self.unknown2id = {w:i for i,w in enumerate(unknown)}
        self.dists = dists
        self.id2un, self.un2id, self.id2kn, self.kn2id, self.fe_un, self.fe_kn, self.sim = getdetails()
        self.SIM =  self.build_sim(bet, weight)
        
        
    def build_sim(self, bet, weight):
        rows = [self.unknown2id[self.id2un[i]] for i in self.id2un]
        cols = [self.known2id[self.id2kn[i]] for i in self.id2kn]
        d = self.dists[rows][:,cols]
        s1 = np.exp(-bet * d)
        s2 = (1 + self.sim)/2
        return weight * s1 + (1-weight)*s2
    
    def mixed(self,w,  threshold=2):
        if w in self.un2id:
            ii = self.un2id[w]
            jj = self.SIM[ii].argmax()
            score = self.SIM[ii].max()
            return self.id2kn[jj], score, 'mixed'
        else:
            i = self.unknown2id[w]
            i_, score = self.dists[i].argmin(), self.dists[i].min()
            if score<=threshold:
                return self.id2known[i_], score, 'spelling'
            else:
                return self.id2known[i_], score, 'unsure'
                
            
        
    def most_similar(self, w, threshold=2):
        proposal, score, type = self.mixed(w, threshold=threshold)
        return proposal

