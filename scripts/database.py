import mysql.connector
from mysql.connector import errorcode


def connect_to_db(host, user, password, database):
    db = mysql.connector.connect(
        host=host, user=user, password=password, database=database
    )
    return db


def create_table(cursor, table_name, stmt):
    try:
        print(f"Creating table {table_name}...")
        cursor.execute(stmt)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print(f"Table {table_name} already exists.")
        else:
            print(err.msg)
    else:
        print("OK")


def drop_table(cursor, table_name):
    try:
        print(f"Dropping table {table_name}...")
        cursor.execute(f"DROP TABLE IF EXISTS {table_name }")
    except mysql.connector.Error as err:
        print(err.msg)
    else:
        print("OK")


def insert_record(cnx, cursor, table, primary_key, fields, record):
    select_record = f"""SELECT {primary_key} FROM {table} WHERE {primary_key}=%(primary_key)s;"""

    insert_values = (
        f"""INSERT INTO {table} """
        f"""({primary_key}, {', '.join(fields)}) """
        f"""VALUES (%s, {', '.join(map(lambda x: '%s', fields))});"""
    )

    try:
        primary_key_value = record[f"{primary_key}"]
        cursor.execute(select_record, {"primary_key": primary_key_value})
        res = cursor.fetchall()

        if len(res) == 0:
            print("Inserting new record...")
            cursor.execute(insert_values, (primary_key_value, ) + tuple(map(lambda x: f"{record[x]}", fields)))
            cnx.commit()
        else:
            print("Record already exists.")
    except mysql.connector.Error as err:
        print(err.msg)
    else:
        print("OK")


def insert_poet(cnx, cursor, record):
    select_poet = f"""SELECT id FROM poet WHERE url=%(url)s;"""

    insert_poet = (
        f"""INSERT INTO poet """
        f"""(name, yob, yod, img_url, bio, url) """
        f"""VALUES (%s, %s, %s, %s, %s, %s);"""
    )

    try:
        cursor.execute(select_poet, {"url": record["url"]})
        res = cursor.fetchall()

        if len(res) == 0:
            print("Inserting new record...")
            cursor.execute(
                insert_poet,
                (
                    record["name"],
                    record["yob"],
                    record["yod"],
                    record["image"],
                    record["bio"],
                    record["url"],
                ),
            )
            cnx.commit()
        else:
            print("Record already exists.")
    except mysql.connector.Error as err:
        print(err.msg)
    else:
        print("OK")