import src.PriotityMeasurements.Calculo_prioridades_dinamicas as calculo
import src.Connexion as Conexion
from datetime import datetime
import datetime
import random
import pandas as pd
import numpy as np

import math


#En la prioridad temporal debemos tener en cuenta el mapeo de las celdas.
#Y cuales estan mas cerca que otras.

start_campaing = datetime.datetime.now()
nDynamicas=5
nStatic=1
nPerson = 10
max_sampling_time_slot = 25
min_sampling_time_slot =15
sampling_period = 60 * 60 * 3
ntimeslots=15
campaign_duration = ntimeslots * (60 * 3 * 60)
min_number_samples=20
recursos=10


def asignacion_recursos_maximo_prioridad_temporal(bd, start,end,campaignID):
    bd.cursor.execute("Select C.Cell_id, C.temporal_priority  "
                           "from CellPriorityMeasurement C, Cell Ce, Surface S"
                           f" where c.timestamp BETWEEN  '{start }' AND '{end}' AND "
                           f"C.cell_id=CE.id AND Ce.surface_id=S.campaign_id AND S.campaign_id={campaignID} AND cell_type='Dynamic' ORDER By C.temporal_priority DESC  Limit 1;" )
    a=bd.cursor.fetchall()
    print(a)
    return a[0][0]

def asignacion_por_prediccion(bd,dinamica, slot):
    list=[]
    for i in range(len(dinamica)):
        list.append(0)
    for k in range(recursos):
        max=0
        indice=-1
        for i in range(len(dinamica)):
            time_pasado = start_campaing + datetime.timedelta(seconds=(slot - 1) * sampling_period)
            pasado = time_pasado.strftime('%Y-%m-%d %H:%M:%S')
            time_start = start_campaing + datetime.timedelta(seconds=slot * sampling_period)
            pasado_fin = time_start + datetime.timedelta(seconds=-1)
            pasado_fin = pasado_fin.strftime('%Y-%m-%d %H:%M:%S')
            doble_pasado= start_campaing + datetime.timedelta(seconds=(slot - 2) * sampling_period)
            doble_pasado_str = doble_pasado.strftime('%Y-%m-%d %H:%M:%S')
            doble_pasado_fin= time_pasado + datetime.timedelta(seconds=-1)
            doble_pasado_fin_str = doble_pasado_fin.strftime('%Y-%m-%d %H:%M:%S')
            bd.cursor.execute(f"Select Count(*) from "
                              f"CellMeasurement where cell_id={dinamica[i]} AND timestamp BETWEEN  "
                              f"'{pasado}' AND '{pasado_fin}' ")
            Cardinal_pasado = bd.cursor.fetchall()[0][0] + list[i]
            bd.cursor.execute(f"Select Count(*) from "
                              f"CellMeasurement where cell_id={dinamica[i]} AND timestamp BETWEEN  "
                              f"'{doble_pasado_str}' AND '{doble_pasado_fin_str}' ")
            Cardinal_doble_pasado = bd.cursor.fetchall()[0][0]
            numero=prioridadTemporal_si_asignamos_recurso(Cardinal_doble_pasado, Cardinal_pasado)
            if numero>max:
                max=numero
                indice=i
        list[indice]=list[indice]+1
    print(list)
    return list


def prioridad_moda(list,indice):
     new=[]
     count=0
     for i in range(len(list)):
         if indice==i:
             new.append( len(list)*(list[i]+1)/(sum(list)+1))
         else:
             new.append(len(list)*(list[i] ) / (sum(list) + 1))
     for i in new:
         if i<1:
             count=count + (1-i)
         if i>1:
             count =count + (i-1)
     return count



def prioridadTemporal_si_asignamos_recurso( pasado, actual):
    b = max(2, min_number_samples - pasado)
    a = max(2, min_number_samples - actual -1)
    AA= max(2, min_number_samples - actual)
    return math.log(AA) * math.log(b, actual + 2)- math.log(a) * math.log(b, actual + 2+1)


