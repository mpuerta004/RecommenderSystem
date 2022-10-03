CREATE DATABASE SocioBee;
Use SocioBee;

# ON DELETE and ON UPDATE
# Mapa y las formas de localización
CREATE TABLE User (
    id INT UNIQUE AUTO_INCREMENT,
    name VARCHAR(30),
    surname VARCHAR(30),
    age INT,
    gender Set('Male', 'Female','Intersexual','I dont want to answer') default 'I dont want to answer',
    PRIMARY KEY (id)
);


CREATE TABLE CampaignManager (
    id INT UNIQUE AUTO_INCREMENT,
    name VARCHAR(30),
    surname VARCHAR(30),
    age INT,
    gender Set('Male', 'Female','Intersexual','I dont want to answer') default 'I dont want to answer',
    PRIMARY KEY (id)
);


CREATE TABLE Campaign (
    id INT UNIQUE AUTO_INCREMENT PRIMARY KEY,
    manager_id INT,
    city varchar(30),
    cell_radius decimal,
    min_samples INT, # minimum number of times a cell has to be visited in a campaign during its sampling period
    sampling_period INT,# seconds during which samples will be grouped by campaign
    planning_limit_time INT, #  upper number of seconds limit that a sampling promise can be scheduled for
    # Igual el mapa.... A new entity called Surface could be created, a campaign may have N surfaces, where each surface has M hexagons
    FOREIGN  KEY (manager_id) REFERENCES CampaignManager(id) 
);

CREATE TABLE Surface (
    id INT UNIQUE AUTO_INCREMENT PRIMARY KEY,
    campaign_id INT,
    FOREIGN  KEY (campaign_id) REFERENCES CampaignManager(id) 
);


CREATE TABLE Boundary (
    id INT UNIQUE AUTO_INCREMENT PRIMARY KEY,
    surface_id INT,
    boundary linestring,
    FOREIGN  KEY (surface_id) REFERENCES CampaignManager(id) 
);

CREATE TABLE Cell(
   id INT UNIQUE AUTO_INCREMENT PRIMARY KEY,
   # https://dev.mysql.com/doc/refman/8.0/en/opengis-geometry-model.html
   center point,
   cell_type set('Dynamic','Static') default 'Dynamic',
   #forma 
   #centerLongitud Decimal,
   #centerLatitude Decimal, 
   surface_id INT,
   FOREIGN KEY (surface_id) REFERENCES Surface(id)
);

CREATE TABLE CellSamplePromise (
   cell_id INT,
   user_id  INT,
   sampling_limit TIMESTAMP, # limit timestamp
   is_active BOOLEAN, # by default set to TRUE but changed once sampling_limit time is exceeded
   # no more than 2 or 3 day from the actual time. 
   FOREIGN KEY (cell_id) REFERENCES Cell(id),
   FOREIGN KEY  (user_id) REFERENCES  User(id),
   PRIMARY KEY (cell_id, user_id, sampling_limit)				
);

CREATE TABLE CellSample (
   id INT UNIQUE AUTO_INCREMENT PRIMARY KEY,
   cell_id INT,
   user_id  INT,
   timestamp TIMESTAMP,
   # https://dev.mysql.com/doc/refman/8.0/en/spatial-types.html
   location point,
   #locationLonguitud Decimal,
   #locationLatitude Decimal, 
   FOREIGN KEY (cell_id) REFERENCES Cell(id),
   FOREIGN KEY  (user_id) REFERENCES  User(id)
   #PRIMARY KEY (cell_id, user_id, sampling_timestamp)				
);

CREATE TABLE AirData (
   id INT UNIQUE AUTO_INCREMENT PRIMARY KEY,
   sample_id INT, 
   No2 Decimal, # I would make a reference to Sample since we can then generalize it
   Co2 Decimal,
   FOREIGN KEY (sample_id) REFERENCES CellSample(id)	
);


