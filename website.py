from flask import Flask
from flask import render_template
from flask import make_response
from flask import jsonify

from datetime import datetime
from datetime import timezone
import functools
import json

from cloudlog import Cloudlog

app = Flask(__name__)
app.config.from_pyfile('config.py')

db = Cloudlog(app.config)

def get_current_status():
    data = db.get_cat()
    return {
        "Current Frequency": data['frequency'],
        "Current Mode": data['mode']
    }

def get_on_air():
    data = db.get_cat()
    if data['timestamp'] == 0:
        return False
    return True

def get_holding_cache_time():
    now = datetime.utcnow().replace(tzinfo=timezone.utc)
    print(str(app.config['COUNTDOWN_END'].timestamp() - now.timestamp()))
    if (app.config['COUNTDOWN_END'].timestamp() - now.timestamp()) < 7200:
        return 60
    else:
        return 7200

def cache(age=60):
    def decorator(f):
        @functools.wraps(f)
        def inner(*args, **kwargs):
            response = make_response(f(*args, **kwargs))
            response.headers['CACHE-CONTROL'] =  "public, max-age=%d" % (age,)
            return response
        return inner
    return decorator

@cache(get_holding_cache_time())
def holding():
    return render_template('holding.html', config=app.config)

@app.route("/api/getstatus")
@cache(10)
def getstatus():
    return jsonify({
        "status": get_current_status(),
        "onair": get_on_air(),
        "contacts": db.count_qsos(),
        "refresh-in": 10000
        })

@app.route("/api/getqsos/since/<timestamp>")
@cache(10)
def getqsossince(timestamp):

    dt = datetime.fromtimestamp(int(timestamp))
    data = db.get_10_qsos_since(dt)
    last_qso_timestamp = 0
    if len(data) > 0:
        last_qso_timestamp = int(data[len(data)-1]['datetime'].timestamp())

    for qso in data:
        qso['date'] = str(qso['datetime'].date())
        qso['time'] = str(qso['datetime'].strftime("%H:%M:%S"))

    return jsonify({
        "qsos": data,
        "last": last_qso_timestamp,
        "refresh-in": 10000
        })

@app.route("/live")
@cache(600)
def live():
    latest = db.get_last_10_qsos()
    last_qso_timestamp = 0
    if len(latest) > 0:
        last_qso_timestamp = int(latest[0]['datetime'].timestamp())
    return render_template('live.html',
        onair=get_on_air(),
        contacts=latest,
        contact_count=db.count_qsos(),
        status=get_current_status(),
        last_qso_timestamp=last_qso_timestamp)

@app.route("/")
def hello():
    #return live()
    return holding()