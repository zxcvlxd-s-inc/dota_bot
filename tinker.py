import random
import pyautogui
import time
import cv2
import numpy as np
from PIL import ImageGrab
from typing import Callable, Optional
from timer import Timer
from game_data import GameData

class DotaAFKBot:
    def __init__(self, log_callback: Optional[Callable[[str], None]] = None):
        self.log_callback = log_callback
        self.game_data:GameData 

        self.last_action_time:float = 0.0
        self.action_interval:int = random.randint(2, 5)
        
        self.spell_binds:list = ["q", "w", "e", "d", "f", "r"]

        self.top_lane_map:list[int, int, int, int] = [191, 199, 805, 816]
        self.mid_lane_map:list[int, int, int, int] = [263, 273, 873, 883]
        self.bot_lane_map:list[int, int, int, int] = [352, 360, 923, 936]
        
        self.radiant_base_map:list[int, int, int, int] = [178, 188, 954, 964]
        self.dire_base_map:list[int, int, int, int] = [365, 369, 787, 791]
        

        self.healthbar_region:list[int] = [745, 1105, 937, 958]


        self.shop_btn_region:list[int] = [1526, 1605, 949, 981]
        self.shopping_list = ["bracer", "power treads", "wraith band"]
        self.items_added = False

        self.item1_region:list[int] = [1587, 1618, 357, 379]
        self.item2_region:list[int] = [1509, 1540, 384, 406]
        self.item3_region:list[int] = [1509, 1540, 357, 379]
        self.item4_region:list[int] = [1587, 1618, 384, 406]


        self.current_lane:list[int] = self.change_lane_to_random()

        self.last_health_check:float = 0.0
        self.health_check_interval:float = 1.0

        self.current_health:float = 1.0
        self.danger_health:float = 0.6

        self.change_lane_timer = Timer()
        self.change_lane_timer._duration = 210.0
        self.change_lane_timer.connect("timeout", self.change_lane_to_random)
        self.change_lane_timer.start()

    def log(self, message: str):
        timestamp = time.strftime('%H:%M:%S')
        full_message = f"{timestamp} - {message}"
        
        if self.log_callback:
            self.log_callback(full_message)

    def human_move_mouse(self, xyxy:list[int], move_time:list[float, float] = [0.3, 0.5], press:bool = False, key=""):
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


    def attack_current_lane(self):
        if self.current_health < self.danger_health:
            return
        self.human_move_mouse(self.current_lane, press=True, key='a')
        self.log("Attack current lane: " + str(self.current_lane))

    def back_to_base(self):
        self.human_move_mouse(self.radiant_base_map, press=True, key='m', move_time=[0.1, 0.15])
        self.log("Go to base")

    def change_lane(self, lane:list[int, int, int, int]) -> None:
        self.current_lane = lane
        self.log("Changed lane to: " + str(self.current_lane))

    def change_lane_to_random(self) -> None:
        rand_id = random.randrange(0, 3)

        self.log("Change lane to random: " + str(rand_id))

        if rand_id == 0: self.change_lane(self.top_lane_map)
        elif rand_id == 1: self.change_lane(self.mid_lane_map)
        elif rand_id == 2: self.change_lane(self.bot_lane_map)

    def check_health(self):
        self.current_health = self.get_health_status()
        
        if self.current_health < self.danger_health:
            self.back_to_base()
        
    def press_spell(self, id:int = 0) -> None:
        pyautogui.press(self.spell_binds[id]) 
        self.log("Spell pressed: " + str(id))

    def press_random_spell(self) -> None:
        self.press_spell(
            random.randrange(0, len(self.spell_binds) -1)
                        )

    def select_hero(self):
        pyautogui.press('1')
        time.sleep(random.uniform(0.05, 0.15))
        pyautogui.press('1')

        self.log("Selected hero")

    def get_gold(self) -> int:

        return 0

    def should_buy_item(self) -> bool:

        return True

    def safe_human_action(self):
        actions = [
            self.check_health,
            self.attack_current_lane
        ]
        rand_actions = [
            self.select_hero,
            self.select_hero,
            self.press_random_spell
        ]
        
        rand_action = random.choice(rand_actions)
        rand_action()
        
        for action in actions:
            action()
    


    def get_health_status(self) -> float:
        screenshot = ImageGrab.grab()
        screenshot = np.array(screenshot)
        screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)

        x_min, x_max, y_min, y_max = self.healthbar_region
        health_bar_width = x_max - x_min
        health_bar_height = y_max - y_min
        

        health_bar_region = screenshot[y_min:y_max, x_min:x_max]

        hsv = cv2.cvtColor(health_bar_region, cv2.COLOR_BGR2HSV)
        lower_green = np.array([35, 50, 50])
        upper_green = np.array([85, 255, 255])
        green_mask = cv2.inRange(hsv, lower_green, upper_green)
        

        contours, _ = cv2.findContours(green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return 1.0

        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)


        health_percentage = w / health_bar_width
        
        return health_percentage



    def should_act(self):
        current_time = time.time()
        if current_time - self.last_action_time > self.action_interval:
            self.last_action_time = current_time
            self.action_interval = random.randint(2, 5)
            return True
        return False
    
    def run_in_game(self):
        if self.should_act():
            self.safe_human_action()