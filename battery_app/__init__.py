from flask import Flask

app = Flask(__name__,  instance_path='C:/Users/gorob/PycharmProjects/PythonDyplomaProject/instance')
app.config['DEBUG'] = True


#blueprints
app.config.from_object(__name__)