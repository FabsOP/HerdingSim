#### IMPORTS ###############################
from widgets.simulation import Simulation
from widgets.main_menu import MainMenu

#music and sounds
import pygame
from mutagen.mp3 import MP3

import random

import time

#### HELPER FUNCTIONS ###################
def playSong(songIdx):
    pygame.mixer.music.load(playlist[songIdx][0])
    pygame.mixer.music.set_volume(playlist[songIdx][1])
    pygame.mixer.music.play()

def scheduleNextSong(sim):
    global songIdx
    inbetweenDelay = 5 #seconds
    duration = int(playlist[songIdx][2] + inbetweenDelay)*1000
    
    print(f"Now playing: [{songIdx+1}] {playlist[songIdx][0]}")
    playSong(songIdx)

    songIdx = (songIdx+1) % len(playlist)
    print(f"Next in queue: [{songIdx+1}] {playlist[songIdx][0]}")
    sim.after(duration, lambda: scheduleNextSong(sim))
    
#### SIMULATION MUSIC ###################################################################################
songIdx = 0
playlist = [("audio/music/answers-from-angels-333760.mp3",0.02, MP3("audio/music/answers-from-angels-333760.mp3").info.length),
            ("audio/music/lost-in-summer-232501.mp3",0.04, MP3("audio/music/lost-in-summer-232501.mp3").info.length),
            ("audio/music/infinityBetweenUs.mp3",0.1, MP3("audio/music/infinityBetweenUs.mp3").info.length)
            ]  #[(song path, volume, duration(s)),..]
random.shuffle(playlist)

pygame.mixer.init()

### MAIN CODE ######################################################
terrainSize = "small"
if __name__ == "__main__":
    MainMenu()
    s = Simulation(terrainSize)
    scheduleNextSong(s)
    s.canvas.update(60, ti=time.time())
    s.mainloop()