import json
import csv
import os
import re
import string

import scripts.sop_sql as sop
import scripts.word_net_sql as wn
from scripts.poem.scrape_poem import scrape_poem
from scripts.poet.scrape_poet import scrape_poet
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


# async def download_coroutine(session, url, cursor, db_cnx):
#     with async_timeout.timeout(10):
#         try:
#             async with session.get(url) as response:
#                 if response.status >= 300:
#                     cursor.execute(f"""DELETE FROM images_synsets WHERE image_url=%(url)s;""", {'url': url})
#                     db_cnx.commit()
#                     print(f'Deleted {url}')
#             return await response.release()
#         except:
#             print("Connection exception:", url)


def main():
    # command line arguments
    # parser = argparse.ArgumentParser()
    # parser.add_argument('-u', '--url', action="store_const", help="foo help")
    # parser.add_argument('-t', '--table', action="store_const", help="foo help")
    # args = parser.parse_args()
    # print(args)
    # table = sys.argv[1]
    # filename = sys.argv[2]

    db_cnx = get_db_cnx()
    cursor = db_cnx.cursor()

    cursor.execute(f"""SELECT * FROM imagenet_image_synset iis WHERE iis.synsetid NOT IN (SELECT gms.synsetid FROM google_mid_synset gms);""")
    rows = cursor.fetchall()

    synset_map = {}
    image_map = {}
    next_image_id = 1

    for row in rows:
        synset_id = row[1]
        image_url = row[3]
        image_id = 0
        if image_map.get(image_url):
            image_id = image_map[image_url]
        else:
            image_map[image_url] = next_image_id
            image_id = next_image_id
            next_image_id = next_image_id + 1

        if synset_map.get(synset_id):
            if len(synset_map[synset_id]) < 7 and image_id not in synset_map[synset_id]:
                synset_map[synset_id].append(image_id)
        else:
            synset_map[synset_id] = [image_id]

    for key, value in image_map.items():
        cursor.execute(f"""INSERT INTO imagenet_images (image_id, image_url) VALUES (%s, %s);""", (value, key))

    for key, values in synset_map.items():
        for value in values:
            cursor.execute(f"""INSERT INTO imagenet_synset_imageid (synsetid, image_id) VALUES (%s, %s);""", (key, value))
        db_cnx.commit()

    # cursor.execute(f"""SELECT * FROM google_mid_imageid;""")
    # rows = cursor.fetchall()
    # rowHash = {}
    #
    # for row in rows:
    #     imageId = row[0]
    #     m_id = row[2]
    #     if rowHash.get(m_id):
    #         if len(rowHash[m_id]) < 7 and imageId not in rowHash[m_id]:
    #             rowHash[m_id].append(imageId)
    #     else:
    #         rowHash[m_id] = [imageId]
    #
    # for key, values in rowHash.items():
    #     for value in values:
    #         cursor.execute(f"""INSERT INTO google_mid_imageid_lean (m_id, image_id) VALUES (%s, %s);""", (key, value))
    #     db_cnx.commit()

    # media_class_rows = sop.select_all_media_classes(cursor)
    # non_wordnet_rows = wn.select_all_non_wordnet(cursor)
    # non_wordnet_hash = {}
    # word_exceptions = []
    #
    # for nwn in non_wordnet_rows:
    #     wordid = nwn[0]
    #     lemma = nwn[1]
    #     non_wordnet_hash[lemma] = wordid
    #
    # word_list = wn.select_all_words(cursor)
    # multi_word_list = []
    #
    # for item in word_list:
    #     lemma = item[1]
    #     if ' ' in lemma:
    #         multi_word_list.append(lemma)
    #
    # word_hash = {}
    # multi_word_hash = {}
    #
    # for item in word_list:
    #     word_id = item[0]
    #     lemma = item[1]
    #     morph = item[2]
    #     if ' ' in lemma:
    #         if morph:
    #             if morph in multi_word_hash:
    #                 multi_word_hash[morph].append(word_id)
    #             else:
    #                 multi_word_hash[morph] = [word_id]
    #         if lemma in multi_word_hash:
    #             multi_word_hash[lemma].append(word_id)
    #         else:
    #             multi_word_hash[lemma] = [word_id]
    #     else:
    #         if morph:
    #             if morph in word_hash:
    #                 word_hash[morph].append(word_id)
    #             else:
    #                 word_hash[morph] = [word_id]
    #         if lemma in word_hash:
    #             word_hash[lemma].append(word_id)
    #         else:
    #             word_hash[lemma] = [word_id]
    #
    # tags = sop.select_tags(cursor)
    #
    # for tag in tags:
    #     tag_id = tag[0]
    #     name = tag[1]
    #
    #     for multi in multi_word_list:
    #         if multi in name:
    #             name.replace(multi, '')
    #             for word_id in multi_word_hash[multi]:
    #                 wn.insert_tag_wordnet(cursor, db_cnx, tag_id, word_id)
    #
    #     cleaned_name = name.translate(str.maketrans('', '', string.punctuation))
    #     words = cleaned_name.split()
    #
    #     for word in words:
    #         word = word.lower()
    #         if word in word_hash:
    #             for word_id in word_hash[word]:
    #                 wn.insert_tag_wordnet(cursor, db_cnx, tag_id, word_id)
    #         elif word in non_wordnet_hash:
    #             word_id = non_wordnet_hash[word]
    #             wn.insert_tag_non_wordnet(cursor, db_cnx, tag_id, word_id)
    #         else:
    #             word_exceptions.append(word)
    #
    # print(word_exceptions)
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

    # with open('data/sound/google_balanced_train_segments.csv') as csv_file:
    #     csv_reader = csv.reader(csv_file, delimiter=',')
    #     line_count = 0
    #     for row in csv_reader:
    #         if line_count < 2:
    #             print(f'Column names are {", ".join(row)}')
    #             line_count += 1
    #         else:
    #             if ',' in row[3]:
    #                 audio_ids = row[3].split(',')
    #                 for i in range(0, len(audio_ids)):
    #                     cursor.execute(f"""INSERT INTO ytid_mid (ytid, m_id) """
    #                                    f"""VALUES (%s, %s);""", (row[0], audio_ids[i]))
    #             else:
    #                 cursor.execute(f"""INSERT INTO ytid_mid (ytid, m_id) """
    #                                f"""VALUES (%s, %s);""", (row[0], row[3]))
    #
    #             db_cnx.commit()
    #             line_count += 1
    #     print(f'Processed {line_count} lines.')

    # with open('data/sound/FSD50K_collection_eval.csv') as csv_file:
    #     csv_reader = csv.reader(csv_file, delimiter=',')
    #     line_count = 0
    #     for row in csv_reader:
    #         if line_count == 0:
    #             print(f'Column names are {", ".join(row)}')
    #             line_count += 1
    #         else:
    #             if ',' in row[1]:
    #                 labels = row[1].split(',')
    #                 audio_ids = row[2].split(',')
    #                 for i in range(0, len(labels)):
    #                     print(labels[i].replace('_', ' '), audio_ids[i])
    #
    #             line_count += 1
    #     print(f'Processed {line_count} lines.')


    # with open(F"data/FSD50K_class_info.json", 'r') as f:
    #     labels = json.load(f)
    #     print(len(labels.keys()))

    # with open(f"data/FSD50K_eval_clips_info.json", 'r') as f:
    #     clips = json.load(f)
    #     for key in clips.keys():
    #         clip = clips[key]

            # if 'attrs' in clip.keys():
            #     if 'Region:' in poet_json['attrs'].keys():
            #         regions = poet_json['attrs']['Region:']
            #         for region in regions:
            #             print(f"Inserting: id:{i} author:{file_name} -> {region}")
            #             cursor.execute(f"""SELECT id FROM region """
            #                            f"""WHERE name=%(name)s;""", {'name': region})
            #             region_row = cursor.fetchone()
            #             region_id = ""
            #             if region_row:
            #                 region_id = region_row[0]
            #             else:
            #                 cursor.execute(f"""INSERT INTO region (name) VALUES (%s);""", [region])
            #                 cursor.execute(f"""SELECT id FROM region """
            #                                f"""WHERE name=%(name)s;""", {'name': region})
            #                 region_id = cursor.fetchone()[0]
            #
            #             cursor.execute(f"""INSERT INTO isfrom (poet_id, region_id) """
            #                            f"""VALUES (%s, %s);""", (i, region_id))
            #             db_cnx.commit()
            #     if 'School/Period:' in poet_json['attrs'].keys():
            #         schools = poet_json['attrs']['School/Period:']
            #         for school in schools:
            #             print(f"Inserting: {file_name} -> {school}")
            #             cursor.execute(f"""SELECT id FROM school """
            #                            f"""WHERE name=%(name)s;""", {'name': school})
            #             school_row = cursor.fetchone()
            #             school_id = ""
            #             if school_row:
            #                 school_id = school_row[0]
            #             else:
            #                 cursor.execute(f"""INSERT INTO school(name) VALUES (%s);""", [school])
            #                 cursor.execute(f"""SELECT id FROM school """
            #                                f"""WHERE name=%(name)s;""", {'name': school})
            #                 school_id = cursor.fetchone()[0]
            #
            #             cursor.execute(f"""INSERT INTO inschool (poet_id, school_id) """
            #                            f"""VALUES (%s, %s);""", (i, school_id))
            #             db_cnx.commit()

    # with open('data/images_synsets_flickr.csv', mode='w') as flickr_csv:
    #     flickr_csv = csv.writer(flickr_csv, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    #     with open("data/images_synsets.csv") as csv_file:
    #         csv_reader = csv.reader(csv_file, delimiter=',')
    #         line_count = 0
    #         urls = []
    #         for row in csv_reader:
    #             if line_count == 0:
    #                 print(f'Column names are {", ".join(row)}')
    #                 line_count += 1
    #             else:
    #                 if "flickr.com" in row[3]:
    #                     row[1] = "1" + row[1]
    #                     flickr_csv.writerow(row)

        # async with aiohttp.ClientSession(loop=loop) as session:
        #     tasks = [download_coroutine(session, url, cursor, db_cnx) for url in urls]
        #     await asyncio.gather(*tasks)
            #     try:
            #         html = requests.get(url)
            #         if html.status_code >= 300:
            #             cursor.execute(f"""DELETE FROM images_synsets WHERE image_url=%(url)s;""", {'url': url})
            #             db_cnx.commit()
            #             print(f'Deleted {url}')
            #             delete_count += 1
            #     except:
            #         exception_urls.append(url)
            #         print("Connection exception:", url)
            #     line_count += 1
            # print(f'Processed {line_count} lines.')

        # print(f'Deleted {delete_count} rows.')
        # print(f'{line_count - delete_count} records remain.')
        # print(f'refused urls', refused_urls)

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
    #     # alter_file_name = lambda path: path[5] if path[3] == "poetrymagazine" else path[4]
    #     # poem = process_data(scrape_poem, url, "url", "/", "test_json", lambda path: path[5] if path[3] == "poetrymagazine" else path[4])
    #     # insert poem into db
    #     if poem:
    #         table = "poem"
    #         primary_key = "url"
    #         fields = ["poet_url", "title", "poem_string", "audio_url", "video_url"]
    #         insert_record(db_cnx, cursor, table, primary_key, fields, poem)

    # all_regions = []
    # all_schools = []
    # poet_regions = {}
    # poet_schools = {}
    # exception_files = []
    # select_poet_stmt = f"""SELECT url FROM poet WHERE id=%s;"""
    # select_poem_stmt = f"""SELECT id, url, title FROM poem WHERE id=%s"""
    #
    # directory = r'/Users/cdhenry/Development/MCIT/550/Project/sound-of-poetry-staging/data/poems'
    # count = 1
    # word_list = wn.select_all_words(cursor)
    # multi_word_list = []
    #
    # for item in word_list:
    #     lemma = item[1]
    #     if ' ' in lemma:
    #         multi_word_list.append(lemma)
    #
    # word_hash = {}
    # multi_word_hash = {}
    #
    # for item in word_list:
    #     word_id = item[0]
    #     lemma = item[1]
    #     morph = item[2]
    #     if ' ' in lemma:
    #         if morph:
    #             if morph in multi_word_hash:
    #                 multi_word_hash[morph].append(word_id)
    #             else:
    #                 multi_word_hash[morph] = [word_id]
    #         if lemma in multi_word_hash:
    #             multi_word_hash[lemma].append(word_id)
    #         else:
    #             multi_word_hash[lemma] = [word_id]
    #     else:
    #         if morph:
    #             if morph in word_hash:
    #                 word_hash[morph].append(word_id)
    #             else:
    #                 word_hash[morph] = [word_id]
    #         if lemma in word_hash:
    #             word_hash[lemma].append(word_id)
    #         else:
    #             word_hash[lemma] = [word_id]
    #
    # for entry in os.scandir(directory):
    #     try:
    #         with open(entry.path, 'r') as p_file:
    #             print("Inserting path: ", entry.path)
    #             poem_json = json.load(p_file)
    #             url = poem_json['url']
    #             # poet_url = poem_json['poet_url']
    #             # title = poem_json['title']
    #             poem_lines = poem_json['poem_lines']
    #             # poem_string = poem_json['poem_string']
    #             # audio_url = poem_json['audio_url']
    #             # video_url = poem_json['video_url']
    #             # tags = poem_json['tags']
    #
    #             # sop.insert_poem(cursor, db_cnx, url, poet_url, title, poem_string, audio_url, video_url)
    #             poem_id = sop.select_poem_row(cursor, url)[0]
    #
    #             #
    #             # for tag in tags:
    #             #     sop.handle_tag(cursor, db_cnx, tag, poem_id)
    #
    #             for line in poem_lines:
    #                 for multi in multi_word_list:
    #                     if multi in line:
    #                         line.replace(multi, '')
    #                         # for word_id in multi_word_hash[multi]:
    #                         #     sop.insert_poem_wordnet(cursor, db_cnx, poem_id, word_id)
    #
    #                 words = re.sub('[^\w\s]', '', line).strip().split(" ")
    #                 for word in words:
    #                     word = word.lower()
    #                     if word not in word_hash:
    #                         # for word_id in word_hash[word]:
    #                         #     print("word:", word, "word_id:", word_id)
    #                         #     sop.insert_poem_wordnet(cursor, db_cnx, poem_id, word_id)
    #                         word_id = wn.insert_non_wordnet(cursor, db_cnx, word)
    #                         sop.insert_poem_non_wordnet(cursor, db_cnx, poem_id, word_id)
    #
    #
    #             # for line in poem_lines:
    #             #     sop.handle_line(cursor, db_cnx, line, poem_id)
    #     except Exception as e:
    #         print(e)
    #         exception_files.append(entry.path)
    #     print(count)
    #     count += 1
    #
    # print(exception_files)
    # for i in range(4652, 5050):
    #     cursor.execute(select_poet_stmt, (i,))
    #     poet_url = cursor.fetchone()[0]
    #     file_name = poet_url.split("/")[4]
    #     with open(f"data/poets/{file_name}.json", 'r') as p_file:
    #         poet_json = json.load(p_file)
    #     if 'attrs' in poet_json.keys():
    #         if 'Region:' in poet_json['attrs'].keys():
    #             regions = poet_json['attrs']['Region:']
    #             for region in regions:
    #                 print(f"Inserting: id:{i} author:{file_name} -> {region}")
    #                 cursor.execute(f"""SELECT id FROM region """
    #                                f"""WHERE name=%(name)s;""", {'name': region})
    #                 region_row = cursor.fetchone()
    #                 region_id = ""
    #                 if region_row:
    #                     region_id = region_row[0]
    #                 else:
    #                     cursor.execute(f"""INSERT INTO region (name) VALUES (%s);""", [region])
    #                     cursor.execute(f"""SELECT id FROM region """
    #                                    f"""WHERE name=%(name)s;""", {'name': region})
    #                     region_id = cursor.fetchone()[0]
    #
    #                 cursor.execute(f"""INSERT INTO isfrom (poet_id, region_id) """
    #                                f"""VALUES (%s, %s);""", (i, region_id))
    #                 db_cnx.commit()
    #         if 'School/Period:' in poet_json['attrs'].keys():
    #             schools = poet_json['attrs']['School/Period:']
    #             for school in schools:
    #                 print(f"Inserting: {file_name} -> {school}")
    #                 cursor.execute(f"""SELECT id FROM school """
    #                                f"""WHERE name=%(name)s;""", {'name': school})
    #                 school_row = cursor.fetchone()
    #                 school_id = ""
    #                 if school_row:
    #                     school_id = school_row[0]
    #                 else:
    #                     cursor.execute(f"""INSERT INTO school(name) VALUES (%s);""", [school])
    #                     cursor.execute(f"""SELECT id FROM school """
    #                                    f"""WHERE name=%(name)s;""", {'name': school})
    #                     school_id = cursor.fetchone()[0]
    #
    #                 cursor.execute(f"""INSERT INTO inschool (poet_id, school_id) """
    #                                f"""VALUES (%s, %s);""", (i, school_id))
    #                 db_cnx.commit()

    cursor.close()


