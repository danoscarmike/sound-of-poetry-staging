import json
import os
import re
import string

from scripts.poem.scrape_poem import scrape_poem
import scripts.sop_sql as sop
import scripts.word_net_sql as wn


def process_poem_json(url):
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


def process_poem(cursor, db_cnx):
    exception_files = []
    count = 1
    directory = r'/Users/cdhenry/Development/MCIT/550/Project/sound-of-poetry-staging/data/poems'

    for entry in os.scandir(directory):
        try:
            with open(entry.path, 'r') as p_file:
                print("Inserting path: ", entry.path)
                poem_json = json.load(p_file)
                url = poem_json['url']
                poet_url = poem_json['poet_url']
                title = poem_json['title']
                poem_lines = poem_json['poem_lines']
                poem_string = poem_json['poem_string']
                audio_url = poem_json['audio_url']
                video_url = poem_json['video_url']
                tags = poem_json['tags']

                sop.insert_poem(cursor, db_cnx, url, poet_url, title, poem_string, audio_url, video_url)
                poem_id = sop.select_poem_row(cursor, url)[0]

                for tag in tags:
                    sop.handle_tag(cursor, db_cnx, tag, poem_id)

                for line in poem_lines:
                    sop.handle_line(cursor, db_cnx, line, poem_id)
        except Exception as e:
            print(e)
            exception_files.append(entry.path)

        print(count)
        count += 1

    print(exception_files)


def process_tags(cursor, db_cnx):
    # media_class_rows = sop.select_all_media_classes(cursor)
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

    tags = sop.select_tags(cursor)

    for tag in tags:
        tag_id = tag[0]
        name = tag[1]

        for multi in multi_word_list:
            if multi in name:
                matches = re.match(r"\b" + multi + r"\b", name)
                if matches:
                    name = re.sub(r"\b" + multi + r"\b", '', name)
                    values = multi_word_hash.get(multi)
                    if values:
                        for word_id in values:
                            wn.insert_tag_wordnet(cursor, db_cnx, tag_id, word_id)

        words = re.sub('[^\w\s-]', '', name).strip().split(" ")

        for word in words:
            word = word.lower()
            if word in word_hash:
                for word_id in word_hash[word]:
                    wn.insert_tag_wordnet(cursor, db_cnx, tag_id, word_id)
            elif word in non_wordnet_hash:
                word_id = non_wordnet_hash[word]
                wn.insert_tag_non_wordnet(cursor, db_cnx, tag_id, word_id)
            else:
                word_exceptions.append(word)

    print(word_exceptions)


def process_words(cursor, db_cnx):
    exception_files = []

    directory = r'/Users/cdhenry/Development/MCIT/550/Project/sound-of-poetry-staging/data/poems'
    count = 1
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

    for entry in os.scandir(directory):
        try:
            with open(entry.path, 'r') as p_file:
                print("Inserting path: ", entry.path)
                poem_json = json.load(p_file)
                url = poem_json['url']
                poem_lines = poem_json['poem_lines']

                poem_id = sop.select_poem_row(cursor, url)[0]

                for line in poem_lines:
                    line.lower()
                    for multi in multi_word_list:
                        matches = re.match(r"\b" + multi + r"\b", line)
                        if matches:
                            line = re.sub(r"\b" + multi + r"\b", '', line)
                            values = multi_word_hash.get(multi)
                            if values:
                                for word_id in values:
                                    sop.insert_poem_wordnet(cursor, db_cnx, poem_id, word_id)

                    words = re.sub('[^\w\s]', '', line).strip().split(" ")
                    for word in words:
                        word = word.lower()
                        if word_hash.get(word):
                            for word_id in word_hash[word]:
                                sop.insert_poem_wordnet(cursor, db_cnx, poem_id, word_id)
                        else:
                            word_id = wn.insert_non_wordnet(cursor, db_cnx, word)
                            sop.insert_poem_non_wordnet(cursor, db_cnx, poem_id, word_id)

        except Exception as e:
            print(e)
            exception_files.append(entry.path)

        print(count)
        count += 1

    print(exception_files)


def process_stats(cursor, db_cnx):
    cursor.execute(f"""SELECT * FROM poem p;""")
    rows = cursor.fetchall()
    word_hash = {}

    for row in rows:
        poem_id = row[0]
        poem_string = row[4]
        words = re.split(' +', poem_string.translate(str.maketrans('', '', string.punctuation)))
        unique_word_count = 0

        for word in words:
            if not word_hash.get(word):
                word_hash[word] = 1
                unique_word_count = unique_word_count + 1

        # cursor.execute(f"""UPDATE poem_media_count p SET p.unique_word_count = %s WHERE p.poem_id = %s;""", (len(words), poem_id))
        # db_cnx.commit()

        cursor.execute(f"""UPDATE poem_media_count p SET p.unique_word_count = %s WHERE p.poem_id = %s;""", (unique_word_count, poem_id))
        db_cnx.commit()