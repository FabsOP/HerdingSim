#### IMPORTS ###############################
from widgets.simulation import Simulation
from widgets.main_menu import MainMenu
from widgets.terrainLoader import TerrainLoader

#music and sounds
import pygame
from mutagen.mp3 import MP3

import random

import time
from terrain import Terrain
import tkinter as tk

# Deployment helper functions
from path_utils import resource_path, user_data_path
import os

#### HELPER FUNCTIONS ###################
def generateTerrain(terrainSize, terrainType, heightMapPath=None, levels=15, invert=True):
    """
    Generates a terrain based on the given parameters.
    """
    canvasMultiplier = {"small": 1.5, "large": 2}
    terrain = Terrain(int(256*canvasMultiplier[terrainSize]), int(256*canvasMultiplier[terrainSize]), invert=invert)
    terrain.load(heightMapPath, terrainType, levels=levels)
    return terrain


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
audio_files = [
    ("audio/music/answers-from-angels-333760.mp3", 0.02),
    ("audio/music/lost-in-summer-232501.mp3", 0.04),
    ("audio/music/infinityBetweenUs.mp3", 0.1),
    ("audio/music/medieval-ambient-236809.mp3", 0.1),
    ("audio/music/chill-lofi-316579.mp3", 0.1),
    ("audio/music/ethereal-nature.mp3", 0.1),
    ("audio/music/flash-news.mp3", 0.1),
    ("audio/music/mystical-world.mp3", 0.1)
]

playlist = []
for audio_file, volume in audio_files:
    path = resource_path(audio_file)  # Wrap path with resource_path()
    duration = MP3(path).info.length
    playlist.append((path, volume, duration))
    
random.shuffle(playlist)

pygame.mixer.init()

### MAIN CODE ######################################################
if __name__ == "__main__":
    
    
    m = MainMenu()
    t = TerrainLoader()
    
    terrainSize = "large"  
    terrain = t.getSelectedTerrain()
    
    # Create the simulation with the generated terrain
    s = Simulation(terrainSize, terrain)
    scheduleNextSong(s)
    s.canvas.update(60, ti=time.time())
        
    s.mainloop()