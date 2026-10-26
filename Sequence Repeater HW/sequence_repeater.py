import gpiozero as gz
import time
import signal

def record_press(led, pattern):
    print("Record press")
    led.on()
    pattern.append(led)

def play_pattern(pattern):
    print("Play pattern")
    for led in pattern:
        led.blink(on_time=0.5, off_time=0.1, n=1, background=False)
    pattern.clear()

def button_events():
    print("Button Events")
    button = gz.Button(25)
    button_red = gz.Button(22)
    button_yellow = gz.Button(23)
    button_green = gz.Button(24)
    red_led = gz.LED(14)
    yellow_led = gz.LED(15)
    green_led = gz.LED(18)
    pattern = []

    button_red.when_pressed = lambda: record_press(red_led, pattern)
    button_red.when_released = lambda: red_led.off()
    button_yellow.when_pressed = lambda: record_press(yellow_led, pattern)
    button_yellow.when_released = lambda: yellow_led.off()
    button_green.when_pressed = lambda: record_press(green_led, pattern)
    button_green.when_released = lambda: green_led.off()
    button.when_pressed = lambda: play_pattern(pattern)

    signal.pause()

def main():
    print("Sequence Repeater")
    button_events()


main()
