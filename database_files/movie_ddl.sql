-- Database and table creation

DROP DATABASE IF EXISTS moviedb;
CREATE DATABASE IF NOT EXISTS moviedb;
USE moviedb;

-- Table definitions with primary keys and foreign keys
CREATE TABLE `movie` (
  `movie_id` int PRIMARY KEY NOT NULL,
  `title` varchar(255) NOT NULL,
  `budget` bigint NOT NULL,
  `revenue` bigint NOT NULL,
  `release_year` varchar(50) NOT NULL,
  `runtime` int NOT NULL,
  `age_rating` varchar(50) NOT NULL,
  `rating` float NOT NULL
);

CREATE TABLE `watchlists` (
  `watchlist_id` INTEGER PRIMARY KEY AUTO_INCREMENT,
  `name` varchar(50),
  `date_created` datetime,
  `last_edited` datetime,
  `description` varchar(255)
);

CREATE TABLE `watchlist_entries` (
  `movie_id` int NOT NULL,
  `watchlist_id` int NOT NULL,
  `rating` int,
  `comment` varchar(300),
  `last_edited` datetime,
  PRIMARY KEY (movie_id, watchlist_id),
  FOREIGN KEY (`movie_id`) REFERENCES `movie` (`movie_id`),
  FOREIGN KEY (`watchlist_id`) REFERENCES `watchlists` (`watchlist_id`)
);

CREATE TABLE `genre` (
  `genre_id` int PRIMARY KEY NOT NULL,
  `genre_name` varchar(50) NOT NULL
);

CREATE TABLE `movie_genre` (
  `genre_id` int NOT NULL,
  `movie_id` int NOT NULL,
  FOREIGN KEY (`genre_id`) REFERENCES `genre` (`genre_id`),
  FOREIGN KEY (`movie_id`) REFERENCES `movie` (`movie_id`)
);

CREATE TABLE `language` (
  `language_id` int PRIMARY KEY NOT NULL,
  `language_name` varchar(50) NOT NULL  
);

CREATE TABLE `movie_subtitle` (
  `movie_id` int NOT NULL,
  `language_id` int NOT NULL,
  FOREIGN KEY (`movie_id`) REFERENCES `movie` (`movie_id`),
  FOREIGN KEY (`language_id`) REFERENCES `language` (`language_id`)
);

CREATE TABLE `movie_audio` (
  `movie_id` int NOT NULL,
  `language_id` int NOT NULL,
  FOREIGN KEY (`movie_id`) REFERENCES `movie` (`movie_id`),
  FOREIGN KEY (`language_id`) REFERENCES `language` (`language_id`)
);


CREATE TABLE `country` (
  `country_id` varchar(3) PRIMARY KEY NOT NULL,
  `country_name` varchar(50) NOT NULL,
  `GDP` bigint NOT NULL,
  `population` int NOT NULL
);

CREATE TABLE `movie_country` (
  `movie_id` int NOT NULL,
  `country_id` varchar(3) NOT NULL,
  FOREIGN KEY (`movie_id`) REFERENCES `movie` (`movie_id`),
  FOREIGN KEY (`country_id`) REFERENCES `country` (`country_id`)
);

CREATE TABLE `production_company` (
  `company_id` int PRIMARY KEY NOT NULL,
  `company_name` varchar(255) NOT NULL,
  `total_movies_produced` int NOT NULL,
  `date_established` datetime NOT NULL
);

CREATE TABLE `movie_company` (
  `movie_id` int NOT NULL,
  `company_id` int NOT NULL,
  FOREIGN KEY (`movie_id`) REFERENCES `movie` (`movie_id`),
  FOREIGN KEY (`company_id`) REFERENCES `production_company` (`company_id`)
);

CREATE TABLE `actor` (
  `actor_id` int PRIMARY KEY NOT NULL,
  `actor_name` varchar(50) NOT NULL,
  `gender` varchar(50) NOT NULL,
  `date_of_birth` datetime NOT NULL,
  `country` varchar(50) NOT NULL
);

CREATE TABLE `director` (
  `director_id` int PRIMARY KEY NOT NULL,
  `director_name` varchar(50) NOT NULL,
  `gender` varchar(10) NOT NULL,
  `date_of_birth` datetime NOT NULL,
  `country` varchar(50) NOT NULL
);

