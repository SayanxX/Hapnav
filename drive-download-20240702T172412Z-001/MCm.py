import math
import numpy as np
#simpson 1/3 rule
s=[]
a=int(input('lower limit of integration:  '))
b=input('upper limit of integration:  ')
#h= float(input('h: '))
h=1/6
n = int((b - a) / h)
x=0
def fx(x):
    return round(2/(1+(x**3)),2)
    
while(x<b):
    v=fx(x)
    s.append(v)
    x=x+h
    
print(s)


def sumofodd(arr):
    con=0
    for i in range(1,n,2):
        con=con+arr[i]
    return round(con,2)
    
def sumofeven(ara):
    sum1=0
    for i in range(2,n-1,2):
        sum1=sum1+ara[i]
    return round(sum1,2)
    
    


o = sumofodd(s)
e = sumofeven(s)
print(o)
print(e)


sol = (h / 3) * ((s[0] + s[n]) + (4 * o) + (2 * e))

print(round(sol,2))