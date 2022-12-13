DROP DATABASE SocioBee;
CREATE DATABASE SocioBee;
Use SocioBee;

-- -----------------------------------------------------
-- Table Hive
-- -----------------------------------------------------
CREATE TABLE Hive (
  id INT NOT NULL AUTO_INCREMENT,
  city varchar(30) not null,
  # Others?
  PRIMARY KEY (id)
);


-- -----------------------------------------------------
-- Table Airdata
-- -----------------------------------------------------
CREATE TABLE AirData (
  id INT NOT NULL AUTO_INCREMENT,
  No2 DOUBLE NULL DEFAULT NULL,
  Co2 DOUBLE NULL DEFAULT NULL,
  PRIMARY KEY (id)
);

-- -----------------------------------------------------
-- Table Member
-- -----------------------------------------------------
CREATE TABLE Member (
  id INT NOT NULL AUTO_INCREMENT,
  name VARCHAR(30) NULL DEFAULT NULL,
  surname VARCHAR(30) NULL DEFAULT NULL,
  age INT NULL DEFAULT NULL,
  mail  varchar(50) not null,
  city VARCHAR(30) NULL DEFAULT NULL,
  gender VARCHAR(30) NULL DEFAULT 'I dont want to answer',
  PRIMARY KEY (id)
  );


-- -----------------------------------------------------
-- Table role
-- -----------------------------------------------------
CREATE TABLE Role (
    hive_id int not null, 
    role ENUM("WorkerBee","QueenBee","BeeKeeper","DroneBee" ) not null default "WorkerBee", 
    member_id int not null,
    PRIMARY KEY (member_id,hive_id, role),
    FOREIGN KEY (hive_id)
    REFERENCES Hive (id),
    FOREIGN KEY (member_id)
    REFERENCES Member (id)
);

-- -----------------------------------------------------
-- Table Campaign
-- -----------------------------------------------------
CREATE TABLE Campaign (
  hive_id int not null, 
  id INT NOT NULL AUTO_INCREMENT,
  creator_id INT NULL DEFAULT NULL,
  city VARCHAR(30) NULL DEFAULT NULL,
  start_timestamp TIMESTAMP NULL DEFAULT NULL,
  cell_edge INT NULL DEFAULT NULL,
  min_samples INT NULL DEFAULT NULL,
  sampling_period INT NULL DEFAULT NULL,
  planning_limit_time INT NULL DEFAULT NULL,
  campaign_duration INT NULL DEFAULT NULL,
  PRIMARY KEY (id, hive_id),
    FOREIGN KEY (creator_id)
    REFERENCES Member (id),
     FOREIGN KEY (hive_id)
    REFERENCES Hive (id)
   );


-- -----------------------------------------------------
-- Table Surface
-- -----------------------------------------------------
CREATE TABLE Surface (
  id INT NOT NULL AUTO_INCREMENT,
  campaign_id INT not NULL,
  PRIMARY KEY (id, campaign_id),
    FOREIGN KEY (campaign_id)
    REFERENCES Campaign (id));


-- -----------------------------------------------------
-- Table Boundary
-- -----------------------------------------------------

CREATE TABLE Boundary (
  id INT NOT NULL AUTO_INCREMENT,
  surface_id INT not NULL ,
  boundary LINESTRING NULL DEFAULT NULL,
  PRIMARY KEY (id, surface_id),
    FOREIGN KEY (surface_id)
    REFERENCES Surface (id))
;


-- -----------------------------------------------------
-- Table Cell
-- -----------------------------------------------------
CREATE TABLE Cell (
  id INT NOT NULL AUTO_INCREMENT,
  inferior_coord POINT not null,
  superior_coord POINT not null,
  center POINT not NULL,
  cell_type VARCHAR(30) NULL DEFAULT 'Dynamic',
  surface_id INT not null,
  #campaign_id INT not null, 
  #Todo: no estoy segura de esto pero bueno... 
  PRIMARY KEY (id),
    FOREIGN KEY (surface_id)
    REFERENCES Surface (id)#,
    #FOREIGN KEY (campaign_id)
    #REFERENCES Campaign (id)
    );


-- -----------------------------------------------------
-- Table Slot
-- -----------------------------------------------------
CREATE TABLE Slot (
id int not null auto_increment,
cell_id INT not null,
start_timestamp timestamp, 
end_timestamp timestamp, 
PRIMARY key(id,cell_id),
FOREIGN KEY (cell_id)
    REFERENCES Cell (id)
);


-- -----------------------------------------------------
-- Table State
-- -----------------------------------------------------
Create TABLE State(
   id INT NOT NULL AUTO_INCREMENT,
   state varchar(20) not null default 'created', 
   # created, send, open, acepted, planningm realized
   initiative_human boolean default False,
   timestamp_update timestamp,
   PRIMARY KEY (id)
   );
   
   

-- -----------------------------------------------------
-- Table CellMeasurement
-- -----------------------------------------------------
CREATE TABLE Measurement (
  id INT NOT NULL AUTO_INCREMENT,
  cell_id INT NOT NULL,
  #campaign_id INT not null,
  member_id INT NOT NULL,
  timestamp TIMESTAMP NULL DEFAULT NULL,
  slot_id int not null, 
  measurement_type VARCHAR(30) NULL DEFAULT 'AirData',
  airdata_id INT DEFAULT NULL,
  location POINT NULL DEFAULT NULL,
  PRIMARY KEY (id, member_id),
    FOREIGN KEY (cell_id)
    REFERENCES Cell (id),
    #FOREIGN KEY (campaign_id)
    #REFERENCES Campaign (id),
    FOREIGN KEY (Airdata_id)
    REFERENCES AirData (id),
    FOREIGN KEY (member_id)
    REFERENCES Member (id),
     FOREIGN KEY (slot_id)
    REFERENCES Slot (id)
    );


-- -----------------------------------------------------
-- Table sociobee.recommendation
-- -----------------------------------------------------
CREATE TABLE Recommendation (
  id int not null auto_increment,
  cell_id INT NOT NULL,
  #campaign_id int not null, 
  member_id INT NOT NULL,
  recommendation_timestamp TIMESTAMP NOT NULL,
  planning_timestamp TIMESTAMP DEFAULT NULL,
  slot_id int, 
  member_current_location POINT NULL, 
  measurement_id INT NULL DEFAULT NULL,
  state_id INT, 
  PRIMARY KEY (id,member_id),
    FOREIGN KEY (cell_id)
    REFERENCES Cell (id),
     #FOREIGN KEY (campaign_id)
    #REFERENCES Campaign (id),
    FOREIGN KEY (state_id)
    REFERENCES State (id),
    FOREIGN KEY (member_id)
    REFERENCES Member (id),
    FOREIGN KEY (measurement_id)
    REFERENCES Measurement (id),
    FOREIGN KEY (slot_id)
    REFERENCES Slot (id)
    );


-- -----------------------------------------------------
-- Table CellPriority
-- -----------------------------------------------------
CREATE TABLE Priority (
  slot_id INT NOT NULL ,
  timestamp TIMESTAMP NOT NULL,
  temporal_priority float8 NULL DEFAULT NULL,
  trend_priority float8 NULL DEFAULT NULL,
  PRIMARY KEY (slot_id, timestamp),
    FOREIGN KEY (slot_id)
    REFERENCES Slot (id));


