from sqlalchemy import func, insert
from battery_app import mqtt, db, socketio
from battery_app.bat_analizer.models import Data, Battery

@socketio.on('unsubscribe')
def handle_unsubscribe():
    mqtt.unsubscribe()
    print('Unsubscribe!')

@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    cycle = 0
    time = 0
    data = dict(topic=message.topic, payload=message.payload.decode())
    socketio.emit('mqtt_message', data=data)
    print(f'Data {data.items()}')
    serial_number = data.get("topic")
    serial_number = serial_number.rsplit('/')
    serial_number = serial_number[2]
    payload = data.get("payload")
    payload = payload.rsplit('"')
    for word in payload:
        if word == 'time':
            if (str.isdigit(payload)):
                time = int(word)
                print(time)
        elif word == 'cycle':
            if (str.isdigit(payload)):
                cycle = int(word)
                print(cycle)
        else:
            print("No data")
    stmt = db.select(Battery.id).where(Battery.serial_number==serial_number)
    bat_id = db.session.execute(stmt)
    db.session.execute(
        insert(Data).values(timestamp=func.now()).execution_options(render_nulls=True),
        {"time": time, "cycle": cycle, "bat_id": bat_id},
    )
    db.session.flush()
    db.session.commit()


@mqtt.on_log()
def handle_logging(client, userdata, level, buf):
    print(level, buf)