import random
import pandas as pd
import numpy as np
import math
t_0 = 0
t_final = 1000
x = 36
nCellsDinamicas = 5  # random.randint(10,15 )
nCellsEstaticas=30
nCellsTotal=nCellsDinamicas+nCellsEstaticas

numeroMininmoSampling=6



def n_sampling():
    dic = []
    # Este diccionario tiene por cada celda dinamica el timeStap ficticio en el que se supone que se ha polinizado.
    for i in range(0, nCellsDinamicas):
        dic.append([])
        longuitud = random.randint(numeroMininmoSampling, t_final)
        t=[]
        for j in range(0,longuitud):
            t.append(random.uniform(0,t_final))
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
    for i in range(0, nCellsDinamicas):

        t = dic[i][0]
        agrupamientos.append([])
        for j in range(1, m + 1):
            insertar = []
            for l in t:  # luego reduces la lista a recorrer par ano tener que recorrerla toda
                if float(t_0 + (j - 1) * x) <= l < float(t_0 + j * x):
                    insertar.append(l)
            agrupamientos[i].append(insertar)
    return agrupamientos


def measurements(reodenamiento):
    m = t_final // x
    if t_final % x != 0:
        m = m + 1
    index = []
    a = list(range(m + 1))
    col = a
    for i in range(0, nCellsTotal):
        index.append(i)
        index.append('P_t'+str(i))
        index.append('P_n'+str(i))

    f = pd.DataFrame(np.zeros((len(col), len(index))), index=col, columns=index)
    for i in range(0, nCellsTotal):
        for j in range(0, m):
            if (i >= nCellsDinamicas):
                f.loc[j + 1, i] = 100
            else:
                y = len(reodenamiento[i][j])
                f.loc[j + 1,i] = y
            #if (j+1 == 5):
            #    f.loc[j+1, 0] = 100
            if(i>=nCellsDinamicas):
                f.loc[j+1, i] = 100
            b = max(2, 100 - f[i][j])
            a= max(2,100-f[i][j+1])
            f.loc[j+1,'P_t'+str(i)] = math.log(a)*math.log(b,f[i][j+1] +2)
    a=0
    for j in range(1, m + 1):
        for l in range(nCellsTotal):
            a=a+f[l][j]
        for i in range(0, nCellsTotal):
            f.loc[j, 'P_n' + str(i)] = (f[i][:j+1].sum() / a) * nCellsTotal
    return f





if __name__ == '__main__':
    dic = n_sampling()
    a = calcular_subordenamientos(dic)
    print(measurements(a))
