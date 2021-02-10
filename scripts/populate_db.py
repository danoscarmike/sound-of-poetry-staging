import os

import mysql.connector
from mysql.connector import errorcode


def connect_to_db(host, user, password, database):
    db = mysql.connector.connect(
      host=host,
      user=user,
      password=password,
      database=database
    )
    return db


def create_table(cursor, table_name):
    try:
        print(f"Creating table {table_name}...")
        cursor.execute(f"CREATE TABLE {table_name} ("
                       "id INT NOT NULL AUTO_INCREMENT, "
                       "name VARCHAR(255) NOT NULL, "
                       "meta VARCHAR(255) NULL, "
                       "bio  MEDIUMTEXT NULL, "
                       "PRIMARY KEY (id));")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print(f"Table {table_name} already exists.")
        else:
            print(err.msg)
    else:
        print("OK")

    cursor.close()


def drop_table(cursor, table_name):
    try:
        print(f"Dropping table {table_name}...")
        cursor.execute(f"DROP TABLE IF EXISTS {table_name }")
    except mysql.connector.Error as err:
        print(err.msg)
    else:
        print("OK")

    cursor.close()


# TODO(danom): generalize this to add any record to any table
def insert_record(cnx, cursor, table_name, record):
    insert_poet = f"""INSERT INTO {table_name} """ \
                  f"""(name, meta, bio) """ \
                  f"""VALUES (%s, %s, %s);"""
    try:
        print("Inserting new record...")
        cursor.execute(insert_poet, (record['name'], record['meta'], record['bio']))
    except mysql.connector.Error as err:
        print(err.msg)
    else:
        print("OK")

    cnx.commit()
    cursor.close()
