import random
import pyautogui
import time
import cv2
import numpy as np
from PIL import ImageGrab
from typing import Callable, Optional
from timer import Timer
import threading


from game_data import GameData, DotaItem

from custom_math import Vector, Rect

class HeroBot:
    def __init__(self, bot_manager, gsi:GameData, log_callback: Optional[Callable[[str], None]] = None):
        self.log_callback = log_callback
        self.bot_manager = bot_manager

        self.gsi:GameData = gsi
        self.gsi.callbacks.append(self.on_update)

        self.current_lane = None
        self.last_lane_time = 0
        self.last_pick_lane_time = 0

        self.current_jungle_camp:Rect
        self.last_jungle_time = 0

        self.in_interface:bool = False

        self.quick_buy_added:bool = False
        self.quick_buy:list[DotaItem] = [
            DotaItem("item_bracer"),
            DotaItem("item_bracer"),
            DotaItem("item_boots"),
            DotaItem("item_glimmer_cape"),
            DotaItem("item_aeon_disk"),
            DotaItem("item_travel_boots"),
            DotaItem("item_crimson_guard"),
            DotaItem("item_pipe"),
        ]
        
        self.spell_binds:list = ["q", "w", "e", "d", "f", "r"]
        self.item_binds:list = [" ", "c", "3", "v", "x", "n"]
        self.tp_bind:str = "4"

        if self.should_pick_lane():
            self.pick_random_lane()
        
        thread = threading.Thread(target=self.act_cycle, daemon=True)
        thread.start()

    def act_cycle(self):
        while True:
            if self.can_act():
                if self.should_go_lane():
                    if self.current_lane:
                        self.attack_rect(self.current_lane)
                
                if not self.should_save():
                    ridx = random.randrange(0, 101)
                    if ridx < 50:
                        self.press_spell(random.randrange(0, len(self.spell_binds)))

            time.sleep(random.randrange(2, 6))

    def add_quickbuy(self):
        if self.in_interface:
            return
        
        self.in_interface = True
        
        try:
            pyautogui.press("f4")
            time.sleep(random.uniform(0.11, 0.21))
            
            for item in self.quick_buy:
                if self.gsi.get_item(item.id_name):
                    continue
                target_item_name = item.get_humanized_name()
                for char in target_item_name:
                    pyautogui.press(char)
                    time.sleep(random.uniform(0.05, 0.15))
                
                pyautogui.hotkey('ctrl', 'shift', "enter")
                self.log(f"{self.gsi.hero_name}: quickbuy added {item.id_name}")
                pyautogui.hotkey('ctrl', 'a')
                time.sleep(random.uniform(0.05, 0.15))
                pyautogui.press("backspace")
                time.sleep(random.uniform(0.05, 0.15))
                
            pyautogui.press("escape")
            time.sleep(random.uniform(0.05, 0.15))
            
        finally:
            self.in_interface = False
            self.quick_buy_added = True

    def add_item_to_quickbuy(self, item_id:str):
        pyautogui.press("f4")
        time.sleep(random.uniform(0.11, 0.21))
        item = DotaItem(item_id)
        target_item_name = item.get_humanized_name()
        for char in target_item_name:
            pyautogui.press(char)
            time.sleep(random.uniform(0.05, 0.15))
        
        pyautogui.hotkey('ctrl', 'shift', "enter")
        self.log(f"{self.gsi.hero_name}: quickbuy added {item.id_name}")
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(random.uniform(0.05, 0.15))
        pyautogui.press("backspace")
        time.sleep(random.uniform(0.05, 0.15))

        pyautogui.press("escape")

    def press_item(self, item_id: str, use_alt = False):
        if not self.gsi.can_use_item(item_id):
            print(1)
            return False

        if item_id != "item_tpscroll":
            item_data, slot = self.gsi.get_item_with_slot(item_id)

            if item_data is None or slot is None:
                print(2)
                return False

            key = None
            if 0 <= slot < len(self.item_binds):
                key = self.item_binds[slot]

            if not key:
                print(3)
                return False

            self.select_hero(move_camera=False)

            if item_id == "item_glimmer_cape":
                use_alt = True
        else:
            key = self.tp_bind


        try:
            if use_alt:
                pyautogui.hotkey('alt', key)
                self.log(f"{self.gsi.hero_name}: used {item_id} (Alt+{key})")
            else:
                pyautogui.press(key)
                self.log(f"{self.gsi.hero_name}: used {item_id} ({key})")

            time.sleep(random.uniform(0.05, 0.1))
            return True

        except Exception as e:
            self.log(f"Error using {item_id}: {e}")
            return False


    def pick_random_lane(self):
        rand_idx = random.randrange(0, 3)
        target_lane = ""
        if rand_idx == 0:
            target_lane = "safe_lane"
        elif rand_idx == 1:
            target_lane = "mid_lane"
        elif rand_idx == 2:
            target_lane = "hard_lane"
        
        self.current_lane = self.bot_manager.world_rects[f"{self.gsi.team}_{target_lane}"]
        self.last_pick_lane_time = self.gsi.time
        
        self.log(f"{self.gsi.hero_name}'s lane: {rand_idx}")

    def should_pick_lane(self):
        if self.gsi.game_state != "in_game":
            return False
    
        if not self.current_lane:
            return True

        return self.gsi.time - self.last_pick_lane_time > 240

    def log(self, message: str):
        timestamp = time.strftime('%H:%M:%S')
        full_message = f"{timestamp} - {message}"
        
        if self.log_callback:
            self.log_callback(full_message)

    def press_spell(self, spell_idx:int):
        self.select_hero()
        key = self.spell_binds[spell_idx]
        pyautogui.press(key)
        self.human_click(960, 540)

    def world_to_minimap(self, world_x: float, world_y: float) -> tuple[int, int]:
        MAP_MIN, MAP_MAX = -8192, 8192 
        MAP_SIZE = MAP_MAX - MAP_MIN #16384
        
        map_rect:Rect = self.bot_manager.world_rects["map_rect"]

        norm_x = (world_x - MAP_MIN) / MAP_SIZE
        norm_y = 1 - ((world_y - MAP_MIN) / MAP_SIZE)

        screen_x = int(map_rect.position.x + (norm_x * map_rect.size.x))
        screen_y = int(map_rect.position.y + (norm_y * map_rect.size.y))
        
        return screen_x, screen_y

    def should_go_jungle(self):
        if not self.can_farm_jungle():
            return False
        if self.gsi.time < 1200:
            return False
         
        if self.gsi.time - self.last_jungle_time < 60:
            return False

    def should_go_lane(self):
        return True

    def attack_rect(self, rect:Rect):
        if self.should_save():
            return
        rand_point = rect.get_random_point()
        self.human_move_mouse(rand_point.x, rand_point.y)
        pyautogui.press("a")

    def get_team_base_rect(self):
        if self.bot_manager.gsi.is_radiant:
            return self.bot_manager.world_rects["radiant_base"]
        else:
            return self.bot_manager.world_rects["dire_base"]

    def distance_to_world_pos(self, x: float, y: float) -> float:
        hero_x, hero_y = self.bot_manager.gsi.position
        dx = hero_x - x
        dy = hero_y - y
        return (dx**2 + dy**2) ** 0.5

    def distance_to_base(self) -> float:
        center:Vector = Vector(0, 0)
        if self.gsi.is_radiant:
            center = Vector(-7000, -6500)
        if self.gsi.is_dire:
            rect = Vector(7000, 6500)
        
        return self.distance_to_world_pos(center.x, center.y)


    def move_to_world_pos(self, x, y):
        screen_x, screen_y = self.world_to_minimap(x, y)
        self.human_click(screen_x, screen_y, mouse_button="right")


    def go_to_base(self, select_hero:bool = True):
        if select_hero:
            self.select_hero()
        rect:Rect = self.get_team_base_rect()
        pos = rect.get_random_point()
        self.human_click(pos.x, pos.y, mouse_button="right")

    def go_to_radiant_safe_lane(self):
        self.move_to_world_pos(6000, -7200)

    def can_farm_jungle(self):
        return self.bot_manager.gsi.level >= 10

    def select_hero(self, move_camera:bool = True):
        pyautogui.press("1")
        if move_camera:
            time.sleep(random.uniform(0.05, 0.11))
            pyautogui.press("1")


    def human_move_mouse(self, x, y):
        if not self.can_act():
            return
        pyautogui.moveTo(
            x + random.randint(-5, 5),
            y + random.randint(-5, 5),
            duration=random.uniform(0.1, 0.4)
        )

    def human_click(self, x, y, mouse_button = "left"):
        self.human_move_mouse(x, y)

        time.sleep(random.uniform(0.05, 0.2))
        if not self.can_act():
            return
        pyautogui.click(button=mouse_button)

    def save_yourself(self):
        self.select_hero()
        
    
        save_items = self.gsi.get_save_items()
        for save_item in save_items:
            self.press_item(save_item["name"])

        if self.distance_to_base() > 4500:
            if self.bot_manager.gsi.can_use_item("item_tpscroll"):
                self.press_item("item_tpscroll", use_alt=True)
                self.log(f"{self.gsi.hero_name}: saving by tp")
                return

        self.go_to_base(select_hero=False)
        self.log(f"{self.gsi.hero_name}: saving")

    def should_save(self) -> bool:
        if not self.can_act(check_interface=False):
            return False
        return self.gsi.health_percent <= 60

    def on_update(self, _data = {}):
        if self.should_save():
            self.save_yourself()
            

    def can_act(self, check_interface:bool = True):
        if not self.bot_manager.running:
            return False

        if not self.bot_manager.is_dota_active():
            return False
        
        if not self.bot_manager.gsi.is_alive:
            return False

        if self.bot_manager.gsi.game_state != "in_game":
            return False
        
        if check_interface:
            if self.in_interface:
                return False 

        return True
    
    def run_in_game(self):
        if not self.can_act():
            return

        if self.should_pick_lane():
            self.pick_random_lane()
        
        if not self.quick_buy_added:
            self.add_quickbuy()
