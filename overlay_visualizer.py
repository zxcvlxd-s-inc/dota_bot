import tkinter as tk
from custom_math import Rect, Vector

from game_data import GameData

class OverlayVisualizer:
    def __init__(self, world_rects: dict, gsi:GameData, scale: float = 0.8):
        self.world_rects = world_rects
        self.scale = scale
        self.root = None
        self.canvas = None
        self.update_id = None
        self.is_visible = False
        self.gsi = gsi


        self.gsi.callbacks.append(self.on_sgi_update)

    def start(self):
        if self.root is not None:
            self.stop()

        self.is_visible = True
        self.root = tk.Toplevel()
        self.root.overrideredirect(True)
        self.root.geometry(f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}+0+0")
        self.root.attributes("-topmost", True)
        self.root.wm_attributes("-alpha", self.scale)

        transparent_color = "gray1"
        self.root.config(bg=transparent_color)
        self.root.wm_attributes("-transparentcolor", transparent_color)

        self.canvas = tk.Canvas(self.root, bg=transparent_color, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.draw_rects()

        self.root.bind("<Button-3>", self.stop)
        self.root.bind("<Escape>", self.stop)

        self.update_id = self.root.after(2000, self.update_overlay)

    def on_sgi_update(self, new_data):
        if self.is_visible:
            if self.canvas:
                self.canvas.delete("pos_text")

                self.canvas.create_text(
                    250, 50,
                    text=f"position: {self.gsi.position}",
                    fill="white",
                    font=("Consolas", 16, "bold"),
                    tags="pos_text"
                )
                

    def world_to_minimap(self, world_x: float, world_y: float) -> tuple[int, int]:
        MAP_MIN, MAP_MAX = -8192, 8192
        MAP_SIZE = MAP_MAX - MAP_MIN #16384
        
        map_rect:Rect = Rect(Vector(159, 756), Vector(233, 233))

        norm_x = (world_x - MAP_MIN) / MAP_SIZE
        norm_y = 1 - ((world_y - MAP_MIN) / MAP_SIZE)

        screen_x = int(map_rect.position.x + (norm_x * map_rect.size.x))
        screen_y = int(map_rect.position.y + (norm_y * map_rect.size.y))
        
        return screen_x, screen_y

    def draw_rects(self):
        if not self.canvas:
            return
        self.canvas.delete("all")
        for name, rect in self.world_rects.items():
            x = rect.position.x
            y = rect.position.y
            w = rect.size.x
            h = rect.size.y
            self.canvas.create_rectangle(x, y, x + w, y + h, outline="red", width=2, fill="")
            self.canvas.create_text(
                x + 5, y - 5,
                text=name,
                fill="yellow", font=("Consolas", 10, "bold"),
                anchor="nw"
            )

    def update_overlay(self):
        if self.is_visible and self.root and self.canvas:
            self.draw_rects()
            self.update_id = self.canvas.after(2000, self.update_overlay)
        else:
            self.update_id = None

    def update_rects(self, new_rects: dict):
        self.world_rects = new_rects
        if self.is_visible and self.canvas:
            self.draw_rects()

    def stop(self, event=None):
        if self.root is None:
            return

        try:
            self.is_visible = False
            if self.update_id is not None:
                try:
                    self.root.after_cancel(self.update_id)
                except Exception:
                    pass
                self.update_id = None

            self.root.destroy()
        except Exception as e:
            print(f"[OverlayVisualizer] Ошибка при остановке: {e}")
        finally:
            self.root = None
            self.canvas = None

    def toggle(self):
        if self.is_visible:
            self.stop()
        else:
            self.start()