from my_app import app
from my_app.bat_analizer.models import MESSAGES

@app.route('/')
@app.route('/hello')
def hello_world():
 return MESSAGES['default']
