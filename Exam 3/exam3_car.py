import mqtt_helper as mh
from rosebot import Rosebot
import signal
import time


class App:

    def __init__(self):
        self.robot = Rosebot()

        self.mqtt_client = mh.MqttClient()
        self.mqtt_client.connect(subscription_topic_name="me435/islamma/to_pi",
                                 publish_topic_name="me435/islamma/to_computer")
        self.mqtt_client.callback = self.mqtt_callback

    def mqtt_callback(self, message_type, message_payload):
        print("Received type: ", message_type)
        print("Received payload: ", message_payload)

        if message_type == "left":
            print("Side: Left", "Direction:", message_payload[0], "Time:", message_payload[1], "Speed:", message_payload[2])
            if message_payload[0] == 1:
                self.robot.drive_system.go(message_payload[2], 0)
            else:
                self.robot.drive_system.go(-message_payload[2], 0)
            time.sleep(message_payload[1])
            self.robot.drive_system.stop()

        if message_type == "right":
            print("Side: Right", "Direction:", message_payload[0], "Time:", message_payload[1], "Speed:", message_payload[2])
            if message_payload[0] == 1:
                self.robot.drive_system.go(0, message_payload[2])
            else:
                self.robot.drive_system.go(0, -message_payload[2])
            time.sleep(message_payload[1])
            self.robot.drive_system.stop()

        if message_type == "both":
            print("Side: Both", "Direction:", message_payload[0], "Time:", message_payload[1], "Speed Left:", message_payload[2], "Speed Right:", message_payload[3])
            if message_payload[0] == 1:
                self.robot.drive_system.go(message_payload[2], message_payload[3])
            else:
                self.robot.drive_system.go(-message_payload[2], -message_payload[3])
            time.sleep(message_payload[1])
            self.robot.drive_system.stop()

def main():
    print("Exam 3 MQTT")
    app = App()

    try:
        while True:
            print("Ultra:", app.robot.ultrasonic.get_cm())
            app.mqtt_client.send_message("ultra", app.robot.ultrasonic.get_cm())
            time.sleep(2)
        
    except KeyboardInterrupt:
        print("Goodbye")
        app.robot.drive_system.stop()
        app.mqtt_client.close()


main()