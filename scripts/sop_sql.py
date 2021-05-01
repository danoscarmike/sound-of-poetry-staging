import re
from . import word_net_sql as wn


def select_all_media_classes(cursor):
    cursor.execute(f"""SELECT * FROM media_class;""")
    return cursor.fetchall()


def insert_poem(cursor, db_cnx, url, poet_url, title, poem_string, audio_url, video_url):
    cursor.execute(
        f"""INSERT INTO poem(url,poet_url,title,poem_string,audio_url,video_url) VALUES (%s,%s,%s,%s,%s,%s);""",
        (url, poet_url, title, poem_string, audio_url, video_url))
    db_cnx.commit()


def select_poem_row(cursor, url):
    cursor.execute(f"""SELECT id FROM poem WHERE url=%(url)s;""", {'url': url})
    return cursor.fetchone()


def select_tag_row(cursor, name):
    cursor.execute(f"""SELECT id FROM tag WHERE name=%(name)s;""", {'name': name})
    return cursor.fetchone()


def select_tags(cursor):
    cursor.execute(f"""SELECT * FROM tag""")
    return cursor.fetchall()


def insert_tag(cursor, db_cnx, tag):
    cursor.execute(f"""INSERT INTO tag(name) VALUES (%s);""", [tag])
    db_cnx.commit()


def insert_istagged(cursor, db_cnx, poem_id, tag_id):
    cursor.execute(f"""INSERT INTO istagged(poem_id, tag_id) VALUES (%s, %s);""", (poem_id, tag_id))
    db_cnx.commit()


def select_taghas_openword_row(cursor, tag_id, word_id):
    cursor.execute(f"""SELECT * FROM taghas_openword WHERE tag_id=%s AND word_id=%s;""", (tag_id, word_id))
    return cursor.fetchone()


def insert_taghas_openword(cursor, db_cnx, tag_id, word_id):
    taghas_openword_row = select_taghas_openword_row(cursor, tag_id, word_id)

    if not taghas_openword_row:
        cursor.execute(f"""INSERT INTO taghas_openword(tag_id, word_id) VALUES (%s, %s);""", (tag_id, word_id))
        db_cnx.commit()
        taghas_openword_row = select_taghas_openword_row(cursor, tag_id, word_id)

    return taghas_openword_row[0]


def select_taghas_closedword_row(cursor, tag_id, word_id):
    cursor.execute(f"""SELECT * FROM taghas_closedword WHERE tag_id=%s AND word_id=%s;""", (tag_id, word_id))
    return cursor.fetchone()


def insert_taghas_closedword(cursor, db_cnx, tag_id, word_id):
    taghas_closedword_row = select_taghas_closedword_row(cursor, tag_id, word_id)

    if not taghas_closedword_row:
        cursor.execute(f"""INSERT INTO taghas_closedword(tag_id, word_id) VALUES (%s, %s);""", (tag_id, word_id))
        db_cnx.commit()
        taghas_closedword_row = select_taghas_closedword_row(cursor, tag_id, word_id)

    return taghas_closedword_row[0]


def select_poemhas_openword_row(cursor, word_id, poem_id):
    cursor.execute(f"""SELECT use_count FROM poemhas_openword WHERE word_id=%s AND poem_id=%s;""", (word_id, poem_id))
    return cursor.fetchone()


def insert_poemhas_openword(cursor, db_cnx, poem_id, word_id):
    poem_word_row = select_poemhas_openword_row(cursor, word_id, poem_id)
    if poem_word_row:
        use_count = poem_word_row[0]
        cursor.execute(
            f"""UPDATE poemhas_openword SET use_count = %s WHERE word_id=%s AND poem_id=%s;""",
            (use_count + 1, word_id, poem_id))
    else:
        cursor.execute(
            f"""INSERT INTO poemhas_openword(poem_id, word_id, use_count) VALUES (%s, %s, %s);""",
            (poem_id, word_id, 1))

    db_cnx.commit()


def select_poemhas_closedword_row(cursor, word_id, poem_id):
    cursor.execute(f"""SELECT use_count FROM poemhas_closedword WHERE word_id=%s AND poem_id=%s;""", (word_id, poem_id))
    return cursor.fetchone()