CREATE TABLE `movie_cast` (
  `movie_id` int NOT NULL,
  `actor_id` int NOT NULL,
  `director_id` int NOT NULL,
  FOREIGN KEY (`movie_id`) REFERENCES `movie` (`movie_id`),
  FOREIGN KEY (`actor_id`) REFERENCES `actor` (`actor_id`),
  FOREIGN KEY (`director_id`) REFERENCES `director` (`director_id`)
);

CREATE TABLE `awards` (
  `award_id` int PRIMARY KEY NOT NULL,
  `category` varchar(255) NOT NULL,
  `organization` varchar(50) NOT NULL
);

CREATE TABLE `movie_awards` (
  `movie_id` int NOT NULL,
  `award_id` int NOT NULL,
  `award_year` int NOT NULL,
  FOREIGN KEY (`movie_id`) REFERENCES `movie` (`movie_id`),
  FOREIGN KEY (`award_id`) REFERENCES `awards` (`award_id`)
);


-- VIEWS DECLARATION

CREATE OR REPLACE VIEW movie_view AS 
SELECT
    m.movie_id,
 m.title,
 m.budget,
 m.revenue,
 m.release_year,
 m.runtime,
 m.age_rating,
 m.rating,
    ma.award_count,
 GROUP_CONCAT(DISTINCT g.genre_name SEPARATOR ', ') AS genres,
    GROUP_CONCAT(DISTINCT s.subtitle_language SEPARATOR ', ') as sub_language,
    MIN(a.actor_id) as actor_id,
    MIN(a.star) as star,
    a.director_id,
    a.director_name,
    MIN(p.company_id) as company_id,
    MIN(p.production_company) as production_company,
    MIN(c.country_name) as country_name
FROM
    movie AS m 
LEFT OUTER JOIN 
    (SELECT movie_id, COUNT(*) AS award_count 
     FROM movie_awards 
     GROUP BY movie_id) AS ma 
ON 
    m.movie_id = ma.movie_id
LEFT OUTER JOIN
 (SELECT movie_id, genre_name
    FROM genre
    JOIN movie_genre
    ON genre.genre_id = movie_genre.genre_id) as g
ON 
 m.movie_id = g.movie_id
LEFT OUTER JOIN
 (SELECT movie_id, language_name as subtitle_language
    FROM movie_subtitle
    JOIN language
    ON movie_subtitle.language_id = language.language_id) as s
ON
 m.movie_id = s.movie_id
LEFT OUTER JOIN
 (SELECT movie_id, actor.actor_id, actor.actor_name AS star, director.director_id, director.director_name
    FROM movie_cast
    JOIN actor
    ON actor.actor_id = movie_cast.actor_id
    JOIN director
    ON movie_cast.director_id = director.director_id) as a
ON
 m.movie_id = a.movie_id
LEFT OUTER JOIN
 (SELECT movie_id, production_company.company_id, company_name AS production_company
    FROM movie_company
    JOIN production_company
    ON movie_company.company_id = production_company.company_id) as p
ON
 m.movie_id = p.movie_id
LEFT OUTER JOIN
 (SELECT movie_id, country_name
    FROM movie_country
    JOIN country
    ON movie_country.country_id = country.country_id) as c
ON
 m.movie_id = c.movie_id
    
GROUP BY 
    m.movie_id,
 m.title,
 m.budget,
 m.revenue,
 m.release_year,
 m.runtime,
 m.age_rating,
 m.rating,
    ma.award_count,
    a.director_id,
    a.director_name;
    
CREATE OR REPLACE VIEW actor_view AS
SELECT
 a.actor_id,
 a.actor_name AS name,
    a.gender,
    a.date_of_birth,
    a.country,
    m.movie_count
FROM
 actor as a
LEFT OUTER JOIN 
    (SELECT actor_id, COUNT(*) AS movie_count 
     FROM movie_cast
     GROUP BY actor_id) AS m 
ON
 a.actor_id = m.actor_id;

CREATE OR REPLACE VIEW director_view AS
SELECT
 d.director_id,
 d.director_name AS name,
    d.gender,
    d.date_of_birth,
    d.country,
    m.movie_count
