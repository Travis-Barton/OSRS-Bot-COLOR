from model.runelite_bot import RuneLiteBot
import time
from utilities.runelite_cv import isolate_colors, get_contour_positions, Color, get_contours
import numpy as np
import random as rd
import pandas as pd
from model.bot import BotStatus
import cv2
import utilities.bot_cv as bcv
import pyautogui as pag
from model.osrs.woodcutting_2 import Woodcutting
wc = Woodcutting()


# Runelite settings:
wc.setup_client('RuneLite', True, True, True)

# Highlighting objects and NPCs

# Mouse movements
wc.mouse.move_to((100, 100), duration=0.3, destination_variance=0, time_variance=0, tween=None)
wc.mouse.move_to((100, 100), duration=0.3, destination_variance=0, time_variance=0, tween=pag.easeInBounce)
wc.mouse.move_to((100, 100), duration=0.3, destination_variance=0, time_variance=0, tween='rand')

# Pre-programmed locations
# points
print(wc.cp_combat)
wc.mouse.move_to(wc.cp_combat, duration=0.3, destination_variance=0, time_variance=0, tween=None)
wc.mouse.click()
print(wc.cp_inventory)
wc.move_to(wc.cp_inventory, duration=0.3, destination_variance=0, time_variance=0, tween=None)
wc.mouse.click()
print(wc.cp_prayer, wc.cp_equipment, wc.cp_logout)

# Areas
wc.rect_minimap
wc.rect_inventory
wc.rect_game_view

# Objects on screen with pyautogui
loc = pag.locateCenterOnScreen('src/images/temp/swordfish.png')
wc.mouse.move_to((loc.x, loc.y))
wc.mouse.click()

loc = pag.locateCenterOnScreen('src/images/temp/swordfish.png', region=())
wc.mouse.move_to((loc.x, loc.y))
wc.mouse.click()


# Built in object detection

loc = wc.get_nearest_tag()
print(loc)

loc = wc.get_hp()
print(loc)
