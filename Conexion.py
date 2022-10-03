import mysql.connector
import Conf

class Connexion:

    def __init__(self):
        self.client = None
        self.cursor=None

    def start(self):
        if self.client == None:
            # cur.execute( "SELECT name FROM User" )
            try:
                self.client = mysql.connector.connect(host='localhost', user='root', passwd='Sesamo940', db='SocioBee')
                self.cursor=self.client.cursor()

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
                self.cursor= False
                return True
            except:
                print("No se ha podido cerrar la conexión")
                return False




if __name__ == '__main__':
    bd = Connexion()
    print(bd.start())


    bd.cursor.execute("INSERT into QueenBee (name, surname, age) values ('tralala','tralalala2',40);")#;'
    bd.client.commit()
    print(bd.cursor.fetchall)
    bd.cursor.execute("Select* from QueenBee")
    for i in bd.cursor.fetchall():
        print(i)
    bd.close()
