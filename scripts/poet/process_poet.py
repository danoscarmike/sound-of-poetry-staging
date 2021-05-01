import json

from scripts.poet.scrape_poet import scrape_poet


def process_poet(url):
    # scrape poet's page's html
    poet = scrape_poet(url.strip("\n"))
    poet_url = poet["url"].split("/")
    file_name = poet_url[4]
    with open(f"data/poets/{file_name}.json", "w") as p_file:
        print(f"writing file: {file_name}.json")
        p_file.write(json.dumps(poet).__str__())
    return poet


def process_poet_attributes(cursor, db_cnx):
    # all_regions = []
    # all_schools = []
    # poet_regions = {}
    # poet_schools = {}
    select_poet_stmt = f"""SELECT url FROM poet WHERE id=%s;"""
    for i in range(4652, 5050):
        cursor.execute(select_poet_stmt, (i,))
        poet_url = cursor.fetchone()[0]
        file_name = poet_url.split("/")[4]
        with open(f"data/poets/{file_name}.json", 'r') as p_file:
            poet_json = json.load(p_file)
        if 'attrs' in poet_json.keys():
            if 'Region:' in poet_json['attrs'].keys():
                regions = poet_json['attrs']['Region:']
                for region in regions:
                    print(f"Inserting: id:{i} author:{file_name} -> {region}")
                    cursor.execute(f"""SELECT id FROM region """
                                   f"""WHERE name=%(name)s;""", {'name': region})
                    region_row = cursor.fetchone()
                    region_id = ""
                    if region_row:
                        region_id = region_row[0]
                    else:
                        cursor.execute(f"""INSERT INTO region (name) VALUES (%s);""", [region])
                        cursor.execute(f"""SELECT id FROM region """
                                       f"""WHERE name=%(name)s;""", {'name': region})
                        region_id = cursor.fetchone()[0]

                    cursor.execute(f"""INSERT INTO isfrom (poet_id, region_id) """
                                   f"""VALUES (%s, %s);""", (i, region_id))
                    db_cnx.commit()
            if 'School/Period:' in poet_json['attrs'].keys():
                schools = poet_json['attrs']['School/Period:']
                for school in schools:
                    print(f"Inserting: {file_name} -> {school}")
                    cursor.execute(f"""SELECT id FROM school """
                                   f"""WHERE name=%(name)s;""", {'name': school})
                    school_row = cursor.fetchone()
                    school_id = ""
                    if school_row:
                        school_id = school_row[0]
                    else:
                        cursor.execute(f"""INSERT INTO school(name) VALUES (%s);""", [school])
                        cursor.execute(f"""SELECT id FROM school """
                                       f"""WHERE name=%(name)s;""", {'name': school})
                        school_id = cursor.fetchone()[0]

                    cursor.execute(f"""INSERT INTO inschool (poet_id, school_id) """
                                   f"""VALUES (%s, %s);""", (i, school_id))
                    db_cnx.commit()