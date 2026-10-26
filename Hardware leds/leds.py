import gpiozero as gz
import time


def main():
    print("Ready")
    # basic_on_off()
    traffic_light()


def basic_on_off():
    print("Basic on off control")

    red_led = gz.DigitalOutputDevice(14)
    yellow_led = gz.DigitalOutputDevice(15)
    green_led = gz.DigitalOutputDevice(18)

    red_led.on()
    time.sleep(1)
    red_led.off()

    yellow_led.on()
    time.sleep(1)
    yellow_led.off()

    green_led.on()
    time.sleep(1)
    green_led.off()


def traffic_light():
    print("Manual traffic light")

    red_led = gz.LED(14)
    yellow_led = gz.LED(15)
    green_led = gz.LED(18)

    while True:
        green_led.on()
        time.sleep(4)
        green_led.off()

        yellow_led.on()
        time.sleep(1)
        yellow_led.off()

        red_led.on()
        time.sleep(3)
        red_led.off()


main()