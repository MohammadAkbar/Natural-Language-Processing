#!/usr/bin/env python
# coding: utf-8

# ## Spell Checker
# *by Mohammad Akbar*

# In order to check spelling we need a dictionary.<br/>
# For this program we will be using the dictionary `words.words()` from the `nltk` (natural language tool kit) module.

# In[5]:


import nltk
nltk.download('wordnet')
from nltk.corpus import brown


# Now we import the regex package `re`.

# In[6]:


import re


# We will use `sortedcontainers` to improve performance.

# In[7]:


from sortedcontainers import SortedSet,SortedList


# Unfortunately, `wordnet` does **NOT** include:<br/> `determiners`, `prepositions`, `pronouns`, `conjunctions`, `particles`, `auxiliary verbs`.<br/>
# Lets add these to our dictionary manually

# In[8]:


ACCEPTED = SortedSet([])
notACCEPTED = SortedSet([])
CUSTOMDICT = SortedSet([])
ALLWORDS = SortedList([])
ALLERRORS = SortedList([])

import os

def genCustom():
    filenms = [name for name in os.listdir("./hardcode") if name.endswith(".txt")]
    print(filenms)
    for filenm in filenms:
        with open("./hardcode/"+filenm,'r') as file:
            print("fileopened",filenm,file)
            for line in file:
                print("*", end =" ")
                word = "".join(line.split())
                if word not in brown.words():
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
    if word in CUSTOMDICT or word in brown.words():
        return True
    return False

#genCustom()
readCustom()


# Time to start parsing our file!

# In[ ]:


def acceptWord(word):
    if word not in ACCEPTED:
        ACCEPTED.add(word)
    if word in notACCEPTED:
        ACCEPTED.discard(word)
    if word in ALLERRORS:
        ALLERRORS.discard(word)
    ALLWORDS.add(word)

def rejectWord(word):
    if word not in notACCEPTED:
        notACCEPTED.add(word)
    ALLERRORS.add(word)

pattern = re.compile(r"([\w\-\\']*[a-zA-Z]+[\w\-\']*)") # regex for words with atleast 1 a-zA-Z
with open("mobydick.txt") as file:                         # open input file
    for count , line in enumerate(file):                      # foreach line
        for match in re.finditer(pattern, line):                 # foreach word in line
            word = line[match.start():match.end()].lower()          # words found in line, forced lowercase
            if word in notACCEPTED:                                 # if word already memoized
                continue                                               # go to next word
            elif word in ACCEPTED or lookUp(word):                  # if word in wordnet, 'asrnv' means nouns,verbs,... 
                acceptWord(word)
            else:                                                   # else word NOT in wordnet
                rejectWord(word)                                    # memoize as notACCEPTED


# Great! We have our file parsed. However, there are some false negatives in `notACCEPTED`.<br/>
# Lets account for words ending with `'s` or `s'`

# In[ ]:


def goodApostrophe(word):
    word_no_apst = re.sub("\'s$|s\'$",'',word)
    if word == word_no_apst:
        return False
    elif word_no_apst in ACCEPTED or lookUp(word):
        return True
    else:
        return False


# In[ ]:


for word in notACCEPTED:
    if goodApostrophe(word):
        acceptWord(word)


# We've go as far as we can with dictionaries, but there are still more words to recognize.<br/>
# Lets include compound words next `compound words` example: *gallant-cross-tree*

# In[ ]:


pattern_compound = re.compile(r"([^\-\s]+)")
for word in notACCEPTED:
    accept_compound = True
    roots = re.findall(pattern_compound, word)
    for r , root in enumerate(roots):
        if root in ACCEPTED or lookUp(root) or goodApostrophe(root):
            continue
        else:
            accept_compound = False
            break
    if word.startswith('-') or word.endswith('-'):
        accept_compound = False
    if accept_compound:
        acceptWord(word)


# In[ ]:


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


# In[ ]:


from IPython.display import HTML, display
import tabulate
import copy

def insert():
    return 1

def delete():
    return 1

def replace():
    return 1

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
        
def minEditDist(strA , strB , max_dist):
    m , n = len(strA) , len(strB)
    if m==0 or n==0 :
        return max(m,n)
    if abs(m - n) > max_dist:
        return abs(m - n)
    table = [['X']*(n+2) for i in range(m+2)]
    for i in range(m+2):
        rowMin = max_dist + 1
        for j in range(n+2):
            if( (i,j)==(0,0) ):
                table[i][j] = 'X'
            elif( (i,j)==(0,1) or (i,j)==(1,0)):
                table[i][j] = '#'
            elif( i==0 ):
                table[i][j] = strB[j-2]
            elif( j==0 ):
                table[i][j] = strA[i-2]
            elif( i==1 ):
                table[i][j] = j-1
            elif( j==1 ):
                table[i][j] = i-1
            elif( strA[i-2] == strB[j-2] ):
                table[i][j] = table[i-1][j-1]
            else: 
                table[i][j] = min(  table[i  ][j-1] + insert(),    # Insert 
                                    table[i-1][j  ] + delete(),    # Remove 
                                    table[i-1][j-1] + replace())    # Replace
            # check termination
            if( i!=0 and j!=0 ):
                rowMin = min(rowMin,table[i][j])
        if( i!=0 and j!=0 and rowMin > max_dist ):
            return max_dist+1
    #if(table[i][j] < max_dist):
        #traceBack(strA,strB,table)
    #display(HTML(tabulate.tabulate(table, tablefmt='html')))
    return table[i][j]
minEditDist("intention" , "execution" , 9)


# In[ ]:


print(wn.synsets('answered'))


# In[ ]:


for lemma in wn.synset('stretch.v.02').lemmas():
    print(lemma, lemma.frame_ids())
    print(" | ".join(lemma.frame_strings()))


# In[ ]:


from nltk import FreqDist
from nltk.corpus import brown
frequency_list = FreqDist(w.lower() for w in brown.words() if re.search('[a-zA-Z]+',w) )
for word in ALLWORDS:
    frequency_list[word.lower()] += 1
    break


# In[ ]:


from ipypb import irange
from operator import itemgetter, attrgetter
from collections import deque
print("here")


# In[ ]:


for i in irange(0,len(notACCEPTED[:]),1):
    misspelled = notACCEPTED[i]
    minEdit = -len(misspelled)
    top3 = deque([[" ",minEdit,0],[" ",minEdit,0],[" ",minEdit,0],[" ",minEdit,0]],3)
    minEdit = top3[2][1]
    for j , Dword in enumerate(frequency_list):
        editDist = -minEditDist(misspelled , Dword , -minEdit)
        if editDist >= minEdit:
            f = -frequency_list[Dword]
            entry = [Dword,editDist,f]
            top4 = list(top3)
            minEdit = top3[2][1]
            top4 += [entry]
            top4 = sorted(top4, key=itemgetter(1,2))
            top3 = deque(top4,3)
    top3list = list(top3)
    top3list.reverse()
    print(misspelled,":",' , '.join([row[0]+" d="+str(-row[1])+" f="+str(-row[2]) for row in top3list]))


# In[ ]:




