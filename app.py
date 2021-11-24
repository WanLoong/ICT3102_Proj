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
BEACON_LOCATIONS = {"DE69F34B12FB": "Lvl 1 Fire Fighting Lobby",
                    "D7EBDC5A92B9": "Lvl 1 Fire Fighting Lobby",
                    "C43298D4E8B2": "Lvl 1 Fire Fighting Lobby",
                    "F3B1B290486D": "Student Club",
                    "D975F28047B3": "Foyer",
                    "DB45ECD1DF33": "Foyer",
                    "ECAC7EDCDF93": "LT2A Lobby",
                    "D7BFA52AA899": "LT2A Lobby",
                    "D249FA5CECA0": "LT2B Lobby",
                    "FDC14F4F7ED4": "LT2B Lobby",
                    "CC1DC599C10B": "LT2B Lobby",
                    "D4A58BB6DCAD": "SR2A Lobby",
                    "E0A4F1CBF31C": "SR2A Lobby",
                    "CC2F5B7F9677": "SR2A Lobby",
                    "DFBC60C04884": "SR2A Lobby",
                    "E180324B7C78": "SR2A Lobby",
                    "F5C3E08B32D5": "SR2A Lobby",
                    "D48A42D20BE1": "Lvl 2 Lift Lobby",
                    "C343BC7CCF92": "Lvl 2 Lift Lobby",
                    "D1B4D89B73A7": "Lvl 4 Fire fighting Lobby",
                    "EC4FB474B11C": "Lvl 4 Fire fighting Lobby",
                    "F3514C561E0B": "SR4G Lobby",
                    "D2622D4F854E": "SR4G Lobby",
                    "CF1EBCE74C9C": "SR4G Lobby",
                    "CCE3EFDACB52": "SR4A Lobby",
                    "DA2D5CCB9488": "SR4G Lobby",
                    "D470075FDA87": "SR4G Lobby",
                    "DF037DD86E53": "SR4H Lobby",
                    "CCF3E1C929FD": "SR4G Lobby",
                    "E1EB15371D96": "SR4E Lobby",
                    "F112F03A720D": "SR4G Lobby",
                    "ED23CBDF8B80": "SR4G Lobby",
                    "FA55EB6C23B4": "SR4A Lobby",
                    "D20FB4E0B1D5": "SR4A Lobby",
                    "C6D01D6A3FF4": "Lvl 4 Lift Lobby",
                    "F4D13305DE3A": "Lvl 4 Lift Lobby",
                    "D92C9A57F7CB": "SR5D Lobby",
                    "FDF4813F84DB": "Lvl 5 Fire fighting Lobby",
                    "EB3E5754BFBB": "SR5F Lobby",
                    "DEE4570CB343": "SR5H Lobby",
                    "F744E95AFEB4": "SR5D Lobby",
                    "EED4DE089809": "SR5C Lobby",
                    "F1E0D560AEFA": "Lvl 5 Lift Lobby",
                    "E4AEB8791C91": "Lvl 5 Lift Lobby",
                    "C53B43C6340A": "Lvl 5 Lift Lobby",
                    "C153830706A5": "Lvl 5 Lift Lobby",
                    "EF708283108E": "Lvl 5 Fire fighting Lobby",
                    "FED95EF5D4C7": "Lvl 5 Fire fighting Lobby",
                    "F1D6EC1553CD": "SR5F Lobby",
                    "E7F82CE7B318": "SR5C Lobby",
                    "DF69B5035B33": "Lvl 6 Fire fighting Lobby",
                    "F3FBA538EC62": "Lvl 6 Fire fighting Lobby",
                    "DA17557BCB38": "SR6A Lobby",
                    "F85E688B4B72": "SR6B Lobby",
                    "F28C771A175B": "SR6H Lobby",
                    "E1A0FBAEA144": "Lvl 6 Fire fighting Lobby",
                    "ECE7966F39E9": "SR6E Lobby",
                    "C22D0D9E578C": "SR6H Lobby",
                    "DF1D0A9FE1E0": "SR6G Lobby",
                    "F40C85E05D70": "SR6H Lobby",
                    "EEF85E5BDCED": "SR6A Lobby",
                    "F68644A3A846": "SR6A Lobby",
                    "C48190F6DE4A": "SR6H Lobby",
                    "D17221428784": "SR6H Lobby",
                    "DDA334403026": "SR6H Lobby",
                    "C00123E26D45": "Lvl 6 Lift Lobby",
                    "ECA9A0061008": "Lvl 6 Lift Lobby",
                    "F798B9A7AC28": "ROOM 1",
                    "EB89094E2F11": "ROOM 2",
                    "DB6073C9C0A4": "ROOM 3",
                    "F32ED305DB62": "ROOM 4",
                    "C88FA9B10AE8": "ROOM 5",
                    "EAC3938DDA2": "Level 7 Fire fighting Lobby",
                    "D59761B61C6C": "Level 7 Fire fighting Lobby",
                    "DB7ADA9F387B": "Level 7 Fire fighting Lobby",
                    "CF8061AE8B38": "SR7B Lobby",
                    "EF20D5A8BD8": "SR7B",
                    "EB5F5BDD1443": "SR7C Lobby",
                    "CA4C2D0DA8BD": "SR7C Lobby",
                    "CBCE44CC874E": "SR7C",
                    "E268B2A4AE9A": "SR7C Lobby",
                    "CD5116F790EE": "SR7D Lobby",
                    "EC5D57A6C8F3": "SR7D Lobby",
                    "D6C01807A019": "SR7D",
                    "F511F9E15121": "SR7D",
                    "C4C4C1329EA2": "SR7D Lobby",
                    "E466B99CB95F": "SR7D Lobby",
                    "FB1868AB3E1B": "SR7E",
                    "F2BA496C4BD1": "SR7E Lobby",
                    "D319E655E91C": "SR7E Lobby",
                    "EBFA572D1DC2": "MR 7A",
                    "FDF33DAEE5A4": "MR 7A",
                    'D11DC16A4F98': "MR 7A",
                    "C2BF4E1F0E2A": "Level 7 Lift Lobby",
                    "C639BBBE3557": "Level 7 Lift Lobby",
                    "DB0896A9CC33": "Level 7 Lift Lobby",
                    # Issued Beacons
                    "EE2CD56C064D": "Issued Beacon 1",
                    "EE53E2BFC002": "Issued Beacon 2",
                    "Add1": "Default Test Location Value"}


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
        beacons.append({"MAC": item['MAC_ADD'], "RSSI": item['RSSI'], "timestamp": d[1]})
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
        first_staff_loc = BEACON_LOCATIONS[str(first_staff['MAC_ADD']).replace(":", "").replace("-", "").replace(" ", "")]
    except KeyError:
        first_staff_loc = "Unknown Location"
    try:
        second_staff_loc = BEACON_LOCATIONS[str(second_staff['MAC_ADD']).replace(":", "").replace("-", "").replace(" ", "")]
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
