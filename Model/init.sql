DROP DATABASE IF EXISTS SocioBeeMVE;
/* DELETE USER 'mve' AT LOCAL SERVER*/
DROP USER IF EXISTS 'mve'@'localhost';
DROP USER IF EXISTS 'mve_automatic'@'localhost';


CREATE DATABASE SocioBeeMVE;
use SocioBeeMVE;

/* CREATE THE USER 'mve' AT LOCAL and REMOTE SERVER WITH PASSWORD 'mvepasswd123' */
CREATE USER IF NOT EXISTS 'mve'@'localhost' IDENTIFIED BY 'mvepasswd123';
CREATE USER IF NOT EXISTS 'mve'@'%' IDENTIFIED BY 'mvepasswd123';
CREATE USER IF NOT EXISTS 'mve_automatic'@'localhost' IDENTIFIED BY 'mvepasswd123';
CREATE USER IF NOT EXISTS 'mve_automatic'@'%' IDENTIFIED BY 'mvepasswd123';

GRANT ALL PRIVILEGES ON SocioBeeMVE.*  TO 'mve'@'localhost';
GRANT ALL PRIVILEGES ON SocioBeeMVE.*  TO 'mve'@'%';
GRANT ALL PRIVILEGES ON SocioBeeMVE.*  TO 'mve_automatic'@'localhost';
GRANT ALL PRIVILEGES ON SocioBeeMVE.*  TO 'mve_automatic'@'%';

-- -----------------------------------------------------
-- Table Member
-- -----------------------------------------------------
CREATE TABLE Member (
  id BIGINT NOT NULL,
  birthday datetime,
  name VARCHAR(30) NULL DEFAULT NULL,
  surname VARCHAR(30) NULL DEFAULT NULL,
  age INT NULL DEFAULT NULL,
  mail  varchar(50) not null,
  city VARCHAR(30) NULL DEFAULT NULL,
  gender Varchar(30) default 'NOANSWER',
  CONSTRAINT gender_type CHECK (gender IN ("NOBINARY","MALE","FEMALE",'NOANSWER')),
  real_user  BOOLEAN,
  PRIMARY KEY (id)
  );

CREATE TABLE  BeeKeeper(
  id INT NOT NULL,
  birthday datetime,
  name VARCHAR(30) NULL DEFAULT NULL,
  surname VARCHAR(30) NULL DEFAULT NULL,
  age INT NULL DEFAULT NULL,
  mail  varchar(50) not null,
  city VARCHAR(30) NULL DEFAULT NULL,
  gender Varchar(30) not null default 'NOANSWER',
  real_user  BOOLEAN,
  CONSTRAINT gender_type_beekeeper CHECK (gender IN ("NOBINARY","MALE","FEMALE",'NOANSWER')),
  PRIMARY KEY (id)
  );


-- -----------------------------------------------------
-- Table Hive
-- -----------------------------------------------------
CREATE TABLE Hive (
  id INT NOT NULL,
  beekeeper_id INT, 
  city varchar(30) not null,
  name varchar(30),
  PRIMARY KEY (id),
   FOREIGN KEY (beekeeper_id)
    REFERENCES BeeKeeper (id)
    ON DELETE CASCADE
);


CREATE TABLE Hive_Member(
  hive_id int not null,
  member_id BIGINT not null,
  role Varchar(30) not null default "WorkerBee",
CONSTRAINT role_type_hiveMember CHECK (role IN ("WorkerBee","QueenBee","DroneBee")),
  primary key (hive_id,member_id,role),
   FOREIGN KEY (member_id)
    REFERENCES Member (id)
    ON DELETE CASCADE,
    FOREIGN KEY (hive_id)
    REFERENCES Hive (id)
    ON DELETE CASCADE
);

Create table Device(
id int not null,
PRIMARY KEY (id),
description varchar(30) null default null,
brand varchar(30) null default null,
model varchar(30) null default null, 
year varchar(30) null default null
);


Create Table Member_Device(
  device_id int Unique default Null,
  member_id BIGINT not null, 
  primary key(member_id),
  FOREIGN KEY (member_id)
    REFERENCES Member (id)
    ON DELETE CASCADE,
    FOREIGN KEY (device_id)
    REFERENCES Device (id)
    ON DELETE CASCADE
);


-- -----------------------------------------------------
-- Table Campaign
-- -----------------------------------------------------
CREATE TABLE Campaign (
  hive_id int not null, 
  id INT NOT NULL AUTO_INCREMENT,
  start_datetime datetime NULL DEFAULT NULL,
  cells_distance float8 NULL DEFAULT NULL,
  min_samples INT NULL DEFAULT NULL,
  sampling_period INT NULL DEFAULT NULL,
  hypothesis  VARCHAR(70) NULL DEFAULT NULL,
  end_datetime datetime NULL DEFAULT NULL,
  title Varchar(70),
  PRIMARY KEY (id, hive_id),
     FOREIGN KEY (hive_id)
    REFERENCES Hive (id)
    ON DELETE CASCADE
   );


