import src.Connexion as Conexion
from datetime import datetime
import datetime
import random
import pandas as pd
import numpy as np
import math


start_campaing = datetime.datetime.now()
print(start_campaing)
nDynamicas=30
nStatic=10
max_sampling_time_slot = 150
min_sampling_time_slot =10
sampling_period = 60 * 60 * 3
ntimeslots=3
campaign_duration = ntimeslots * (60 * 3 * 60)
min_number_samples=100

print(start_campaing+datetime.timedelta(seconds=campaign_duration))


# Dados los datos del CampaignManager y el numeor de celdas Estaticas y Dinamicas crea los datos.
# Falta los datos de la surface.
# No se si deberia venirnos con el id del CampaignManager

def generarUNACampaña(bd, Campaing_dic, n_cellDynamic, n_cellStatic):
        # Generar el CampaignManager y obtener su ID
        # Generar la campaña
        print(Campaing_dic)
        CampaignID = bd.insertCampaign(manager_id=str(Campaing_dic["manager_id"]),
                                       min_samples=str(campaing_dic["min_samples"]),
                                       start_timestamp="'"+str(campaing_dic["start_timestamp"])+"'",
                                       sampling_period=str(campaing_dic["sampling_period"]),
                                       campaign_duration=str(campaing_dic["campaign_duration"])
                                       )
        # Crear la Surface
        Surface_id = bd.insertSurface(campaign_id=CampaignID)
        bd.client.commit()
        # Generar las celdas de la campaña
        ListDynamicCellsID = []
        ListStaticCellsID = []
        for i in range(n_cellDynamic):
            id=bd.insertCell(surface_id=Surface_id)
            ListDynamicCellsID.append(id)
        for i in range(n_cellStatic):
            ListStaticCellsID.append(bd.insertCell(cell_type="'Static'", surface_id=Surface_id))
        return ListDynamicCellsID, ListStaticCellsID

def generarDataINCell():
    nTimeSlots=6

def insertData(bd,dinamicaID, estaticaID):
    m = campaign_duration // sampling_period
    if campaign_duration % sampling_period != 0:
        m = m + 1
    for k in dinamicaID:
        for i in range(0, m):
            timestamp_time_slot = start_campaing + datetime.timedelta(seconds=i*sampling_period)
            timestamp_time_slot = timestamp_time_slot.strftime('%Y-%m-%d %H:%M:%S')
            n_Medidas = random.randint(min_sampling_time_slot, max_sampling_time_slot)
            for j in range(0, n_Medidas):
                bd.insertCellMeasurement(cell_id=k, timestamp="'" + timestamp_time_slot + "'")
    for k in estaticaID:
        for i in range(0, m):
            timestamp_time_slot = start_campaing + datetime.timedelta(seconds=i*sampling_period)
            timestamp_time_slot = timestamp_time_slot.strftime('%Y-%m-%d %H:%M:%S')
            n_Medidas = 100
            for j in range(0, n_Medidas):
                bd.insertCellMeasurement(cell_id=k, timestamp="'" + timestamp_time_slot + "'")

