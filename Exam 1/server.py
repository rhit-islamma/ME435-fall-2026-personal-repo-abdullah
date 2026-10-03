import flask
import serial

app = flask.Flask(__name__)

ser = serial.Serial("/dev/ttyACM0", baudrate=9600)


@app.route("/api/led/on")
def led_on():
    ser.write("LED ON\n".encode())
    response = ser.readline().decode()
    return response


@app.route("/api/led/off")
def led_off():
    ser.write("LED OFF\n".encode())
    response = ser.readline().decode()
    return response


@app.route("/api/flash/<num_flashes>/<period_ms>")
def flash(num_flashes, period_ms):
    command = "FLASH " + num_flashes + " " + period_ms + "\n"
    ser.write(command.encode())
    response = ser.readline().decode()
    return response


app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)