import src.Connexion as Conexion
from datetime import datetime
import datetime
import random
import pandas as pd
import numpy as np

import math

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

print(start_campaing + datetime.timedelta(seconds=campaign_duration))


# Dados los datos del CampaignManager y el numeor de celdas Estaticas y Dinamicas crea los datos.
# Falta los datos de la surface.
# No se si deberia venirnos con el id del CampaignManager

# def generarUNACampaña(bd, Campaing_dic, n_cellDynamic, n_cellStatic):
#         # Generar el CampaignManager y obtener su ID
#         # Generar la campaña
#         print(Campaing_dic)
#         CampaignID = bd.insertCampaign(manager_id=str(Campaing_dic["manager_id"]),
#                                        min_samples=str(Campaing_dic["min_samples"]),
#                                        start_timestamp="'"+str(Campaing_dic["start_timestamp"])+"'",
#                                        sampling_period=str(Campaing_dic["sampling_period"]),
#                                        campaign_duration=str(Campaing_dic["campaign_duration"])
#                                        )
#         # Crear la Surface
#         Surface_id = bd.insertSurface(campaign_id=CampaignID)
#         bd.client.commit()
#         # Generar las celdas de la campaña
#         ListDynamicCellsID = []
#         ListStaticCellsID = []
#         for i in range(n_cellDynamic):
#             id=bd.insertCell(surface_id=Surface_id)
#             ListDynamicCellsID.append(id)
#         for i in range(n_cellStatic):
#             ListStaticCellsID.append(bd.insertCell(cell_type="'Static'", surface_id=Surface_id))
#         return ListDynamicCellsID, ListStaticCellsID

def generarUNACampana(bd, Campaing_dic, n_cellDynamic, n_cellStatic):
    # Generar el CampaignManager y obtener su ID
    # Generar la campaña
    print(Campaing_dic)
    CampaignID = bd.insertCampaign(manager_id=str(Campaing_dic["manager_id"]),
                                   min_samples=str(Campaing_dic["min_samples"]),
                                   start_timestamp="'" + str(Campaing_dic["start_timestamp"]) + "'",
                                   sampling_period=str(Campaing_dic["sampling_period"]),
                                   campaign_duration=str(Campaing_dic["campaign_duration"])
                                   )
    # Crear la Surface
    Surface_id = bd.insertSurface(campaign_id=CampaignID)
    bd.client.commit()
    # Generar las celdas de la campaña
    ListDynamicCellsID = []
    ListStaticCellsID = []
    for i in range(n_cellDynamic):
        id = bd.insertCell(surface_id=Surface_id)
        ListDynamicCellsID.append(id)
    for i in range(n_cellStatic):
        ListStaticCellsID.append(bd.insertCell(cell_type="'Static'", surface_id=Surface_id))
    return ListDynamicCellsID, ListStaticCellsID, CampaignID


def calculoPrioridad(bd, i, slot, start_campaing,bool=True,inicio_str='Null'):
    time_pasado = start_campaing + datetime.timedelta(seconds=(slot - 1) * sampling_period)
    pasado = time_pasado.strftime('%Y-%m-%d %H:%M:%S')
    time_start = start_campaing + datetime.timedelta(seconds=slot * sampling_period)
    start = time_start.strftime('%Y-%m-%d %H:%M:%S')
    pasado_fin = time_start + datetime.timedelta(seconds=-1)
    pasado_fin = pasado_fin.strftime('%Y-%m-%d %H:%M:%S')
    Final_time_slot = start_campaing + datetime.timedelta(seconds=(slot + 1) * sampling_period - 1)
    end = Final_time_slot.strftime('%Y-%m-%d %H:%M:%S')
    bd.cursor.execute(f"Select Count(*) from "
                      f"CellMeasurement where cell_id={i} AND timestamp BETWEEN  "
                      f"'{pasado}' AND '{pasado_fin}' ")
    Cardinal_pasado = bd.cursor.fetchall()[0][0]
    bd.cursor.execute(f"Select Count(*) from "
                      f"CellMeasurement where cell_id={i} AND timestamp BETWEEN  "
                      f"'{start}' AND '{end}' ")
    Cardinal_actual = bd.cursor.fetchall()[0][0]
    b = max(2, min_number_samples - int(Cardinal_pasado))
    a = max(2, min_number_samples - int(Cardinal_actual))
    result = math.log(a) * math.log(b, int(Cardinal_actual) + 2)
    # print(result)
    bd.cursor.execute(f"Select Count(*) from "
                      f"CellMeasurement where timestamp <= '{end}' ")
    Cardinal_total = bd.cursor.fetchall()[0][0]
    bd.cursor.execute(f"Select Count(*) from "
                      f"CellMeasurement where cell_id={i} AND timestamp <= '{end}' ")
    Cardinal_total_celda = bd.cursor.fetchall()[0][0]
    result_tendy = (Cardinal_total_celda / Cardinal_total) * (nDynamicas + nStatic)
    if inicio_str=='Null':
        inicio_str=start
    if bool:
        id = bd.insertCellPriorityMeasurement(cell_id=i, timestamp="'" + inicio_str + "'",
                                          temporal_priority=result, trend_priority=result_tendy)
    return result, result_tendy


