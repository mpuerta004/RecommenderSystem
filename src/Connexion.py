import mysql.connector
import src.Conf as conf

# data = [
#   ('Jane', date(2005, 2, 12)),
#   ('Joe', date(2006, 5, 23)),
#   ('John', date(2010, 10, 3)),
# ]
# stmt = "INSERT INTO employees (first_name, hire_date) VALUES (%s, %s)"
# cursor.executemany(stmt, data)

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

    def insertUser(self, name="NULL", surname="NULL", age="NULL", gender="'I dont want to answer'"):
        self.cursor.execute(f"INSERT INTO USER (name,surname,age,gender) value ({name},{surname},{age},{gender})")
        bd.client.commit()
        id = int(self.cursor.lastrowid)
        return id

    def insertCampaignManager(self, name="NULL", surname="NULL", age="NULL", gender="'I dont want to answer'"):
        self.cursor.execute(
            f"INSERT INTO CampaignManager (name,surname,age,gender) value ({name},{surname},{age},{gender})")
        self.client.commit()
        id = int(self.cursor.lastrowid)

        return id

    def insertCampaign(self, manager_id="NULL", city="NULL", start_timestamp="NULL", cell_radius="NULL",
                       min_samples="NULL", sampling_period="NULL", planning_limit_time="NULL",
                       campaign_duration="NULL"):

        self.cursor.execute(
            f"INSERT INTO Campaign (manager_id,city,start_timestamp,cell_radius,min_samples,"
            f" sampling_period,planning_limit_time,campaign_duration) value"
            f"({manager_id},{city},{start_timestamp},{cell_radius},{min_samples},{sampling_period},"
            f"{planning_limit_time},{campaign_duration})")

        self.client.commit()
        id = int(self.cursor.lastrowid)
        return id

    def insertSurface(self, campaign_id="Null"):
        self.cursor.execute(f"INSERT INTO Surface (campaign_id) value ({campaign_id})")
        self.client.commit()
        id = int(self.cursor.lastrowid)

        return id

    def insertBoundary(self,surface_id="Null",boundary="Null"):
        self.cursor.execute(f"INSERT INTO Boundary (surface_id,boundary) value ({surface_id},{boundary})")
        self.client.commit()
        id = int(self.cursor.lastrowid)

        return id
    def insertCell(self,center="Null",cell_type="'Dynamic'",surface_id="Null"):
        self.cursor.execute(f"INSERT INTO Cell (center,cell_type,surface_id) value ({center},{cell_type},{surface_id})")
        self.client.commit()
        id = int(self.cursor.lastrowid)
        return id

    def insertCellPriorityMeasurement(self,cell_id,timestamp,temporal_priority="Null",trend_priority="Null"):
        self.cursor.execute(f"INSERT INTO CellPriorityMeasurement (cell_id,timestamp,temporal_priority,trend_priority) "
                            f"value ({cell_id},{timestamp},{temporal_priority},{trend_priority})")
        self.client.commit()
        id = int(self.cursor.lastrowid)
        return id
    #Cuidado hay funciones que no tienene id
    def insertCellMeasurementPromise(self, cell_id,user_id,sampling_limit,is_active="TRUE"):
        self.cursor.execute(
            f"INSERT INTO CellMeasurementPromise (cell_id,user_id,sampling_limit,is_active) "
            f"value ({cell_id},{user_id},{sampling_limit},{is_active})")
        self.client.commit()
        id = int(self.cursor.lastrowid)
        return id

    def insertCellMeasurement(self,cell_id="Null",user_id="Null",timestamp="Null",measurement_type="'AirData'",
                              data_id="Null",location="Null"):
        self.cursor.execute(
            f"INSERT INTO  CellMeasurement (cell_id,user_id,timestamp,measurement_type,data_id,location) "
            f"value ({cell_id},{user_id},{timestamp},{measurement_type},{data_id},{location})")
        self.client.commit()
        id = int(self.cursor.lastrowid)
        return id

    def insertAirData(self,measurement_id="Null",No2="Null",Co2="Null"):
        self.cursor.execute(
            f"INSERT INTO  AirData (measurement_id,No2,Co2) "
            f"value ({measurement_id},{No2},{Co2})")
        self.client.commit()
        id = int(self.cursor.lastrowid)
        return id

    def insertRecommendation(self, cell_id,user_id, recommendation_timestamp="NULL", state="'"+"Rejected"+"'"):
        self.cursor.execute(
            f"INSERT INTO  Recommendation (cell_id,user_id,recommendation_timestamp,state) "
            f"value ({cell_id},{user_id},{recommendation_timestamp},{state})")
        self.client.commit()
        id = int(self.cursor.lastrowid)
        return id
    def vaciarDatos(self):
        try:
            self.cursor.execute("Delete from AirData;")  # ;'
            self.client.commit()
            self.cursor.execute("ALTER TABLE AirData AUTO_INCREMENT = 1;")  # ;'
            self.cursor.execute("Delete from CellMeasurement;")  # ;'
            self.client.commit()
            self.cursor.execute("ALTER TABLE CellMeasurement AUTO_INCREMENT = 1;")  # ;'
            self.cursor.execute("Delete from CellMeasurementPromise;")  # ;'
            self.client.commit()
            self.cursor.execute("Delete from CellPriorityMeasurement;")  # ;'
            self.client.commit()
            self.cursor.execute("Delete from Cell;")
            self.client.commit()
            self.cursor.execute("ALTER TABLE Cell AUTO_INCREMENT = 1;")  # ;'
            self.cursor.execute("Delete from Boundary;")
            self.client.commit()
            self.cursor.execute("ALTER TABLE Boundary AUTO_INCREMENT = 1;")  # ;'
            self.cursor.execute("Delete from Surface;")
            self.client.commit()
            self.cursor.execute("ALTER TABLE Surface AUTO_INCREMENT = 1;")  # ;'
            self.cursor.execute("Delete from Campaign;")
            self.client.commit()
            self.cursor.execute("ALTER TABLE Campaign AUTO_INCREMENT = 1;")  # ;'
            self.cursor.execute("Delete from CampaignManager;")
            self.client.commit()
            self.cursor.execute("ALTER TABLE CampaignManager AUTO_INCREMENT = 1;")  # ;'
            self.cursor.execute("Delete from User;")
            self.client.commit()
            self.cursor.execute("ALTER TABLE USer AUTO_INCREMENT = 1;")  # ;'
            self.client.commit()

            return True
        except:
            return False


if __name__ == '__main__':
    bd = Connexion()
    print(bd.start())
    print(bd.insertUser())
    print(bd.insertCampaignManager())
    print(bd.vaciarDatos())
    bd.close()


# Tendria que hacer lo msimo con los alters pero no lo voy a hacer porque no los voy a usar creo
