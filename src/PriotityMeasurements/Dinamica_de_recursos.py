#!/usr/bin/python

import sys
sys.path.append("/home/ubuntu/carpeta_compartida_docker/RecommenderSystem/src")
print(sys.path)
from Connexion import Connexion
from PriotityMeasurements.Calculo_prioridades_dinamicas import generarUNACampana 
from datetime import datetime
import datetime
import random
import pandas as pd
import numpy as np

import math

#En la prioridad temporal debemos tener en cuenta el mapeo de las celdas.
#Y cuales estan mas cerca que otras.

start_campaing = datetime.datetime.now()
nDynamicas=10
nStatic=1
nPerson = 10
max_sampling_time_slot = 25
min_sampling_time_slot =15
sampling_period = 60 * 60
ntimeslots=3
campaign_duration = ntimeslots * (60 * 3 * 60)
min_number_samples=120
recursos=2

#
# def asignacion_recursos_maximo_prioridad_temporal(bd, start,end,campaignID):
#     bd.cursor.execute("Select C.Cell_id, C.temporal_priority  "
#                            "from CellPriorityMeasurement C, Cell Ce, Surface S"
#                            f" where c.timestamp BETWEEN  '{start }' AND '{end}' AND "
#                            f"C.cell_id=CE.id AND Ce.surface_id=S.campaign_id AND S.campaign_id={campaignID} AND cell_type='Dynamic' ORDER By C.temporal_priority DESC  Limit 1;" )
#     a=bd.cursor.fetchall()
#     print(a)
#     return a[0][0]
#
# def asignacion_por_prediccion(bd,dinamica, slot):
#     list=[]
#     for i in range(len(dinamica)):
#         list.append(0)
#     for k in range(recursos):
#         max=0
#         indice=-1
#         for i in range(len(dinamica)):
#             time_pasado = start_campaing + datetime.timedelta(seconds=(slot - 1) * sampling_period)
#             pasado = time_pasado.strftime('%Y-%m-%d %H:%M:%S')
#
#             time_start = start_campaing + datetime.timedelta(seconds=slot * sampling_period)
#             time_start_str= time_start.strftime('%Y-%m-%d %H:%M:%S')
#             end = time_start + datetime.timedelta(seconds=sampling_period-1)
#             end_str= end.strftime('%Y-%m-%d %H:%M:%S')
#             pasado_fin = time_start + datetime.timedelta(seconds=-1)
#             pasado_fin = pasado_fin.strftime('%Y-%m-%d %H:%M:%S')
#             bd.cursor.execute(f"Select Count(*) from "
#                               f"CellMeasurement where cell_id={dinamica[i]} AND timestamp BETWEEN  "
#                               f"'{pasado}' AND '{pasado_fin}' ")
#             Cardinal_pasado = bd.cursor.fetchall()[0][0] + list[i]
#             bd.cursor.execute(f"Select Count(*) from "
#                               f"CellMeasurement where cell_id={dinamica[i]} AND timestamp BETWEEN  "
#                               f"'{time_start_str}' AND '{end_str}' ")
#             Cardinal_actual = bd.cursor.fetchall()[0][0]
#             numero=prioridadTemporal_si_asignamos_recurso(Cardinal_pasado, Cardinal_actual)
#             if numero>max:
#                 max=numero
#                 indice=i
#         list[indice]=list[indice]+1
#     print(list)
#     return list
#
#
# def prioridad_moda(list,indice):
#      new=[]
#      count=0
#      for i in range(len(list)):
#          if indice==i:
#              new.append( len(list)*(list[i]+1)/(sum(list)+1))
#          else:
#              new.append(len(list)*(list[i] ) / (sum(list) + 1))
#      for i in new:
#          if i<1:
#              count=count + (1-i)
#          if i>1:
#              count =count + (i-1)
#      return count
#
#
#
# def prioridadTemporal_si_asignamos_recurso( pasado, actual):
#     b = max(2, min_number_samples - pasado)
#     a = max(2, min_number_samples - actual -1)
#     AA= max(2, min_number_samples - actual)
#     return math.log(AA) * math.log(b, actual + 2)- math.log(a) * math.log(b, actual + 2+1)
#
#
#
#
#
#
#
# def CalculoPrioridades(bd, dinamica, statica,CampaignID):
#     m = campaign_duration // sampling_period
#     if campaign_duration % sampling_period != 0:
#         m = m + 1
#     for slot in range(0,m):
#         print(slot)
#         if slot==0:
#             calculo.insertar_CellMEasurement(bd,slot, dinamica,statica)
#             for i in dinamica:
#
#                 calculo.calculoPrioridad(bd, i, slot, start_campaing, True )
#             for i in estatica:
#
#                 calculo.calculoPrioridad(bd, i, slot, start_campaing, True)
#         else:
#             # inicio= start_campaing.strftime('%Y-%m-%d %H:%M:%S')
#             # inicio_fin= start_campaing + datetime.timedelta(seconds=sampling_period-1)
#             # fin_inicio=inicio_fin.strftime('%Y-%m-%d %H:%M:%S')
#             time_pasado = start_campaing + datetime.timedelta(seconds=(slot - 1) * sampling_period)
#             pasado = time_pasado.strftime('%Y-%m-%d %H:%M:%S')
#             time_start = start_campaing + datetime.timedelta(seconds=slot * sampling_period)
#             start = time_start.strftime('%Y-%m-%d %H:%M:%S')
#             pasado_fin = time_start + datetime.timedelta(seconds=-1)
#             pasado_fin = pasado_fin.strftime('%Y-%m-%d %H:%M:%S')
#             Final_time_slot = start_campaing + datetime.timedelta(seconds=(slot + 1) * sampling_period - 1)
#             end = Final_time_slot.strftime('%Y-%m-%d %H:%M:%S')
#             for l in range(5):
#                 list =asignacion_por_prediccion(bd, dinamica,slot)
#                 inicio_un_poco_mas = time_start + datetime.timedelta(seconds=l*sampling_period/5)
#                 inicio_str= inicio_un_poco_mas.strftime('%Y-%m-%d %H:%M:%S')
#                 print(inicio_str)
#                 for i in range(len(dinamica)):
#                     # bd.cursor.execute(f"Select Count(*) from "
#                     #                           f"CellMeasurement where cell_id={dinamica[i]} AND timestamp BETWEEN  "
#                     #                           f"'{inicio}' AND '{fin_inicio}' ")
#                     numero = random.randint(0, 3)
#                     comienza = random.randint(0, 1)
#                     Cardinal_actual =  list[i] + numero
#                     for n in range(Cardinal_actual):
#                         bd.insertCellMeasurement(cell_id=dinamica[i], timestamp="'" + inicio_str + "'")
#                     # else:
#                     #         bd.cursor.execute(f"Select Count(*) from "
#                     #                           f"CellMeasurement where cell_id={dinamica[i]} AND timestamp BETWEEN  "
#                     #                           f"'{pasado}' AND '{pasado_fin}' ")
#                     #         numero = random.randint(0, 3)
#                     #         comienza = random.randint(0, 1)
#                     #         if comienza == 0:
#                     #             numero = -numero
#                     #         Cardinal_actual = int(bd.cursor.fetchall()[0][0]) + numero
#                     #         for n in range(Cardinal_actual):
#                     #             bd.insertCellMeasurement(cell_id=i, timestamp="'" + start + "'")
#                 for i in statica:
#                     # bd.cursor.execute(f"Select Count(*) from "
#                     #                           f"CellMeasurement where cell_id={i} AND timestamp BETWEEN  "
#                     #                           f"'{pasado}' AND '{pasado_fin}' ")
#
#                     Cardinal_actual = min_number_samples//5
#                     for n in range(Cardinal_actual):
#                         bd.insertCellMeasurement(cell_id=i, timestamp="'" + inicio_str + "'")
#                 for i in dinamica:
#
#                     calculo.calculoPrioridad(bd, i, slot, start_campaing,True,inicio_str)
#                 for i in estatica:
#                     bool = False
#                     if l == 5:
#                         bool = True
#                     calculo.calculoPrioridad(bd, i, slot, start_campaing,True,inicio_str)
#
#             # mayor=0
#             # id_mayor=-1
#             # for i in dinamica:
#             #     pPrioridad, pModa=calculo.calculoPrioridad(bd,i, slot, start_campaing)
#             #     pPrioridad_new,pModa=calculoPrioridad_si_asignamos_recurso(bd,i, slot, start_campaing)
#             #     if pPrioridad-pPrioridad_new>mayor:
#             #         mayor = pPrioridad-pPrioridad_new
#             #         id_mayor=i
#             # for i in statica:
#             #     pPrioridad, pModa=calculo.calculoPrioridad(bd,i, slot, start_campaing)
#             #     pPrioridad_new,pModa=calculoPrioridad_si_asignamos_recurso(bd,i, slot, start_campaing)
#             #     if pPrioridad-pPrioridad_new>mayor:
#             #         mayor = pPrioridad-pPrioridad_new
#             #         id_mayor=i
#
# #----------------------------------------------------------------------------------------------------------------