FROM
 director as d
LEFT OUTER JOIN 
    (SELECT director_id, COUNT(*) AS movie_count 
     FROM movie_cast
     GROUP BY director_id) AS m 
ON
 d.director_id = m.director_id;


CREATE OR REPLACE VIEW production_view AS
SELECT
 p.company_id,
 p.company_name,
    m.movie_count
FROM
 production_company as p
LEFT OUTER JOIN 
    (SELECT company_id, COUNT(*) AS movie_count 
     FROM movie_company
     GROUP BY company_id) AS m 
ON
 p.company_id = m.company_id;
    
SELECT * FROM production_view;

CREATE OR REPLACE VIEW awards_view AS
SELECT
 a.award_id,
    a.organization,
    a.category,
    COALESCE(m.times_given, 0) AS times_given
FROM
 awards as a
LEFT OUTER JOIN 
    (SELECT award_id, COUNT(*) AS times_given 
     FROM movie_awards
     GROUP BY award_id) AS m
ON
 a.award_id = m.award_id;



-- PROCEDURES AND TRIGGERS


-- Procedure which given a watchlist id, returns each of its entries (basically the data for each entry in the watchlist 
-- entries table where the watchlist_id matches, and also the name of the movie it connects to)
DELIMITER //

CREATE PROCEDURE get_watchlist_entries(IN watchlist_id INT)
BEGIN
    SELECT
        watchlist_entries.watchlist_id, 
        watchlist_entries.movie_id,
        movie.title AS movie_name,
        watchlist_entries.rating,
        watchlist_entries.comment,
        watchlist_entries.last_edited
    FROM watchlist_entries
    INNER JOIN movie
        ON watchlist_entries.movie_id = movie.movie_id
    WHERE watchlist_entries.watchlist_id = watchlist_id;
END //

DELIMITER ;

-- Trigger to update last_edited on a watchlist_entry row when the row is modified

DELIMITER $$ 
CREATE TRIGGER update_watchlist_entry_last_edited 
BEFORE UPDATE ON watchlist_entries 
FOR EACH ROW 
BEGIN 
SET NEW.last_edited = NOW(); 
END$$ 
DELIMITER ;


-- Search procedure which returns all records where an attribute value matches a given string for a given view
DELIMITER $$

