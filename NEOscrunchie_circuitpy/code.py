# SPDX-FileCopyrightText: 2018 Kattni Rembor for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""CircuitPython Essentials NeoPixel example"""
import time
import board
from rainbowio import colorwheel
import neopixel
import random
from digitalio import DigitalInOut, Direction, Pull
from math import sin, pi 

pixel_pin = board.IO2
numpix = 16

strip = neopixel.NeoPixel(pixel_pin, numpix, brightness=0.3, auto_write=False)

max_len = 20
min_len = 5
num_flashes = 10
master_brightness = 1.0

mode = 0

pin8 = DigitalInOut(board.IO8)
pin8.direction = Direction.OUTPUT
pin8.value = False
pin11 = DigitalInOut(board.IO11)
pin11.direction = Direction.OUTPUT
pin8.value = False


btn1 = DigitalInOut(board.IO10)
btn1.direction = Direction.INPUT
btn1.pull = Pull.UP

btn2 = DigitalInOut(board.IO13)
btn2.direction = Direction.INPUT
btn2.pull = Pull.UP


GAMMA = bytes([int((i / 255) ** 2.6 * 255 + 0.5) for i in range(256)])

def apply_gamma(r, g, b):
    return (GAMMA[r], GAMMA[g], GAMMA[b])


