DROP DATABASE IF EXISTS Telegram_bot_db;
/* DELETE USER 'mve' AT LOCAL SERVER*/
DROP USER IF EXISTS 'telegram_bot'@'localhost';
DROP USER IF EXISTS 'telegram_bot_automatic'@'localhost';


CREATE DATABASE Telegram_bot_db;
use Telegram_bot_db;

/* CREATE THE USER 'mve' AT LOCAL and REMOTE SERVER WITH PASSWORD 'mvepasswd123' */
CREATE USER IF NOT EXISTS 'telegram_bot'@'localhost' IDENTIFIED BY 'telegram_botpasswd123';
CREATE USER IF NOT EXISTS 'telegram_bot'@'%' IDENTIFIED BY 'telegram_botpasswd123';
CREATE USER IF NOT EXISTS 'telegram_bot_automatic'@'localhost' IDENTIFIED BY 'telegram_botpasswd123';
CREATE USER IF NOT EXISTS 'telegram_bot_automatic'@'%' IDENTIFIED BY 'telegram_botpasswd123';

GRANT ALL PRIVILEGES ON Telegram_bot_db.*  TO 'telegram_bot'@'localhost';
GRANT ALL PRIVILEGES ON Telegram_bot_db.*  TO 'telegram_bot'@'%';
GRANT ALL PRIVILEGES ON Telegram_bot_db.*  TO 'telegram_bot_automatic'@'localhost';
GRANT ALL PRIVILEGES ON Telegram_bot_db.*  TO 'telegram_bot_automatic'@'%';

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
  PRIMARY KEY (id)
  );

CREATE TABLE Last_user_position(
  member_id BIGINT NOT NULL,
  location POINT NOT NULL,
  PRIMARY KEY (member_id),
  FOREIGN KEY (member_id)
    REFERENCES Member (id)
    ON DELETE CASCADE
);



-- -----------------------------------------------------
-- Table sociobee.recommendation
-- -----------------------------------------------------
CREATE TABLE Recommendation (
  id int not null auto_increment,
  posicion VARCHAR(30) not Null, 
  member_id BIGINT NOT NULL,
  state  VARCHAR(15),
  point POINT,
  CONSTRAINT state_type CHECK (state IN ("NOTIFIED","ACCEPTED","REALIZED","NON_REALIZED")),
  PRIMARY KEY (id,member_id),
    FOREIGN KEY (member_id)
    REFERENCES Member (id)
    ON DELETE CASCADE
    );

CREATE Table Measurement(
  url VARCHAR(100) not null,
  location POINT, 
  id BIGINT, 
  PRIMARY KEY (id)
)
