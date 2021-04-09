# Code for CS 171, Winter, 2021

import Tree
import requests
import json

url2 = "https://poe.ninja/api/data/itemoverview?league=Ritual&type=UniqueWeapon"
item_list = requests.get(url2).json()["lines"]
item_names = []
for item in item_list:
    item_names.append(item["name"])
tokenized_names = {}
for name in item_names:
    tokenized_names[name] = name.replace(' ','_')


verbose = False
def printV(*args):
    if verbose:
        print(*args)

# A Python implementation of the AIMA CYK-Parse algorithm in Fig. 23.5 (p. 837).
def CYKParse(words, grammar):
    T = {}
    P = {}
    # Instead of explicitly initializing all P[X, i, k] to 0, store
    # only non-0 keys, and use this helper function to return 0 as needed.
    def getP(X, i, k):
        key = str(X) + '/' + str(i) + '/' + str(k)
        if key in P:
            return P[key]
        else:
            return 0
    # Insert lexical categories for each word
    for i in range(len(words)):
        for X, p in getGrammarLexicalRules(grammar, words[i]):
            P[X + '/' + str(i) + '/' + str(i)] = p
            T[X + '/' + str(i) + '/' + str(i)] = Tree.Tree(X, None, None, lexiconItem=words[i])
    printV('P:', P)
    printV('T:', [str(t)+':'+str(T[t]) for t in T])
    # Construct X_i:j from Y_i:j + Z_j+i:k, shortest spans first
    for i, j, k in subspans(len(words)):
        for X, Y, Z, p in getGrammarSyntaxRules(grammar):

            if Z == None:
                printV('LOCATED C1F')
                printV('i:', i, 'j:', j, 'k:', k, '', X, '->', Y, '['+str(p)+']', 
                        'PY =' ,getP(Y, i, j), p, '=', getP(Y, i, j) * p)
                
                PY = getP(Y, i, j) * p

                if PY > getP(X, i, j):
                    printV('     inserting from', i, '-', j, ' ', X, '->', T[Y+'/'+str(i)+'/'+str(j)],
                                'because', PY, '=', getP(Y, i, j),'*', p, '>', getP(X, i, j), '=',
                                'getP(' + X + ',' + str(i) + ',' + str(j) + ')')
                    P[X + '/' + str(i) + '/' + str(k)] = PY
                    T[X + '/' + str(i) + '/' + str(k)] = Tree.Tree(X, T[Y+'/'+str(i)+'/'+str(j)],None)

            else:
                printV('i:', i, 'j:', j, 'k:', k, '', X, '->', Y, Z, '['+str(p)+']', 
                        'PYZ =' ,getP(Y, i, j), getP(Z, j+1, k), p, '=', getP(Y, i, j) * getP(Z, j+1, k) * p)

                PYZ = getP(Y, i, j) * getP(Z, j+1, k) * p

                if PYZ > getP(X, i, k):
                    printV('     inserting from', i, '-', k, ' ', X, '->', T[Y+'/'+str(i)+'/'+str(j)], T[Z+'/'+str(j+1)+'/'+str(k)],
                                'because', PYZ, '=', getP(Y, i, j), '*', getP(Z, j+1, k), '*', p, '>', getP(X, i, k), '=',
                                'getP(' + X + ',' + str(i) + ',' + str(k) + ')')
                    P[X + '/' + str(i) + '/' + str(k)] = PYZ
                    T[X + '/' + str(i) + '/' + str(k)] = Tree.Tree(X, T[Y+'/'+str(i)+'/'+str(j)], T[Z+'/'+str(j+1)+'/'+str(k)])
        printV('T:', [str(t)+':'+str(T[t]) for t in T])
    return T, P

# Python uses 0-based indexing, requiring some changes from the book's
# 1-based indexing: i starts at 0 instead of 1

def subspans(N):
    for length in range(2, N+2):
        for i in range(N+2 - length):
            k = i + length - 1
            for j in range(i, k):
                yield i,j,k
# These two getXXX functions use yield instead of return so that a single pair can be sent back,
# and since that pair is a tuple, Python permits a friendly 'X, p' syntax
# in the calling routine.
def getGrammarLexicalRules(grammar, word):
    for rule in grammar['lexicon']:
        if rule[1] == word:
            yield rule[0], rule[2]

def getGrammarSyntaxRules(grammar):
    rulelist = []
    for rule in grammar['syntax']:
            yield rule[0], rule[1], rule[2], rule[3]

