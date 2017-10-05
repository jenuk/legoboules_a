import ev3dev.ev3 as ev3
from time import sleep

screen = ev3.Screen()

screen.draw.text((50, 50), "Hello World!")
screen.update()

sleep(2)