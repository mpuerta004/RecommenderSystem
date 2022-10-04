import mysql.connector
import src.Conf as conf


class Connexion:

    def __init__(self):
        self.client = None
        self.cursor = None

    def start(self):
        if self.client == None:
            try:
                self.client = mysql.connector.connect(host='localhost', user='root', passwd=conf.passwd, db='SocioBee')
                self.cursor = self.client.cursor()

                return True
            except:
                print("No se ha podido establecer la conexión:")
                return False
        else:
            return True

    def close(self):
        if self.client is None:
            return True
        else:
            try:
                self.client.close()
                self.client = None
                self.cursor = False
                return True
            except:
                print("No se ha podido cerrar la conexión")
                return False

    def vaciarDatos(self):
        try:
            self.cursor.execute("Delete from AirData;")  # ;'
            self.client.commit()
            self.cursor.execute("Delete from CellMeasurement;")  # ;'
            self.client.commit()
            self.cursor.execute("Delete from CellMeasurementPromise;")  # ;'
            self.client.commit()
            self.cursor.execute("Delete from CellPriorityMeasurement;")  # ;'
            self.client.commit()
            self.cursor.execute("Delete from Cell;")
            self.client.commit()
            self.cursor.execute("Delete from Boundary;")
            self.client.commit()
            self.cursor.execute("Delete from Surface;")
            self.client.commit()
            self.cursor.execute("Delete from Campaign;")
            self.client.commit()
            self.cursor.execute("Delete from CampaignManager;")
            self.client.commit()
            self.cursor.execute("Delete from User;")
            self.client.commit()
            return True
        except:
            return False


if __name__ == '__main__':
    bd = Connexion()
    print(bd.start())
    print(bd.vaciarDatos())

    # bd.cursor.execute("INSERT into CampaignManager (name, surname, age) values ('tralala','tralalala2',40);")  # ;'
    # bd.client.commit()
    # print(int(bd.cursor.lastrowid))

    #bd.cursor.execute("Select* from QueenBee")
    #for i in bd.cursor.fetchall():
    #    print(i)
    bd.close()
