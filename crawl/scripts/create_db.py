import MySQLdb as mysql
import datetime

#open the file
from .utils import helper

HOST, USER, PASSWORD, DATABASE = helper.mysql_settings()
con = mysql.connect(host=HOST, user=USER, passwd=PASSWORD)
cur = con.cursor()

cur.execute('drop database if exists '+DATABASE)
cur.execute('create database '+DATABASE)
cur.execute('use '+DATABASE);

# every distro
cur.execute("""CREATE TABLE distros (
id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
name VARCHAR(255) NOT NULL UNIQUE,
description TEXT,
website TEXT
) ENGINE=INNODB""")

# every repo
cur.execute("""CREATE TABLE repos (
id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
distro_id INT UNSIGNED NOT NULL,
branch VARCHAR(255) NOT NULL,
codename VARCHAR(255) NOT NULL,
component VARCHAR(255) NOT NULL,
architecture VARCHAR(16),
discovered DATETIME NOT NULL,
FOREIGN KEY (distro_id) REFERENCES distros(id) ON DELETE CASCADE
) ENGINE=INNODB""")

# every crawl
cur.execute("""CREATE TABLE crawls (
id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
repo_id INT UNSIGNED,
package_id INT UNSIGNED,
time DATETIME NOT NULL,
release_count INT UNSIGNED,
FOREIGN KEY (repo_id) REFERENCES repos(id) ON DELETE CASCADE
) ENGINE=INNODB""")

# every package
cur.execute("""CREATE TABLE packages (
id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
name VARCHAR(255) NOT NULL UNIQUE,
source_id INT UNSIGNED,
FOREIGN KEY (source_id) REFERENCES packages(id) ON DELETE SET NULL
) ENGINE=INNODB""")

# for every release
cur.execute("""CREATE TABLE releases (
id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
package_id INT UNSIGNED,
version VARCHAR(64) NOT NULL,
revision VARCHAR(64),
epoch VARCHAR(64) NOT NULL,
repo_id INT UNSIGNED,
released DATETIME NOT NULL,
FOREIGN KEY (package_id) REFERENCES packages(id) ON DELETE SET NULL,
FOREIGN KEY (repo_id) REFERENCES repos(id) ON DELETE CASCADE
) ENGINE=INNODB""")

cur.execute('CREATE UNIQUE INDEX rel_index ON releases (package_id, version, revision, repo_id)')

# extra info
cur.execute("""CREATE TABLE extra (
id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
release_id BIGINT UNSIGNED,
content TEXT,
FOREIGN KEY (release_id) REFERENCES releases(id) ON DELETE CASCADE
) ENGINE=INNODB""") 

con.close()