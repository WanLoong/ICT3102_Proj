
from flask import Flask, render_template, request, abort, jsonify
import sqlite3
import time
import json

app = Flask(__name__)
OLD_DURATION = 20  # Period of beacons to keep


@app.route('/post', methods=["POST"])
def beaconPost():
     # input_json = request.get_json(force=True)
     # dictToReturn = {'MAC_ADD':input_json['MAC_ADD'],  "RSSI" :input_json['RSSI'] , 'Staff_ID': input_json['Staff_ID']}
     #once data is recieved call the api

     input_json = request.get_json(force=True)
     #retrieve a list of beacon objects
     beaconObjList = {"Beacon" : input_json}
     # Store the beacon list
     staff_id = int(beaconObjList['Beacon'][0]['STAFF_ID'])
     if staff_id > 1:
         staff_id = 1
     store_beacon_list(beaconObjList['Beacon'][0], staff_id=staff_id)
     for data in beaconObjList["Beacon"]:
        print(data)
     return jsonify(beaconObjList)


def store_beacon_list(beaconList, staff_id=0):
    current_timestamp = int(time.time())
    old_timestamp = current_timestamp-OLD_DURATION
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
    sql = "SELECT * FROM staff_"+staff_id+" WHERE timestamp BETWEEN ? AND ?"
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
    return jsonify(retrieve_all_staff_beacons())

@app.route('/')
def home():
    first_staff, second_staff, first_staff_timestamp, second_staff_timestamp = retrieve_all_staff_beacons()
    return render_template("index.html", beaconMacAddress=first_staff['MAC_ADD'], beaconRSSI=first_staff['RSSI'],
                           beaconTimestamp=first_staff_timestamp, beacon2MacAddress=second_staff['MAC_ADD'],
                           beacon2RSSI=second_staff['RSSI'], beacon2Timestamp=second_staff_timestamp)

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5000, debug=True)