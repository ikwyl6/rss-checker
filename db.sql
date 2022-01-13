/* Run as root */
/*CREATE USER rss_checker@localhost IDENTIFIED BY 'password';
GRANT ALL ON rss_checker.* TO rss_checker@localhost;
*/

/* Run below as rss_checker */
/* Below created with SHOW TABLE CREATE */
CREATE DATABASE rss_checker;
USE rss_checker; 

CREATE TABLE 'groups' (
	  'group_id' int(4) NOT NULL AUTO_INCREMENT,
	  'name' varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
	  PRIMARY KEY ('group_id'));
CREATE TABLE 'feed' (\
	  'id' int(11) NOT NULL AUTO_INCREMENT,\
	  'group_id' int(4) DEFAULT NULL,\
	  'title' varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,\
	  'url' varchar(1000) COLLATE utf8mb4_unicode_ci NOT NULL,\
	  'comments' int(1) DEFAULT NULL,\
	  'updated' datetime NOT NULL,\
	  PRIMARY KEY ('id'),\
	  KEY 'group_id' ('group_id'),\
	  CONSTRAINT 'feed_ibfk_1' FOREIGN KEY ('group_id') REFERENCES 'groups' ('group_id'));

