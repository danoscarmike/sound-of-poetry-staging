import csv
import re
import string

import scripts.sop_sql as sop
import scripts.word_net_sql as wn


def filter_imagenet_images():
    with open('data/images_synsets_flickr.csv', mode='w') as flickr_csv:
        flickr_csv = csv.writer(flickr_csv, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        with open("data/images_synsets.csv") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            urls = []
            for row in csv_reader:
                if line_count == 0:
                    print(f'Column names are {", ".join(row)}')
                    line_count += 1
                else:
                    if "flickr.com" in row[3]:
                        row[1] = "1" + row[1]
                        flickr_csv.writerow(row)


def process_imagenet_images(cursor, db_cnx):
    cursor.execute(f"""SELECT * FROM imagenet_image_synset iis """
                   f"""WHERE iis.synsetid NOT IN (SELECT gms.synsetid FROM google_mid_synset gms);""")
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


def process_google_images(cursor, db_cnx):
    cursor.execute(f"""SELECT * FROM google_mid_imageid;""")
    rows = cursor.fetchall()
    row_hash = {}

    for row in rows:
        image_id = row[0]
        m_id = row[2]
        if row_hash.get(m_id):
            if len(row_hash[m_id]) < 7 and image_id not in row_hash[m_id]:
                row_hash[m_id].append(image_id)
        else:
            row_hash[m_id] = [image_id]

    for key, values in row_hash.items():
        for value in values:
            cursor.execute(f"""INSERT INTO google_mid_imageid_lean (m_id, image_id) VALUES (%s, %s);""", (key, value))
        db_cnx.commit()


def process_media_classes(cursor, db_cnx):
    non_wordnet_rows = wn.select_all_non_wordnet(cursor)
    non_wordnet_hash = {}
    word_exceptions = []

    for nwn in non_wordnet_rows:
        wordid = nwn[0]
        lemma = nwn[1]
        non_wordnet_hash[lemma] = wordid

    word_list = wn.select_all_words(cursor)
    multi_word_list = []

    for item in word_list:
        lemma = item[1]
        matches = re.findall(f"[\s{string.punctuation}]", lemma)
        if len(matches):
            multi_word_list.append(lemma)

    word_hash = {}
    multi_word_hash = {}

    for item in word_list:
        word_id = item[0]
        lemma = item[1]
        morph = item[2]
        matches = re.findall(f"[\s{string.punctuation}]", lemma)
        if len(matches):
            if morph:
                if morph in multi_word_hash:
                    multi_word_hash[morph].append(word_id)
                else:
                    multi_word_hash[morph] = [word_id]
            if lemma in multi_word_hash:
                multi_word_hash[lemma].append(word_id)
            else:
                multi_word_hash[lemma] = [word_id]
        else:
            if morph:
                if morph in word_hash:
                    word_hash[morph].append(word_id)
                else:
                    word_hash[morph] = [word_id]
            if lemma in word_hash:
                word_hash[lemma].append(word_id)
            else:
                word_hash[lemma] = [word_id]

    media_class_rows = sop.select_all_media_classes(cursor)

    for row in media_class_rows:
        m_id = row[0]
        name = row[1]

        for multi in multi_word_list:
            name = name.lower()
            if multi in name:
                matches = re.match(r"\b" + multi + r"\b", name)
                if matches:
                    name = re.sub(r"\b" + multi + r"\b", '', name)
                    values = multi_word_hash.get(multi)
                    if values:
                        for word_id in values:
                            wn.insert_media_class_wordnet(cursor, db_cnx, m_id, word_id)

        words = re.sub('[^\w\s-]', '', name).strip().split(" ")
        for word in words:
            word = word.lower()
            if word in word_hash:
                for word_id in word_hash[word]:
                    wn.insert_media_class_wordnet(cursor, db_cnx, m_id, word_id)
            elif word in non_wordnet_hash:
                word_id = non_wordnet_hash[word]
                wn.insert_media_class_non_wordnet(cursor, db_cnx, m_id, word_id)
            else:
                word_exceptions.append(word)
                wn.insert_non_wordnet(cursor, db_cnx, word)

    print(word_exceptions)