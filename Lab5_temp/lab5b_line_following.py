from rosebot import Rosebot
import time

SPEED = 30  # ADDED (not Fisher): tune on the track

def main():
    print("Lab 5b Line Following")
    robot = Rosebot()


    try:
        while True:

            # ADDED (not Fisher): everything in this loop body except the comments.
            cm = robot.ultrasonic.get_cm()
            word = robot.line_sensors.get_line_word()
            print(cm, word)
            # Get ultrasonic sensor
            # if distance < 20 cm
            #   stop the robot
            # else
            if cm < 20:
                robot.drive_system.stop()
            #   Get the line sensor readings.
            #   Adjust wheel speeds based on YOUR strategy
            elif word == "WBW" or word == "BBB":  # centered (or crossing): straight
                robot.drive_system.go(SPEED, SPEED)
            elif word == "BBW":  # line a little left: ease left
                robot.drive_system.go(0, SPEED)
            elif word == "BWW":  # line far left: spin left
                robot.drive_system.go(-SPEED, SPEED)
            elif word == "WBB":  # line a little right: ease right
                robot.drive_system.go(SPEED, 0)
            elif word == "WWB":  # line far right: spin right
                robot.drive_system.go(SPEED, -SPEED)
            # "WWW" (lost the line) or "BWB": keep doing the last command

            time.sleep(0.02)  # ADDED (not Fisher): was 0.1, faster loop for steering

    except KeyboardInterrupt:
        # Handle Ctrl-C to exit the program cleanly.
        robot.drive_system.stop()
        print("Goodbye!")

main()
