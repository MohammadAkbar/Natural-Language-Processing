#!/usr/bin/env python

import time

def insert():
    return 1

def delete():
    return 1

def replace(a,b):
    if a==b:
        return 0
    return 1

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

table = [[0]*(100) for i in range(100)]
def minEditDist(strA , strB , max_dist):
    strA , strB = prep(strA,strB)
    m , n = len(strA) , len(strB)
    if m==0 or n==0 :
        return max(m,n)
    if abs(m - n) > max_dist:
        return max_dist+1
    
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