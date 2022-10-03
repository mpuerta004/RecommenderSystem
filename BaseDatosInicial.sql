Create database SocioBee;
Use SocioBee;

# ON DELETE and ON UPDATE
# Mapa y las formas de localización
CREATE TABLE User (
    id INT UNIQUE AUTO_INCREMENT,
    name VARCHAR(30),
    surname VARCHAR(30),
    age INT,
    gender Set('Male', 'Female','Intersexual','I dont want to answer') default 'I dont want to answer',
    PRIMARY KEY (UserID)
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
    admin_id INT,
    city varchar(30),
    #cellSize decimal,
    # Igual el mapa.... A new entity called Surface could be created, a campaign may have N surfaces, where each surface has M hexagons
    FOREIGN  KEY (createdBy) REFERENCES CampaignManager(id) 
);

CREATE TABLE Cell(
   id INT UNIQUE AUTO_INCREMENT PRIMARY KEY,
   # https://dev.mysql.com/doc/refman/8.0/en/opengis-geometry-model.html
   center point,
   type set('Dynamic','Static') default 'Dynamic',
   #forma 
   #centerLongitud Decimal,
   #centerLatitude Decimal, 
   campaign_id INT,
   min_visits_required Decimal, # what do you mean by necessity, should it be 
       FOREIGN KEY (isInCampaign) REFERENCES Campaign(campaignID)
);

CREATE TABLE AirDataPromise (
   cell_id INT,
   user_id  INT,
   sampling_limit TIMESTAMP, # limit timestamp
   # no more than 2 or 3 day from the actual time. 
   FOREIGN KEY (cell_id) REFERENCES Cell(id),
   FOREIGN KEY  (user_id) REFERENCES  User(id),
   PRIMARY KEY (cell_id, user_id, sampling_limit)				
);

CREATE TABLE AirData (
   cell_id INT,
   user_id  INT,
   sampling_timestamp TIMESTAMP,
   # https://dev.mysql.com/doc/refman/8.0/en/spatial-types.html
   location point,
   #locationLonguitud Decimal,
   #locationLatitude Decimal, 
   No2 Decimal, # I would make a reference to Sample since we can then generalize it
   Co2 Decimal,
   FOREIGN KEY (cell_id) REFERENCES Cell(id),
   FOREIGN KEY  (user_id) REFERENCES  User(id),
   PRIMARY KEY (cell_id, user_id, sampling_timestamp)				
);
