import csv
import json


def process_fsd_sounds():
    with open('data/sound/FSD50K_collection_eval.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                print(f'Column names are {", ".join(row)}')
                line_count += 1
            else:
                if ',' in row[1]:
                    labels = row[1].split(',')
                    audio_ids = row[2].split(',')
                    for i in range(0, len(labels)):
                        print(labels[i].replace('_', ' '), audio_ids[i])

                line_count += 1
        print(f'Processed {line_count} lines.')

    with open(F"data/FSD50K_class_info.json", 'r') as f:
        labels = json.load(f)
        print(len(labels.keys()))

    # with open(f"data/FSD50K_eval_clips_info.json", 'r') as f:
    #     clips = json.load(f)
    #     for key in clips.keys():
    #         clip = clips[key]


def process_google_audioset(cursor, db_cnx):
    with open('data/sound/google_balanced_train_segments.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count < 2:
                print(f'Column names are {", ".join(row)}')
                line_count += 1
            else:
                if ',' in row[3]:
                    audio_ids = row[3].split(',')
                    for i in range(0, len(audio_ids)):
                        cursor.execute(f"""INSERT INTO ytid_mid (ytid, m_id) """
                                       f"""VALUES (%s, %s);""", (row[0], audio_ids[i]))
                else:
                    cursor.execute(f"""INSERT INTO ytid_mid (ytid, m_id) """
                                   f"""VALUES (%s, %s);""", (row[0], row[3]))

                db_cnx.commit()
                line_count += 1
        print(f'Processed {line_count} lines.')