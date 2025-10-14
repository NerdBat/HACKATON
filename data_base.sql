CREATE TABLE IF NOT EXISTS `traffic_data` (
  `City` VARCHAR(100),
  `Vehicle Type` VARCHAR(50),
  `Weather` VARCHAR(50),
  `Economic Condition` VARCHAR(50),
  `Day Of Week` VARCHAR(20),
  `Hour Of Day` TINYINT UNSIGNED,
  `Speed` DECIMAL(10,4),
  `Is Peak Hour` BOOLEAN,
  `Random Event Occurred` BOOLEAN,
  `Energy Consumption` DECIMAL(12,4),
  `Traffic Density` DECIMAL(12,4)
);



CREATE TABLE IF NOT EXISTS `traffic_viz` (
  `City` VARCHAR(100),
  `Vehicle Type` VARCHAR(50),
  `Weather` VARCHAR(50),
  `Economic Condition` VARCHAR(50),
  `Day Of Week` VARCHAR(20),
  `Hour Of Day` TINYINT UNSIGNED,
  `Speed` VARCHAR(20),
  `Is Peak Hour` BOOLEAN,
  `Random Event Occurred` BOOLEAN,
  `Energy Consumption` VARCHAR(20),
  `Traffic Density` VARCHAR(20)
);


-- source fic.sql