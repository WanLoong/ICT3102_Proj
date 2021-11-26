from flask import Flask, render_template, request, abort, jsonify
import sqlite3
import time
import json
from flask_compress import Compress

app = Flask(__name__)
COMPRESS_ALGORITHM = ['gzip']
COMPRESS_SIZE = 400
app.config['COMPRESS_ALGORITHM'] = COMPRESS_ALGORITHM
app.config['COMPRESS_MIN_SIZE'] = COMPRESS_SIZE
OLD_DURATION = 20  # Period of beacons to keep
Compress(app)
BEACON_LOCATIONS = {"DE69F34B12FB": {'level': '1', 'location': "Fire Fighting Lobby"},
                    "D7EBDC5A92B9": {'level': '1', 'location': "Fire Fighting Lobby"},
                    "C43298D4E8B2": {'level': '1', 'location': "Fire Fighting Lobby"},
                    "F3B1B290486D": {'level': '1', 'location': "Student Club"},
                    "D975F28047B3": {'level': '1', 'location': "Foyer"},
                    "DB45ECD1DF33": {'level': '1', 'location': "Foyer"},
                    "ECAC7EDCDF93": {'level': '2', 'location': "LT2A Lobby"},
                    "D7BFA52AA899": {'level': '2', 'location': "LT2A Lobby"},
                    "D249FA5CECA0": {'level': '2', 'location': "LT2B Lobby"},
                    "FDC14F4F7ED4": {'level': '2', 'location': "LT2B Lobby"},
                    "CC1DC599C10B": {'level': '2', 'location': "LT2B Lobby"},
                    "D4A58BB6DCAD": {'level': '2', 'location': "SR2A Lobby"},
                    "E0A4F1CBF31C": {'level': '2', 'location': "SR2A Lobby"},
                    "CC2F5B7F9677": {'level': '2', 'location': "SR2A Lobby"},
                    "DFBC60C04884": {'level': '2', 'location': "SR2A Lobby"},
                    "E180324B7C78": {'level': '2', 'location': "SR2A Lobby"},
                    "F5C3E08B32D5": {'level': '2', 'location': "SR2A Lobby"},
                    "D48A42D20BE1": {'level': '2', 'location': "Lift Lobby"},
                    "C343BC7CCF92": {'level': '2', 'location': "Lift Lobby"},
                    "D1B4D89B73A7": {'level': '4', 'location': "Fire fighting Lobby"},
                    "EC4FB474B11C": {'level': '4', 'location': "Fire fighting Lobby"},
                    "F3514C561E0B": {'level': '4', 'location': "SR4G Lobby"},
                    "D2622D4F854E": {'level': '4', 'location': "SR4G Lobby"},
                    "CF1EBCE74C9C": {'level': '4', 'location': "SR4G Lobby"},
                    "CCE3EFDACB52": {'level': '4', 'location': "SR4A Lobby"},
                    "DA2D5CCB9488": {'level': '4', 'location': "SR4G Lobby"},
                    "D470075FDA87": {'level': '4', 'location': "SR4G Lobby"},
                    "DF037DD86E53": {'level': '4', 'location': "SR4H Lobby"},
                    "CCF3E1C929FD": {'level': '4', 'location': "SR4G Lobby"},
                    "E1EB15371D96": {'level': '4', 'location': "SR4E Lobby"},
                    "F112F03A720D": {'level': '4', 'location': "SR4G Lobby"},
                    "ED23CBDF8B80": {'level': '4', 'location': "SR4G Lobby"},
                    "FA55EB6C23B4": {'level': '4', 'location': "SR4A Lobby"},
                    "D20FB4E0B1D5": {'level': '4', 'location': "SR4A Lobby"},
                    "C6D01D6A3FF4": {'level': '4', 'location': "Lift Lobby"},
                    "F4D13305DE3A": {'level': '4', 'location': "Lift Lobby"},
                    "D92C9A57F7CB": {'level': '5', 'location': "SR5D Lobby"},
                    "FDF4813F84DB": {'level': '5', 'location': "Fire fighting Lobby"},
                    "EB3E5754BFBB": {'level': '5', 'location': "SR5F Lobby"},
                    "DEE4570CB343": {'level': '5', 'location': "SR5H Lobby"},
                    "F744E95AFEB4": {'level': '5', 'location': "SR5D Lobby"},
                    "EED4DE089809": {'level': '5', 'location': "SR5C Lobby"},
                    "F1E0D560AEFA": {'level': '5', 'location': "Lift Lobby"},
                    "E4AEB8791C91": {'level': '5', 'location': "Lift Lobby"},
                    "C53B43C6340A": {'level': '5', 'location': "Lift Lobby"},
                    "C153830706A5": {'level': '5', 'location': "Lift Lobby"},
                    "EF708283108E": {'level': '5', 'location': "Fire fighting Lobby"},
                    "FED95EF5D4C7": {'level': '5', 'location': "Fire fighting Lobby"},
                    "F1D6EC1553CD": {'level': '5', 'location': "SR5F Lobby"},
                    "E7F82CE7B318": {'level': '5', 'location': "SR5C Lobby"},
                    "DF69B5035B33": {'level': '6', 'location': "Fire fighting Lobby"},
                    "F3FBA538EC62": {'level': '6', 'location': "Fire fighting Lobby"},
                    "DA17557BCB38": {'level': '6', 'location': "SR6A Lobby"},
                    "F85E688B4B72": {'level': '6', 'location': "SR6B Lobby"},
                    "F28C771A175B": {'level': '6', 'location': "SR6H Lobby"},
                    "E1A0FBAEA144": {'level': '6', 'location': "Fire fighting Lobby"},
                    "ECE7966F39E9": {'level': '6', 'location': "SR6E Lobby"},
                    "C22D0D9E578C": {'level': '6', 'location': "SR6H Lobby"},
                    "DF1D0A9FE1E0": {'level': '6', 'location': "SR6G Lobby"},
                    "F40C85E05D70": {'level': '6', 'location': "SR6H Lobby"},
                    "EEF85E5BDCED": {'level': '6', 'location': "SR6A Lobby"},
                    "F68644A3A846": {'level': '6', 'location': "SR6A Lobby"},
                    "C48190F6DE4A": {'level': '6', 'location': "SR6H Lobby"},
                    "D17221428784": {'level': '6', 'location': "SR6H Lobby"},
                    "DDA334403026": {'level': '6', 'location': "SR6H Lobby"},
                    "C00123E26D45": {'level': '6', 'location': "Lift Lobby"},
                    "ECA9A0061008": {'level': '6', 'location': "Lift Lobby"},
                    "F798B9A7AC28": {'level': '6', 'location': "ROOM 1"},
                    "EB89094E2F11": {'level': '6', 'location': "ROOM 2"},
                    "DB6073C9C0A4": {'level': '6', 'location': "ROOM 3"},
                    "F32ED305DB62": {'level': '6', 'location': "ROOM 4"},
                    "C88FA9B10AE8": {'level': '6', 'location': "ROOM 5"},
                    "EAC3938DDA2": {'level': '7', 'location': "Fire fighting Lobby"},
                    "D59761B61C6C": {'level': '7', 'location': "Fire fighting Lobby"},
                    "DB7ADA9F387B": {'level': '7', 'location': "Fire fighting Lobby"},
                    "CF8061AE8B38": {'level': '7', 'location': "SR7B Lobby"},
                    "EF20D5A8BD8": {'level': '7', 'location': "SR7B"},
                    "EB5F5BDD1443": {'level': '7', 'location': "SR7C Lobby"},
                    "CA4C2D0DA8BD": {'level': '7', 'location': "SR7C Lobby"},
                    "CBCE44CC874E": {'level': '7', 'location': "SR7C"},
                    "E268B2A4AE9A": {'level': '7', 'location': "SR7C Lobby"},
                    "CD5116F790EE": {'level': '7', 'location': "SR7D Lobby"},
                    "EC5D57A6C8F3": {'level': '7', 'location': "SR7D Lobby"},
                    "D6C01807A019": {'level': '7', 'location': "SR7D"},
                    "F511F9E15121": {'level': '7', 'location': "SR7D"},
                    "C4C4C1329EA2": {'level': '7', 'location': "SR7D Lobby"},
                    "E466B99CB95F": {'level': '7', 'location': "SR7D Lobby"},
                    "FB1868AB3E1B": {'level': '7', 'location': "SR7E"},
                    "F2BA496C4BD1": {'level': '7', 'location': "SR7E Lobby"},
                    "D319E655E91C": {'level': '7', 'location': "SR7E Lobby"},
                    "EBFA572D1DC2": {'level': '7', 'location': "MR 7A"},
                    "FDF33DAEE5A4": {'level': '7', 'location': "MR 7A"},
                    'D11DC16A4F98': {'level': '7', 'location': "MR 7A"},
                    "C2BF4E1F0E2A": {'level': '7', 'location': "Lift Lobby"},
                    "C639BBBE3557": {'level': '7', 'location': "Lift Lobby"},
                    "DB0896A9CC33": {'level': '7', 'location': "Lift Lobby"},
                    # Issued Beacons
                    "EE2CD56C064D": {'level': 'Unknown', 'location': "Issued Beacon 1"},
                    "EE53E2BFC002": {'level': 'Unknown', 'location': "Issued Beacon 2"},
                    "Add1": {'level': 'Unknown', 'location': "Default Test Location Value"}}


