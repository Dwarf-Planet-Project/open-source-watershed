# -*- coding: utf-8 -*-
import psycopg2 as db
import datetime
import sys
import subprocess
sys.path.append("")

#open the file
from utils import helper
import utils.db.users as users

HOST, USER, PASSWORD, DATABASE = helper.mysql_settings()
con = db.connect(host=HOST, user=USER, password=PASSWORD, database=DATABASE)
cur = con.cursor()

cur.execute("""DROP SCHEMA public CASCADE""")
cur.execute("""CREATE SCHEMA public""")

cur.execute("""CREATE TABLE users (
id SERIAL NOT NULL,
handle VARCHAR(255) NOT NULL UNIQUE,
pswhash TEXT NOT NULL,
email VARCHAR(255) NOT NULL UNIQUE,
PRIMARY KEY (id)
)""")

# every distro
cur.execute("""CREATE TABLE distros (
id SERIAL NOT NULL,
name VARCHAR(255) NOT NULL,
color VARCHAR(7),
description TEXT,
website TEXT,
PRIMARY KEY (id)
)""")

# every repo
cur.execute("""CREATE TABLE repos (
id SERIAL NOT NULL,
distro_id INT NOT NULL REFERENCES distros(id),
codename VARCHAR(255) NOT NULL,
component VARCHAR(255) NOT NULL,
architecture VARCHAR(16),
last_crawl TIMESTAMP,
PRIMARY KEY (id)
)""")

cur.execute("""CREATE TABLE branches (
id SERIAL NOT NULL,
repo_id INT NOT NULL REFERENCES repos(id),
branch VARCHAR(16) NOT NULL,
start TIMESTAMP,
PRIMARY KEY (id)
)""")

# every package
cur.execute("""CREATE TABLE packages (
id SERIAL NOT NULL,
name VARCHAR(255) NOT NULL UNIQUE,
PRIMARY KEY (id)
)""")

cur.execute("""CREATE TABLE package_info (
id SERIAL NOT NULL,
package_id INT NOT NULL REFERENCES packages(id),
user_id INT NOT NULL,
_when TIMESTAMP NOT NULL,
cpe VARCHAR(255),
homepage VARCHAR(255),
description TEXT,
PRIMARY KEY (id)
)""")

cur.execute("""CREATE TABLE package_notes (
id SERIAL NOT NULL,
user_id INT NOT NULL,
package_id INT NOT NULL,
_when TIMESTAMP NOT NULL,
note TEXT NOT NULL,
_public BOOL NOT NULL
)""")

# for user reviews
cur.execute("""CREATE TABLE reviews (
id SERIAL NOT NULL,
user_id INT NOT NULL REFERENCES users(id),
_when TIMESTAMP NOT NULL,
good BOOL
)""")

# package links
cur.execute("""CREATE TABLE links (
id SERIAL NOT NULL,
package_tgt INT NOT NULL REFERENCES packages(id),
distro_tgt INT REFERENCES distros(id),
package_src INT NOT NULL REFERENCES packages(id),
distro_src INT REFERENCES distros(id),
PRIMARY KEY(id),
UNIQUE (package_tgt, distro_tgt, package_src, distro_src)
)""")

cur.execute("""CREATE TABLE link_reviews (
link_id INT NOT NULL REFERENCES links(id)
) INHERITS (reviews)""")

cur.execute("""CREATE TABLE releases (
id SERIAL NOT NULL,
package_id INT NOT NULL REFERENCES packages(id),
version VARCHAR(255) NOT NULL,
revision VARCHAR(255) NOT NULL DEFAULT '0',
released TIMESTAMP NOT NULL,
PRIMARY KEY (id)
)""")

# for every downstream release
cur.execute("""CREATE TABLE dreleases (
repo_id INT NOT NULL REFERENCES repos(id),
FOREIGN KEY (package_id) REFERENCES packages(id) ON DELETE CASCADE,
PRIMARY KEY (id)
) INHERITS (releases)""")

# for every upstream release
cur.execute("""CREATE TABLE usources (
id SERIAL NOT NULL PRIMARY KEY,
name VARCHAR(255) NOT NULL,
description VARCHAR(255),
last_crawl TIMESTAMP,
user_id INT REFERENCES users(id),
UNIQUE (name, user_id)
)""")

cur.execute("""CREATE TABLE ureleases (
usource_id INT NOT NULL REFERENCES usources(id),
FOREIGN KEY (package_id) REFERENCES packages(id) ON DELETE CASCADE,
PRIMARY KEY (id),
UNIQUE (package_id, version, revision, usource_id)
) INHERITS (releases)""")

# explore tables
cur.execute("""CREATE TABLE explore (
id SERIAL NOT NULL PRIMARY KEY,
name VARCHAR(255) NOT NULL,
url TEXT NOT NULL,
target_depth SMALLINT,
good_packages VARCHAR(255)[],
bad_packages VARCHAR(255)[],
bad_tokens VARCHAR(255)[],
bad_versions VARCHAR(255)[],
deadends VARCHAR(255)[],
user_id INT NOT NULL REFERENCES users(id),
last_crawl TIMESTAMP
)""")

cur.execute("""CREATE TABLE explore_releases (
explore_id INT NOT NULL REFERENCES explore(id),
urelease_id INT NOT NULL REFERENCES ureleases(id),
PRIMARY KEY (explore_id, urelease_id)
)""")

cur.execute("""CREATE TABLE explore_review (
explore_id INT NOT NULL REFERENCES explore(id),
FOREIGN KEY (user_id) REFERENCES users(id)
) INHERITS (reviews)""")

# sourceforge tables
cur.execute("""CREATE TABLE sf (
id SERIAL NOT NULL PRIMARY KEY,
name VARCHAR(255) NOT NULL,
project_num INT NOT NULL,
packages VARCHAR(255)[],
bad_tokens VARCHAR(255)[],
bad_versions VARCHAR(255)[],
user_id INT REFERENCES users(id),
last_crawl TIMESTAMP,
UNIQUE (name)
)""")

cur.execute("""CREATE TABLE sf_releases (
sf_id INT NOT NULL REFERENCES sf(id),
urelease_id INT NOT NULL REFERENCES ureleases(id)
)""")

cur.execute("""CREATE TABLE sf_reviews (
sf_id INT NOT NULL REFERENCES sf(id),
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
) INHERITS (reviews)""")

# package sets
cur.execute("""CREATE TABLE groups (
id SERIAL NOT NULL PRIMARY KEY,
user_id INT NOT NULL REFERENCES users(id),
name VARCHAR(255)
)""")

cur.execute("""CREATE TABLE group_packages (
group_id INT REFERENCES groups(id),
package_id INT REFERENCES packages(id)
)""")

# cache may not be needed for rev3
cur.execute("""CREATE TABLE cache (
id SERIAL NOT NULL PRIMARY KEY,
cached TIMESTAMP NOT NULL,
k VARCHAR(255) NOT NULL UNIQUE,
v BYTEA,
status SMALLINT NOT NULL DEFAULT 1
)""")

cur.execute("""CREATE TABLE cache_deps (
id BIGSERIAL NOT NULL PRIMARY KEY,
package_id INT REFERENCES packages(id),
distro_id INT REFERENCES distros(id),
cache_id INT REFERENCES cache(id)
)""")

con.commit()
con.close()

f = open("/usr/share/postgresql/contrib/pgcrypto.sql")
subprocess.call(["psql",DATABASE], stdin=f)
f.close()

users.create("tannewt", "test", "scott.shawcroft@gmail.com")