def insertar_CellMEasurement(bd, slot, dinamica, statica):
    time_start = start_campaing + datetime.timedelta(seconds=slot * sampling_period)
    start = time_start.strftime('%Y-%m-%d %H:%M:%S')
    for i in dinamica:
        n_Medidas = random.randint(min_sampling_time_slot, max_sampling_time_slot)
        for n in range(n_Medidas):
            bd.insertCellMeasurement(cell_id=i, timestamp="'" + start + "'")
    for t in statica:
        n_Medidas = min_number_samples
        for n in range(n_Medidas):
            bd.insertCellMeasurement(cell_id=t, timestamp="'" + start + "'")


def CalculoPrioridades(bd, dinamica, statica, CampaignID):
    m = campaign_duration // sampling_period
    if campaign_duration % sampling_period != 0:
        m = m + 1
    for slot in range(0, m):
        insertar_CellMEasurement(bd, slot, dinamica, statica)
        for i in dinamica:
            ptemporal, pModa = calculoPrioridad(bd, i, slot, start_campaing)
        for i in estatica:
            ptemporal, pModa = calculoPrioridad(bd, i, slot, start_campaing)


def comprobacion_numeros(bd, dinamica, statica):
    m = campaign_duration // sampling_period
    if campaign_duration % sampling_period != 0:
        m = m + 1
    index = []
    l=40*5+40
    a = list(range(l))
    col = a
    for i in range(0, nDynamicas + nStatic):
        if (i < nDynamicas):
            name = dinamica[i]
            index.append(name)
            # index.append("cell_id"+str(i))
            index.append('P_t' + str(name))
            # index.append('P_n' + str(name))
        else:
            name = statica[i - nDynamicas]
            index.append(name)
            # index.append("cell_id"+str(i))
            index.append('P_t' + str(name))
            index.append('P_n' + str(name))
    f = pd.DataFrame(np.zeros((len(col), len(index))), index=a,columns=index)
    ac=-1
    for slot in range(0, m):
        ac=ac+1
        time_start = start_campaing + datetime.timedelta(seconds=slot * sampling_period)
        start = time_start.strftime('%Y-%m-%d %H:%M:%S')
        Final_time_slot = start_campaing + datetime.timedelta(seconds=(slot + 1) * sampling_period - 1)
        end = Final_time_slot.strftime('%Y-%m-%d %H:%M:%S')
        for i in dinamica:

            bd.cursor.execute(f"Select Count(*) from "
                              f"CellMeasurement where cell_id={i} AND timestamp BETWEEN  "
                              f"'{start}' AND '{end}' ")
            a = bd.cursor.fetchall()

            if a == []:
                a = 0
            else:
                a = a[0][0]
            f.loc[ac, i] = a
            bd.cursor.execute(f"Select temporal_priority, trend_priority from "
                              f"CellPriorityMeasurement where cell_id={i} AND timestamp BETWEEN  "
                              f"'{start}' AND '{end}' ")
            a = bd.cursor.fetchall()

            if a == []:
                a = 0
            else:
                a = a[0][0]
            f.loc[ac, 'P_t' + str(i)] = a
            # f.loc[slot, 'P_n' + str(i)] = a[1]
        for i in statica:
            bd.cursor.execute(f"Select Count(*) from "
                                  f"CellMeasurement where cell_id={i} AND timestamp BETWEEN  "
                                  f"'{start}' AND '{end}' ")
            a = bd.cursor.fetchall()
            if a == []:
                a = 0
            else:
                a = a[0][0]
            print(a)
            f.loc[ac, i] = a
            bd.cursor.execute(f"Select temporal_priority, trend_priority from "
                                  f"CellPriorityMeasurement where cell_id={i} AND timestamp BETWEEN  "
                                  f"'{start}' AND '{end}' ")
            a = bd.cursor.fetchall()
            if a == []:
                a = 0
            else:
                a = a[0][0]
            f.loc[ac, 'P_t' + str(i)] = a


        # llll

        for l in range(5):
            ac=ac+1
            inicio_un_poco_mas = time_start + datetime.timedelta(seconds=l * sampling_period / 5)
            inicio_str = inicio_un_poco_mas.strftime('%Y-%m-%d %H:%M:%S')
            final_un_poco_mas = time_start + datetime.timedelta(seconds= ((l+1) * sampling_period / 5 ) -1)
            final_sub_str=final_un_poco_mas.strftime('%Y-%m-%d %H:%M:%S')
            for i in dinamica:


                bd.cursor.execute(f"Select Count(*) from "
                                  f"CellMeasurement where cell_id={i} AND timestamp BETWEEN  "
                                  f"'{inicio_str}' AND '{final_sub_str}' ")
                a = bd.cursor.fetchall()

                if a == []:
                    a = 0
                else:
                    a = a[0][0]
                f.loc[ac, i] = a
                bd.cursor.execute(f"Select temporal_priority, trend_priority from "
                                  f"CellPriorityMeasurement where cell_id={i} AND timestamp BETWEEN  "
                                  f"'{inicio_str}' AND '{final_sub_str}' ")
                a=bd.cursor.fetchall()

                if a == []:
                    a = 0
                else:
                    a = a[0][0]
                f.loc[ac, 'P_t' + str(i)] = a
                # f.loc[slot, 'P_n' + str(i)] = a[1]
            for i in statica:
                bd.cursor.execute(f"Select Count(*) from "
                                  f"CellMeasurement where cell_id={i} AND timestamp BETWEEN  "
                                  f"'{inicio_str}' AND '{final_sub_str}' ")
                a = bd.cursor.fetchall()
                if a==[]:
                    a=0
                else:
                    a=a[0][0]
                print(a)
                f.loc[ac, i] = a
                bd.cursor.execute(f"Select temporal_priority, trend_priority from "
                                  f"CellPriorityMeasurement where cell_id={i} AND timestamp BETWEEN  "
                                  f"'{inicio_str}' AND '{final_sub_str}' ")
                a = bd.cursor.fetchall()
                if a == []:
                    a = 0
                else:
                    a = a[0][0]
                f.loc[ac, 'P_t' + str(i)] = a
                # f.loc[slot,'P_n'+str(i)]=a[1]
    return f


if __name__ == '__main__':
    bd = Conexion.Connexion()
    bd.start()
    bd.vaciarDatos()
    bd.vaciarDatos()
    # sampling_period = 3 horas.
    # Tiempo de duracion de la campaña 18 horas.
    # # timeslots = 6

    campaing_dic = {"manager_id": bd.insertQueenBee(),
                    "min_samples": min_number_samples,
                    "sampling_period": sampling_period,
                    "campaign_duration": campaign_duration,
                    "start_timestamp": start_campaing.strftime('%Y-%m-%d %H:%M:%S')
                    }
    dinamica, estatica, CampaignID = generarUNACampana(bd, campaing_dic, nDynamicas, nStatic)
    print(dinamica)
    print(estatica)
    CalculoPrioridades(bd, dinamica, estatica, CampaignID)
    f = comprobacion_numeros(bd, dinamica, estatica)
    f.to_csv("example_data.csv", sep=';', float_format='%.3f', decimal=",")
    print(f)
    bd.close()
