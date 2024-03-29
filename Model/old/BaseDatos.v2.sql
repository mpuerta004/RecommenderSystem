DROP DATABASE SocioBee;
CREATE DATABASE SocioBee;
Use SocioBee;


-- -----------------------------------------------------
-- Table Airdata
-- -----------------------------------------------------
CREATE TABLE AirData (
  id INT NOT NULL AUTO_INCREMENT UNIQUE,
  No2 DOUBLE NULL DEFAULT NULL,
  Co2 DOUBLE NULL DEFAULT NULL,
  PRIMARY KEY (id)
);


-- -----------------------------------------------------
-- Table QueenBee
-- -----------------------------------------------------
CREATE TABLE QueenBee (
  id INT NOT NULL AUTO_INCREMENT UNIQUE,
  name VARCHAR(30) NULL DEFAULT NULL,
  surname VARCHAR(30) NULL DEFAULT NULL,
  age INT NULL DEFAULT NULL,
  city VARCHAR(30) NULL DEFAULT NULL,
  gender VARCHAR(30) NULL DEFAULT 'I dont want to answer',
  PRIMARY KEY (id));


-- -----------------------------------------------------
-- Table Campaign
-- -----------------------------------------------------
CREATE TABLE Campaign (
  id INT NOT NULL AUTO_INCREMENT UNIQUE,
  queenBee_id INT NULL DEFAULT NULL,
  city VARCHAR(30) NULL DEFAULT NULL,
  start_timestamp TIMESTAMP NULL DEFAULT NULL,
  cell_edge INT NULL DEFAULT NULL,
  min_samples INT NULL DEFAULT NULL,
  sampling_period INT NULL DEFAULT NULL,
  planning_limit_time INT NULL DEFAULT NULL,
  campaign_duration INT NULL DEFAULT NULL,
  PRIMARY KEY (id),
    FOREIGN KEY (queenBee_id)
    REFERENCES QueenBee (id)
   );


-- -----------------------------------------------------
-- Table Surface
-- -----------------------------------------------------
CREATE TABLE Surface (
  id INT NOT NULL AUTO_INCREMENT UNIQUE,
  campaign_id INT NULL DEFAULT NULL,
  PRIMARY KEY (id),
    FOREIGN KEY (campaign_id)
    REFERENCES Campaign (id));


-- -----------------------------------------------------
-- Table Boundary
-- -----------------------------------------------------
CREATE TABLE Boundary (
  id INT NOT NULL AUTO_INCREMENT UNIQUE,
  surface_id INT NULL DEFAULT NULL,
  boundary LINESTRING NULL DEFAULT NULL,
  PRIMARY KEY (id),
    FOREIGN KEY (surface_id)
    REFERENCES Surface (id))
;



-- -----------------------------------------------------
-- Table Cell
-- -----------------------------------------------------
CREATE TABLE Cell (
  id INT NOT NULL AUTO_INCREMENT UNIQUE,
  inferior_coord POINT not null,
  superior_coord POINT not null,
  center POINT NULL DEFAULT NULL,
  cell_type VARCHAR(30) NULL DEFAULT 'Dynamic',
  surface_id INT NULL DEFAULT NULL,
  PRIMARY KEY (id),
    FOREIGN KEY (surface_id)
    REFERENCES Surface (id)
    );



-- -----------------------------------------------------
-- Table Slot
-- -----------------------------------------------------
CREATE TABLE Slot (
id int not null auto_increment unique,
cell_id int not null,
start_timestamp timestamp, 
end_timestamp timestamp, 
PRIMARY key(cell_id,id),
FOREIGN KEY (cell_id)
    REFERENCES Cell (id)
);


-- -----------------------------------------------------
-- Table State
-- -----------------------------------------------------
Create TABLE State(
   id INT NOT NULL AUTO_INCREMENT UNIQUE,
   created boolean default True,
   send boolean default null,
   open boolean default null,
   acepted boolean default null,
   planning boolean default null,
   realized boolean default null,
   timestamp_update timestamp,
   PRIMARY KEY (id)
   );
   
   
-- -----------------------------------------------------
-- Table Participant
-- -----------------------------------------------------
CREATE TABLE Participant (
  id INT NOT NULL AUTO_INCREMENT UNIQUE,
  name VARCHAR(30) NULL DEFAULT NULL,
  surname VARCHAR(30) NULL DEFAULT NULL,
  age INT NULL DEFAULT NULL,
  city VARCHAR(30) NULL DEFAULT NULL,
  gender VARCHAR(30) NULL DEFAULT 'I dont want to answer',
  PRIMARY KEY (id));


-- -----------------------------------------------------
-- Table CellMeasurement
-- -----------------------------------------------------
CREATE TABLE CellMeasurement (
  id INT NOT NULL AUTO_INCREMENT UNIQUE,
  cell_id INT NULL DEFAULT NULL,
  participant_id INT NULL DEFAULT NULL,
  timestamp TIMESTAMP NULL DEFAULT NULL,
  measurement_type VARCHAR(30) NULL DEFAULT 'AirData',
  airdata_id INT NULL DEFAULT NULL,
  location POINT NULL DEFAULT NULL,
  PRIMARY KEY (id),
    FOREIGN KEY (cell_id)
    REFERENCES Cell (id),
    FOREIGN KEY (Airdata_id)
    REFERENCES AirData (id),
    FOREIGN KEY (participant_id)
    REFERENCES Participant (id)
    );


-- -----------------------------------------------------
-- Table sociobee.recommendation
-- -----------------------------------------------------
CREATE TABLE Recommendation (
  cell_id INT NOT NULL,
  participant_id INT NOT NULL,
  recommendation_timestamp TIMESTAMP NOT NULL,
  planning_timestamp TIMESTAMP DEFAULT NULL,
  cellMeasurement_id INT NULL DEFAULT NULL,
  state_id INT, 
  PRIMARY KEY (participant_id, cell_id, recommendation_timestamp),
    FOREIGN KEY (cell_id)
    REFERENCES Cell (id),
    FOREIGN KEY (state_id)
    REFERENCES State (id),
    FOREIGN KEY (participant_id)
    REFERENCES Participant (id),
    FOREIGN KEY (cellMeasurement_id)
    REFERENCES CellMeasurement (id)
    );


-- -----------------------------------------------------
-- Table CellMeasurementpromise
-- -----------------------------------------------------
CREATE TABLE MeasurementPromise (
  cell_id INT NOT NULL,
  participant_id INT NOT NULL,
  cellMeasurement_id INT NULL DEFAULT NULL,
  state_id INT,
  timestamp_send timestamp,
  promise_timestamp timestamp default NULL,
  PRIMARY KEY (cell_id, participant_id,timestamp_send),
    FOREIGN KEY (cell_id)
    REFERENCES Cell (id),
    FOREIGN KEY (state_id)
    REFERENCES State (id),
    FOREIGN KEY (participant_id)
    REFERENCES Participant (id),
    FOREIGN KEY (cellMeasurement_id)
    REFERENCES CellMeasurement (id)
    );


-- -----------------------------------------------------
-- Table CellPriority
-- -----------------------------------------------------
CREATE TABLE CellPriority (
  slot_id INT NOT NULL ,
  timestamp TIMESTAMP NOT NULL,
  temporal_priority float8 NULL DEFAULT NULL,
  trend_priority float8 NULL DEFAULT NULL,
  PRIMARY KEY (slot_id, timestamp),
    FOREIGN KEY (slot_id)
    REFERENCES Slot (id));


