import os

from scripts.scrape_poet import scrape_poet
from scripts.database import *


_DB_HOST = 'localhost'
_DB_USER = 'root'
_DB_PASSWORD = os.environ['MYSQL_PW']


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

    with open('scripts/poet_urls.txt', 'r') as f:
        poet_urls = f.readlines()

    for url in poet_urls:
        poet = scrape_poet(url.strip('\n'))
        print(poet)

        # insert poet into db
        insert_record(db_cnx, cursor, 'poet', poet)

    cursor.close()


if __name__ == "__main__":
    main()