def insert_poemhas_closedword(cursor, db_cnx, poem_id, word_id):
    poem_word_row = select_poemhas_closedword_row(cursor, word_id, poem_id)

    if poem_word_row:
        use_count = poem_word_row[0]
        cursor.execute(
            f"""UPDATE poemhas_closedword SET use_count = %s WHERE word_id=%s AND poem_id=%s;""",
            (use_count + 1, word_id, poem_id))
    else:
        cursor.execute(
            f"""INSERT INTO poemhas_closedword(poem_id, word_id, use_count) VALUES (%s, %s, %s);""",
            (poem_id, word_id, 1))

    db_cnx.commit()


def select_poem_wordnet_row(cursor, word_id, poem_id):
    cursor.execute(f"""SELECT use_count FROM poem_wordnet WHERE word_id=%s AND poem_id=%s;""", (word_id, poem_id))
    return cursor.fetchone()


def insert_poem_wordnet(cursor, db_cnx, poem_id, word_id):
    poem_wordnet_row = select_poem_wordnet_row(cursor, word_id, poem_id)
    if poem_wordnet_row:
        use_count = poem_wordnet_row[0]
        cursor.execute(
            f"""UPDATE poem_wordnet SET use_count = %s WHERE word_id=%s AND poem_id=%s;""",
            (use_count + 1, word_id, poem_id))
    else:
            cursor.execute(
            f"""INSERT INTO poem_wordnet(poem_id, word_id, use_count) VALUES (%s, %s, %s);""",
            (poem_id, word_id, 1))

    db_cnx.commit()


def select_poem_non_wordnet_row(cursor, word_id, poem_id):
    cursor.execute(f"""SELECT use_count FROM poem_non_wordnet WHERE word_id=%s AND poem_id=%s;""", (word_id, poem_id))
    return cursor.fetchone()


def insert_poem_non_wordnet(cursor, db_cnx, poem_id, word_id):
    poem_wordnet_row = select_poem_non_wordnet_row(cursor, word_id, poem_id)
    if poem_wordnet_row:
        use_count = poem_wordnet_row[0]
        cursor.execute(
            f"""UPDATE poem_non_wordnet SET use_count = %s WHERE word_id=%s AND poem_id=%s;""",
            (use_count + 1, word_id, poem_id))
    else:
            cursor.execute(
            f"""INSERT INTO poem_non_wordnet(poem_id, word_id, use_count) VALUES (%s, %s, %s);""",
            (poem_id, word_id, 1))

    db_cnx.commit()


def handle_tag(cursor, db_cnx, tag, poem_id):
    tag_row = select_tag_row(cursor, tag)

    if not tag_row:
        insert_tag(cursor, db_cnx, tag)

    tag_id = select_tag_row(cursor, tag)[0]
    insert_istagged(cursor, db_cnx, poem_id, tag_id)

    words = re.sub(' +', ' ', re.sub('[^\w\s]', '', tag).strip()).split(" ")
    for word in words:
        word_row = wn.select_open_word_row(cursor, word)
        if word_row:
            word_id = word_row[0]
            insert_taghas_openword(cursor, db_cnx, tag_id, word_id)
        else:
            morph_word_row = wn.select_morph_word_row(cursor, word)
            if morph_word_row:
                for morph_word_id in morph_word_row:
                    insert_taghas_openword(cursor, db_cnx, tag_id, morph_word_id[0])
            else:
                closed_word_id = wn.insert_closed_word(cursor, db_cnx, word)
                insert_taghas_closedword(cursor, db_cnx, tag_id, closed_word_id)


def handle_line(cursor, db_cnx, line, poem_id):
    words = re.sub('[^\w\s]', '', line).strip().split(" ")
    for word in words:
        word_row = wn.select_open_word_row(cursor, word)
        if word_row:
            word_id = word_row[0]
            insert_poemhas_openword(cursor, db_cnx, poem_id, word_id)
        else:
            morph_word_row = wn.select_morph_word_row(cursor, word)
            if morph_word_row:
                for morph_word_id in morph_word_row:
                    insert_poemhas_openword(cursor, db_cnx, poem_id, morph_word_id[0])
            else:
                closed_word_id = wn.insert_closed_word(cursor, db_cnx, word)
                insert_poemhas_closedword(cursor, db_cnx, poem_id, closed_word_id)
