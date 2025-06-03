import os
from logging.handlers import SMTPHandler
from urllib import request
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_babel import Babel
import newrelic.agent
from flask_migrate import Migrate
from redis import Redis
from flask_mqtt import Mqtt
from flask_socketio import SocketIO
from battery_app.bat_analizer import views as views
from battery_app.bat_analizer.views import user, articles
from elasticsearch import Elasticsearch
from flask_mail import Mail


#elasticsearch instance
es = Elasticsearch('https://192.168.1.6:9200/',
                   ca_certs='C:\Users\gorob\elasticsearch-9.0.1/config/certs/http_ca.crt',
 verify_certs=False,basic_auth=("elastic", ''))
es.indices.create(index='articls', ignore=400)


#app monitoring with New relic
newrelic.agent.initialize('newrelic.ini')

#languages
ALLOWED_LANGUAGES = {
 'en': 'English',
 'uk': 'Ukrainian',
}

#app instance creation
app = Flask(__name__,  instance_path='C:/Users/gorob/PycharmProjects/PythonDyplomaProject/instance')

#configuration variabls
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] ='sqlite:////tmp/battery_app.db'
app.config['LOG_FILE'] = 'application.log'
app.config['MQTT_BROKER_URL'] = 'io.adafruit.com'
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_USERNAME'] = 'Hor'
app.config['MQTT_PASSWORD'] = ''
app.config['MQTT_KEEPALIVE'] = 5
app.config['MQTT_TLS_ENABLED'] = False
app.config['MQTT_CLEAN_SESSION'] = False
app.config['OPENAI_KEY'] = ''
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'admin'
app.config['MAIL_PASSWORD'] = ''
app.config['MAIL_DEFAULT_SENDER'] = ('Sender', 'gorobchenkotatyana16@gmail.com')
app.config.from_object(__name__)

#mqtt
mqtt = Mqtt(app)
socketio = SocketIO()

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


#DB creation
db = SQLAlchemy(app)
with app.app_context():
 db.create_all()

#migration db creation
migration = Migrate(app, db)

# admin object creation
admin = Admin(app, index_view=views.MyAdminIndexView())
admin.add_view(views.UserAdminView(views.User, db.session))

#blueprints registration
app.register_blueprint(user)
app.register_blueprint (articles)


#languoges regulation
babel = Babel(app)

def get_locale():
 return request.accept_languages.best_match(ALLOWED_LANGUAGES.keys())

babel.init_app(app, locale_selector=get_locale)

#setup coocie
redis = Redis()

#class to wrap data and time formatting
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

#globals
app.jinja_env.globals['momentjs'] = momentjs

#app factory
def create_app(alt_config={}):
    app = Flask(__name__, template_folder=alt_config.get('TEMPLATE_FOLDER', 'templates'))
    app.config['UPLOAD_FOLDER'] =os.path.realpath('.') + '/battery_app/static/uploads'
    app.config['SQLALCHEMY_DATABASE_URI'] ='sqlite:////tmp/test.db'
    app.config['WTF_CSRF_SECRET_KEY'] = 'random key for form'
    app.config['LOG_FILE'] = 'application.log'
    app.config.update(alt_config)
    if not app.debug:
        import logging
        from logging import FileHandler, Formatter
        from logging.handlers import SMTPHandler
        file_handler = FileHandler(app.config['LOG_FILE'])
        app.logger.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        file_handler.setFormatter(Formatter('%(asctime)s %(levelname)s:%(message)s ''[in %(pathname)s:%(lineno)d]'))
        app.secret_key = 'some_random_key'
    return app

def create_db(app):
    db.init_app(app)
    with app.app_context():
       db.create_all()
       return db