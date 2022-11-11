DROP DATABASE SocioBee;
CREATE DATABASE SocioBee;
Use SocioBee;

# ON DELETE and ON UPDATE


CREATE TABLE Participant (
    id INT UNIQUE AUTO_INCREMENT,
    name VARCHAR(30),
    surname VARCHAR(30),
    age INT,
    city VARCHAR(30),
    gender  VARCHAR(30) default 'I dont want to answer',
    PRIMARY KEY (id)
);

CREATE TABLE QueenBee (
    id INT UNIQUE AUTO_INCREMENT,
    name VARCHAR(30),
    surname VARCHAR(30),
    age INT,
    city VARCHAR(30),
    gender VARCHAR(30) default 'I dont want to answer',
    PRIMARY KEY (id)
);


CREATE TABLE Campaign (
    id INT UNIQUE AUTO_INCREMENT PRIMARY KEY,
    queenBee_id INT,
    city varchar(30),
    start_timestamp timestamp,
    cell_edge INT,
    min_samples INT, # minimum number of times a cell has to be visited in a campaign during its sampling period
    sampling_period INT,# seconds during which samples will be grouped by campaign
    planning_limit_time INT, #  upper number of seconds limit that a sampling promise can be scheduled for
    campaign_duration INT, # seconds during the campaign.
    # A new entity called Surface could be created, a campaign may have M surfaces, where each surface has N hexagons
    FOREIGN  KEY (queenBee_id) REFERENCES QueenBee(id) 
);

CREATE TABLE Surface (
    id INT UNIQUE AUTO_INCREMENT PRIMARY KEY,
    campaign_id INT,
    FOREIGN  KEY (campaign_id) REFERENCES Campaign(id)
);


CREATE TABLE Boundary (
    id INT UNIQUE AUTO_INCREMENT PRIMARY KEY,
    surface_id INT,
    boundary linestring,
    FOREIGN  KEY (surface_id) REFERENCES Surface(id) 
);

CREATE TABLE Cell(
   id INT UNIQUE AUTO_INCREMENT PRIMARY KEY,
   # https://dev.mysql.com/doc/refman/8.0/en/opengis-geometry-model.html
   inferior_coord point,
   superior_coord point,
   center point,
   #Point abajo y arriba de la celda.
   cell_type Varchar(30)  default 'Dynamic', #set('Dynamic','Static')
   surface_id INT,
   FOREIGN KEY (surface_id) REFERENCES Surface(id)
);

CREATE TABLE CellMeasurement (
   id INT UNIQUE AUTO_INCREMENT PRIMARY KEY,
   cell_id INT,
   participant_id  INT,
   timestamp TIMESTAMP,
   measurement_type Varchar(30) default 'AirData', #set('AirData','Sound')
   data_id INT,
   # https://dev.mysql.com/doc/refman/8.0/en/spatial-types.html
   location point,
   FOREIGN KEY (cell_id) REFERENCES Cell(id),
   FOREIGN KEY  (participant_id) REFERENCES  Participant(id)
);

CREATE TABLE CellPriorityMeasurement (
   #This is the priority of pollinating a cell in the timeslot [start_timeSlot,start_timeSlot+sampling_period)
   cell_id INT,
   timestamp TIMESTAMP,
   #end_timeSlot TIMESTAMP,
   temporal_priority float8, 
   trend_priority float8, 
   FOREIGN KEY (cell_id) REFERENCES Cell(id),
   PRIMARY KEY (cell_id,timestamp)
);



CREATE TABLE AirData (
   id INT UNIQUE AUTO_INCREMENT PRIMARY KEY,
   cell_measurement_id INT,
   No2 float8, # I would make a reference to Measurement since we can then generalize it
   Co2 float8,
   FOREIGN KEY (cell_measurement_id) REFERENCES CellMeasurement(id)
);

CREATE TAble Recommendation(
    id INT AUTO_INCREMENT,
    cell_id INT,
    participant_id INT,
    is_active BOOLEAN default TRUE,
    recommendation_timestamp TIMESTAMP,
    cell_measurement_id INT default NULL,
    state Varchar(30)  default 'Rejected', #SET('Rejected', 'Open', 'Planning', 'Realized')
    FOREIGN KEY (cell_id) REFERENCES CellPriorityMeasurement(cell_id),
    FOREIGN KEY (cell_id) REFERENCES Cell(id),
    FOREIGN KEY (participant_id) REFERENCES  Participant(id),
    FOREIGN KEY (cell_measurement_id) REFERENCES CellMeasurement(id),
    Primary KEY (id, participant_id, cell_id)
);
CREATE TABLE CellMeasurementPromise (
   id INT UNIQUE AUTO_INCREMENT,
   cell_id INT,
   participant_id  INT,
   #sampling_limit TIMESTAMP, # limit timestamp -> planning_limit_time
   cell_measurement_id INT,
   recommendation_id INT,
   is_active BOOLEAN default TRUE, # by default set to TRUE but changed once sampling_limit time is exceeded
   FOREIGN KEY (cell_id) REFERENCES Cell(id),
   FOREIGN KEY  (participant_id) REFERENCES  Participant(id),
   FOREIGN KEY  (cell_measurement_id) REFERENCES CellMeasurement(id),
   FOREIGN KEY  (recommendation_id) REFERENCES Recommendation(id),
   PRIMARY KEY (id, cell_id, participant_id)
);


