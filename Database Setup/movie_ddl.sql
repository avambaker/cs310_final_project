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
    MIN(p.company_id),
    MIN(p.production_company),
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

