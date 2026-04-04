import pyautogui
import time
import random
import cv2
import numpy as np
import os
import customtkinter as ctk
import threading
import tkinter as tk
from PIL import ImageGrab, Image, ImageTk
import json
from pathlib import Path

import pygetwindow as gw

from rect_select import ScreenRectSelector
from overlay_visualizer import OverlayVisualizer

from hero_bot import HeroBot
from game_data import GameData

from custom_math import Rect
from custom_math import Vector

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("green")


main_font = ("Consolas", 16, "bold")

class BotManagerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.title("Bot Manager")
        self.geometry("600x800")
        #self.set_app_icon("icon.png")

        self.world_rects = {}

        self.calibration_file = Path("calibration.json")
        if not self.load_calibration():
            self.world_rects = {
                "map_rect": Rect(Vector(159, 756), Vector(233, 233)),

                "radiant_base": Rect(Vector(175, 954), Vector(13, 13)),
                "dire_base": Rect(Vector(363, 786), Vector(7, 7)),

                "radiant_safe_lane": Rect(Vector(363, 786), Vector(7, 7)),
                "dire_safe_lane": Rect(Vector(363, 786), Vector(7, 7)),

                "radiant_mid_lane": Rect(Vector(363, 786), Vector(7, 7)),
                "dire_mid_lane": Rect(Vector(363, 786), Vector(7, 7)),

                "radiant_hard_lane": Rect(Vector(363, 786), Vector(7, 7)),
                "dire_hard_lane": Rect(Vector(363, 786), Vector(7, 7)),
            }

 

        self.running: bool = False
        
        self.gsi = GameData()   

        self.hero_bot:HeroBot = HeroBot(self, gsi=self.gsi, log_callback=self.log_message)
        self.overlay = OverlayVisualizer(world_rects=self.world_rects, gsi=self.gsi, scale=0.6)
        
        self.gsi.start()
        
        self.accept_templates_dir: str = "img/accept_btn/"
        self.play_btn_templates_dir: str = "img/play_btn/"
        self.find_game_templates_dir: str = "img/find_game_btn"
        self.rand_hero_templates_dir: str = "img/rand_hero_btn/"
        self.dota_map_templates_dir: str = "img/dota_map/"
        self.up_spell_templates_dir: str = "img/up_spell/"
        self.shop_templates_dir: str = "img/shop/"
        self.dota_ui_templates_dir: str = "img/dota_ui/"
        
        self.rect_selector = ScreenRectSelector()

        self.setup_ui()

    def on_closing(self):
        self.overlay.stop()
        self.running = False
        self.destroy()

    def select_rect(self, rect_name: str):
        self.rect_selector.select_rect(rect_name, self.on_rect_selected)

    def on_rect_selected(self, name: str, rect: Rect):
        self.world_rects[name] = rect
        self.save_calibration()
        self.overlay.update_rects(self.world_rects)

    def save_calibration(self):
        data = {}
        for key, rect in self.world_rects.items():
            data[key] = {
                "x": int(rect.position.x),
                "y": int(rect.position.y),
                "w": int(rect.size.x),
                "h": int(rect.size.y)
            }
        try:
            self.calibration_file.write_text(
                json.dumps(data, indent=2, ensure_ascii=False),
                encoding="utf-8"
            )
            self.log_message(f"Saved calibration.json: {self.calibration_file}")
        except Exception as e:
            self.log_message(f"Error saving calibration.json: {e}")

    def load_calibration(self) -> bool:
        if not self.calibration_file.exists():
            return False
        try:
            data = json.loads(self.calibration_file.read_text(encoding="utf-8"))
            for name, values in data.items():
                pos = Vector(values["x"], values["y"])
                size = Vector(values["w"], values["h"])
                self.world_rects[name] = Rect(pos, size)
            self.log_message(f"Loaded calibration.json form: {self.calibration_file}")
            
            return True
        except Exception as e:
            self.log_message(f"Error loading calibration.json: {e}")
            return False

    def set_app_icon(self, icon_filename: str):
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            icon_path = os.path.join(script_dir, icon_filename)
            
            if os.path.exists(icon_path):
                if icon_filename.lower().endswith('.png'):
                    ico_path = os.path.join(script_dir, 'temp_icon.ico')
                    self.convert_png_to_ico(icon_path, ico_path)
                    icon_path = ico_path
                
                self.iconbitmap(icon_path)
                
                if os.name == 'nt':
                    try:
                        import ctypes
                        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('dota.bot.manager.v1')
                    except:
                        pass
                        
            else:
                pass
                
        except Exception as e:
            pass

    def is_dota_active(self) -> bool:
        try:
            active_window = gw.getActiveWindow()
            if not active_window:
                return False

            window_title = active_window.title.lower()

            if "dota2" in window_title or "dota 2" in window_title:
                return True

            return False
        except Exception as e:
            return False

    def convert_png_to_ico(self, png_path: str, ico_path: str):
        try:
            img = Image.open(png_path)
            img.save(ico_path, format='ICO', sizes=[(16, 16), (32, 32), (48, 48), (64, 64)])
        except Exception as e:
            pass

    def setup_ui(self):
        main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="black")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        
        title_label = ctk.CTkLabel(main_frame, text="Dota 2 AzFK Bot Manager",
                                  font=main_font)
        title_label.pack(pady=20)
        
        self.status_label = ctk.CTkLabel(main_frame, text="Status: Inactive",
                                        font=main_font,)
        self.status_label.pack(pady=10)
        
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent", corner_radius=0)
        button_frame.pack(pady=20)
        
        self.start_button = ctk.CTkButton(button_frame, text="Start", font=main_font,
                                         command=self.start_bot, width=120, corner_radius=0)
        self.start_button.pack(side="left", padx=10)
        
        self.stop_button = ctk.CTkButton(button_frame, text="Stop", 
                                        command=self.stop_bot, width=120, font=main_font,
                                        fg_color="red", state="disabled", corner_radius=0)
        self.stop_button.pack(side="left", padx=10)

        """ Calibration """
        calibrate_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        calibrate_frame.pack(pady=10, fill="x")

        for rect_name in self.world_rects:
            calibrate_btn = ctk.CTkButton(
                calibrate_frame,
                text=f"Calibrate {rect_name}",
                font=main_font,
                command=lambda name=rect_name: self.select_rect(name)
            )
            calibrate_btn.pack(pady=2, fill="x")

        """ ------ """

        self.ingame_label = ctk.CTkLabel(main_frame, text="Ingame: False", font=main_font)
        self.ingame_label.pack(padx=10)


        """ Logging """
        self.log_text = ctk.CTkTextbox(
            main_frame,
            height=300, corner_radius=0, font=("Consolas", 16, "bold"))
        self.log_text.pack(fill="both", expand=True, pady=10)
        self.log_text.configure(state="disabled")
        """ ------ """

        """ Overlay """
        self.overlay_button = ctk.CTkButton(calibrate_frame, text="Show overlay (F1)", font=main_font,
                                            command=self.toggle_overlay, fg_color="purple")
        self.overlay_button.pack(pady=10, fill="x")

        self.bind("<F1>", lambda e: self.toggle_overlay())

        """ ------ """

    def toggle_overlay(self):
        self.overlay.toggle()

    def log_message(self, message: str):
        self.after(0, self._add_log_message, message)

    def _add_log_message(self, message: str):
        self.log_text.configure(state="normal")
        self.log_text.insert("end", f"{message}\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def start_bot(self):
        if not self.running:
            self.running = True
            self.start_button.configure(state="disabled")
            self.stop_button.configure(state="normal")
            self.status_label.configure(text="Status: Active")
            self.log_message("Bot is running")

            self.bot_thread = threading.Thread(target=self.bot_loop, daemon=True)
            self.bot_thread.start()
    
    def stop_bot(self):
        if self.running:
            self.running = False
            self.start_button.configure(state="normal")
            self.stop_button.configure(state="disabled")
            self.status_label.configure(text="Status: Inactive")
            self.log_message("Bot stopped")


    def get_images_from_directory(self, directory_path: str):
        image_extensions = ['.png', '.jpg', '.jpeg', '.webp']
        
        if not os.path.exists(directory_path):
            self.log_message(f"Директория не найдена: {directory_path}")
            return []
        
        all_files = os.listdir(directory_path)
        image_files = [file for file in all_files 
                      if any(file.lower().endswith(ext) for ext in image_extensions)]
        
        image_paths = [os.path.join(directory_path, file) for file in image_files]
        
        return image_paths
    
    def find_picture(self, templates: list[str], click: bool = False, 
                    debug: bool = False, debug_name: str = "", pass_value: float = 0.8) -> bool:
        try:
            screenshot = ImageGrab.grab()
            screenshot = np.array(screenshot)
            screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)

            for img in templates:
                if not os.path.exists(img):
                    continue
                    
                template = cv2.imread(img)
                if template is None:
                    continue
                    
                result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                
                if max_val > pass_value:
                    if click:
                        button_center = (max_loc[0] + template.shape[1]//2, 
                                        max_loc[1] + template.shape[0]//2)
                        pyautogui.click(button_center)
                    return True
            return False
        except Exception as e:
            self.log_message(f"find_picture error: {str(e)}")
            return False
    
    def check_ingame(self) -> bool:
        return self.find_picture(self.get_images_from_directory(self.dota_ui_templates_dir), 
                               click=False, pass_value=0.6, debug_name="in_game")
    
    def bot_loop(self):
        self.log_message("Bot loop started")
        try:
            while self.running:
                self.ingame_label.configure(text=f"State: {self.gsi.game_state}")


                if self.gsi.game_state == "main_menu":
                    if self.find_picture(self.get_images_from_directory(self.play_btn_templates_dir), 
                                        click=True, debug_name="Play Button"):
                        continue
                    
                    if self.find_picture(self.get_images_from_directory(self.find_game_templates_dir), 
                                        click=True, debug_name="Find Game"):
                        continue
                    
                    if self.find_picture(self.get_images_from_directory(self.accept_templates_dir), 
                                        click=True, debug_name="Accept Game"):
                        continue
                
                elif self.gsi.game_state == "hero_selection":
                    if self.find_picture(self.get_images_from_directory(self.rand_hero_templates_dir), 
                                        click=True, debug_name="Random Hero"):
                        continue
                
                
                elif self.gsi.game_state == "in_game":
                    if self.is_dota_active():
                        self.hero_bot.run_in_game()
                        self.find_picture(self.get_images_from_directory(self.up_spell_templates_dir), 
                                click=True, debug_name="Upgrade Spell")
                
                time.sleep(0.5)

        except Exception as e:
            self.log_message(f"Bot loop error: {e}")
        
        self.log_message("Bot loop stopped")

if __name__ == "__main__":
    app = BotManagerApp()
    app.mainloop()