@app.route('/post', methods=["POST"])
def beaconPost():
    # input_json = request.get_json(force=True)
    # dictToReturn = {'MAC_ADD':input_json['MAC_ADD'],  "RSSI" :input_json['RSSI'] , 'Staff_ID': input_json['Staff_ID']}
    # once data is received call the api

    input_json = request.get_json(force=True)
    # retrieve a list of beacon objects
    beaconObjList = {"Beacon": input_json}
    # Store the beacon list
    staff_id = int(beaconObjList['Beacon'][0]['STAFF_ID'])
    if staff_id > 1:
        staff_id = 1
    elif staff_id < 0:
        staff_id = 0
    store_beacon_list(beaconObjList['Beacon'][0], staff_id=staff_id)
    return "1"


def store_beacon_list(beaconList, staff_id=0):
    current_timestamp = int(time.time())
    old_timestamp = current_timestamp - OLD_DURATION
    conn = sqlite3.connect("staff_db.sqlite")
    cur = conn.cursor()
    sql = f'INSERT INTO staff_' + str(staff_id) + f' (beacons, timestamp) VALUES (?, ?)'
    cur.execute(sql, (json.dumps(beaconList), current_timestamp,))
    conn.commit()
    sql_remove_old = f'DELETE FROM staff_' + str(staff_id) + f' WHERE timestamp < ?'
    cur.execute(sql_remove_old, (old_timestamp,))
    conn.commit()
    conn.close()