def CalculoPrioridades(bd, dinamica, statica,CampaignID):
    m = campaign_duration // sampling_period
    if campaign_duration % sampling_period != 0:
        m = m + 1
    m=100
    for slot in range(0,m):
        print(slot)
        if slot==0:
            calculo.insertar_CellMEasurement(bd,slot, dinamica,statica)

        else:
            inicio= start_campaing.strftime('%Y-%m-%d %H:%M:%S')
            inicio_fin= start_campaing + datetime.timedelta(seconds=sampling_period-1)
            fin_inicio=inicio_fin.strftime('%Y-%m-%d %H:%M:%S')
            time_pasado = start_campaing + datetime.timedelta(seconds=(slot - 1) * sampling_period)
            pasado = time_pasado.strftime('%Y-%m-%d %H:%M:%S')
            time_start = start_campaing + datetime.timedelta(seconds=slot * sampling_period)
            start = time_start.strftime('%Y-%m-%d %H:%M:%S')
            pasado_fin = time_start + datetime.timedelta(seconds=-1)
            pasado_fin = pasado_fin.strftime('%Y-%m-%d %H:%M:%S')
            Final_time_slot = start_campaing + datetime.timedelta(seconds=(slot + 1) * sampling_period - 1)
            end = Final_time_slot.strftime('%Y-%m-%d %H:%M:%S')
            list =asignacion_por_prediccion(bd, dinamica,slot)
            for i in range(len(dinamica)):
                bd.cursor.execute(f"Select Count(*) from "
                                          f"CellMeasurement where cell_id={dinamica[i]} AND timestamp BETWEEN  "
                                          f"'{inicio}' AND '{fin_inicio}' ")
                numero = random.randint(0, 3)
                comienza = random.randint(0, 1)
                if comienza==0:
                    numero=-numero
                Cardinal_actual = int(bd.cursor.fetchall()[0][0]) + list[i] + numero
                for n in range(Cardinal_actual):
                    bd.insertCellMeasurement(cell_id=dinamica[i], timestamp="'" + start + "'")
                # else:
                #         bd.cursor.execute(f"Select Count(*) from "
                #                           f"CellMeasurement where cell_id={dinamica[i]} AND timestamp BETWEEN  "
                #                           f"'{pasado}' AND '{pasado_fin}' ")
                #         numero = random.randint(0, 3)
                #         comienza = random.randint(0, 1)
                #         if comienza == 0:
                #             numero = -numero
                #         Cardinal_actual = int(bd.cursor.fetchall()[0][0]) + numero
                #         for n in range(Cardinal_actual):
                #             bd.insertCellMeasurement(cell_id=i, timestamp="'" + start + "'")
            for i in statica:
                bd.cursor.execute(f"Select Count(*) from "
                                          f"CellMeasurement where cell_id={i} AND timestamp BETWEEN  "
                                          f"'{pasado}' AND '{pasado_fin}' ")

                Cardinal_actual = int(bd.cursor.fetchall()[0][0])
                for n in range(Cardinal_actual):
                    bd.insertCellMeasurement(cell_id=i, timestamp="'" + start + "'")
        for i in dinamica:
            calculo.calculoPrioridad(bd, i, slot, start_campaing)
        for i in estatica:
            calculo.calculoPrioridad(bd, i, slot, start_campaing)
            # mayor=0
            # id_mayor=-1
            # for i in dinamica:
            #     pPrioridad, pModa=calculo.calculoPrioridad(bd,i, slot, start_campaing)
            #     pPrioridad_new,pModa=calculoPrioridad_si_asignamos_recurso(bd,i, slot, start_campaing)
            #     if pPrioridad-pPrioridad_new>mayor:
            #         mayor = pPrioridad-pPrioridad_new
            #         id_mayor=i
            # for i in statica:
            #     pPrioridad, pModa=calculo.calculoPrioridad(bd,i, slot, start_campaing)
            #     pPrioridad_new,pModa=calculoPrioridad_si_asignamos_recurso(bd,i, slot, start_campaing)
            #     if pPrioridad-pPrioridad_new>mayor:
            #         mayor = pPrioridad-pPrioridad_new
            #         id_mayor=i






if __name__ == '__main__':
    bd = Conexion.Connexion()
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
    dinamica, estatica, CampaignID = calculo.generarUNACampana(bd, campaing_dic, nDynamicas, nStatic)
    print(dinamica)
    print(estatica)
    CalculoPrioridades(bd, dinamica, estatica,CampaignID)
    f = calculo.comprobacion_numeros(bd, dinamica, estatica)
    f.to_csv("example_data.csv", sep=';', float_format='%.3f', decimal=",")
    print(f)
    bd.close()
