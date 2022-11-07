import sys
sys.path.append("/home/ubuntu/carpeta_compartida_docker/RecommenderSystem/src")
from datetime import datetime
from typing import Sequence
from pydantic import BaseModel, HttpUrl
from Connexion import Connexion



# class Recipe(BaseModel):
#     id: int
#     label: str
#     source: str
#     url: HttpUrl


# class RecipeSearchResults(BaseModel):
#     results: Sequence[Recipe]


# class RecipeCreate(BaseModel):
#     label: str
#     source: str
#     url: HttpUrl
#     submitter_id: int

# Todo comprobar si estan bien los string y los int porque no estoy segura...
class Participant():
    id: int
    name: str
    age = int
    surname: str
    gender: str

    # def __init__(self, bd: Connexion = None, name=None, surname=None, age=None, gender="'I dont want to answer'", id: int = None):
    def __init__(self, bd: Connexion = None, name=None, surname=None, age:int=None, gender=None, id: int = None):
        if bd == None:
            self.id = int(id)
            self.name = name
            self.surname = surname
            self.age = age
            self.gender = gender
        else:
            try:
                bd.start()
                bd.cursor.execute("INSERT INTO Participant (name,surname,age,gender) value (%s,%s,%s,%s)" %
                                  ("'{}'".format(name) if name != None else "NULL",
                                   "'{}'".format(
                                       surname) if surname != None else "NULL",
                                   "{}".format(age) if age != None else "NULL",
                                   "'{}'".format(gender) if gender != None else "'I dont want to answer'"))
                bd.client.commit()
                self.id = int(bd.cursor.lastrowid)
                self.name = name
                self.surname = surname
                self.age = age
                self.gender = "I dont want to answer"
            except Exception as err:
                print(err)

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def get_surname(self):
        return self.surname

    def get_age(self):
        return self.age

    def get_gender(self):
        return self.gender

# Todo: Creo que valor predefinido esta en mil sitios


class QueenBee():
    id: int
    name: str
    age = str
    surname: str
    gender: str

    def __init__(self, base: Connexion = None, name=None, surname=None, age=None, gender="I dont want to answer", id: int = None):
        if base == None:

            self.id = int(id)
            self.name = name
            self.surname = surname
            self.age = age
            self.gender = gender
        else:
            try:
                base.start()
                base.cursor.execute("INSERT INTO QueenBee (name,surname,age,gender) value (%s,%s,%s,%s)" %
                                    ("'{}'".format(name) if name != None else "NULL",
                                     "'{}'".format(
                                         surname) if surname != None else "NULL",
                                     "{}".format(
                                         age) if age != None else "NULL",
                                     "'{}'".format(gender) if gender != None else "'I dont want to answer'"))
                base.client.commit()
                self.id = int(base.cursor.lastrowid)
                self.name = name
                self.surname = surname
                self.age = age
                self.gender = "I dont want to answer"

            except Exception as err:
                print(err)

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def get_surname(self):
        return self.surname

    def get_age(self):
        return self.age

    def get_gender(self):
        return self.gender


