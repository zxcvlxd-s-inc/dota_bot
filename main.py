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
from hero_bot import HeroBot
from game_data import GameData

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("green")


class BotManagerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Bot Manager")
        self.geometry("800x600")
        self.set_app_icon("icon.png")
        
        self.ingame: bool = False
        self.running: bool = False
        
        self.gsi = GameData()
        self.gsi.start()

        self.hero_bot:HeroBot = HeroBot(self.gsi, log_callback=self.log_message)
        
        self.accept_templates_dir: str = "img/accept_btn/"
        self.play_btn_templates_dir: str = "img/play_btn/"
        self.find_game_templates_dir: str = "img/find_game_btn"
        self.rand_hero_templates_dir: str = "img/rand_hero_btn/"
        self.dota_map_templates_dir: str = "img/dota_map/"
        self.up_spell_templates_dir: str = "img/up_spell/"
        self.shop_templates_dir: str = "img/shop/"
        self.dota_ui_templates_dir: str = "img/dota_ui/"
        
        self.setup_ui()
    

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
                print(f"Файл иконки не найден: {icon_filename}")
                
        except Exception as e:
            print(f"Ошибка установки иконки: {e}")

    def convert_png_to_ico(self, png_path: str, ico_path: str):
        try:
            img = Image.open(png_path)
            img.save(ico_path, format='ICO', sizes=[(16, 16), (32, 32), (48, 48), (64, 64)])
        except Exception as e:
            print(f"Ошибка конвертации PNG в ICO: {e}")

    def setup_ui(self):
        main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="black")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        
        title_label = ctk.CTkLabel(main_frame, text="Dota 2 AFK Bot Manager", 
                                  font=ctk.CTkFont(size=24, weight="bold"))
        title_label.pack(pady=20)
        
        self.status_label = ctk.CTkLabel(main_frame, text="Status: Inactive", 
                                        font=ctk.CTkFont(size=16))
        self.status_label.pack(pady=10)
        
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent", corner_radius=0)
        button_frame.pack(pady=20)
        
        self.start_button = ctk.CTkButton(button_frame, text="Start", 
                                         command=self.start_bot, width=120, corner_radius=0)
        self.start_button.pack(side="left", padx=10)
        
        self.stop_button = ctk.CTkButton(button_frame, text="Stop", 
                                        command=self.stop_bot, width=120, 
                                        fg_color="red", state="disabled", corner_radius=0)
        self.stop_button.pack(side="left", padx=10)

        self.ingame_label = ctk.CTkLabel(main_frame, text="Ingame: False", font=ctk.CTkFont(size=14, weight="bold"))
        self.ingame_label.pack(padx=10)

        log_label = ctk.CTkLabel(main_frame, text="Actions:", 
                                font=ctk.CTkFont(size=14, weight="bold"))
        log_label.pack(pady=(30, 10), anchor="w")
        
        self.log_text = ctk.CTkTextbox(main_frame, height=300, corner_radius=0)
        self.log_text.pack(fill="both", expand=True, pady=10)
        self.log_text.configure(state="disabled")
    

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
                        self.log_message(f"Click: {debug_name}")
                    return True
            return False
        except Exception as e:
            self.log_message(f"Ошибка в find_picture: {str(e)}")
            return False
    
    def check_ingame(self) -> bool:
        return self.find_picture(self.get_images_from_directory(self.dota_ui_templates_dir), 
                               click=False, pass_value=0.6, debug_name="in_game")
    
    def bot_loop(self):
        self.log_message("Bot loop started")
        try:
            while self.running:
                self.ingame_label.configure(text=f"Ingame: {self.ingame}")


                if not self.ingame:
                    if self.find_picture(self.get_images_from_directory(self.play_btn_templates_dir), 
                                        click=True, debug_name="Play Button"):
                        continue
                    
                    if self.find_picture(self.get_images_from_directory(self.find_game_templates_dir), 
                                        click=True, debug_name="Find Game"):
                        continue
                    
                    if self.find_picture(self.get_images_from_directory(self.accept_templates_dir), 
                                        click=True, debug_name="Accept Game"):
                        continue
                    
                    if self.find_picture(self.get_images_from_directory(self.rand_hero_templates_dir), 
                                        click=True, debug_name="Random Hero"):
                        continue
                
                
                self.ingame = self.check_ingame()
                self.log_message("Ingame: " + str(self.ingame))


                if self.ingame:
                    self.hero_bot.run_in_game()
                
                time.sleep(random.uniform(1, 2))
        except Exception as e:
            self.log_message(f"Bot loop error: {e}")
        
        self.log_message("Bot loop stopped")

if __name__ == "__main__":
    app = BotManagerApp()
    app.mainloop()