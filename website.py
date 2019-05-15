from flask import Flask
from flask import render_template
from flask import make_response

from datetime import datetime
from datetime import timezone
import functools

app = Flask(__name__)
app.config.from_pyfile('config.py')

def temp_get_contacts():
    contacts = [
        {
            "datetime": datetime(2007, 12, 5, 10, 12, 4),
            "callsign": "TE5T",
            "frequency": "14.169",
            "mode": "USB",
            "report_sent": "59",
            "report_recv": "59"
        },
    ]

    return contacts

def temp_count_contacts():
    return 42

def get_current_status():
    return {
        "Current Frequency":"14.269MHz",
        "Current Mode": "USB"
    }

def get_on_air():
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

@app.route("/live")
@cache(60)
def live():
    return render_template('live.html',
        onair=get_on_air(),
        contacts=temp_get_contacts(),
        contact_count=temp_count_contacts(),
        status=get_current_status())

@app.route("/")
def hello():
    #return live()
    return holding()