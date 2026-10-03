import flask
import serial

app = flask.Flask(__name__)

ser = serial.Serial("/dev/ttyACM0", baudrate=9600)


@app.route("/api/led/on")
def led_on():
    ser.write(b"LED ON\n")
    return ser.readline().decode().strip()


@app.route("/api/led/off")
def led_off():
    ser.write(b"LED OFF\n")
    return ser.readline().decode().strip()


@app.route("/api/flash/<num_flashes>/<period_ms>")
def flash(num_flashes, period_ms):
    command = f"FLASH {num_flashes} {period_ms}\n"
    ser.write(command.encode())
    return ser.readline().decode().strip()


app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)