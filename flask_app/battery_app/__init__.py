from logging.handlers import SMTPHandler
from flask_socketio import SocketIO
from urllib import request
import newrelic.agent
from flask import Flask
from flask_babel import Babel
from flask_mail import Mail
from flask_mqtt import Mqtt
from redis import Redis

#app instance creation
app = Flask(__name__)

#configuration variables
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] ='sqlite+pysqlite:///battery_analizer.db'
app.config['LOG_FILE'] = 'application.log'
app.config['MQTT_BROKER_URL'] = 'io.adafruit.com'
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_USERNAME'] = 'Hor'
app.config['MQTT_PASSWORD'] = ''
app.config['MQTT_KEEPALIVE'] = 5
app.config['MQTT_TLS_ENABLED'] = False
app.config['MQTT_CLEAN_SESSION'] = False
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'admin'
app.config['MAIL_PASSWORD'] = ''
app.config['MAIL_DEFAULT_SENDER'] = ('Sender', 'gorobchenkotatyana16@gmail.com')
app.config.from_object(__name__)

#####app monitoring#######
#app monitoring with New relic
#newrelic.agent.initialize('newrelic.ini')

##### errors handling######
#mail instance
mail = Mail(app)

#logging
if not app.debug:
    import logging
    from logging import FileHandler, Formatter
    file_handler = FileHandler(app.config['LOG_FILE'])
    app.logger.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    mail_handler = SMTPHandler(("smtp.gmail.com", 587),'hackyouall26@gmail.com', 'hackyouall26@gmail.com','Error occurred in your application',secure=())
    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler)
    for handler in [file_handler, mail_handler]:
        handler.setFormatter(Formatter('%(asctime)s %(levelname)s: %(message)s ''[in %(pathname)s:%(lineno)d]'))

#####languoges setting########
#languages
ALLOWED_LANGUAGES = {
 'en': 'English',
 'uk': 'Ukrainian',
}
babel = Babel(app)
def get_locale():
   return request.accept_languages.best_match(ALLOWED_LANGUAGES.keys())
babel.init_app(app, locale_selector=get_locale)

##########3data and time formatting###########
from markupsafe import Markup
class momentjs(object):
    def __init__(self, timestamp):
        self.timestamp = timestamp
    def render(self, format):
     return Markup( "<script>\n document.write(moment(\"%s\").%s);"
                       "\n</script>" % ( self.timestamp.strftime("%Y-%m-%dT%H:%M:%S"),format))
     def format(self, fmt):
        return self.render("format(\"%s\")" % fmt)
     def calendar(self):
      return self.render("calendar()")
     def fromNow(self):
        return self.render("fromNow()")
app.jinja_env.globals['momentjs'] = momentjs


########setup coocie#########3
redis = Redis()

######mqtt########3
#mqtt
mqtt = Mqtt(app)
socketio = SocketIO(app)