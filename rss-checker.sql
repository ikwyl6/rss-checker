/* Run as root */
/*CREATE USER rss_checker@localhost IDENTIFIED BY 'password';
GRANT ALL ON rss_checker.* TO rss_checker@localhost;
*/

/* Run as rss_checker */
CREATE TABLE feed (\
	id INT PRIMARY KEY NOT NULL auto_increment, \
	title VARCHAR(500), \
	url VARCHAR(1000) NOT NULL, \
	comments INT(1), \
	updated DATETIME NOT NULL);
/*
CREATE TABLE rss (\
	id INT PRIMARY KEY NOT NULL auto_increment, \
	feed_id INT NOT NULL,\
	title VARCHAR(500),\
	url VARCHAR(1000) NOT NULL,\
	published DATETIME NOT NULL, \
	FOREIGN KEY (feed_id) REFERENCES feed(id) ON DELETE CASCADE);
*/

