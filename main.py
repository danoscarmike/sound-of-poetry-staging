import json
import os
import re
import string

import scripts.sop_sql as sop
import scripts.word_net_sql as wn
from scripts.database import *

_DB_HOST = "localhost"
_DB_USER = "root"
_DB_PASSWORD = "password"
_DB_NAME = "sop"

_CREATE_POET_STMT = (
    f"CREATE TABLE poet ("
    "id INT NOT NULL AUTO_INCREMENT, "
    "name VARCHAR(255) NOT NULL, "
    "yob int, "
    "yod int, "
    "img_url VARCHAR(255), "
    "bio  MEDIUMTEXT NULL, "
    "url VARCHAR(255) NOT NULL, "
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
    "FOREIGN KEY (poet_id) REFERENCES poet(id),"
    "FOREIGN KEY (region_id) REFERENCES region(id));"
)

_CREATE_INSCHOOL_STMT = (
    f"CREATE TABLE inschool ("
    "poet_id INT NOT NULL,"
    "school_id INT NOT NULL,"
    "PRIMARY KEY (poet_id, school_id),"
    "FOREIGN KEY (poet_id) REFERENCES poet(id),"
    "FOREIGN KEY (school_id) REFERENCES school(id));"
)

_CREATE_POEM_STMT = (
    f"CREATE TABLE poem ("
    "id INT NOT NULL AUTO_INCREMENT,"
    "url VARCHAR(255) NOT NULL,"
    "poet_url VARCHAR(255),"
    "title TEXT,"
    "poem_string MEDIUMTEXT NOT NULL,"
    "audio_url VARCHAR(255),"
    "video_url VARCHAR(255),"
    "PRIMARY KEY(id));"
)

_CREATE_TAG_STMT = (
    f"CREATE TABLE tag ("
    "id INT NOT NULL AUTO_INCREMENT,"
    "name TEXT,"
    "PRIMARY KEY(id));"
)

_CREATE_ISTAGGED_STMT = (
    f"CREATE TABLE istagged ("
    "poem_id INT NOT NULL,"
    "tag_id INT NOT NULL,"
    "PRIMARY KEY(poem_id, tag_id),"
    "FOREIGN KEY(poem_id) REFERENCES poem(id),"
    "FOREIGN KEY(tag_id) REFERENCES tag(id));"
)

_CREATE_TAGHAS_OPENWORD_STMT = (
    f"CREATE TABLE taghas_openword ("
    "tag_id INT NOT NULL,"
    "word_id INT(10) UNSIGNED NOT NULL,"
    "PRIMARY KEY(tag_id, word_id),"
    "FOREIGN KEY(word_id) REFERENCES words(wordid),"
    "FOREIGN KEY(tag_id) REFERENCES tag(id));"
)

_CREATE_TAGHAS_CLOSEDWORD_STMT = (
    f"CREATE TABLE taghas_closedword ("
    "tag_id INT NOT NULL,"
    "word_id INT(10) UNSIGNED NOT NULL,"
    "PRIMARY KEY(tag_id, word_id),"
    "FOREIGN KEY(word_id) REFERENCES closed_words(wordid),"
    "FOREIGN KEY(tag_id) REFERENCES tag(id));"
)

_CREATE_POEMHAS_OPENWORD_STMT = (
    f"CREATE TABLE poemhas_openword ("
    "poem_id INT NOT NULL,"
    "word_id INT(10) UNSIGNED NOT NULL,"
    "use_count INT NOT NULL,"
    "PRIMARY KEY(poem_id, word_id),"
    "FOREIGN KEY(word_id) REFERENCES words(wordid),"
    "FOREIGN KEY(poem_id) REFERENCES poem(id));"
)

_CREATE_POEMHAS_CLOSEDWORD_STMT = (
    f"CREATE TABLE poemhas_closedword ("
    "poem_id INT NOT NULL,"
    "word_id INT(10) UNSIGNED NOT NULL,"
    "use_count INT NOT NULL,"
    "PRIMARY KEY(poem_id, word_id),"
    "FOREIGN KEY(word_id) REFERENCES closed_words(wordid),"
    "FOREIGN KEY(poem_id) REFERENCES poem(id));"
)

