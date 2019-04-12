#!/usr/bin/env python
# coding: utf-8

# ## Spell Checker
# *by Mohammad Akbar*

# In order to check spelling we need a dictionary.<br/>
# For this program we will be using the dictionary `words.words()` from the `nltk` (natural language tool kit) module.

# In[1]:


import nltk
nltk.download('wordnet')
from nltk.corpus import wordnet as wn
from nltk import FreqDist
nltk.download('brown')
from nltk.corpus import brown
from ipypb import irange
from operator import itemgetter, attrgetter
from collections import deque


# Now we import the regex package `re`.

# In[2]:


import re


# We will use `sortedcontainers` to improve performance.

# In[3]:


from sortedcontainers import SortedSet,SortedList


# Unfortunately, `wordnet` does **NOT** include:<br/> `determiners`, `prepositions`, `pronouns`, `conjunctions`, `particles`, `auxiliary verbs`.<br/>
# Lets add these to our dictionary manually

# In[4]:


ACCEPTED = SortedSet([])
notACCEPTED = SortedSet([])
CUSTOMDICT = SortedSet([])
ALLWORDS = SortedList([])
ALLERRORS = SortedList([])

import os

def genCustom():
    filenms = [name for name in os.listdir("./hardcode") if name.endswith(".txt")]
    for filenm in filenms:
        with open("./hardcode/"+filenm,'r') as file:
            print("fileopened",filenm,file)
            for line in file:
                print("*", end =" ")
                word = "".join(line.split())
                if wn.synsets(word,'asrnv'):
                    ACCEPTED.add(word.lower())
    f = open("./hardcode/custom_dict.txt", "w")
    for word in ACCEPTED:
        f.write(word+"\n")
    f.close()

def readCustom():
    with open("./hardcode/custom_dict.txt",'r') as file:
        for line in file:
            word = "".join(line.split())
            CUSTOMDICT.add(word.lower())

def lookUp(word):
    if word in CUSTOMDICT or wn.synsets(word,'asrnv'):
        if word in ACCEPTED:
            return True
        else:
            acceptWord(word)
            return True
    return False

#genCustom()
readCustom()
print("done reading")


# Time to start parsing our file!

# In[5]:


def acceptWord(word):
    ACCEPTED.add(word)
    notACCEPTED.discard(word)
    ALLERRORS.discard(word)
    ALLWORDS.add(word)

def rejectWord(word):
    notACCEPTED.add(word)
    ALLERRORS.add(word)

pattern = re.compile(r"([\w\-\']*[a-zA-Z]+[\w\-\']*)") # regex for words with atleast 1 a-zA-Z
with open("mobydick.txt") as file:                         # open input file
    for count , line in enumerate(file):                      # foreach line
        for match in re.finditer(pattern, line):                 # foreach word in line
            word = line[match.start():match.end()].lower().strip("-")          # words found in line, forced lowercase
            if word in notACCEPTED:                                 # if word already memoized
                continue                                               # go to next word
            elif lookUp(word):                  # if word in wordnet, 'asrnv' means nouns,verbs,... 
                acceptWord(word)
            else:                                                   # else word NOT in wordnet
                rejectWord(word)                                    # memoize as notACCEPTED


# Great! We have our file parsed. However, there are some false negatives in `notACCEPTED`.<br/>
# Lets account for words ending with `'s` or `s'`

# In[6]:


def goodApostrophe(word):
    word_no_apst = re.sub("(\'s$)|(s\'$)",'',word)
    if word == word_no_apst:
        return False
    elif lookUp(word_no_apst):
        return True
    else:
        return False


# In[7]:


for word in notACCEPTED:
    if goodApostrophe(word):
        acceptWord(word)
notACCEPTED = notACCEPTED.difference(ACCEPTED)


# We've go as far as we can with dictionaries, but there are still more words to recognize.<br/>
# Lets include compound words next `compound words` example: *gallant-cross-tree*

# In[8]:


pattern_compound = re.compile(r"([^\-]+)")
for word in notACCEPTED:
    accept_compound = True
    roots = filter(None, word.split('-'))
    for r , root in enumerate(roots):
        if lookUp(root) or goodApostrophe(root):
            continue
        else:
            accept_compound = False
            break
    #if word.startswith('-') or word.endswith('-'):
    #    accept_compound = False
    if accept_compound:
        acceptWord(word)
notACCEPTED = notACCEPTED.difference(ACCEPTED)


# In[9]:


from IPython.display import display, Markdown, Latex
display(Markdown( "**" 
      + format(len(ALLWORDS), ',d')
      + "** (*correctly spelled*) + **"
      + format(len(ALLERRORS), ',d')
      + "** (*NOT in dictionary*) = **" 
      + format(len(ALLWORDS)+len(ALLERRORS), ',d')
      + "** (*total words*)<br/>**"
      + '{0:.2%}'.format(float(len(ALLWORDS))/float(len(ALLWORDS)+len(ALLERRORS))) 
      + "** *correctly spelled*"))


