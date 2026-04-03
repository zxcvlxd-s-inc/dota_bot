import random
import pyautogui
import time
import cv2
import numpy as np
from PIL import ImageGrab
from typing import Callable, Optional
from timer import Timer
from game_data import GameData

class HeroBot:
    def __init__(self, game_data:GameData, world_points, log_callback: Optional[Callable[[str], None]] = None):
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
        
        print(screen_x, screen_y)
        return screen_x, screen_y

    def move_to_world_pos(self, x, y):
        screen_x, screen_y = self.world_to_minimap(x, y)
        pyautogui.click(screen_x, screen_y, button='right')


    """ Goto fountain """
    def go_to_radiant_fountain(self):
        vec = self.world_points["radiant_base"] 
        self.move_to_world_pos(vec[0], vec[1])

    def go_to_dire_fountain(self):
        vec = self.world_points["dire_base"] 
        self.move_to_world_pos(vec[0], vec[1])

    def auto_go_to_fountain(self):
        if self.game_data.is_radiant:
            self.go_to_radiant_fountain()
        else:
            self.go_to_dire_fountain()

    """ ------ """

    def go_to_radiant_safe_lane(self):
        self.move_to_world_pos(6000, -7200)

    def can_farm_jungle(self):
        return self.game_data.level >= 10

    def human_move_mouse(self, xyxy:list[int], move_time:list[float] = [0.3, 0.5], press:bool = False, key=""):
        map_x = random.randint(xyxy[0], xyxy[1])
        map_y = random.randint(xyxy[2], xyxy[3])
        time_aa = random.uniform(move_time[0], move_time[1]) 
        pyautogui.moveTo(map_x, map_y, duration=time_aa)
        if press:
            if key == "mouse1":
                pyautogui.click()
                return
            elif key == "mouse2":
                pyautogui.click(button="right")
                return
            pyautogui.press(key)

    def on_update(self, _data = None):
        #if self.game_data.health_percent <= 50:
        #    self.auto_go_to_fountain()
        pass


    def should_act(self):
        current_time = time.time()
        if current_time - self.last_action_time > self.action_interval:
            self.last_action_time = current_time
            self.action_interval = random.randint(2, 5)
            return True
        return False
    
    def run_in_game(self):
        self.on_update()
  