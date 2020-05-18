CREATE DATABASE IF NOT EXISTS `majorProject` DEFAULT CHARACTER SET utf8mb4 DEFAULT COLLATE utf8mb4_bin;
USE `majorProject`;

-- -----------------------------------------------------
-- Table `branch`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `branch` (
  `id` BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(255) NOT NULL,
  PRIMARY KEY (`id`,`name`),
  UNIQUE INDEX `name_unique` (`name` ASC));

  -- -----------------------------------------------------
  -- Table `class`
  -- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `class` (
    `id` BIGINT(20)  NOT NULL,
    `branch_id` BIGINT(20) UNSIGNED NOT NULL,
    `strength` BIGINT(20) UNSIGNED NOT NULL,
    PRIMARY KEY (`id`),
    CONSTRAINT `class_branch_id_fk`
      FOREIGN KEY (`branch_id`)
      REFERENCES `branch` (`id`)
      ON DELETE CASCADE
      ON UPDATE CASCADE
);
 -----------------------------------------------------
  -- Table `staff`
 ----------------------------------------------------
CREATE TABLE IF NOT EXISTS `staff` (
        `id` BIGINT(20) NOT NULL,
        `branch_id` BIGINT(20) UNSIGNED NOT NULL,
        `name` VARCHAR(255)  NOT NULL,
        `email` VARCHAR(255) NOT NULL,
        `mobile` VARCHAR(20) NOT NULL,
        PRIMARY KEY (`id`,`email`),
        CONSTRAINT `staff_branch_id_fk`
          FOREIGN KEY (`branch_id`)
          REFERENCES `branch` (`id`)
          ON DELETE CASCADE
          ON UPDATE CASCADE
 );

 -----------------------------------------------------
  -- Table `subject`
 ----------------------------------------------------
CREATE TABLE IF NOT EXISTS `subject` (
        `id` BIGINT(20) NOT NULL,
        `branch_id` BIGINT(20) UNSIGNED NOT NULL,
        `name` BIGINT(20) UNSIGNED NOT NULL,
        `credits` INT(10) NOT NULL,
        PRIMARY KEY (`id`,`name`,`branch_id`),
        CONSTRAINT `subject_branch_id_fk`
        FOREIGN KEY (`branch_id`)
        REFERENCES `branch` (`id`)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);
---------------------------------------------------------
  -- Table `time_table`
---------------------------------------------------------
CREATE TABLE IF NOT EXISTS `time_table`(
        `class_id` BIGINT(20) NOT NULL,
        `staff_id` BIGINT(20) NOT NULL,
        `period` INT(10) NOT NULL,
        `subject_id` BIGINT(20) NOT NULL,
        `day` INT(10) NOT NULL,
        PRIMARY KEY (`class_id`,`period`,`day`),

        CONSTRAINT `class_time_table_id_fk`
        FOREIGN KEY (`class_id`)
        REFERENCES `class` (`id`),

        CONSTRAINT `staff_time_table_id_fk`
        FOREIGN KEY (`staff_id`)
        REFERENCES `staff` (`id`),

        CONSTRAINT `subject_time_table_id_fk`
        FOREIGN KEY (`subject_id`)
        REFERENCES `subject` (`id`)
);
-------------------------------------------------------------
  -- Table `images`
------------------------------------------------------------

CREATE TABLE IF NOT EXISTS `images`(
      `name` VARCHAR(255) NOT NULL,
      `class_id` BIGINT(20) NOT NULL,
      `period` INT(10) NOT NULL,
      `isprocessed` INT(10) NOT NULL,
      PRIMARY KEY(`name`),
      CONSTRAINT `class_images_id_fk`
      FOREIGN KEY (`class_id`)
      REFERENCES `class` (`id`)
);

---------------------------------------------------------------
  -- Table `gestures`
---------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `gestures`(
      `name` VARCHAR(255) NOT NULL,
      `left_turned` INT(10) NOT NULL,
      `right_turned` INT(10) NOT NULL,
      `back_turned` INT(10) NOT NULL,
      `raised_hands` INT(10) NOT NULL,
      `total` INT(10) NOT NULL,
      PRIMARY KEY (`name`)

);
----------------------------------------------------------------
  -- Table `expressions`
----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `expressions`(

  `name` VARCHAR(255) NOT NULL,
  `happy` INT(10) NOT NULL,
  `angry` INT(10) NOT NULL,
  `sad` INT(10) NOT NULL,
  `suprised` INT(10) NOT NULL,
  `fear` INT(10) NOT NULL,
  `neutral` INT(10) NOT NULL,
  `disgust` INT(10) NOT NULL,
  `total` INT(10) NOT NULL,
  PRIMARY KEY (`name`)

);