RED = (255, 0, 0)
YELLOW = (255, 150, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
PURPLE = (180, 0, 255)

white = (255, 255, 255)

red = (250, 2, 2)
orange = (255, 80, 0)
yellow = (235, 155, 0)
green = (10, 235, 5)
blue = (20, 30, 245)
indigo = (75, 0, 130)
violet = (235, 0, 255)
pink = (235,80,110)

colors = [red, orange, yellow, green, pink, blue, indigo, violet]

colors_red = [red, orange, yellow]

colors_rainbow = [
    red,
    orange,
    yellow,
    green,
    blue,
    indigo,
    violet
]

warm_white = (150, 70, 20)
colors_ww = [warm_white] #this is needed by breath() and ffs()

#from fireflies.py
colors_ffs = [
    (232, 100, 255),  # Purple
    (200, 200, 20),  # Yellow
    (30, 200, 200),  # Blue
    (150,50,10),
    (50,200,10),
]

PASTEL_RAW = [
    (255, 179, 186),  # Pastel Pink
    (255, 223, 186),  # Pastel Orange
    (255, 255, 186),  # Pastel Yellow
    (186, 255, 201),  # Pastel Green
    (186, 225, 255),  # Pastel Blue
    (201, 186, 255),  # Pastel Purple
    (255, 186, 241),  # Pastel Magenta
]

PPB = [
    (255, 169, 180),  # Pastel Pink
    (201, 186, 255),  # Pastel Purple
    (255, 186, 241),  # Pastel Magenta
]

# Gamma corrected pastel colors
colors_pastel = [apply_gamma(r, g, b) for (r, g, b) in PASTEL_RAW]
colors_ppb = [apply_gamma(r, g, b) for (r, g, b) in PPB]

color_sets = [colors_pastel, colors_ppb, colors_ffs]


def setup_flash(current_colors):
    flashing = []

    num_flashes = 10

    for _ in range(num_flashes):
        pix = random.randint(0, numpix - 1)
        col = random.choice(current_colors)
        flash_len = random.randint(min_len, max_len)
        flashing.append([pix, col, flash_len, 0, 1])
    
    return flashing

def ffs(run_time, current_colors, delay):
    num_flashes = 10
    flashing = setup_flash(current_colors)
    start_time = time.monotonic()
    
    while time.monotonic() - start_time < run_time or run_time == 1000:
        if not btn1.value:
            return 1
        if not btn2.value:
            return 2
        strip.show()
        for i in range(num_flashes):
            pix = flashing[i][0]
            brightness = flashing[i][3] / flashing[i][2]
            color = flashing[i][1]
            scaled_color = tuple(int(c * brightness)*master_brightness for c in color)
            strip[pix] = scaled_color

            # Reverse if at peak
            if flashing[i][3] == flashing[i][2]:
                flashing[i][4] = -1

            # Reset if fully faded out
            if flashing[i][3] == 0 and flashing[i][4] == -1:
                pix = random.randint(0, numpix - 1)
                col = random.choice(current_colors)
                flash_len = random.randint(min_len, max_len)
                flashing[i] = [pix, col, flash_len, 0, 1]

            flashing[i][3] += flashing[i][4]
        
        time.sleep(delay)
    return 0

def color_chase(device, color, wait=0.05):
    for i in range(numpix):
        if not btn1.value:
            return 1
        elif not btn2.value:
            return 2
        else:
            pass
        device[i] = color
        time.sleep(wait)
        device.show()
    time.sleep(0.2)


def rainbow_cycle(device, wait):
    for j in range(255):
        for i in range(numpix):
            if not btn1.value:
                return 1
            if not btn2.value:
                return 2
            rc_index = (i * 256 // numpix) + j
            device[i] = colorwheel(rc_index & 255)
        device.show()
        time.sleep(wait)

def breath(cols=colors_red, num_flashes=None):
    """doesnt need anything, takes in strip(obj), color SET, blink time, steps
    max brightness scaled to balance out the effect"""
    global master_brightness
    intime = 1.2
    numsteps = 30

    delay = intime/numsteps
    
    strip.fill((0,0,0))
    strip.show()
    if not num_flashes:
        num_flashes = random.randint(1, 5)
    
    for i in range(num_flashes):
        current_col = random.choice(cols)
        #print(current_col)
        for step in range(numsteps):
            if not btn1.value:
                return 1
            if not btn2.value:
                return 2
            scaled_color = tuple(int(c * (sin(pi * (step / numsteps)))*master_brightness) for c in current_col)
            
            for pix in range(numpix):
                strip[pix] = scaled_color 
            
            #print(strip.get_pixel(1))
            strip.show()
            time.sleep(delay)


def smooth_brightness(col, initB, endB, intime=0.5, numsteps=20):
    delay = intime/numsteps
    stepwidth = (endB - initB)/numsteps
    strip.fill(tuple(round(c*initB) for c in col))
    brightness = initB
    for step in range(numsteps):
        if not btn1.value:
            return 1
        if not btn2.value:
            return 2
        brightness += stepwidth
        scaled_color = tuple(int(c * brightness) for c in col)
        strip.fill(scaled_color)
        strip.show()
        
        time.sleep(delay)

def handle_return(value):
    ''' handles returns to change mode and brightness'''
    global mode, master_brightness
    
    if not value: #no press
        return
    if value == 1: #mode switch pressed
        if mode == 0:
            mode = 1
            time.sleep(0.3)
            color_chase(strip, orange)
        elif mode == 1:
            mode = 2
            time.sleep(0.3)
            breath(colors_ww, 1)
            
        elif mode == 2:
            mode = 0
            time.sleep(0.3)
            color_chase(strip, colors_ppb[0])
    
    if value == 2: #brightness toggle pressed
        if master_brightness == 0.3:
            time.sleep(0.2)
            color_chase(strip, warm_white)
            master_brightness = 1.0
            if smooth_brightness(warm_white, 0.3, 1.0, 1.0) == 2:
                mode = 3
                strip.fill((255,255,255))
                strip.show()
                time.sleep(0.3)
            
        elif master_brightness == 1.0:
            time.sleep(0.2)
            color_chase(strip, warm_white)
            smooth_brightness(warm_white, 1.0, 0.3, 1.0)
            master_brightness = 0.3

while True: 
    if mode == 1:
        rand_mode = random.choice([0,0,0,0,1,1,2])
        
        if rand_mode ==0:
            #ret_value = ffs(5, colors_red, 0.035)
            
            handle_return(ffs(5, colors_red, 0.035))
        
        if rand_mode == 1:
            handle_return(breath(colors_red))
            
        if rand_mode == 2:
            for color in colors_red:
                color_chase(strip, color)
    
    elif mode == 2:
        handle_return(ffs(5, colors_ww, 0.04))
        
    elif mode == 3:
        if not btn1.value:
            mode = 0
        if not btn2.value:
            mode = 0
    
    else:
        rand_mode = random.choice([0,0,0,0,0,1,2,2,2])
        
        if rand_mode == 0:
            handle_return(ffs(5, colors_ww, 0.04))
            
        
        elif rand_mode == 1:
            handle_return(breath(colors_pastel))
        
        elif rand_mode == 2:
            run_time = random.randint(4,20)
    
            current_colors = random.choice(color_sets)
    
            delay = random.choice([0.01, 0.015, 0.015, 0.025])
            if run_time > 8:
                delay = 0.035
            handle_return(ffs(run_time, current_colors, delay))