class Campaign():
    id: int
    queenBee_id: int
    city: str
    start_timestamp: datetime  # timestamp,
    cell_edge: int
    min_samples: int  # INT, # minimum number of times a cell has to be visited in a campaign during its sampling period
    sampling_period: int  # INT,# seconds during which samples will be grouped by campaign
    planning_limit_time: int
    campaign_duration: int  # se

    def __init__(self, queenBee_id: int, city: str, campaign_duration: int, base: Connexion = None, start_timestamp: datetime = None,
                 cell_edge: int = 10, min_samples: int = 12, sampling_period: int = 3600, planning_limit_time: int = 172800, id: int = None):
        if base == None:
            self.id = int(id)
            self.sampling_period = sampling_period
            self.campaign_duration = campaign_duration
            self.cell_edge = cell_edge
            self.city = city
            self.start_timestamp = start_timestamp
            self.min_samples = min_samples
            self.planning_limit_time = planning_limit_time
            self.queenBee_id = int(queenBee_id)
        else:
            try:
                base.start()
                base.cursor.execute(f"INSERT INTO Campaign (queenBee_id,city,start_timestamp,cell_edge,min_samples,"
                                    f" sampling_period,planning_limit_time,campaign_duration) value (%s,%s,%s,%s,%s,%s,%s,%s)" %
                                    (
                                        "{}".format(
                                            queenBee_id) if queenBee_id != None else "NULL",
                                        "'{}'".format(
                                            city) if city != None else "NULL",
                                        "'{}'".format(start_timestamp.strftime(
                                            '%Y-%m-%d %H:%M:%S')) if start_timestamp != None else "NULL",
                                        "{}".format(
                                            cell_edge) if cell_edge != None else "NULL",
                                        "{}".format(
                                            min_samples) if min_samples != None else "NULL",
                                        "{}".format(
                                            sampling_period) if sampling_period != None else "NULL",
                                        "{}".format(planning_limit_time) if planning_limit_time != None else "NULL",
                                        "{}".format(campaign_duration) if campaign_duration != None else "NULL"))

                base.client.commit()
                self.id = int(base.cursor.lastrowid)
                self.sampling_period = sampling_period
                self.campaign_duration = campaign_duration
                self.cell_edge = cell_edge
                self.city = city
                self.start_timestamp = start_timestamp
                self.min_samples = min_samples
                self.planning_limit_time = planning_limit_time
                self.queenBee_id = int(queenBee_id)
            except Exception as err:
                print(err)

    def get_id(self):
        return self.id

    def get_city(self):
        return self.city

    def get_min_samples(self):
        return self.min_samples

    def get_queenBee_id(self):
        return self.queenBee_id

    def get_start_timestamp(self):
        return self.start_timestamp

    def get_cell_edge(self):
        return self.cell_edge

    def get_sampling_period(self):
        return self.sampling_period

    def get_planning_limit_time(self):
        return self.planning_limit_time

    def get_campaign_duration(self):
        return self.campaign_duration


class Surface():
    id: int
    campaign_id: int

    def __init__(self, campaign_id: int = None, base: Connexion = None, id: int = None):
        if base != None:
            try:
                base.start()
                base.cursor.execute(
                    "INSERT INTO Surface (campaign_id) value (%s)" %
                    ("'{}'".format(campaign_id) if campaign_id != None else "NULL"))
                base.client.commit()
                self.id = int(base.cursor.lastrowid)
                self.campaign_id = campaign_id
            except Exception as err:
                print(err)
        else:
            self.id = int(id)
            self.campaign_id = int(campaign_id)

    def get_id(self):
        return self.id

    def get_campaign_id(self):
        return self.campaign_id


class Boundary():
    id: int
    surface_id: int
    boundary: str

    def __init__(self, surface_id: int, id: int = None, base: Connexion = None, boundary: str = None) -> None:
        if base != None:
            try:
                base.start()
                base.cursor.execute(
                    f"INSERT INTO Boundary (surface_id) value (%s)" % ("{}".format(
                        surface_id) if surface_id != None else "NULL"))
                base.client.commit()
                self.id = int(base.cursor.lastrowid)
                self.surface_id = surface_id
                self.boundary = boundary
            except Exception as err:
                print(err)
        else:
            self.id = id
            self.surface_id = surface_id
            self.boundary = boundary

    def get_id(self):
        return self.id

    def get_surface_id(self):
        return self.surface_id

    def get_boundary(self):
        return self.boundary


class Cell():
    id: int
    # Todo: esto debe ser un Point
    center: tuple()
    cell_type: str
    surface_id: int

    def __init__(self, surface_id: int, id: int = None, base: Connexion = None, center: tuple() = None, cell_type="Dynamic"):
        if base == None:
            self.id = int(id)
            self.center = center
            self.cell_type = cell_type
            self.surface_id = int(surface_id)
        else:
            try:
                base.start()
                # Todo: mirar si el center esta bien integrado.
                base.cursor.execute(
                    "INSERT INTO Cell (center,cell_type,surface_id) value (%s,%s,%s)" % (
                        "{}".format(
                            center) if center != None else "NULL",
                        "'{}'".format(
                            cell_type) if cell_type != None else "'Dynamic'",
                        "{}".format(
                            surface_id) if surface_id != None else "'Dynamic'"))
                base.client.commit()
                self.id = int(base.cursor.lastrowid)
                self.center = center
                self.cell_type = "Dynamic"
                self.surface_id = surface_id
            except Exception as err:
                print(err)

    def get_id(self):
        return self.id

    def get_center(self):
        return self.center

    def get_cell_type(self):
        return self.cell_type

    def get_surface_id(self):
        return self.surface_id


