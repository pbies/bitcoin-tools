#!/usr/bin/python3

def modInverse(A, M): 
  
    for X in range(1, M): 
        if (((A % M) * (X % M)) % M == 1): 
            return X 
    return -1
