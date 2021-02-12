import json
import os

from scripts.scrape_poet import scrape_poet
from scripts.database import *


_DB_HOST = 'localhost'
_DB_USER = 'root'
_DB_PASSWORD = os.environ['MYSQL_PW']

_CREATE_POET_STMT = (f"CREATE TABLE poet ("
                       "id INT NOT NULL AUTO_INCREMENT, "
                       "name VARCHAR(255) NOT NULL, "
                       "meta VARCHAR(255) NULL, "
                       "bio  MEDIUMTEXT NULL, "
                       "PRIMARY KEY (id));")

_CREATE_AUTHORED_STMT = ()

_CREATE_REGION_STMT = ()

_CREATE_SCHOOL_STMT = ()




def main():
    # establish a connection with the database
    # and create a cursor
    db_cnx = connect_to_db(_DB_HOST,
                           _DB_USER,
                           _DB_PASSWORD,
                           'poetry')
    cursor = db_cnx.cursor()

    # drop table
    drop_table(cursor, 'poet')

    # create table
    create_table(cursor, 'poet')

    with open('data/poet_urls.txt', 'r') as f:
        poet_urls = f.readlines()

    for url in poet_urls:
        # scrape poet's page's html
        poet = scrape_poet(url.strip('\n'))
        poet_name = poet["name"].lower().split(" ")
        file_name = "-".join(poet_name)
        with open(f"data/{file_name}.json", 'w') as p_file:
            print(f"writing file: {file_name}.json")
            p_file.write(json.dumps(poet).__str__())
        # insert poet into db
        insert_record(db_cnx, cursor, 'poet', poet)


    cursor.close()


if __name__ == "__main__":
    main()