def reciboUser():
    aletorio = random.random()
    if aletorio>0.95:
        return "user", True
    else:
        return "Null", False

def calculoPrioridadTemporal(bd, indicesDinamica, segundo):
    momento_actual = start_campaing + datetime.timedelta(seconds=segundo)
    for slot in range(0,ntimeslots):
        time_pasado = start_campaing + datetime.timedelta(seconds=(slot - 1) * sampling_period)

        time_pasado_str = time_pasado.strftime('%Y-%m-%d %H:%M:%S')
        time_pasado_fin = time_pasado + datetime.timedelta(seconds=sampling_period-1)
        time_pasado_fin_str=time_pasado_fin.strftime('%Y-%m-%d %H:%M:%S')

        time_start = start_campaing + datetime.timedelta(seconds=slot * sampling_period)
        time_start_str = time_start.strftime('%Y-%m-%d %H:%M:%S')
        time_end = time_start + datetime.timedelta(seconds=sampling_period-1)
        time_end_str=time_end.strftime('%Y-%m-%d %H:%M:%S')

        momento_actual_str= momento_actual.strftime('%Y-%m-%d %H:%M:%S')

        if (time_start <= momento_actual and momento_actual <= time_end) :
            print(f"slot actual {slot}")
            for i in indicesDinamica:
                bd.cursor.execute(f"Select Count(*) from "
                              f"CellMeasurement where cell_id={i} AND timestamp BETWEEN  "
                              f"'{time_pasado_str}' AND '{time_pasado_fin}' ")
                Cardinal_pasado = bd.cursor.fetchall()[0][0]
                bd.cursor.execute(f"Select Count(*) from "
                          f"CellMeasurement where cell_id={i} AND timestamp BETWEEN  "
                          f"'{time_start_str}' AND '{time_end_str}' ")
                Cardinal_actual = bd.cursor.fetchall()[0][0]
                print(f"Cardinal actual de la celda {Cardinal_actual}")
                b = max(2, min_number_samples - int(Cardinal_pasado))
                a = max(2, min_number_samples - int(Cardinal_actual))
                result = math.log(a) * math.log(b, int(Cardinal_actual) + 2)

                bd.cursor.execute(f"Select Count(*) from "
                          f"CellMeasurement where timestamp <= '{time_end_str}' ")
                Cardinal_total = bd.cursor.fetchall()[0][0]

                bd.cursor.execute(f"Select Count(*) from "
                          f"CellMeasurement where cell_id={i} AND timestamp <= '{time_end_str}' ")
                Cardinal_total_celda = bd.cursor.fetchall()[0][0]
                if Cardinal_total==0:
                    result_tendy= 0.0
                else:
                    result_tendy = (Cardinal_total_celda / Cardinal_total) * (nDynamicas + nStatic)
                print(f"Prioridad {result} insertada en el momento {momento_actual_str}")
                id = bd.insertCellPriorityMeasurement(cell_id=i, timestamp="'" + momento_actual_str + "'",
                                              temporal_priority=result, trend_priority=result_tendy)



