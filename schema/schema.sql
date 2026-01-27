-- Now drop tables in correct order
IF OBJECT_ID('plant_reading', 'U') IS NOT NULL DROP TABLE plant_reading;
IF OBJECT_ID('plant', 'U') IS NOT NULL DROP TABLE plant;
IF OBJECT_ID('origin', 'U') IS NOT NULL DROP TABLE origin;
IF OBJECT_ID('botanist', 'U') IS NOT NULL DROP TABLE botanist;
IF OBJECT_ID('city', 'U') IS NOT NULL DROP TABLE city;
IF OBJECT_ID('country', 'U') IS NOT NULL DROP TABLE country;

CREATE TABLE botanist (
    botanist_id SMALLINT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    phone VARCHAR(255) NOT NULL
);
CREATE TABLE plant (
    plant_id SMALLINT NOT NULL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    scientific_name VARCHAR(255) NULL,
    origin_id SMALLINT NOT NULL,
    botanist_id SMALLINT NOT NULL,
    image_license_url VARCHAR(255) NULL,
    image_url VARCHAR(255) NULL,
    thumbnail VARCHAR(255) NULL
);
CREATE TABLE origin (
    origin_id SMALLINT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    city_id BIGINT NOT NULL,
    lat FLOAT NOT NULL,
    long FLOAT NOT NULL
);
CREATE TABLE plant_reading (
    plant_reading_id BIGINT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    plant_id SMALLINT NOT NULL,
    soil_moisture FLOAT NOT NULL,
    temperature FLOAT NOT NULL,
    recording_taken DATE NOT NULL,
    last_watered DATE NOT NULL
);
CREATE TABLE country (
    country_id SMALLINT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    country_name VARCHAR(255) NOT NULL
);
CREATE TABLE city (
    city_id BIGINT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    city_name VARCHAR(255) NOT NULL,
    country_id SMALLINT NOT NULL
);
ALTER TABLE plant_reading
    ADD CONSTRAINT FK_plant_reading_plant_id FOREIGN KEY (plant_id) REFERENCES plant(plant_id);
ALTER TABLE origin
    ADD CONSTRAINT FK_origin_city_id FOREIGN KEY (city_id) REFERENCES city(city_id);
ALTER TABLE plant
    ADD CONSTRAINT FK_plant_origin_id FOREIGN KEY (origin_id) REFERENCES origin(origin_id);
ALTER TABLE plant
    ADD CONSTRAINT FK_plant_botanist_id FOREIGN KEY (botanist_id) REFERENCES botanist(botanist_id);
ALTER TABLE city
    ADD CONSTRAINT city_country_id_foreign FOREIGN KEY (country_id) REFERENCES country(country_id);