# 'Grammar' here is used to include both the syntax part and the lexicon part.
# 
def getGrammarItems():
    grammar_lex = {
        'syntax' : [
            ['NP', 'Name', None, 0.2],
            ['NP', 'Noun', None, 0.2],
            ['VP', 'Noun', 'VP', 0.2],
            ['VP', 'Verb', 'NP', 0.2],
            ['VP', 'Verb', 'NP+AdverbPhrase', 0.3],
            ['VP', 'Verb', 'Article', 0.3], 
            ['VP', 'AdverbPhrase', 'AdverbPhrase', 0.4],
            ['VP', 'VP', 'NP+Prep+NP', 0.01],
            ['VP', 'NP+Prep', 'VP', 0.01],
            ['NP', 'Article', 'Noun', 0.5],
            ['NP', 'Adjective', 'Noun', 0.5],
            ['NP+AdverbPhrase', 'NP', 'AdverbPhrase', 0.2],
            ['NP+AdverbPhrase', 'NP', 'Adverb', 0.15],
            ['NP+AdverbPhrase', 'Adverb', 'NP+AdverbPhrase', 0.05],
            ['AdverbPhrase', 'AdverbPhrase', 'VP', 0.02],
            ['NP+Prep', 'Noun', 'Preposition', 0.2],
            ['NP+Prep+NP', 'NP+Prep', 'NP', 0.2],
            ['Adj+Prep+NP', 'Adjective','Prep+NP',1.0],
            ['Prep+NP', 'Preposition', 'NP',1.0],
            ['AdverbPhrase', 'Adverb', 'AdverbPhrase', 0.2],
            ['AdverbPhrase', 'AdverbPhrase', 'Adverb', 0.3],
            ['AdverbPhrase', 'Adverb', 'VP', 0.3], #step 5
            ['AdverbPhrase', 'Preposition', 'AdverbPhrase', 0.4],
            ['AdverbPhrase', 'Preposition', 'NP', 0.2],
            ['NP+VP','Name','VP',1.0],
            ['S', 'Greeting', 'S', 0.25],
            ['S', 'Pronoun', 'Verb', 0.25],
            ['S', 'WQuestion', 'VP', 0.25],
            ['S', 'WQuestion', 'NP+VP', 0.25],
            ['AdverbPhrase', 'Article', 'AdverbPhrase',0.2],#new
            ['VP', 'Verb', 'AdverbPhrase',0.1]

        ],
        'lexicon' : [
            ['Greeting', 'Hi', 0.5],
            ['Greeting', 'Hello', 0.5],
            ['WQuestion', 'What', 0.25],
            ['WQuestion', 'How', 0.25],
            ['WQuestion', 'Which', 0.25],
            ['WQuestion', 'Will', 0.25],
            ['WQuestion', 'Is', 0.1],
            ['Verb', 'am', 0.1],
            ['Verb', 'is', 0.3],
            ['Verb','be',0.3],
            ['Verb','are',0.2],
            ['Verb','does',0.3],
            ['Verb', 'more', 0.2],
            ['Verb', 'less', 0.2],
            ['Verb','higher',0.2],
            ['Verb','lower',0.2],
            ['Pronoun', 'I', 1.0],
            ['Noun', 'type', 0.4],
            ['Noun', 'kind', 0.4],
            ['Noun','weapon', 0.1],
            ['Noun', 'price', 0.4],
            ['Noun', 'cost', 0.4],
            ['Noun', 'fee', 0.4],
            ['Noun', 'requirement', 0.4],
            ['Noun', 'appearance', 0.3],
            ['Noun', 'description', 0.3],
            ['Noun', 'implicit', 0.3],
            ['Noun', 'modifiers', 0.3],
            ['Noun', 'explicit', 0.3],
            ['Noun', 'look', 0.3],
            ['Noun', 'chaos', 0.3],
            ['Noun', 'exalted', 0.3],
            ['Noun', 'value', 0.3],
            ['Article', 'the', 0.3],
            ['Article', 'a', 0.3],
            ['Article', 'level', 0.5],
            ['Article', 'expensive', 0.5],
            ['Adjective', 'my', 0.5],
            ['Adverb', 'now', 0.3],
            ['Preposition', 'of', 0.5],
            ['Preposition', 'with', 0.5],
            ['Preposition', 'in', 0.3],
            ['Preposition', 'than', 0.2],
            ['Preposition', 'like', 0.2]
         ]
    }
    for key,value in tokenized_names.items():
        grammar_lex["lexicon"].append(['Name', value, 0.002])
    return grammar_lex
# Unit testing code
if __name__ == '__main__':
    verbose = True
    #CYKParse([ 'Is','Doomfletch', 'more', 'expensive', 'than','Soul_Taker'], getGrammarItems())
    #CYKParse(['What','is', 'the', 'exalted','value' ,'of' ,'Soul_Taker'], getGrammarItems())