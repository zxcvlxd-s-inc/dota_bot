import tkinter as tk
from custom_math import Rect


class OverlayVisualizer:
    def __init__(self, world_rects: dict, scale: float = 0.8):
        self.world_rects = world_rects
        self.scale = scale
        self.root = None
        self.canvas = None
        self.update_id = None
        self.is_visible = False

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