@app.route('/extractbeacon', methods=["GET"])
def extract_beacon():
    if request.method == "GET":
        staff_id = request.args.get("staff_id")
        if int(staff_id) > 1:
            staff_id = 1
        elif int(staff_id) < 0:
            staff_id = 0
        start_time = request.args.get("start_time")
        end_time = request.args.get("end_time")
        data = retrieve_staff_beacons(staff_id, start_time, end_time)
        return data


def retrieve_staff_beacons(staff_id, start_timestamp, end_timestamp):
    conn = sqlite3.connect("staff_db.sqlite")
    cur = conn.cursor()
    sql = "SELECT * FROM staff_" + staff_id + " WHERE timestamp BETWEEN ? AND ?"
    cur.execute(sql, (start_timestamp, end_timestamp,))
    data = cur.fetchall()
    conn.close()
    beacons = []
    for d in data:
        item = json.loads(d[0])
        beacons.append({"level": BEACON_LOCATIONS[item['MAC_ADD']]['level'], "location": BEACON_LOCATIONS[item['MAC_ADD']]['location'], "timestamp": d[1]})
    return jsonify({"location": beacons})


def retrieve_all_staff_beacons():
    conn = sqlite3.connect("staff_db.sqlite")
    cur = conn.cursor()
    cur.execute("SELECT * FROM staff_0 ORDER BY timestamp DESC")
    staff_data = cur.fetchone()
    cur.execute("SELECT * FROM staff_1 ORDER BY timestamp DESC")
    staff_data_2 = cur.fetchone()
    conn.close()
    first_staff = json.loads(staff_data[0])
    second_staff = json.loads(staff_data_2[0])
    first_staff_timestamp = staff_data[1]
    second_staff_timestamp = staff_data_2[1]
    return first_staff, second_staff, first_staff_timestamp, second_staff_timestamp


@app.route('/update', methods=["GET"])
def update():
    first_staff, second_staff, first_staff_timestamp, second_staff_timestamp = retrieve_all_staff_beacons()
    try:
        first_staff_item = BEACON_LOCATIONS[str(first_staff['MAC_ADD']).replace(":", "").replace("-", "").replace(" ", "")]
        first_staff_loc = f"Level {first_staff_item['level']} {first_staff_item['location']}"
    except KeyError:
        first_staff_loc = "Unknown Location"
    try:
        second_staff_item = BEACON_LOCATIONS[str(second_staff['MAC_ADD']).replace(":", "").replace("-", "").replace(" ", "")]
        second_staff_loc = f"Level {second_staff_item['level']} {second_staff_item['location']}"
    except KeyError:
        second_staff_loc = "Unknown Location"
    return jsonify([{'MAC_ADD': first_staff['MAC_ADD'], 'RSSI': first_staff['RSSI'],
                     'timestamp': first_staff_timestamp, 'location': first_staff_loc},
                    {'MAC_ADD': second_staff['MAC_ADD'], 'RSSI': second_staff['RSSI'],
                     'timestamp': second_staff_timestamp, 'location': second_staff_loc}
                    ])


@app.route('/')
def home():
    first_staff, second_staff, first_staff_timestamp, second_staff_timestamp = retrieve_all_staff_beacons()
    try:
        first_staff_loc = BEACON_LOCATIONS[str(first_staff['MAC_ADD']).replace(":", "").replace("-", "").replace(" ", "")]
    except KeyError:
        first_staff_loc = "Unknown Location"
    try:
        second_staff_loc = BEACON_LOCATIONS[str(second_staff['MAC_ADD']).replace(":", "").replace("-", "").replace(" ", "")]
    except KeyError:
        second_staff_loc = "Unknown Location"
    return render_template("index.html", beaconMacAddress=first_staff['MAC_ADD'], beaconRSSI=first_staff['RSSI'],
                           beaconTimestamp=first_staff_timestamp, beacon2MacAddress=second_staff['MAC_ADD'],
                           beacon2RSSI=second_staff['RSSI'], beacon2Timestamp=second_staff_timestamp,
                           beaconLoc=first_staff_loc, beacon2Loc=second_staff_loc)

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5000, debug=True)