#Esta funcion debe devolver una lista de 10 elementos con los indices en orden de prioridad de las celdas que es importante polinizar.
#Creo que generar una lista de  [0,0,1,3] no es relevante para el usuario asi que no se podran repetir numero
def CalculoDinamicaPrioridad(bd, indicesDinamicas,segundo,campaignID):
    if 3>len(indicesDinamicas):
        cardinal_lista=len(indicesDinamicas)
    else:
        cardinal_lista=3
    calculoPrioridadTemporal(bd, indicesDinamicas, segundo)
    #Calculo el tiempo
    time=start_campaing + datetime.timedelta(seconds=segundo)
    time_str= time.strftime('%Y-%m-%d %H:%M:%S')
    #rPregunto a la base de datos el orden de prioridad temporal.
    bd.cursor.execute("Select C.Cell_id, C.temporal_priority  "
                      "from CellPriorityMeasurement C, Cell Ce, Surface S"
                      f" where C.timestamp ='{time_str}' AND "
                      f"C.cell_id=Ce.id AND Ce.surface_id=S.campaign_id AND S.campaign_id={campaignID} AND cell_type='Dynamic' ORDER By C.temporal_priority DESC  Limit {cardinal_lista};")
    a = bd.cursor.fetchall()
    result = []
    for i in a:
        result.append(i[0])
    return result



