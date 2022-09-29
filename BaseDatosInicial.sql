Create database SocioBee;
Use SocioBee;

# ON DELETE and ON UPDATE
# Mapa y las formas de localización
CREATE TABLE User (
    userID INT UNIQUE AUTO_INCREMENT,
    name VARCHAR(30),
    surame VARCHAR(30),
    age INT,
    gender Set('Male', 'Female','Intersexual','I dont want to answer') default 'I dont want to answer',
    PRIMARY KEY (UserID)
);


CREATE TABLE QueenBee (
    queenBeeID INT UNIQUE AUTO_INCREMENT,
    name VARCHAR(30),
    surame VARCHAR(30),
    age INT,
    gender Set('Male', 'Female','Intersexual','I dont want to answer') default 'I dont want to answer',
    PRIMARY KEY (queenBeeID)
);


CREATE TABLE Campaign (
    campaignID INT UNIQUE AUTO_INCREMENT PRIMARY KEY,
    createdBy INT,
    city varchar(30),
    cellSize decimal,
    # Igual el mapa.... 
    FOREIGN  KEY (createdBy) REFERENCES QueenBee(queenBeeID) 
);

CREATE TABLE Cell(
   cellID INT UNIQUE AUTO_INCREMENT PRIMARY KEY,
   # https://dev.mysql.com/doc/refman/8.0/en/spatial-types.html
   centerLonguitud Decimal,
   centerLatitude Decimal, 
   isInCampaign INT,
   #Mirar este tipo de dato a ver si es el correcto.
   necessityOfCoverage Decimal,
       FOREIGN KEY (isInCampaign) REFERENCES Campaign(campaignID)
);

CREATE TABLE AirDataPomise (
   dataFromCell INT,
   futureTime TIMESTAMP,
   # no more than 2 or 3 day from the actual time. 
   capturedBy  INT,
          FOREIGN KEY (dataFromCell) REFERENCES Cell(cellID),
          FOREIGN KEY  (capturedBy) REFERENCES  User(userID),
Primary Key (dataFromCell, capturedBy, futureTime)				
);

CREATE TABLE AirData (
   dataFromCell INT,
   time TIMESTAMP,
   capturedBy  INT,
   # https://dev.mysql.com/doc/refman/8.0/en/spatial-types.html
   locationLonguitud Decimal,
   locationLatitude Decimal, 
   No2 Decimal,
   Co2 Decimal,
          FOREIGN KEY (dataFromCell) REFERENCES Cell(cellID),
          FOREIGN KEY  (capturedBy) REFERENCES  User(userID),
Primary Key (dataFromCell, capturedBy, time)				
);

