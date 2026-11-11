"""
Etch A Sketch - Pi side (runs on the Pi 5 + 7" screen).
Two rotary encoders draw. Mouse/touch picks color, width, RESET, SAVE.
Everything is sent over MQTT so the MATLAB GUI shows the same drawing.

Wiring (KY-040 encoders). Each 5-wire ribbon stays together on 5 pins in a row
(odd pin row). One GPIO per encoder is used as a power/ground pin (~1 mA, safe).
  X encoder: CLK=pin 11 (GPIO17), DT=pin 13 (GPIO27), SW=pin 15 (GPIO22),
             + = pin 17 (3.3V),    GND = pin 19 (GPIO10, set LOW in code)
  Y encoder: CLK=pin 31 (GPIO6),  DT=pin 33 (GPIO13), SW=pin 35 (GPIO19),
             + = pin 37 (GPIO26, set HIGH in code), GND = pin 39 (GND)

Messages (same both ways):
  "pots"  {"x": 0..1, "y": 0..1}   new pen position
  "color" a name from PEN_COLORS
  "width" 1..10
  "bg"    a name from BG_COLORS
  "reset"
  "save"
"""
import gpiozero as gz
import mqtt_helper as mh
import subprocess
import time
import tkinter
from tkinter import ttk

STEP = 0.01      # pen move per encoder click (drawing is 0..1)
WIDTH = 960      # drawing area in pixels (screen is 1024x600)
HEIGHT = 480

# Same names + colors as the MATLAB app
PEN_COLORS = {"Graphite": "#33363D", "Ocean": "#3D5A80", "Teal": "#2A9D8F",
              "Terracotta": "#E07A5F", "Plum": "#7B5E7B", "Olive": "#6A7F3F"}
BG_COLORS = {"Silver": "#E8E6E1", "Cream": "#F4EDE1", "Mint": "#DCEFE7",
             "Sky": "#DDE8F3", "Blush": "#F6E1DE", "Slate": "#3A3F47"}


class App:

    def __init__(self, root):
        self.x = 0.5
        self.y = 0.5
        self.color = "Graphite"
        self.width = 2

        # GUI (same style as Fisher's Tkinter example in mqtt_helper.py)
        root.title("Etch A Sketch")
        root.configure(bg="red")
        root.attributes("-fullscreen", True)
        root.bind("<Escape>", lambda event: root.destroy())

        self.canvas = tkinter.Canvas(root, width=WIDTH, height=HEIGHT, bg=BG_COLORS["Silver"])
        self.canvas.grid(row=0, column=0, columnspan=5, padx=32, pady=10)

        reset_button = ttk.Button(root, text="RESET")
        reset_button.grid(row=1, column=0)
        reset_button["command"] = lambda: self.reset(True)

        self.color_box = ttk.Combobox(root, values=list(PEN_COLORS), state="readonly", width=10)
        self.color_box.set(self.color)
        self.color_box.grid(row=1, column=1)
        self.color_box.bind("<<ComboboxSelected>>", lambda event: self.set_color(self.color_box.get(), True))

        self.width_box = ttk.Spinbox(root, from_=1, to=10, width=4)
        self.width_box.set(self.width)
        self.width_box.grid(row=1, column=2)
        self.width_box["command"] = lambda: self.set_width(int(self.width_box.get()), True)

        self.bg_box = ttk.Combobox(root, values=list(BG_COLORS), state="readonly", width=10)
        self.bg_box.set("Silver")
        self.bg_box.grid(row=1, column=3)
        self.bg_box.bind("<<ComboboxSelected>>", lambda event: self.set_bg(self.bg_box.get(), True))

        save_button = ttk.Button(root, text="SAVE")
        save_button.grid(row=1, column=4)
        save_button["command"] = lambda: self.save(True)

        # MQTT (same as gpio_mqtt.py)
        self.mqtt_client = mh.MqttClient()
        self.mqtt_client.connect(subscription_topic_name="me435/smithic/to_pi",
                                 publish_topic_name="me435/smithic/to_computer",
                                 use_off_campus_broker=True)  # False on campus
        self.mqtt_client.callback = self.mqtt_callback

        # GPIO pins used as encoder ground / power so the ribbons stay together
        self.x_ground = gz.DigitalOutputDevice(10, initial_value=False)
        self.y_power = gz.DigitalOutputDevice(26, initial_value=True)

        # Encoders + their push buttons
        self.enc_x = gz.RotaryEncoder(a=17, b=27, max_steps=0)
        self.enc_y = gz.RotaryEncoder(a=6, b=13, max_steps=0)
        self.enc_x.when_rotated_clockwise = lambda: self.go_to(self.x + STEP, self.y, True)
        self.enc_x.when_rotated_counter_clockwise = lambda: self.go_to(self.x - STEP, self.y, True)
        self.enc_y.when_rotated_clockwise = lambda: self.go_to(self.x, self.y + STEP, True)
        self.enc_y.when_rotated_counter_clockwise = lambda: self.go_to(self.x, self.y - STEP, True)
        self.button_x = gz.Button(22)
        self.button_x.when_pressed = lambda: self.reset(True)
        self.button_y = gz.Button(19)
        self.button_y.when_pressed = lambda: self.save(True)

    def mqtt_callback(self, message_type, message_payload):
        print("Received type: ", message_type)
        print("Received payload: ", message_payload)

        if message_type == "pots":
            self.go_to(message_payload["x"], message_payload["y"], False)

        if message_type == "color":
            self.set_color(message_payload, False)

        if message_type == "width":
            self.set_width(message_payload, False)

        if message_type == "bg":
            self.set_bg(message_payload, False)

        if message_type == "reset":
            self.reset(False)

        if message_type == "save":
            self.save(False)

    def go_to(self, x, y, send):
        x = min(max(x, 0), 1)
        y = min(max(y, 0), 1)
        self.canvas.create_line(self.x * WIDTH, (1 - self.y) * HEIGHT, x * WIDTH, (1 - y) * HEIGHT,
                                fill=PEN_COLORS[self.color], width=self.width, capstyle="round")
        self.x = x
        self.y = y
        if send:
            self.mqtt_client.send_message("pots", {"x": round(x, 3), "y": round(y, 3)})

    def set_color(self, color, send):
        self.color = color
        self.color_box.set(color)
        if send:
            self.mqtt_client.send_message("color", color)

    def set_width(self, width, send):
        self.width = width
        self.width_box.set(width)
        if send:
            self.mqtt_client.send_message("width", width)

    def set_bg(self, color, send):
        self.canvas.configure(bg=BG_COLORS[color])
        self.bg_box.set(color)
        if send:
            self.mqtt_client.send_message("bg", color)

    def reset(self, send):
        self.canvas.delete("all")
        if send:
            self.mqtt_client.send_message("reset")

    def save(self, send):
        file_name = time.strftime("etch_%Y%m%d_%H%M%S.png")
        subprocess.run(["grim", file_name])  # screenshot (Pi OS Wayland)
        print("Saved", file_name)
        if send:
            self.mqtt_client.send_message("save")


def main():
    print("Etch A Sketch")
    root = tkinter.Tk()
    app = App(root)
    root.mainloop()
    app.mqtt_client.close()


main()