_CREATE_POEM_WORDNET_STMT = (
    f"CREATE TABLE poem_wordnet ("
    "poem_id INT NOT NULL,"
    "word_id INT(10) UNSIGNED NOT NULL,"
    "use_count INT NOT NULL,"
    "PRIMARY KEY(poem_id, word_id),"
    "FOREIGN KEY(word_id) REFERENCES words(wordid),"
    "FOREIGN KEY(poem_id) REFERENCES poem(id));"
)

_CREATE_POEM_WORDCOUNT_STMT = (
    f"CREATE TABLE poem_wordcount ("
    "poem_id INT NOT NULL,"
    "word VARCHAR(255) NOT NULL,"
    "use_count INT NOT NULL,"
    "PRIMARY KEY(poem_id, word),"
    "FOREIGN KEY(poem_id) REFERENCES poem(id));"
)


def get_db_cnx():
    # establish a connection with the database
    # and create a cursor
    return connect_to_db(_DB_HOST, _DB_USER, _DB_PASSWORD, _DB_NAME)


def main():
    db_cnx = get_db_cnx()
    cursor = db_cnx.cursor()

    # drop table
    # drop_table(cursor, "poem_wordnet")
    # drop_table(cursor, "poem_wordcount")
    # drop_table(cursor, "tag_hasword")
    # drop_table(cursor, "poemhas_openword")
    # drop_table(cursor, "poemhas_closedword")
    # drop_table(cursor, "taghas_openword")
    # drop_table(cursor, "taghas_closedword")
    # drop_table(cursor, 'istagged')
    # drop_table(cursor, 'tag')
    # drop_table(cursor, 'poem')
    # drop_table(cursor, 'isfrom')
    # drop_table(cursor, 'inschool')
    # drop_table(cursor, 'school')
    # drop_table(cursor, 'region')
    # drop_table(cursor, 'poet')

    # create table
    # create_table(cursor, "poem_wordnet", _CREATE_POEM_WORDNET_STMT)
    # create_table(cursor, "poem_wordcount", _CREATE_POEM_WORDCOUNT_STMT)
    # create_table(cursor, "poem", _CREATE_POEM_STMT)
    # create_table(cursor, "tag", _CREATE_TAG_STMT)
    # create_table(cursor, "istagged", _CREATE_ISTAGGED_STMT)
    # create_table(cursor, "poemhas_openword", _CREATE_POEMHAS_OPENWORD_STMT)
    # create_table(cursor, "poemhas_closedword", _CREATE_POEMHAS_CLOSEDWORD_STMT)
    # create_table(cursor, "taghas_openword", _CREATE_TAGHAS_OPENWORD_STMT)
    # create_table(cursor, "taghas_closedword", _CREATE_TAGHAS_CLOSEDWORD_STMT)
    # create_table(cursor, "poet", _CREATE_POET_STMT)
    # create_table(cursor, "region", _CREATE_REGION_STMT)
    # create_table(cursor, "school", _CREATE_SCHOOL_STMT)
    # create_table(cursor, "isfrom", _CREATE_ISFROM_STMT)
    # create_table(cursor, "inschool", _CREATE_INSCHOOL_STMT)

    # with open("data/urls/poet_urls.txt", "r") as f:
    #     poet_urls = f.readlines()
    #
    # for url in poet_urls:
    #     # scrape poet's page's html
    #     poet = process_poet(url)
    #     # insert poet into db
    #     insert_poet(db_cnx, cursor, poet)

    # with open("data/urls/poem_urls.txt", "r") as f:
    #     poem_urls = f.readlines()
    #
    # for url in poem_urls:
    #     # scrape poem's page's html
    #     poem = process_poem(url)
    #     # insert poem into db
    #     if poem:
    #         table = "poem"
    #         primary_key = "url"
    #         fields = ["poet_url", "title", "poem_string", "audio_url", "video_url"]
    #         insert_record(db_cnx, cursor, table, primary_key, fields, poem

    cursor.close()


if __name__ == "__main__":
    main()
