
import re
import time

def GetFile(path_file):
    '''
    Retrieve the content of a given file
    path_file: is the path of the file
    '''
    with open(path_file,'r', encoding='utf-8') as file:
        lines = file.readlines()
    return lines

def GetSentence(line):
    '''
    Retrieve the original sentence from the parsed sentence
    '''
    split_line = line.split()
    words_in_the_phrase = [w.replace(')','') for w in split_line if '(' not in w]
    return ' '.join(words_in_the_phrase)


"""
def CreateFile(pathfile,lines):
    '''
    create a file from the given   `lines`
    '''
    lines = '\n'.join(lines)
    with open(pathfile,'w', encoding='utf-8')  as f:
        f.write(lines)
"""
def CreateFile(pathfile, lines):

    with open(pathfile, 'a',  encoding='utf-8') as f:
        for line in lines:
            f.write(line+'\n')

#####=====================================############
def GetLevel(line):
    '''
    Simple level order tree traversal algorithm
    goal: find the   `level` of every symbol a typical line
    
    '''
    list_of_level = []
    split_line = line.split()
    cur_level = 0
    for word in split_line[1:]: #doesn't consider the first parenthese
        if '(' in word:
            cur_level = cur_level +1
            list_of_level.append(cur_level)
        elif ')' in word:
            nb_parenthese = len([v for v in word if v==')'])
            cur_level=  cur_level - nb_parenthese
    
    return list_of_level

def GetFirstPart(word):
     '''
     keep the first part of a compounded word
     '''
     parts = word.split('-')
     firstpart = parts[0]
     return firstpart


#===========================================================##
def ExtractPCFG(lines):
    '''
    extract the rules and lexion given the training corpus  `lines `
    '''
    lexicon = {}
    rules ={}
    rules_prob = {} #
    rules_count = {} #
    
    vocab_prob = {} #
    vocab_count = {} #
    for line in lines:
        split_line = line.split()
        splitted_line = list(split_line)
        words = [w for w in split_line if '(' not in w]
        levels = GetLevel(line)
        
        symbols = []
        index_sent = []
        for index_line,l in  enumerate(split_line):
            if l not in words:
                symbols.append(l)
                index_sent.append(index_line)
        
        symbols = symbols[1:]
        index_sent = index_sent[1:]
        
        for ind_level,level in enumerate(levels):
            all_values = []
            if ind_level<(len(levels)-1):
                next_level = levels[ind_level+1]
            else:
                next_level = -10
            ind_plus = 1
            
            if (next_level==(level+1)):
                while ((next_level!=(level))):
                    if (next_level==(level+1)):
                        all_values.append(symbols[ind_level+ind_plus])
                    ind_plus = ind_plus + 1
                    if (ind_level+ind_plus)<(len(levels)):
                        next_level = levels[ind_level+ind_plus]
                    else:
                        next_level = -10
                        break
                    
            if len(all_values)>0:
                if len(all_values)==1:
                    splitted_line[index_sent[ind_level+1]] = splitted_line[index_sent[ind_level]]
                    symbols[ind_level+1] = splitted_line[index_sent[ind_level]]
                        
                else:
                    clean_values = [GetFirstPart(re.sub('\(|\)','',i_word)) for i_word in all_values]
                    root = GetFirstPart(re.sub('\(|\)','',symbols[ind_level]))
                    
                    if root not in rules:
                        rules[root] = set()
                        rules_count[root] = 0
                    rules[root].add(tuple(clean_values))
                    rules_count[root] +=1
                    tuple_proba = tuple([root,tuple(clean_values)])
                    if tuple_proba not in rules_prob:
                        rules_prob[tuple_proba]=0
                    rules_prob[tuple_proba] +=1
            
        for w in words:
            index_word_split_line = splitted_line.index(w)
            previous_word = splitted_line[index_word_split_line-1]
            
            if w.replace(')','') not in lexicon:
                lexicon[w.replace(')','')] = set()
                vocab_count[w.replace(')','')] = 0
            lexicon[w.replace(')','')].add(GetFirstPart(previous_word.replace('(','')))
            vocab_count[w.replace(')','')] += 1
            tuple_proba = tuple([w.replace(')',''),GetFirstPart(previous_word.replace('(',''))])
            if tuple_proba not in vocab_prob:
                vocab_prob[tuple_proba] = 0
            vocab_prob[tuple_proba] += 1

    
    for items in vocab_prob:
        word = items[0]
        word_count = vocab_count[word]
        vocab_prob[items] = vocab_prob[items]/word_count


    for items in rules_prob:
        rule = items[0]
        rule_count = rules_count[rule]
        rules_prob[items] = rules_prob[items]/rule_count
    
    return lexicon,rules,vocab_prob,rules_prob
#============================================================================#
def ToChomsky(old_rules,old_rules_prob):
    '''
    Convert the rules to Chomsky normal form.
    Here we deal only with
    '''
    new_rules = dict(old_rules)
    new_rules_prob = dict(old_rules_prob)
    for rule in old_rules:
        symbols = old_rules[rule]
        for symbol in symbols:
            if len(symbol)>2:
                new_rules[rule].remove(symbol)
                new_symbol = list(symbol)
                while len(new_symbol)!=2:
                    merge = tuple([new_symbol[0],new_symbol[1]])
                    new_symbol = [new_symbol[0] +'+' +new_symbol[1]] + new_symbol[2:]
                    new_rules[new_symbol[0]] =  set()
                    new_rules[new_symbol[0]].add(merge)
                    actual = tuple([new_symbol[0],merge])
                    new_rules_prob[actual] = 1
                
                to_add = tuple([rule,tuple(new_symbol)])
                to_remove = tuple([rule,tuple(symbol)])
                new_rules_prob[to_add] = old_rules_prob[to_remove]
                del new_rules_prob[to_remove]
                
                new_rules[rule].add(tuple(new_symbol))
    return new_rules,new_rules_prob

#=============================================================================#
def SummarizeRules(rules):
    '''
    Output the number of non-terminal symbols and their number
    
    '''
    all_symbols = set()
    for rule in rules:
        all_symbols.add(rule)
        symbols = rules[rule]
        for symbol in symbols:
            for unit_symbol in symbol:
                all_symbols.add(unit_symbol)
    return all_symbols, len(all_symbols)  
#=============================================================================#
def ReverseRules(rules):
    '''
    Turn a {rule: symbol} dict to a {symbol:rule} dict
    '''
    reversed_rules= {}
    for rule in rules:
        symbols = rules[rule]
        for symbol in symbols:
            if symbol not in reversed_rules:
                reversed_rules[symbol] = set()
            reversed_rules[symbol].add(rule)
    return reversed_rules

#=============================================================================#
def EvalFile(sents, filename, parser):

    dt = time.time()

    with open(filename, 'a',  encoding='utf-8') as f:
        for i, sent in enumerate(sents):
            print(i)
            answer = parser.parse(sent)

            f.write(answer+'\n')

    dt = time.time() - dt
    print('elapsed time: %.3f'%(dt/60))
