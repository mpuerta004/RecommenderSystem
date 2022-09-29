import random
import pandas as pd
import numpy as np
import math
t_0 = 0
t_final = 900
x = 100
nCells = 2  # random.randint(10,15 )

numeroMininmoSampling=500
def n_sampling():
    dic = []
    for i in range(0, nCells):
        dic.append([])
        longuitud = random.randint(numeroMininmoSampling, t_final)
        t = random.sample(range(0, t_final), longuitud)
        t.sort()
        dic[i].append(t)
        data = []
        dic[i].append(data)
        dic[i].append([])
    return dic


def calcular_subordenamientos(dic):
    m = t_final// x
    if t_final % x != 0:
        m = m + 1
    agrupamientos = []
    for i in range(0, nCells):

        t = dic[i][0]
        agrupamientos.append([])
        for j in range(1, m + 1):
            insertar = []
            for l in t:  # luego reduces la lista a recorrer par ano tener que recorrerla toda
                if t_0 + (j - 1) * x <= l & l < t_0 + j * x:
                    insertar.append(l)
            agrupamientos[i].append(insertar)
    return agrupamientos


def generar(reodenamiento, dic):
    m = t_final // x
    if t_final % x != 0:
        m = m + 1
    index = []
    a = list(range(m + 1))
    col = a
    for i in range(0, nCells):
        index.append(i)
        index.append('P_t'+str(i))
        index.append('P_n'+str(i))

    f = pd.DataFrame(np.zeros((len(col), len(index))), index=col, columns=index)
    for i in range(0, nCells):
        for j in range(0, m):

            y = len(reodenamiento[i][j])
            f.loc[j + 1,i] = y
            if (j+1 == 1):
                f.loc[j+1, 0] = 100
            b=max(2,100-f[i][j])
            f.loc[j+1,'P_t'+str(i)] = max(1,math.log(max(1,abs(f[i][j+1]-100))))*math.log(b,f[i][j+1] +2)
    a=0
    for j in range(1, m + 1):
        for l in range(nCells):
            a=a+f[l][j]
        for i in range(0, nCells):
            print(f[i][:j+1].sum())
            f.loc[j, 'P_n' + str(i)] = (f[i][:j+1].sum() / a) * nCells
    return f

def generar_normal(reodenamiento, dic):
    m = t_final // x
    if t_final % x != 0:
        m = m + 1
    index = []
    a = list(range(m + 1))
    col = a
    for i in range(0, nCells):
        index.append(i)
        index.append('P_t'+str(i))
    f = pd.DataFrame(np.zeros((len(col), len(index))), index=col, columns=index)
    for i in range(0, nCells):
        for j in range(0, m):
            y = len(reodenamiento[i][j])
            f.loc[j + 1,i] = y

        print(f)
    return f




if __name__ == '__main__':
    dic = n_sampling()
    a = calcular_subordenamientos(dic)
    print(a)
    print(generar(a, dic))