def RL(bd,user, listIndicesDinamicaPrioridad):
    t = len(listIndicesDinamicaPrioridad)
    return listIndicesDinamicaPrioridad[random.randint(0,t-1)]

def UpdateMedicionesSinRecommendacion(bd,indicesDinamicas,segundo):
    for i in indicesDinamicas:
        aletorio = random.random()
        if aletorio > 0.85:
            print(f"Adicionales {i}")
            a= random.randint(0,1)
            time = start_campaing + datetime.timedelta(seconds=segundo)
            time_str = time.strftime('%Y-%m-%d %H:%M:%S')
            bd.insertCellMeasurement(cell_id=i, timestamp="'" + time_str + "'")


def asignacion_recursos(bd,indicesDinamicas, indicesEstaticas,CampaignID):
    mediciones =[]
    #horas=(sampling_period * ntimeslots) / (60 * 60)
    for segundo in range(sampling_period*ntimeslots):
        print("----------------------------------------")
        if segundo%30 ==0:
            time = start_campaing + datetime.timedelta(seconds=segundo)
            time_str = time.strftime('%Y-%m-%d %H:%M:%S')
            for j in indicesEstaticas:
                bd.insertCellMeasurement(cell_id=str(j),timestamp="'"+time_str+"'")

        user,bool = reciboUser()
        if bool:
            listIndicesDinamicaPrioridad = CalculoDinamicaPrioridad(bd, indicesDinamicas,segundo,CampaignID)
            print(listIndicesDinamicaPrioridad)
            celda_polinizar = RL(bd, user, listIndicesDinamicaPrioridad )
            print(celda_polinizar)
            mediciones.append([user, celda_polinizar, random.randint(1,180)])
        new=[]
        for i in range(0,len(mediciones)):
            mediciones[i][2]=mediciones[i][2]-1
            if mediciones[i][2]==0:
                time = start_campaing + datetime.timedelta(seconds=segundo)
                time_str = time.strftime('%Y-%m-%d %H:%M:%S')
                bd.insertCellMeasurement(cell_id=str(mediciones[i][1]),timestamp="'"+time_str+"'")
            else:
                new.append(mediciones[i])
        mediciones=new
        UpdateMedicionesSinRecommendacion(bd,indicesDinamicas,segundo)







if __name__ == '__main__':
    bd = Connexion()
    bd.start()
    bd.vaciarDatos()
    bd.vaciarDatos()
    #sampling_period = 3 horas.
    #Tiempo de duracion de la campaña 18 horas.
    # # timeslots = 6

    campaing_dic={"manager_id":bd.insertQueenBee(),
                  "min_samples":min_number_samples,
                  "sampling_period":sampling_period,
                    "campaign_duration": campaign_duration,
                    "start_timestamp": start_campaing.strftime('%Y-%m-%d %H:%M:%S')
    }
    dinamica, estatica, CampaignID = generarUNACampana(bd, campaing_dic, nDynamicas, nStatic)
    print(dinamica)
    print(estatica)
    asignacion_recursos(bd, dinamica, estatica,CampaignID)
    f = calculo.comprobacion_numeros(bd, dinamica, estatica)
    f.to_csv("example_data.csv", sep=';', float_format='%.3f', decimal=",")
    print(f)
    bd.close()

#estoy aqui quiero polinizar y el planning. ->
# con el planning -> moda.