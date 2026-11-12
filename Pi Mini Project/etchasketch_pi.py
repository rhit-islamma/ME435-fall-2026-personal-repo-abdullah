"""
Etch A Sketch on the Pi 5.
Two rotary encoders draw. The mouse picks colors, width, reset and save.
Everything is sent over MQTT to the MATLAB app.

Wiring (each encoder ribbon on 5 pins in a row):
  X encoder: CLK=pin 11, DT=pin 13, SW=pin 15, +=pin 17 (3.3V), GND=pin 19 (GPIO10 set low)
  Y encoder: CLK=pin 31, DT=pin 33, SW=pin 35, +=pin 37 (GPIO26 set high), GND=pin 39
"""
import os
os.environ.setdefault("DISPLAY", ":0")  # use the Pi screen when run over SSH
os.environ.setdefault("WAYLAND_DISPLAY", "wayland-0")
os.environ.setdefault("XDG_RUNTIME_DIR", "/run/user/1000")

import gpiozero as gz
import mqtt_helper as mh
import signal
import subprocess
import time
import tkinter
from tkinter import ttk

STEP = 0.01
WIDTH = 960
HEIGHT = 480
RED = "#E8261C"

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

        root.title("Etch A Sketch")
        root.configure(bg=RED)
        root.attributes("-fullscreen", True)
        root.bind("<Escape>", lambda event: root.destroy())
        root.columnconfigure(0, weight=1)
        root.columnconfigure(3, weight=1)

        self.canvas = tkinter.Canvas(root, width=WIDTH, height=HEIGHT, bg=BG_COLORS["Silver"], highlightthickness=0)
        self.canvas.grid(row=0, column=0, columnspan=4, padx=32, pady=(12, 6))

        save_button = tkinter.Button(root, text="SAVE", bg="#F5646F", fg="white", font=("Arial", 12, "bold"))
        save_button.grid(row=1, column=0, rowspan=3)
        save_button["command"] = lambda: self.save(True)

        bg_label = tkinter.Label(root, text="B.g. color:", bg=RED, fg="white", font=("Arial", 11, "bold"))
        bg_label.grid(row=1, column=1, sticky="e")
        color_label = tkinter.Label(root, text="Line color:", bg=RED, fg="white", font=("Arial", 11, "bold"))
        color_label.grid(row=2, column=1, sticky="e")
        width_label = tkinter.Label(root, text="Width", bg=RED, fg="white", font=("Arial", 11, "bold"))
        width_label.grid(row=3, column=1, sticky="e")

        self.bg_box = ttk.Combobox(root, values=list(BG_COLORS), state="readonly", width=12)
        self.bg_box.set("Silver")
        self.bg_box.grid(row=1, column=2, sticky="w")
        self.bg_box.bind("<<ComboboxSelected>>", lambda event: self.set_bg(self.bg_box.get(), True))

        self.color_box = ttk.Combobox(root, values=list(PEN_COLORS), state="readonly", width=12)
        self.color_box.set(self.color)
        self.color_box.grid(row=2, column=2, sticky="w")
        self.color_box.bind("<<ComboboxSelected>>", lambda event: self.set_color(self.color_box.get(), True))

        self.width_box = ttk.Spinbox(root, from_=1, to=10, width=12)
        self.width_box.set(self.width)
        self.width_box.grid(row=3, column=2, sticky="w")
        self.width_box["command"] = lambda: self.set_width(int(self.width_box.get()), True)

        reset_button = tkinter.Button(root, text="RESET", bg="#A61C1C", fg="white", font=("Arial", 12, "bold"))
        reset_button.grid(row=1, column=3, rowspan=3)
        reset_button["command"] = lambda: self.reset(True)

        self.mqtt_client = mh.MqttClient()
        self.mqtt_client.connect(subscription_topic_name="me435/smithic/to_pi",
                                 publish_topic_name="me435/smithic/to_computer",
                                 use_off_campus_broker=True)  # False on campus
        self.mqtt_client.callback = self.mqtt_callback

        self.x_ground = gz.DigitalOutputDevice(10, initial_value=False)
        self.y_power = gz.DigitalOutputDevice(26, initial_value=True)

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
        if x < 0:
            x = 0
        if x > 1:
            x = 1
        if y < 0:
            y = 0
        if y > 1:
            y = 1
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
        subprocess.run(["grim", file_name])
        print("Saved", file_name)
        if send:
            self.mqtt_client.send_message("save")


def main():
    print("Etch A Sketch")
    root = tkinter.Tk()
    app = App(root)

    signal.signal(signal.SIGINT, lambda sig, frame: root.destroy())  # Ctrl+C closes the app
    def keep_checking():
        root.after(200, keep_checking)
    keep_checking()

    root.mainloop()
    app.mqtt_client.close()


main()
