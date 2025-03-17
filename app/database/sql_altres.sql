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

ALTER TABLE `users` ADD `reset_token` VARCHAR(255) NULL AFTER `image`;
ALTER TABLE `users` ADD `token_expiry` DATETIME NULL AFTER `is_verified`;

ALTER TABLE `users` ADD `is_verified` INT NOT NULL DEFAULT '0' AFTER `created_at`;