-- -----------------------------------------------------
-- Table role
-- -----------------------------------------------------
CREATE TABLE Campaign_Member (
    campaign_id int not null, 
    role VARCHAR(30) not null default "WorkerBee", 
    CONSTRAINT role_type CHECK (role IN ("WorkerBee","QueenBee","DroneBee")),
    member_id BIGINT not null,
    PRIMARY KEY (campaign_id, member_id,role),
    FOREIGN KEY (campaign_id)
    REFERENCES Campaign (id)
    ON DELETE CASCADE,
    FOREIGN KEY (member_id)
    REFERENCES Member (id)
    ON DELETE CASCADE
);


-- -----------------------------------------------------
-- Table Boundary
-- -----------------------------------------------------

CREATE TABLE Boundary (
    id INT NOT NULL AUTO_INCREMENT,
    radius float8,
    centre POINT,
    PRIMARY KEY (id))
;


-- -----------------------------------------------------
-- Table Surface
-- -----------------------------------------------------
CREATE TABLE Surface (
  id INT NOT NULL AUTO_INCREMENT,
  campaign_id INT not NULL,
  boundary_id INT not null,
  PRIMARY KEY (id, campaign_id),
    FOREIGN KEY (campaign_id)
    REFERENCES Campaign (id)
    ON DELETE CASCADE,
     FOREIGN KEY (boundary_id)
    REFERENCES Boundary (id)
    ON DELETE CASCADE
    );


-- -----------------------------------------------------
-- Table Cell
-- -----------------------------------------------------
CREATE TABLE Cell (
  id INT NOT NULL AUTO_INCREMENT,
  centre POINT not NULL,
  radius INT,
  cell_type VARCHAR(30) DEFAULT 'Dynamic',
  surface_id INT not null,
  CONSTRAINT cell_type CHECK (cell_type IN ("DYNAMIC","STATIC")),
  PRIMARY KEY (id),
    FOREIGN KEY (surface_id)
    REFERENCES Surface (id)
    ON DELETE CASCADE#,
    );



-- -----------------------------------------------------
-- Table Cell
-- -----------------------------------------------------
CREATE TABLE Bio_inspired (
  cell_id INT NOT NULL,
  member_id BIGINT NOT NULL,
  threshold float, 
  PRIMARY KEY (cell_id,member_id),
    FOREIGN KEY (cell_id)
    REFERENCES Cell (id)
    ON DELETE CASCADE,
    FOREIGN KEY (member_id)
    REFERENCES Member (id)
    ON DELETE CASCADE
    );

-- -----------------------------------------------------
-- Table Slot
-- -----------------------------------------------------
CREATE TABLE Slot (
id int not null auto_increment,
cell_id INT not null,
start_datetime datetime, 
end_datetime datetime, 
PRIMARY key(id,cell_id),
FOREIGN KEY (cell_id)
    REFERENCES Cell (id)
    ON DELETE CASCADE
);



-- -----------------------------------------------------
-- Table sociobee.recommendation
-- -----------------------------------------------------
CREATE TABLE Recommendation (
  id int not null auto_increment,
  member_id BIGINT NOT NULL,
  sent_datetime datetime NOT NULL,
  state  VARCHAR(15),
  update_datetime datetime,
  slot_id int, 
  member_current_location POINT NULL, 
  CONSTRAINT state_type CHECK (state IN ("NOTIFIED","ACCEPTED","REALIZED","NON_REALIZED")),
  PRIMARY KEY (id,member_id),

    FOREIGN KEY (member_id)
    REFERENCES Member (id)
    ON DELETE CASCADE,
    FOREIGN KEY (slot_id)
    REFERENCES Slot (id)
    ON DELETE CASCADE
    );

-- -----------------------------------------------------
-- Table CellMeasurement
-- -----------------------------------------------------
CREATE TABLE Measurement (
  id INT NOT NULL AUTO_INCREMENT,
  member_id BIGINT NOT NULL,
  device_id int default null, 
  datetime datetime NULL DEFAULT NULL,
  slot_id int not null, 
  location POINT NULL DEFAULT NULL,
  recommendation_id int null default Null, 
  no2 DOUBLE NULL DEFAULT NULL,
  co2 DOUBLE NULL DEFAULT NULL,
  o3 DOUBLE NULL DEFAULT NULL,
  so02 DOUBLE NULL DEFAULT NULL,
  pm10 DOUBLE NULL DEFAULT NULL,
  pm25 DOUBLE NULL DEFAULT NULL,
  pm1 DOUBLE NULL DEFAULT NULL,
  benzene DOUBLE NULL DEFAULT NULL,
  PRIMARY KEY (id, member_id),

    FOREIGN KEY (member_id)
    REFERENCES Member (id)
    ON DELETE CASCADE,
     FOREIGN KEY (slot_id)
    REFERENCES Slot (id)
        ON DELETE CASCADE,
     FOREIGN KEY (device_id)
    REFERENCES Device (id)
        ON DELETE CASCADE,
        FOREIGN KEY (recommendation_id)
    REFERENCES Recommendation (id)
    ON DELETE CASCADE
    );




-- -----------------------------------------------------
-- Table CellPriority
-- -----------------------------------------------------
CREATE TABLE Priority (
  slot_id INT NOT NULL ,
  datetime datetime NOT NULL,
  temporal_priority float8 NULL DEFAULT NULL,
  trend_priority float8 NULL DEFAULT NULL,
  PRIMARY KEY (slot_id, datetime),
    FOREIGN KEY (slot_id)
    REFERENCES Slot (id)
    ON DELETE CASCADE);