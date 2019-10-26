#coding: utf-8
import os
import sys
import time
import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306
import glob
from threading import Thread
from PIL import Image

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

with open(os.devnull, 'w') as f:
    # disable stdout
    oldstdout = sys.stdout
    sys.stdout = f
    from pygame import mixer

    # enable stdout
    sys.stdout = oldstdout

# Raspberry Pi pin configuration:
RST = 24
# Note the following are only used with SPI:
DC = 23
SPI_PORT = 0
SPI_DEVICE = 0

# Beaglebone Black pin configuration:
# RST = 'P9_12'
# Note the following are only used with SPI:
# DC = 'P9_15'
# SPI_PORT = 1
# SPI_DEVICE = 0

# 128x32 display with hardware I2C:
#disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST)

# 128x64 display with hardware I2C:
disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST)

# 128x32 display with hardware SPI:
# disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST, dc=DC, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=8000000))

# 128x64 display with hardware SPI:
# disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST, dc=DC, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=8000000))

# Initialize library.
disp.begin()

# Clear display.
disp.clear()
disp.display()

# Load image based on OLED display height.  Note that image is converted to 1 bit color.
#if disp.height == 64:
#    image = Image.open('happycat_oled_64.ppm').convert('1')
#else:
#    image = Image.open('happycat_oled_32.ppm').convert('1')

# Alternatively load a different format image, resize it, and convert to 1 bit color.
#image = Image.open('happycat.png').resize((disp.width, disp.height), Image.ANTIALIAS).convert('1')

# Display image.
#disp.image(image)
#disp.display()


def ShowFrame(FrameDirectory,FileName):
    #print("Image: " + FileName)
    disp.image(Image.open(FrameDirectory).resize((disp.width, disp.height), Image.ANTIALIAS).convert("1"))
    disp.display()


def progress(count, total, suffix=''):
    bar_len = 50
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '#' * filled_len + '.' * (bar_len - filled_len)

    sys.stdout.write('\r%s %s%s[%s]' % (suffix, percents, '%', bar ))
    sys.stdout.flush()

def MSToTime(MS):
    millis = int(MS)
    seconds=(millis/1000)%60
    seconds = int(seconds)
    minutes=(millis/(1000*60))%60
    minutes = int(minutes)
    hours=(millis/(1000*60*60))%24

    if hours == 0:
        return("%02d:%02d" % (minutes, seconds))
    else:
        return("%02d:%02d:%02d" % (hours,minutes, seconds))


directory = "/home/pi/Adafruit_Python_SSD1306/examples/Shelter_SSD1306" #Modify this line of code to point to your image sequence folder & Audio file
VideoFrameRate = 23.976 #Change this value to your desired Frame Rate
ImageFileType = ".png" #Change .png to your image file type
AudioFileType = ".mp3" #Change .mp3 to your audio file type

RawFrameTime = round((((1000/VideoFrameRate))/1000),4)
FrameTime = round((((1000/VideoFrameRate)-0.5)/1000),4)
TotalFrames = len(glob.glob1(directory,"*"+ImageFileType))
filedir = os.listdir(directory)
filedir.sort()
AudioFile = False
TotalLoops = 0
mixer.init()

for Afile in filedir:
    if Afile.endswith(AudioFileType):
        print("Found: " + Afile + ", using it as audio playback")
        mixer.music.load(os.path.join(directory, Afile))
        AudioFile = True
        break
    
print("Total Frames: " + str(TotalFrames) + "\nRaw Frame Time: " + str(RawFrameTime) + "\nActual Frame Time: " + str(FrameTime) + "\nTarget FPS: " + str(VideoFrameRate) + "\nTotal Duration: " + MSToTime((RawFrameTime*1000)*TotalFrames) + "\n")

while True:
    counter = 1
    if AudioFile:
        mixer.music.play()
    time.sleep(0.75) #Optional offset from audio playing to image displaying on OLED. Remove if un-needed

    for file in filedir:
        if file.endswith(ImageFileType):
            Thread(target=ShowFrame, args=[os.path.join(directory, file),file]).start()
            Thread(target=progress, args=[counter,len(filedir), ("Playing: " + MSToTime((RawFrameTime*1000)*counter)+"/"+MSToTime((RawFrameTime*1000)*len(filedir)))]).start()
            counter+=1
            time.sleep(FrameTime)

    if mixer.music.get_busy():
        mixer.music.stop()

    TotalLoops+=1
    time.sleep(1)