def measurements(bd,dinamicas,estatica):
    m = campaign_duration // sampling_period
    if campaign_duration % sampling_period != 0:
        m = m + 1
    index = []
    a = list(range(m + 1))
    col = a
    for i in range(0, nDynamicas+nStatic):
        index.append(i)
        #index.append("cell_id"+str(i))
        index.append('P_t' + str(i))
        index.append('P_n' + str(i))

    f = pd.DataFrame(np.zeros((len(col), len(index))), index=col, columns=index)
    for i in range(0, nDynamicas+nStatic):
        for j in range(0, m) : #MIRAR SI EL Indice va hasta donde quiero.
            if (i >= nDynamicas):
                f.loc[j + 1, i] = 100 # No necesito preguntar pero se podria.
                #f.loc[j+1,"cell_id"+str(i)]=estatica[i-nDynamicas]
                cell_id=estatica[i-nDynamicas]
                timestamp_time_slot = start_campaing + datetime.timedelta(seconds=j*sampling_period)
                timestamp_time = "'"+str(timestamp_time_slot.strftime('%Y-%m-%d %H:%M:%S'))+"'"

            else:
                #f.loc[j+1,'cell_id'+str(i)]=dinamica[i]
                cell_id=str(dinamicas[i])
                timestamp_time_slot = start_campaing + datetime.timedelta(seconds=j*sampling_period)
                timestamp_time = "'"+str(timestamp_time_slot.strftime('%Y-%m-%d %H:%M:%S'))+"'"
                end_time_slot_time = timestamp_time_slot + datetime.timedelta(seconds=sampling_period-1)
                end_time = "'"+ str(end_time_slot_time.strftime('%Y-%m-%d %H:%M:%S'))+"'"
                print(timestamp_time , end_time)
                bd.cursor.execute("Select Count(*) from CellMeasurement where "
                                      f"cell_id={cell_id} AND "
                                      f"timestamp between {timestamp_time} and {end_time}")
                elemento=bd.cursor.fetchall()[0][0]
                print(elemento)
                f.loc[j + 1, i] = elemento
            # if (j+1 == 5):
            #    f.loc[j+1, 0] = 100
            b = max(2, 100 - f[i][j])
            a = max(2, 100 - f[i][j + 1])
            result=math.log(a) * math.log(b, f[i][j + 1] + 2)
            f.loc[j + 1, 'P_t' + str(i)] =result # math.log(a) * math.log(b, f[i][j + 1] + 2)
    a = 0
    for j in range(1, m + 1):
        timestamp_time_slot = start_campaing + datetime.timedelta(seconds=(j-1)* sampling_period)
        timestamp_time = "'" + str(timestamp_time_slot.strftime('%Y-%m-%d %H:%M:%S')) + "'"
        for l in range(nDynamicas+nStatic):
             a = a + f[l][j]
        for i in range(0, nDynamicas+nStatic):
            if (i >= nDynamicas):
                cell_id=estatica[i-nDynamicas]
            else:
                cell_id = dinamicas[i]
            result= (f[i][:j + 1].sum() / a) * (nDynamicas+nStatic)
            f.loc[j, 'P_n' + str(i)] =result
            bd.insertCellPriorityMeasurement(cell_id=cell_id,start_sampling_period=timestamp_time,
                                             temporal_priority=f['P_t'+str(i)][j],trend_priority=result)

    return f

if __name__ == '__main__':
    bd = Conexion.Connexion()
    bd.start()
    bd.vaciarDatos()
    bd.vaciarDatos()
    #sampling_period = 3 horas.
    #Tiempo de duracion de la campaña 18 horas.
    # # timeslots = 6

    campaing_dic={"manager_id":bd.insertCampaignManager(),
                  "min_samples":min_number_samples,
                  "sampling_period":sampling_period,
                    "campaign_duration":campaign_duration,
                    "start_timestamp": start_campaing.strftime('%Y-%m-%d %H:%M:%S')
    }
    dinamica, estatica = generarUNACampaña(bd, campaing_dic, nDynamicas, nStatic)
    print(dinamica)
    print(estatica)
    #Insertar las datos!
    insertData(bd,dinamica,estatica)
    f=measurements(bd,dinamica,estatica)
    f.to_csv('h.csv',sep=';',float_format='%.3f')
    bd.close()
# Generar varias campañas.
# # --- INPUTS--------
# nCanpañas = [1]  # Cada una de estas las ha creado un CampaignManager diferente. Estos usuarios se suponen que
# # deberian estar en la base datos yo los creare.
# nCellsDinamicas = [[40]]
# nCellsEstaticas = [[14]]
# #------------
# Total_estatico=[]
# Total_dinamico=[]
#
# for i in range(0,len(nCanpañas)):
#     CampaignManagerID=bd.insertCampaignManager()
#     indices_campaña_estatico=[]
#     indices_campaña_dinamico=[]
#     for j in range(0,nCanpañas[i]):
#         ncellEstaticas_campaña = nCellsEstaticas[i][j]
#         nCellsDynamica_campaña = nCellsDinamicas[i][j]
#         #Hay que mejorar esto pero bueno
#         una,dos=generarUNACampaña(bd,CampaignManagerID,ncellEstaticas_campaña,nCellsDynamica_campaña)
#         indices_campaña_estatico.append(dos)
#         indices_campaña_dinamico.append(una)
#     Total_estatico.append(indices_campaña_estatico)
#     Total_dinamico.append(indices_campaña_dinamico)
# print(Total_dinamico, Total_estatico)
