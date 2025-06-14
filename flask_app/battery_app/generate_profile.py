from werkzeug.middleware.profiler import ProfilerMiddleware
from flask_app.battery_app import app

app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions = [10])
app.run(debug=True)
