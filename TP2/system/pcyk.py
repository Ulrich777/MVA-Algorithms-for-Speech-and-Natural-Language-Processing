from helper import GetSentence, GetFirstPart, ExtractPCFG, ToChomsky, ReverseRules, SummarizeRules
import numpy as np
from string import punctuation

wordstops = list(punctuation.replace("'",''))


def GetPostTag(line, ajust=False):
    split_line = line.split()
    splitted_line = list(split_line)
    words = [w for w in split_line if '(' not in w]
    #print(words)
    
    posttags = []
    for w in words:
        index_word_split_line = splitted_line.index(w)
        previous_word = splitted_line[index_word_split_line-1]
        if ajust:
            posttags.append(GetFirstPart(previous_word[1:]))
        else:
            posttags.append(previous_word[1:])
        
    if posttags[0] =='SENT':
        return ['SENT']
    else:
        return posttags

class ParsingTree(object):
    '''
    Initializing a tree that will be build by backward induction for decoding PCYK outputs
    '''
    def __init__(self):
        '''
        Attributs de base de la class
        '''
        self.left = None
        self.right = None
        self.data = None
        self.index_right = 0
        self.index_left = 0
        

class PCYK():
    
    def __init__(self, lines, fix_spelling_error = False, oov=None):
        self.lines = lines
        self.sentences = [GetSentence(line) for line in lines]
        
        self.lexicon,rules,self.vocab_prob,rules_prob = ExtractPCFG(self.lines)
        self.rules,self.rules_prob = ToChomsky(rules,rules_prob)
        self.reversed_rules = ReverseRules(rules)
        self.all_symbols, self.n_symbols = SummarizeRules(self.rules)
        self.all_symbols = list(self.all_symbols)
        self.fix = fix_spelling_error
        self.oov = oov
        self.pos_tagger_unknow_vocab=None
        
        
    def MakeTable(self,sent):
        '''
        AImplement the PCYK algorithm
         `sent`: sentence to parse
        '''
        if self.fix:
            # yet to come
            pass

        words = sent.split()
        n_words = len(words)
        table = np.zeros((n_words+1,n_words+1,self.n_symbols))
        back=  {}
        for j in range(1,n_words+1):
            word= words[j-1]
            if word in self.lexicon:
                list_of_possible_symbols = self.lexicon[word]
                proposal = word
                all_proba = None
            else:
                if self.oov==None:
                    all_proba = 1/self.n_symbols
                    list_of_possible_symbols = [1]
                else:
                    proposal = self.oov.most_similar(word, threshold=2)
                    if proposal is None:
                        all_proba = 1/self.n_symbols
                        list_of_possible_symbols = [1]
                    else:
                        list_of_possible_symbols = self.lexicon[proposal]
                        all_proba = None
                    
                    #
                    #closest_word = OOV(word, vocab)
                    #closest_symbol = GetSymbol(closest_word)
                    #table[j-1,j,self.all_non_terminal.index(closest_symbol)] = 1
                    
            for a in list_of_possible_symbols:
                if all_proba ==None:
                    tuple_proba = tuple([proposal,a])
                    table[j-1,j,self.all_symbols.index(a)] =  self.vocab_prob[tuple_proba]

                      
                else:
                    table[j-1,j,:] = all_proba*np.ones((self.n_symbols))
                    
            
            list_to_run_through = list(range(0,j-1))
            list_to_run_through.reverse()
        
            for i in list_to_run_through:
                for k in range(i+1,j):
                    possible_B = np.array(self.all_symbols)[table[i,k,:]>0]
                    possible_C = np.array(self.all_symbols)[table[k,j,:]>0]
                    
                    for B in possible_B:
                        for C in possible_C:
                            tuple_symbol = tuple([B,C])
                            if tuple_symbol in self.reversed_rules:
                                list_of_possible_rules = self.reversed_rules[tuple_symbol]
                                all_proba = 0
                            else:
                                continue
                            
                            for rule in list_of_possible_rules:
                                A = rule
                                tuple_proba = tuple([rule,tuple_symbol])
                                proba_A_BC = self.rules_prob[tuple_proba]
                                proba_B = table[i,k,self.all_symbols.index(B)]
                                proba_C = table[k,j,self.all_symbols.index(C)]
                                
                                full_proba = proba_A_BC*proba_B*proba_C
                                
                                if (table[i,j,self.all_symbols.index(A)]<full_proba):
                                    table[i,j,self.all_symbols.index(A)] = full_proba
                                    back[tuple([i,j,A])] = tuple([k,B,C])
        return table,back
 
    def BackwardInduction(self,back,k,A,B,C,root,left,right):
        """
         `root `: tree we backpropagate from
         `back ` : the backward table return by CYK algorithm
         `a `: Unique rule A
         `b `: left symbol in A-->BC
         `c `: right symbol in A-->BC
         `left `: the i in the path i-->k of CYK algorithm
         `right `: the j in the path k-->j of CYK algorithm
        
        """
        if k==-1:
            i = left
            j = right
            
            if tuple([i,j,A]) in back:
                root.left = ParsingTree()
                root.right = ParsingTree()
            
                new_k,new_B,new_C = back[tuple([i,j,A])]
                root.left.data = new_B
                root.right.data = new_C
                self.BackwardInduction(back,new_k,A,new_B,new_C,root,left,right)
                
        else:  
            root.left.index_left = left
            root.left.index_right = k
            
            
            root.right.index_left = k 
            root.right.index_right = right
            
            if tuple([left,k,B]) in back:
                _k,_B,_C = back[tuple([left,k,B])]
                #print(B_k,B_B,B_C)
                root.left.left = ParsingTree()
                root.left.right= ParsingTree()
                root.left.left.data = _B
                root.left.right.data = _C
                self. BackwardInduction(back,_k,A,_B,_C,root.left,left,k)
             
            if tuple([k,right,C]) in back:
                k_,B_,C_ = back[tuple([k,right,C])]
                root.right.left = ParsingTree()
                root.right.right= ParsingTree()
                root.right.left.data = B_
                root.right.right.data = C_
                self.BackwardInduction(back,k_,A,B_,C_,root.right,k,right)
                

  
        
    
    def GetOptimalTree(self,line):
        '''
        Backpropagate through all the sentence to retrieve the optimal parsing tree
        
        '''
            
        words = line.split()
        n_words = len(words)
        
        
        table,back = self.MakeTable(line)
        
        root = ParsingTree()
        
        root.data = 'SENT'
        root.index_left = 0
        root.index_right = n_words
        self.BackwardInduction(back,-1,'SENT',0,0,root,0,n_words)
        
        
        return root
    
    def ReadTree(self,list_to_complete,root):
        '''
        traverse the tree and extract the output
         `root ` : root of the tree
        '''
        i = root.index_left
        j = root.index_right
        symbol = root.data
        if (('+' not in symbol)or(symbol =='P+D')):
            list_to_complete[i] += ' (' +symbol
        
        list_to_complete[j] += ')'
        if root.left != None:
            self.ReadTree(list_to_complete,root.left)
        
        
                
        if root.right != None:
            self.ReadTree(list_to_complete,root.right)
        
    def OOVProposal(self, token, threshold=2):
        if token in self.lexicon:
            proposal = token
        else:
            proposal =  self.oov.most_similar(token, threshold=threshold)
        tags = self.lexicon[proposal]
        best_tag = ''
        best_prob = -1
        for tag in tags:
            prob = self.vocab_prob[(proposal, tag)]
            if prob>best_prob:
                prob = best_prob
                best_tag = tag
        return best_tag      

    def OOVParse(self, sent, threshold=2):
        ans = ''
        n = len(sent.split())
        for i, token in enumerate(sent.split()):
            if i<n-1:
                ans += '('+self.OOVProposal(token, threshold=threshold)+ ' '+ token + ') '
            else:
                ans += '('+self.OOVProposal(token, threshold=threshold)+ ' '+ token + ')' 
        return '( (SENT '+ans+'))'
    
    def parse(self,line):
        '''
        `line`: sentencre to parse
        parse the sentence and outputs in the same format as the SEQUOIA file
        '''
        tree_parse = self.GetOptimalTree(line)
        #line_to_use = line.replace("\'","\' ")
        #global punctuation_list
        #for punc in punctuation_list:
            #line_to_use = line_to_use.replace(punc,' '+ punc+ ' ')

        words = line.split()
        n_words = len(words)
        
        
        list_symbols = []
        
        for i in range(n_words+1):
            list_symbols.append('')
        
        self.ReadTree(list_symbols,tree_parse)
        list_word_symbol = []
        list_word_symbol.append('(')
        for i in range(n_words):
            list_word_symbol.append(list_symbols[i])
            list_word_symbol.append(' ')
            list_word_symbol.append(words[i])
        
        list_word_symbol.append(list_symbols[-1])
        list_word_symbol.append(')')
            
        ans = ''.join(list_word_symbol) 
        if len(GetPostTag(ans))==1:
            ans = self.OOVParse(line)
        return ans