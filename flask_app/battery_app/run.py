from flask_app.battery_app import socketio, app

socketio.run(app, host='127.0.0.1', port = 5008, debug=True,allow_unsafe_werkzeug=True)