def get_db_cnx():
    # establish a connection with the database
    # and create a cursor
    return connect_to_db(_DB_HOST, _DB_USER, _DB_PASSWORD, _DB_NAME)


def process_data(scrape, url, key, split_key_char, directory, alter_file_name):
    data = scrape(url.strip("\n"))
    if data:
        file_name_arr = data[key].lower().split(split_key_char)
        if alter_file_name:
            file_name_arr = alter_file_name(file_name_arr)
        file_name = "-".join(file_name_arr)
        with open(f"data/{directory}/{file_name}.json", "w") as f:
            print(f"writing file: {file_name}.json")
            f.write(json.dumps(data).__str__())
        return data


def process_poet(url):
    # scrape poet's page's html
    poet = scrape_poet(url.strip("\n"))
    poet_url = poet["url"].split("/")
    file_name = poet_url[4]
    with open(f"data/poets/{file_name}.json", "w") as p_file:
        print(f"writing file: {file_name}.json")
        p_file.write(json.dumps(poet).__str__())
    return poet


def process_poem(url):
    # scrape poet's page's html
    poem = scrape_poem(url.strip("\n"))

    if poem:
        key = poem["url"].split("/")
        poem_id = ""
        poem_title = ""

        if len(key) > 6:
            poem_id = key[5]
            poem_title = key[6]
        else:
            poem_id = key[4]
            poem_title = key[5]

        poem_title = poem_title.strip("-")
        file_name = f"{poem_title}-{poem_id}"
        with open(f"data/poems/{file_name}.json", "w") as p_file:
            print(f"writing file: {file_name}.json")
            p_file.write(json.dumps(poem).__str__())

    return poem


if __name__ == "__main__":
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(main(loop))
    main()
    # db_cnx = get_db_cnx()`
    # cursor = db_cnx.cursor()
    # poet = process_poet("https://www.poetryfoundation.org/poets/asiya-wadud")
    # insert_record(db_cnx, cursor, poet)
