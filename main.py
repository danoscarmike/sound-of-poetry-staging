from scripts.scrape_poet import scrape_poet
from scripts.populate_db import *


_DB_HOST = 'localhost'
_DB_USER = 'root'
_DB_PASSWORD = os.environ['MYSQL_PW']


def main():
    # scrape a poets details from the poetry foundation
    yeats = scrape_poet('william-butler-yeats')

    # establish a connection with the database
    # and create a cursor
    db_cnx = connect_to_db(_DB_HOST,
                           _DB_USER,
                           _DB_PASSWORD,
                           'poetry')
    cursor = db_cnx.cursor()

    # insert poet into db
    insert_record(db_cnx, cursor, 'poet', yeats)


if __name__ == "__main__":
    main()





