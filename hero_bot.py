import random
import pyautogui
import time
import cv2
import numpy as np
from PIL import ImageGrab
from typing import Callable, Optional
from timer import Timer
from game_data import GameData

from custom_math import Vector, Rect

class HeroBot:
    def __init__(self, game_data:GameData, world_points:dict[str, Rect], log_callback: Optional[Callable[[str], None]] = None):
        self.log_callback = log_callback
        self.game_data:GameData = game_data


        self.world_points = world_points

        self.game_data.on_update_callback = self.on_update

        self.last_action_time:float = 0.0
        self.action_interval:int = random.randint(2, 5)
        
        self.spell_binds:list = ["q", "w", "e", "d", "f", "r"]

    def log(self, message: str):
        timestamp = time.strftime('%H:%M:%S')
        full_message = f"{timestamp} - {message}"
        
        if self.log_callback:
            self.log_callback(full_message)

    def world_to_minimap(self, world_x: float, world_y: float) -> tuple[int, int]:
        MAP_MIN, MAP_MAX = -8000, 8000 
        MAP_SIZE = MAP_MAX - MAP_MIN # 16000
        
        MINIMAP_X_START, MINIMAP_Y_START = 159, 756 
        MINIMAP_WIDTH, MINIMAP_HEIGHT = 233, 233 

        norm_x = (world_x - MAP_MIN) / MAP_SIZE
        norm_y = 1 - ((world_y - MAP_MIN) / MAP_SIZE)

        screen_x = int(MINIMAP_X_START + (norm_x * MINIMAP_WIDTH))
        screen_y = int(MINIMAP_Y_START + (norm_y * MINIMAP_HEIGHT))
        
        return screen_x, screen_y

    def move_to_world_pos(self, x, y):
        screen_x, screen_y = self.world_to_minimap(x, y)
        self.human_click(screen_x, screen_y, mouse_button="right")


    """ Goto fountain """
    def go_to_radiant_fountain(self):
        rect:Rect = self.world_points["radiant_base"]
        pos = rect.get_random_point()
        self.human_click(pos.x, pos.y, mouse_button="right")

    def go_to_dire_fountain(self):
        rect:Rect = self.world_points["dire_base"]
        pos = rect.get_random_point()
        self.human_click(pos.x, pos.y, mouse_button="right")

    def auto_go_to_fountain(self):
        self.select_hero()
        if self.game_data.is_radiant:
            self.go_to_radiant_fountain()
        else:
            self.go_to_dire_fountain()

    """ ------ """

    def go_to_radiant_safe_lane(self):
        self.move_to_world_pos(6000, -7200)

    def can_farm_jungle(self):
        return self.game_data.level >= 10

    def select_hero(self, move_camera:bool = True):
        pyautogui.press("1")
        if move_camera:
            time.sleep(0.1)
            pyautogui.press("1")


    def human_click(self, x, y, mouse_button = "left"):
        pyautogui.moveTo(
            x + random.randint(-5, 5),
            y + random.randint(-5, 5),
            duration=random.uniform(0.1, 0.4)
        )

        time.sleep(random.uniform(0.05, 0.2))
        pyautogui.click(button=mouse_button)


    def on_update(self, _data = None):
        if self.game_data.health_percent <= 50:
            self.auto_go_to_fountain()
        pass


    def should_act(self):
        if self.game_data.game_state == "in_game":
            return True

        return False
    
    def run_in_game(self):
        self.on_update()
  