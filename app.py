
from flask import Flask, render_template, request, abort, jsonify

app = Flask(__name__)

@app.route('/post', methods=["POST"])
def testpost():
     input_json = request.get_json(force=True)
     dictToReturn = {'MAC_ADD':input_json['MAC_ADD'], 'Staff_ID': input_json['Staff_ID']}
     #once data is recieved call the api
     return jsonify(dictToReturn)


@app.route('/')
def home():
    return render_template("index.html", beaconMacAaddress="2C:54:91:88:C9:E3", beaconLocation="SR3B", beaconTimestamp="17-09-21 12:00:17")

if __name__ == '__main__':

    app.run(host='0.0.0.0', port=5000)