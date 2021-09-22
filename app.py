
from flask import Flask, render_template, request, abort, jsonify

app = Flask(__name__)


@app.route('/post', methods=["POST"])
def testpost():
     # input_json = request.get_json(force=True)
     # dictToReturn = {'MAC_ADD':input_json['MAC_ADD'],  "RSSI" :input_json['RSSI'] , 'Staff_ID': input_json['Staff_ID']}
     #once data is recieved call the api

     input_json = request.get_json(force=True)
     #retrieve a list of beacon objects
     beaconObjList = {"Beacon" : input_json['Beacon']}
     for data in beaconObjList["Beacon"]:
        print(data)
     return jsonify(beaconObjList)

@app.route('/extractbeacon', methods=["GET"])
def extract_beacon():
    if request.method == "GET":
        staff_id = request.args.get("staff_id")
        start_time = request.args.get("start_time")
        end_time = request.args.get("end_time")

        return jsonify({
            "staff_id": staff_id,
            "start_time": start_time,
            "end_time": end_time
        })


@app.route('/')
def home():
    return render_template("index.html", beaconMacAaddress="2C:54:91:88:C9:E3", beaconLocation="SR3C", beaconTimestamp="17-09-21 12:00:17")

if __name__ == '__main__':

    app.run(host='0.0.0.0', port=5000)