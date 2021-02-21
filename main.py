import json
import os

from scripts.scrape_poet import scrape_poet
from scripts.database import *


_DB_HOST = os.environ["SOP_DEV_HOST"]
_DB_USER = "danom"
_DB_PASSWORD = os.environ["MYSQL_PW"]
_DB_NAME = "sop_dev"

_CREATE_POET_STMT = (
    f"CREATE TABLE poet ("
    "id INT NOT NULL AUTO_INCREMENT, "
    "name VARCHAR(255) NOT NULL, "
    "yob int, "
    "yod int, "
    "img_url VARCHAR(255), "
    "bio  MEDIUMTEXT NULL, "
    "pf_url VARCHAR(255) NOT NULL, "
    "PRIMARY KEY (id));"
)

_CREATE_REGION_STMT = (
    f"CREATE TABLE region ("
    "id INT NOT NULL AUTO_INCREMENT, "
    "name VARCHAR(255) NOT NULL, "
    "PRIMARY KEY (id));"
)

_CREATE_SCHOOL_STMT = (
    f"CREATE TABLE school ("
    "id INT NOT NULL AUTO_INCREMENT, "
    "name VARCHAR(255) NOT NULL, "
    "PRIMARY KEY (id));"
)

_CREATE_ISFROM_STMT = (
    f"CREATE TABLE isfrom ("
    "poet_id INT NOT NULL,"
    "region_id INT NOT NULL,"
    "PRIMARY KEY (poet_id, region_id),"
    "poet_id FOREIGN KEY REFERENCES poet(id)),"
    "region_id FOREIGN KEY REFERENCES region(id);"
)

_CREATE_INSCHOOL_STMT = (
    f"CREATE TABLE inschool ("
    "poet_id INT NOT NULL,"
    "school_id INT NOT NULL,"
    "PRIMARY KEY (poet_id, school_id),"
    "poet_id FOREIGN KEY REFERENCES poet(id)),"
    "school_id FOREIGN KEY REFERENCES school(id);"
)


def main():
    db_cnx = get_db_cnx()
    cursor = db_cnx.cursor()

    # drop table
    # drop_table(cursor, 'poet')

    # create table
    create_table(cursor, "poet", _CREATE_POET_STMT)

    with open("data/poet_urls.txt", "r") as f:
        poet_urls = f.readlines()

    for url in poet_urls:
        # scrape poet's page's html
        poet = process_poet(url)
        # insert poet into db
        insert_record(db_cnx, cursor, poet)

    cursor.close()


def get_db_cnx():
    # establish a connection with the database
    # and create a cursor
    return connect_to_db(_DB_HOST, _DB_USER, _DB_PASSWORD, _DB_NAME)


def process_poet(url):
    # scrape poet's page's html
    poet = scrape_poet(url.strip("\n"))
    poet_name = poet["name"].lower().split(" ")
    file_name = "-".join(poet_name)
    with open(f"data/{file_name}.json", "w") as p_file:
        print(f"writing file: {file_name}.json")
        p_file.write(json.dumps(poet).__str__())
    return poet


if __name__ == "__main__":
    # main()
    db_cnx = get_db_cnx()
    cursor = db_cnx.cursor()
    poet = process_poet("https://www.poetryfoundation.org/poets/asiya-wadud")
    insert_record(db_cnx, cursor, poet)