class CellMeasurement():
    id: int
    cell_id: int
    participant_id: int
    timestamp: datetime
    measurement_type: str  # set('AirData','Sound') default 'AirData',
    data_id: int
    # https://dev.mysql.com/doc/refman/8.0/en/spatial-types.html
    # Todo: esto e sun point
    location: tuple()  # point,

    def __init__(self, cell_id=str, data_id: int = None, participant_id: int = None, timestamp: datetime = None, location: tuple() = None, id: int = None, base: Connexion = None, measurement_type: str = "AirData") -> None:
        if base == None:
            self.id = int(id)
            self.cell_id = int(cell_id)
            self.timestamp =  datetime.strptime(timestamp, "%d-%m-%Y %H:%M:%S")
            self.measurement_type = measurement_type
            self.data_id = int(data_id)
            self.location = location
            self.participant_id = int(participant_id)
        else:
            try:
                base.start()
                # Todo: location no se si esta bien
                base.cursor.execute(
                    "INSERT INTO  CellMeasurement (cell_id,participant_id,timestamp,measurement_type,data_id,location) "
                    "value (%s,%s,%s,%s,%s,%s)" %
                    ("{}".format(cell_id) if cell_id != None else "NULL",
                     "{}".format(
                         participant_id) if participant_id != None else "NULL",
                        "'{}'".format(timestamp.strftime(
                            '%Y-%m-%d %H:%M:%S')) if timestamp != None else "NULL",
                        "'{}'".format(
                            measurement_type) if measurement_type != None else "'AirData'",
                     "{}".format(data_id) if data_id != None else "NULL",
                     "{}".format(location) if location != None else "NULL"))
                base.client.commit()
                self.id = int(base.cursor.lastrowid)
                self.cell_id = cell_id
                self.timestamp = timestamp
                self.measurement_type = "AirData"
                self.data_id = data_id
                self.location = location
                self.participant_id = participant_id
            except Exception as err:
                print(err)

    def get_id(self):
        return self.id

    def get_cell_id(self):
        return self.cell_id

    def get_participant_id(self):
        return self.participant_id

    def get_measurement_type(self):
        return self.measurement_type

    def get_location(self):
        return self.location


class CellPriorityMeasurement():
    cell_id: int
    timestamp: datetime
    # end_timeSlot TIMESTAMP,
    temporal_priority: float
    trend_priority: float

    def __init__(self, cell_id: int, timestamp: datetime, base: Connexion = None, temporal_priority: float = None, trend_priority: float = None):
        if base == None:
            self.cell_id = cell_id
            self.timestamp = datetime.strptime(timestamp, "%d-%m-%Y %H:%M:%S")
            self.temporal_priority = temporal_priority
            self.trend_priority = trend_priority
        else:
            try:
                base.cursor.execute("INSERT INTO CellPriorityMeasurement (cell_id,timestamp,temporal_priority,trend_priority) "
                                    "value (%s,%s,%s,%s)" % (
                                        "{}".format(
                                            cell_id) if cell_id != None else "NULL",
                                        timestamp.strftime(
                                            '%Y-%m-%d %H:%M:%S') if timestamp != None else "NULL",
                                        "{}".format(
                                            temporal_priority) if temporal_priority != None else "NULL",
                                        "{}".format(trend_priority) if trend_priority != None else "NULL"))

                base.client.commit()
                self.cell_id = cell_id
                self.timestamp = timestamp
                self.temporal_priority = temporal_priority
                self.trend_priority = trend_priority
            except Exception as err:
                print(err)

    def get_cell_id(self):
        return self.cell_id

    def get_timestamp(self):
        return self.timestamp

    def get_temporal_priority(self):
        return self.temporal_priority

    def get_trend_prioriry(self):
        return self.trend_priority


class AirData():
    id: int
    cell_measurement_id: int
    No2: float
    Co2: float

    def __init__(self, base: Connexion = None, id: int = None, cell_measuerement_id: int = None, No2: float = None, Co2: float = None):
        if base == None:
            self.id = id
            self.cell_measurement_id = cell_measuerement_id
            self.Co2 = Co2
            self.No2 = No2
        else:
            try:
                base.start()
                base.cursor.execute("INSERT INTO  AirData (cell_measurement_id,No2,Co2) value (%s,%s,%s)" % (
                    "{}".format(
                        cell_measuerement_id) if cell_measuerement_id != None else "NULL",
                    "{}".format(No2) if No2 != None else "NULL",
                    "{}".format(Co2) if Co2 != None else "NULL"))
                base.client.commit()
                self.id = int(base.cursor.lastrowid)
                self.cell_measurement_id = cell_measuerement_id
                self.Co2 = Co2
                self.No2 = No2
            except Exception as err:
                print(err)

    def get_id(self):
        return self.id

    def get_cell_measurement_id(self):
        return self.cell_measurement_id

    def get_No2(self):
        return self.No2

    def get_Co2(self):
        return self.Co2


