import gpiozero as gz
import time


def main():
    print("Pushbuttons")

    button = gz.Button(25)

    while True:
        if button.is_pressed:
            print("Button is pressed")
        else:
            print("Button is not pressed")

        time.sleep(0.5)


main()