CREATE PROCEDURE search_view(
	IN view_name VARCHAR(255), 
	IN search_value VARCHAR(255) 
)
BEGIN
	SET @column_query = CONCAT(
    	'SELECT GROUP_CONCAT(COLUMN_NAME)
     	FROM INFORMATION_SCHEMA.COLUMNS
     	WHERE TABLE_NAME = ''', view_name, '''
     	AND TABLE_SCHEMA = DATABASE()'
	);

	
	PREPARE stmt1 FROM @column_query;
	EXECUTE stmt1;
	DEALLOCATE PREPARE stmt1;

	
	SET @columns = (SELECT GROUP_CONCAT(COLUMN_NAME)
                	FROM INFORMATION_SCHEMA.COLUMNS
                	WHERE TABLE_NAME = view_name AND TABLE_SCHEMA = DATABASE());

	
	SET @search_query = CONCAT(
    	'SELECT * FROM ', view_name, '
     	WHERE CONCAT_WS('', '', ', @columns, ') LIKE ''%', search_value, '%'''
	);

	PREPARE stmt2 FROM @search_query;
	EXECUTE stmt2;
	DEALLOCATE PREPARE stmt2;
END$$

DELIMITER ;


-- automatically set a default rating for movies added to a watchlist without a user-provided rating
DELIMITER $$

CREATE TRIGGER set_default_rating
BEFORE INSERT ON watchlist_entries
FOR EACH ROW
BEGIN
	IF NEW.rating IS NULL THEN
		SET NEW.rating = 3;
	END IF;

END $$

DELIMITER ;



DELIMITER $$

CREATE PROCEDURE filter_movie_view(
	IN age_rating_filter VARCHAR(50),
	IN award_count_filter INT,
	IN budget_filter INT,
	IN country_filter VARCHAR(255),
	IN director_name_filter VARCHAR(255),
	IN genre_filter VARCHAR(255),
	IN production_company_filter VARCHAR(255),
	IN rating_filter FLOAT,
	IN release_date_filter DATE,
	IN revenue_filter BIGINT,
	IN runtime_filter INT,
	IN starname_filter VARCHAR(255),
	IN language_filter VARCHAR(255),
	IN title_filter VARCHAR(255)
)
BEGIN
	-- Base query
	SET @query = 'SELECT * FROM movie_view WHERE 1=1';

	-- Add filters dynamically
	IF age_rating_filter IS NOT NULL THEN
    	SET @query = CONCAT(@query, ' AND age_rating = ''', age_rating_filter, '''');
	END IF;

	IF award_count_filter IS NOT NULL THEN
    	SET @query = CONCAT(@query, ' AND award_count = ', award_count_filter);
	END IF;

	IF budget_filter IS NOT NULL THEN
    	SET @query = CONCAT(@query, ' AND budget = ', budget_filter);
	END IF;

	IF country_filter IS NOT NULL THEN
    	SET @query = CONCAT(@query, ' AND country = ''', country_filter, '''');
	END IF;

	IF director_name_filter IS NOT NULL THEN
    	SET @query = CONCAT(@query, ' AND director_name = ''', director_name_filter, '''');
	END IF;

	IF genre_filter IS NOT NULL THEN
    	SET @query = CONCAT(@query, ' AND FIND_IN_SET(''', genre_filter, ''', genres)');
	END IF;

	IF production_company_filter IS NOT NULL THEN
    	SET @query = CONCAT(@query, ' AND production_company = ''', production_company_filter, '''');
	END IF;

	IF rating_filter IS NOT NULL THEN
    	SET @query = CONCAT(@query, ' AND rating = ', rating_filter);
	END IF;

	IF release_date_filter IS NOT NULL THEN
    	SET @query = CONCAT(@query, ' AND STR_TO_DATE(release_year, ''%Y-%m-%d'') = ''', release_date_filter, '''');
	END IF;

	IF revenue_filter IS NOT NULL THEN
    	SET @query = CONCAT(@query, ' AND revenue = ', revenue_filter);
	END IF;

	IF runtime_filter IS NOT NULL THEN
    	SET @query = CONCAT(@query, ' AND runtime = ', runtime_filter);
	END IF;

	IF starname_filter IS NOT NULL THEN
    	SET @query = CONCAT(@query, ' AND FIND_IN_SET(''', starname_filter, ''', star_name)');
	END IF;

	IF language_filter IS NOT NULL THEN
    	SET @query = CONCAT(@query, ' AND FIND_IN_SET(''', language_filter, ''', sub_language)');
	END IF;

	IF title_filter IS NOT NULL THEN
    	SET @query = CONCAT(@query, ' AND title = ''', title_filter, '''');
	END IF;

	-- Execute the dynamically built query
	PREPARE stmt FROM @query;
	EXECUTE stmt;
	DEALLOCATE PREPARE stmt;
END$$

DELIMITER ;


DELIMITER $$

CREATE PROCEDURE filter_actor_view(
	IN nationality_filter VARCHAR(255),
	IN date_of_birth_filter DATE,
	IN gender_filter VARCHAR(10),
	IN movie_count_filter INT,
	IN name_filter VARCHAR(255)
)
BEGIN
	-- Base query
	SET @query = 'SELECT * FROM actor_view WHERE 1=1';

	-- Add gender filter
	IF gender_filter IS NOT NULL THEN
    	SET @query = CONCAT(@query, ' AND gender = ''', gender_filter, '''');
	END IF;

	-- Add date of birth filter
	IF date_of_birth_filter IS NOT NULL THEN
    	SET @query = CONCAT(@query, ' AND date_of_birth = ''', date_of_birth_filter, '''');
	END IF;

	-- Add nationality filter
	IF nationality_filter IS NOT NULL THEN
    	SET @query = CONCAT(@query, ' AND nationality = ''', nationality_filter, '''');
	END IF;

	IF name_filter IS NOT NULL THEN
    	SET @query = CONCAT(@query, ' AND name = ''', name_filter, '''');
	END IF;

	-- Add movie count filter
	IF movie_count_filter IS NOT NULL THEN
    	SET @query = CONCAT(@query, ' AND movie_count = ', movie_count_filter);
	END IF;

	-- Execute the dynamically built query
	PREPARE stmt FROM @query;
	EXECUTE stmt;
	DEALLOCATE PREPARE stmt;
END$$

DELIMITER ;

DELIMITER $$

CREATE PROCEDURE filter_director_view(
	IN nationality_filter VARCHAR(255),
	IN date_of_birth_filter DATE,
	IN gender_filter VARCHAR(10),
	IN movie_count_filter INT,
	IN name_filter VARCHAR(255)
)
BEGIN
	-- Base query
	SET @query = 'SELECT * FROM director_view WHERE 1=1';

	-- Add gender filter
	IF gender_filter IS NOT NULL THEN
    	SET @query = CONCAT(@query, ' AND gender = ''', gender_filter, '''');
	END IF;

	-- Add date of birth filter
	IF date_of_birth_filter IS NOT NULL THEN
    	SET @query = CONCAT(@query, ' AND date_of_birth = ''', date_of_birth_filter, '''');
	END IF;

	-- Add nationality filter
	IF nationality_filter IS NOT NULL THEN
    	SET @query = CONCAT(@query, ' AND country = ''', nationality_filter, '''');
	END IF;

IF name_filter IS NOT NULL THEN
    	SET @query = CONCAT(@query, ' AND name = ''', name_filter, '''');
	END IF;

	-- Add movie count filter
	IF movie_count_filter IS NOT NULL THEN
    	SET @query = CONCAT(@query, ' AND movie_count = ', movie_count_filter);
	END IF;

	-- Execute the dynamically built query
	PREPARE stmt FROM @query;
	EXECUTE stmt;
	DEALLOCATE PREPARE stmt;
END$$

DELIMITER ;

DELIMITER $$

CREATE PROCEDURE filter_production_view(
	IN company_name_filter VARCHAR(255),
	IN movie_count_filter INT
)
BEGIN
	SET @query = 'SELECT
                	p.company_id,
                	p.company_name,
                	m.movie_count
              	FROM
                	production_company AS p
              	LEFT OUTER JOIN
                	(SELECT company_id, COUNT(*) AS movie_count
                 	FROM movie_company
                 	GROUP BY company_id) AS m
              	ON
                	p.company_id = m.company_id
              	WHERE 1=1';

	-- Apply company name filter
	IF company_name_filter IS NOT NULL THEN
    	SET @query = CONCAT(@query, ' AND p.company_name = ''', company_name_filter, '''');
	END IF;

	-- Apply movie count filter
	IF movie_count_filter IS NOT NULL THEN
    	SET @query = CONCAT(@query, ' AND m.movie_count = ', movie_count_filter);
	END IF;

	-- Execute the dynamically built query
	PREPARE stmt FROM @query;
	EXECUTE stmt;
	DEALLOCATE PREPARE stmt;
END$$

DELIMITER ;

DELIMITER $$

CREATE PROCEDURE filter_awards_view(
	IN category_filter VARCHAR(255),
	IN organization_filter VARCHAR(255),
	IN timesgiven_filter INT
)
BEGIN
	-- Base query
	SET @query = 'SELECT
                	a.award_id,
                	a.organization,
                	a.category,
                	m.times_given
              	FROM
                	awards AS a
              	LEFT OUTER JOIN
                	(SELECT award_id, COUNT(*) AS times_given
                 	FROM movie_awards
                 	GROUP BY award_id) AS m
              	ON
                	a.award_id = m.award_id
              	WHERE 1=1';

	-- Apply filters dynamically
	IF category_filter IS NOT NULL THEN
    	SET @query = CONCAT(@query, ' AND a.category = ''', category_filter, '''');
	END IF;

	IF organization_filter IS NOT NULL THEN
    	SET @query = CONCAT(@query, ' AND a.organization = ''', organization_filter, '''');
	END IF;

	IF timesgiven_filter IS NOT NULL THEN
    	SET @query = CONCAT(@query, ' AND m.times_given = ', timesgiven_filter);
	END IF;

	-- Execute the dynamically built query
	PREPARE stmt FROM @query;
	EXECUTE stmt;
	DEALLOCATE PREPARE stmt;
END$$

DELIMITER ;

