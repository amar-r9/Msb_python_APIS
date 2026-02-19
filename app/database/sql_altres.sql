ALTER TABLE `students` ADD `score` INT NOT NULL DEFAULT '0' AFTER `dob`;
ALTER TABLE `categories` ADD `is_future` INT NOT NULL DEFAULT '1' AFTER `icon`;
ALTER TABLE `quiz_subcategories` ADD `icon` VARCHAR(255) NULL AFTER `q_category_id`;
ALTER TABLE `users` ADD `image` VARCHAR(255) NULL AFTER `email`;


-- updated
ALTER TABLE `students` ADD `points` INT NOT NULL DEFAULT '0' AFTER `score`, ADD `likes` INT NOT NULL DEFAULT '0' AFTER `points`;



RENAME TABLE `categories` TO `categories`;
RENAME TABLE `quiz_subcategories` TO `subcategories`;
ALTER TABLE `subcategories` CHANGE `category_id` `category_id` INT(11) NULL DEFAULT NULL;


RENAME TABLE `subcategories` TO `sub_categories`;
ALTER TABLE `submissions` CHANGE `subcategory_talent_id` `category_id` INT(11) NULL DEFAULT NULL;
ALTER TABLE `submissions` CHANGE `talent_id` `sub_category_id` INT(11) NULL DEFAULT NULL;
ALTER TABLE `students` ADD `city` VARCHAR(255) NULL AFTER `state_id`;





CREATE TABLE `user_points` (`id` INT NOT NULL AUTO_INCREMENT , `user_id` INT NULL,`submission_id` INT NULL , `user_points`INT NULL , `school_id` INT NULL , `points` INT NULL , `point_type` INT NULL COMMENT '1=submition,2=like ' , PRIMARY KEY (`id`)) ENGINE = InnoDB;
ALTER TABLE `submissions` CHANGE `date_time` `created_at` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE `submissions` ADD `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP AFTER `created_at`;


ALTER TABLE `likes` ADD `school_id` INT NULL AFTER `likes`;
ALTER TABLE `likes` CHANGE `created_by` `user_id` INT(11) NULL DEFAULT NULL;
ALTER TABLE `likes` ADD `like_type` INT NOT NULL COMMENT '1=submissions' AFTER `likes`;

ALTER TABLE `likes` ADD `created_by` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP AFTER `school_id`, ADD `updated_by` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP AFTER `created_by`;

ALTER TABLE `comments` CHANGE `date_time` `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE `comments` ADD `school_id` INT NOT NULL AFTER `comment`, ADD `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP AFTER `school_id`;

ALTER TABLE `comments` CHANGE `created_by` `user_id` INT(11) NOT NULL;
ALTER TABLE `students` ADD `rank` INT NULL AFTER `points`;
ALTER TABLE `comments` CHANGE `parent_id` `parent_id` INT(11) NULL;



ALTER TABLE `schools` ADD `rank` INT NOT NULL DEFAULT '0' AFTER `name`;

-- update
ALTER TABLE `users` ADD `image` VARCHAR(255) NULL AFTER `email`;
ALTER TABLE `users` ADD `reset_token` VARCHAR(255) NULL AFTER `image`;

ALTER TABLE `users` ADD `is_verified` INT NOT NULL DEFAULT '0' AFTER `created_at`;
ALTER TABLE `users` ADD `token_expiry` DATETIME NULL AFTER `is_verified`;

-- 2-05-2025
-- new
DROP TABLE quizzes;
DROP TABLE `quiz_answers`, `quiz_options`;


CREATE TABLE `quizzes` (
  `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT,
  `category_id` int(10) UNSIGNED NOT NULL,
  `sub_category_id` int(10) UNSIGNED NOT NULL,
  `grade_id` int(10) UNSIGNED NOT NULL,
  `name` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;



CREATE TABLE `questions` (
  `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT,
  `quiz_id` int(10) UNSIGNED NOT NULL,
  `category_id` int(10) UNSIGNED NOT NULL,
  `sub_category_id` int(10) UNSIGNED NOT NULL,
  `grade_id` int(10) UNSIGNED NOT NULL,
  `name` text NOT NULL,
   PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;


CREATE TABLE `question_options` (
  `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT,
  `quiz_id` int(10) UNSIGNED NOT NULL,
  `category_id` int(10) UNSIGNED NOT NULL,
  `sub_category_id` int(10) UNSIGNED NOT NULL,
  `grade_id` int(10) UNSIGNED NOT NULL,
  `question_id` int(10) UNSIGNED NOT NULL,
  `name` text NOT NULL,
  `is_correct` tinyint(1) DEFAULT 0,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

CREATE TABLE `student_answers` (
  `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT,
  `user_id` int(10) UNSIGNED NOT NULL,
  `quiz_id` int(10) UNSIGNED NOT NULL,
  `category_id` int(10) UNSIGNED NOT NULL,
  `sub_category_id` int(10) UNSIGNED NOT NULL,
  `grade_id` int(10) UNSIGNED NOT NULL,
  `question_id` int(10) UNSIGNED NOT NULL,
  `question_option_id` int(10) UNSIGNED NOT NULL,
  `is_correct` tinyint(1) DEFAULT 0,
   PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;



-- 02-09-2025

ALTER TABLE `users` ADD `is_active` INT NOT NULL DEFAULT '1' AFTER `is_verified`;

-- 02-09-2025
ALTER TABLE `sub_categories` ADD `description` TEXT NULL DEFAULT NULL AFTER `category_id`;


-- 11-09-2025
ALTER TABLE `sub_categories` 
-- ADD `grade` VARCHAR(255) NULL DEFAULT NULL AFTER `description`,
ADD `start_date` DATETIME NULL DEFAULT NULL AFTER `description`,
ADD `end_date` DATETIME NULL DEFAULT NULL AFTER `start_date`;

--7-10-2025
CREATE TABLE `Talentgrade_id` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(255) NOT NULL, -- This will store "1-3", "4-6", etc.
  `grades_array` JSON NOT NULL,        -- This will store the array [1, 2, 3]
  PRIMARY KEY (`id`)
) ENGINE=InnoDB;

-- 2. Populate the table with the required data
INSERT INTO `Talentgrade_id` (`name`, `grades_array`) VALUES 
('1-3', '[1, 2, 3]'),
('4-6', '[4, 5, 6]'),
('7-10', '[7, 8, 9, 10]');

-- 3. Add a foreign key column to your sub_categories table
-- This links a sub-category to one of these new grade groups.

ALTER TABLE `sub_categories` 
ADD COLUMN `Talentgrade_id` INT NULL,
ADD FOREIGN KEY (`Talentgrade_id`) REFERENCES `Talentgrades`(`id`);