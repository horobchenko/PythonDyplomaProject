from flask_app.battery_app import socketio, app

if __name__ == '__main__':
    socketio.run(app, host='127.0.0.1', port = 50000, debug=False,allow_unsafe_werkzeug=True)