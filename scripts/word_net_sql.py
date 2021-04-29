def select_open_word_row(cursor, word):
    cursor.execute(f"""SELECT wordid FROM words WHERE lemma=%s;""", [word])
    return cursor.fetchone()


def select_morph_word_row(cursor, word):
    cursor.execute(f"""SELECT morphid FROM morphs WHERE morph=%s;""", [word])
    morph_row = cursor.fetchone()

    if morph_row:
        morph_id = morph_row[0]
        cursor.execute(f"""SELECT wordid FROM morphmaps WHERE morphid=%s;""", [morph_id])
        return cursor.fetchall()

    return None


def select_closed_word_row(cursor, word):
    cursor.execute(f"""SELECT wordid FROM closed_words WHERE lemma=%s;""", [word.lower()])
    return cursor.fetchone()


def insert_closed_word(cursor, db_cnx, word):
    closed_word_row = select_closed_word_row(cursor, word)

    if not closed_word_row:
        cursor.execute(f"""INSERT INTO closed_words(lemma) VALUES (%s);""", [word.lower()])
        db_cnx.commit()
        closed_word_row = select_closed_word_row(cursor, word)

    return closed_word_row[0]


def select_non_wordnet_row(cursor, word):
    cursor.execute(f"""SELECT wordid FROM non_wordnet WHERE lemma=%s;""", [word.lower()])
    return cursor.fetchone()


def insert_non_wordnet(cursor, db_cnx, word):
    non_wordnet_row = select_non_wordnet_row(cursor, word)

    if not non_wordnet_row:
        cursor.execute(f"""INSERT INTO non_wordnet(lemma) VALUES (%s);""", [word.lower()])
        db_cnx.commit()
        non_wordnet_row = select_non_wordnet_row(cursor, word)

    return non_wordnet_row[0]


def select_all_words(cursor):
    cursor.execute(f"""SELECT w.wordid, w.lemma, m.morph FROM words w LEFT JOIN morphology m ON w.wordid = m.wordid;""")
    return cursor.fetchall()


def select_all_non_wordnet(cursor):
    cursor.execute(f"""SELECT * FROM non_wordnet""")
    return cursor.fetchall()


def insert_media_class_non_wordnet(cursor, db_cnx, m_id, word_id):
    cursor.execute(f"""INSERT INTO media_class_non_wordnet VALUES (%s, %s) ON DUPLICATE KEY UPDATE m_id = %s, word_id = %s;""", (m_id, word_id, m_id, word_id))
    db_cnx.commit()


def insert_media_class_wordnet(cursor, db_cnx, m_id, word_id):
    cursor.execute(f"""INSERT INTO media_class_wordnet VALUES (%s, %s) ON DUPLICATE KEY UPDATE m_id = %s, word_id = %s;""", (m_id, word_id, m_id, word_id))
    db_cnx.commit()


def insert_tag_non_wordnet(cursor, db_cnx, tag_id, word_id):
    cursor.execute(f"""INSERT INTO tag_non_wordnet VALUES (%s, %s) ON DUPLICATE KEY UPDATE tag_id = %s, word_id = %s;""", (tag_id, word_id, tag_id, word_id))
    db_cnx.commit()


def insert_tag_wordnet(cursor, db_cnx, tag_id, word_id):
    cursor.execute(f"""INSERT INTO tag_wordnet VALUES (%s, %s) ON DUPLICATE KEY UPDATE tag_id = %s, word_id = %s;""", (tag_id, word_id, tag_id, word_id))
    db_cnx.commit()