# In[10]:


from IPython.display import HTML, display
import tabulate
import copy

def insert():
    return 1

def delete():
    return 1

def replace(a,b):
    if a==b:
        return 0
    return 2

def traceBack( strA , strB , table):
    align = []
    linetop = ""
    linemid = ""
    linebot = ""
    new_table = copy.deepcopy(table)
    i = len(table)-1 
    j = len(table[0])-1
    while((i,j)!=(1,1)):
        T = table[i][j]
        S = table[i  ][j-1] + insert() if (j-1>0) else 1000000
        D = table[i-1][j  ] + delete() if (i-1>0) else 1000000
        R = 100000
        if(j>1 and i>1):
            if(table[0][j] == table[i][0]):
                R = table[i][j]
            else:
                R = table[i-1][j-1] + replace()
        #print(table[i][j]," ? ", table[i-1][j-1])
        if (S >= R <= D):
            #print("Replace")
            linetop = table[i][0] + " " + linetop
            linemid = "|" + " " + linemid
            linebot = table[0][j] + " " + linebot
            align = [table[i][0] + " - " + table[0][j]] + align
            j = j-1
            i = i-1
        elif (R >= D <= S):
            #print("Delete")
            linetop = table[i][0] + " "+ linetop
            linemid = "|" + " " + linemid
            linebot = "*" + " "+ linebot
            align = [table[i][0] + " - *"] + align
            i = i-1
        else:
            #print("Insert")
            linetop = "*" + " "+ linetop
            linemid = "|" + " " + linemid
            linebot = table[0][j] + " "+ linebot
            align = ["* - " + table[0][j]] + align
            j = j-1
        new_table[i][j] = "<b>" + str(new_table[i][j]) + "</b>"
    print('\n'.join([linetop,linemid,linebot])) 
    #display(HTML(tabulate.tabulate(new_table, tablefmt='html')))
        
def prep(strA , strB):
    m , n = len(strA) , len(strB)
    min_mn = min(m,n)
    start = 0
    end = 1
    while( start < min_mn):
        if strA[start] == strB[start]:
            start+=1
        else:
            strA = strA[start:]
            strB = strB[start:]
            m , n = len(strA) , len(strB)
            min_mn = min(m,n)
            while( end < min_mn):
                if strA[-end] == strB[-end]:
                    end+=1
                else:
                    break
            if(end==1):
                break
            strA = strA[:-end]
            strB = strB[:-end]
            break
    return strA , strB;
    
def minEditDist(strA , strB , max_dist):
    strA , strB = prep(strA,strB)
    m , n = len(strA) , len(strB)
    if m==0 or n==0 :
        return max(m,n)
    if abs(m - n) > max_dist:
        return max_dist+1
    table = [[0]*(n+1) for i in range(m+1)]
    for i in range(m+1):
        rowMin = max_dist + 1
        for j in range(n+1):
            if( i==0 ):
                table[i][j] = j
            elif( j==0 ):
                table[i][j] = i
            else: 
                table[i][j] = min(  table[i  ][j-1] + insert(),    # Insert 
                                    table[i-1][j  ] + delete(),    # Remove 
                                    table[i-1][j-1] + replace(strA[i-1] , strB[j-1]))    # Replace
            # check termination
            rowMin = min(rowMin,table[i][j])
        if( rowMin > max_dist ):
            return max_dist+1
    #if(table[i][j] < max_dist):
        #traceBack(strA,strB,table)
    #display(HTML(tabulate.tabulate(table, tablefmt='html')))
    return int(table[i][j])


# In[11]:


frequency_list = FreqDist(w.lower().strip("-") for w in brown.words() if (re.search('[a-zA-Z]+',w) and lookUp(w)) )
for word in ALLWORDS:
    frequency_list[word.lower()] += 1


# In[12]:


notACCEPTED = notACCEPTED.difference(ACCEPTED)


# In[13]:


for i in irange(0,len(notACCEPTED),1):
    misspelled = notACCEPTED[i]
    maxEdit = len(misspelled)
    top3 = [[" ",maxEdit,0],[" ",maxEdit,0],[" ",maxEdit,0]]
    for DwordR in frequency_list:
        Dword = str(DwordR)
        editDist = minEditDist(misspelled , Dword , maxEdit)
        if editDist <= maxEdit:
            f = int(frequency_list[Dword])
            entry = [ Dword , editDist , f ]
            top3 += [entry]
            top3 = sorted(top3, key=lambda x: (x[1], -x[2]))[:3]
            maxEdit = int(top3[2][1])
    print(misspelled + ": " + ', '.join( list(map( lambda x : x[0],top3))))


# In[ ]:


print(lookUp("world's"))

