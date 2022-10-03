import Conexion

# --- INPUTS
nCanpañas = 5
nCellsDinamicas = [5, 50, 30, 4, 6]
nCellsEstaticas = [30, 60, 1, 3, 4]

# ---------

nCellsTotal = []
for i in range(0, nCanpañas):
    nCellsTotal.append(nCellsDinamicas[i] + nCellsEstaticas[i])


def CrearCampañas(bd, queenBeeID):
    for j in range(0, nCanpañas):
        bd.cursor.execute("INSERT into Campaign (createdBy) values (" + str(queenBeeID) + ");")  # ;'
        bd.client.commit()
    bd.cursor.execute("Select campaignID from Campaign Where createdBy=" + str(queenBeeID) + ";")
    CampanaIDs = []
    for j in bd.cursor.fetchall():
        CampanaIDs.append(j[0])
    tipo = 'Dynamic'
    ListOfCellIDs = []
    for c in range(len(CampanaIDs)):
        for i in range(0, nCellsTotal[c]):
            if i == nCellsDinamicas:
                tipo = 'Static'
            bd.cursor.execute(
                "INSERT into Cell (type,isInCampaign) values ('" + tipo + "'," + str(CampanaIDs[c]) + ");")
            bd.client.commit()
        bd.cursor.execute("Select cellID from Cell Where isInCampaign=" + str(CampanaIDs[c]) + ";")
        ListCells = []
        for t in bd.cursor.fetchall():
            ListCells.append(t[0])
        ListOfCellIDs.append(ListCells)
    return ListOfCellIDs


if __name__ == '__main__':
    bd = Conexion.Connexion()
    bd.start()
    bd.vaciarDatos()
    # --- Se supone que tendriamos esta info! --------
    bd.cursor.execute("INSERT into QueenBee (name, surname, age) values ('tralala','tralalala2',40);")  # ;'
    bd.client.commit()
    bd.cursor.execute("Select queenBeeID from QueenBee where name ='tralala' and surname='tralalala2'" ) # aqui tendremos mas datos para preguntar
    for i in bd.cursor.fetchall():
        print(i)  # Optimizar
    queenBeeID = i[0]
    # ------

    ListOfCells = CrearCampañas(bd, queenBeeID)
    print(ListOfCells)
    bd.close()
