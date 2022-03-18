CREATE DATABASE ImageStore;
USE ImageStore;
CREATE TABLE image_table(
   image_key VARCHAR(255) NOT NULL,
   image_tag VARCHAR(255) NOT NULL,
   PRIMARY KEY (image_key)
);
CREATE TABLE cache_properties(
    param_key INT NOT NULL AUTO_INCREMENT,
    update_time INT NOT NULL,
    max_capacity INT NOT NULL,
    replacement_method VARCHAR(255) NOT NULL,
    PRIMARY KEY (param_key)
);
CREATE TABLE cache_stats(
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	  cache_size INT NOT NULL,
      key_count INT NOT NULL,
      request_count INT NOT NULL,
      miss_count INT NOT NULL,
      PRIMARY KEY (created_at)
      );
CREATE TABLE cache_policy (
    param_key INT NOT NULL AUTO_INCREMENT,
    max_miss_rate FLOAT NOT NULL,
    min_miss_rate FLOAT NOT NULL,
    exp_ratio FLOAT NOT NULL,
    shrink_ratio FLOAT NOT NULL,
    PRIMARY KEY (param_key)
);