class CellMeasurementPromise():
    id: int
    cell_id: int
    participant_id: int
    cell_measurement_id: int
    recommendation_id: int
    is_active: bool  # BOOLEAN default TRUE

    def __init__(self, base: Connexion = None, id: int = None, cell_id: int = None, participant_id: int = None,cell_measurement_id: int = None, recomendation_id: int = None, is_active: bool = True):
        if base == None:
            self.id = id
            self.cell_id = cell_id
            self.participant_id = participant_id
            self.cell_measurement_id = cell_measurement_id
            self.recommendation_id = recomendation_id
            self.is_active = is_active
        else:
            try:
                base.start()
                base.cursor.execute(
                    "INSERT INTO CellMeasurementPromise (cell_id,participant_id, cell_measurement_id,recomendation_id,is_active) value (%s,%s,%s)" % (
                        "{}".format(cell_id) if cell_id != None else "NULL",
                        "{}".format(
                            participant_id) if participant_id != None else "NULL",
                        "{}".format(
                            cell_measurement_id) if cell_measurement_id != None else "NULL",
                        "{}".format(
                            recomendation_id) if recomendation_id != None else "NULL",
                        "{}".format(is_active)))
                base.client.commit()
                self.id = int(base.cursor.lastrowid)
                self.cell_id = cell_id
                self.participant_id = participant_id
                self.cell_measurement_id = cell_measurement_id
                self.recommendation_id = recomendation_id
                self.is_active = is_active
            except Exception as err:
                print(err)

    def get_id(self):
        return self.id

    def get_cell_id(self):
        return self.id

    def get_participant_id(self):
        return self.participant_id

    def get_measurement_id(self):
        return self.cell_measurement_id

    def get_recomendation_id(self):
        return self.recommendation_id

    def get_is_active(self):
        return self.is_active


class Recommendation():
    id: int
    cell_id: int
    participant_id: int
    cell_measurement_id: int
    is_active: bool  # BOOLEAN default TR
    timestamp: datetime  # TIMESTAMP,

    def __init__(self, id: int = None, base: Connexion = None, timestamp: datetime = None, cell_id: int = None, participant_id: int = None, cell_measurement_id: int = None, recomendation_id: int = None, is_active: bool = True):
        if base == None:
            self.id = id
            self.cell_id = cell_id
            self.participant_id = participant_id
            self.cell_measurement_id = cell_measurement_id
            self.timestamp = timestamp
            self.is_active = is_active

        else:
            try:
                base.start()
                base.cursor.execute("INSERT INTO  Recommendation (cell_id,participant_id,cell_measurement_id,timestamp,is_active) values (%s,%s,%s,%s,%s)" % (
                    "{}".format(cell_id) if cell_id != None else "NULL",
                    "{}".format(
                        participant_id) if participant_id != None else "NULL",
                    "{}".format(
                        cell_measurement_id) if cell_measurement_id != None else "NULL",
                    "'{}'".format(timestamp.strftime(
                        '%Y-%m-%d %H:%M:%S')) if timestamp != None else "NULL",
                    "{}".format(
                        is_active)))

                base.client.commit()
                id = int(base.cursor.lastrowid)
                self.cell_id = cell_id
                self.participant_id = participant_id
                self.cell_measurement_id = cell_measurement_id
                self.timestamp = timestamp
                self.is_active = is_active

            except Exception as err:
                print(err)

    def get_id(self):
        return self.id

    def get_participant_id(self):
        return self.participant_id

    def get_cell_id(self):
        return self.cell_id

    def get_cell_measurement_id(self):
        return self.cell_measurement_id

    def get_timestamp(self):
        return self.timestamp

    def get_is_active(self):
        return self.is_active


# Todo comporbar si los requisitos estan bien o no!
# Todo comporbar que los formatos son los indicados.
# Geojson -> formato de entrada para la generacion de campañas
if __name__ == '__main__':

    bd = Connexion()
    con = bd.start()
    print(con)
    if con == True:
        a = QueenBee(base=bd)
        print(a.id)

    bd.close()
