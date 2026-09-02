#### IMPORTS ###############################
from herdsim.ui.simulation import Simulation
from herdsim.ui.main_menu import MainMenu
from herdsim.ui.terrainLoader import TerrainLoader

#music and sounds
import pygame
from mutagen.mp3 import MP3

import random

import time

# Deployment helper functions
from herdsim.utils.path_utils import resource_path

#fix rendering
import ctypes


#### HELPER FUNCTIONS ###################
def playSong(songIdx):
    pygame.mixer.music.load(playlist[songIdx][0])
    pygame.mixer.music.set_volume(playlist[songIdx][1])
    pygame.mixer.music.play()

def songDuration(songIdx):
    path, volume, duration = playlist[songIdx]
    if duration is None:
        duration = MP3(path).info.length
        playlist[songIdx] = (path, volume, duration)
    return duration

def scheduleNextSong(sim):
    global songIdx
    inbetweenDelay = 5 #seconds
    duration = int(songDuration(songIdx) + inbetweenDelay)*1000
    
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
    ("audio/music/ambient-background-music-331731.mp3", 0.1),
    ("audio/music/medieval-ambient-236809.mp3", 0.1),
    ("audio/music/chill-lofi-316579.mp3", 0.1),
    ("audio/music/ethereal-nature.mp3", 0.1),
    ("audio/music/flash-news.mp3", 0.1),
    ("audio/music/mystical-world.mp3", 0.1)
]

playlist = [(resource_path(audio_file), volume, None) for audio_file, volume in audio_files]

random.shuffle(playlist)

### MAIN CODE ######################################################
def main():
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)  # or (2) for per-monitor
        print("DPI awareness set successfully.")
    except Exception:
        print("DPI awareness setting failed or not supported on this OS.")
        pass
    
    pygame.mixer.init()

    m = MainMenu()
    t = TerrainLoader()
    
    terrainSize = "large"  
    terrain = t.getSelectedTerrain()
    
    # Create the simulation with the generated terrain
    s = Simulation(terrainSize, terrain)
    scheduleNextSong(s)
    s.canvas.update(60, ti=time.time())
        
    s.mainloop()


if __name__ == "__main__":
    main()
