import tkinter as tk
from custom_math import Rect


class OverlayVisualizer:
    """
    Класс для отображения полупрозрачного оверлея с именами и границами калибровочных областей.
    """

    def __init__(self, world_rects: dict, scale: float = 0.8):
        """
        :param world_rects: Словарь Rect'ов (название -> Rect)
        :param scale: Прозрачность оверлея (0.0 - прозрачный, 1.0 - непрозрачный)
        """
        self.world_rects = world_rects
        self.scale = scale

        self.root = None
        self.is_visible = False

    def start(self):
        if self.is_visible:
            return

        self.is_visible = True

        self.root = tk.Toplevel()
        self.root.overrideredirect(True)
        self.root.geometry(f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}+0+0")
        self.root.attributes("-topmost", True)
        self.root.wm_attributes("-alpha", self.scale)

        transparent_color = "gray1"
        self.root.config(bg=transparent_color)
        self.root.wm_attributes("-transparentcolor", transparent_color)

        canvas = tk.Canvas(self.root, bg=transparent_color, highlightthickness=0)
        canvas.pack(fill="both", expand=True)

        self.draw_rects(canvas)

        self.root.bind("<Button-3>", self.stop)
        self.root.bind("<Escape>", self.stop)

        self.update_id = self.root.after(2000, lambda: self.update_overlay(canvas))

    def draw_rects(self, canvas: tk.Canvas):
        canvas.delete("all")

        for name, rect in self.world_rects.items():
            x = rect.position.x
            y = rect.position.y
            w = rect.size.x
            h = rect.size.y

            canvas.create_rectangle(
                x, y, x + w, y + h,
                outline="red", width=2, fill=""
            )

            canvas.create_text(
                x + 5, y - 5,
                text=name,
                fill="yellow", font=("Consolas", 10, "bold"),
                anchor="nw",
                tags="text"
            )

    def update_overlay(self, canvas: tk.Canvas):
        if self.is_visible:
            self.draw_rects(canvas)
            self.update_id = canvas.after(2000, lambda: self.update_overlay(canvas))

    def update_rects(self, new_rects: dict):
        """Обновляет данные об областях."""
        self.world_rects = new_rects
        if self.is_visible:
            #redraw if overlay is active 
            pass

    def stop(self, event=None):
        if self.root:
            if not self.is_visible:
                return

            self.is_visible = False
            if hasattr(self, 'update_id'):
                self.root.after_cancel(self.update_id)
            self.root.destroy()
            self.root = None

    def toggle(self):
        if self.is_visible:
            self.stop()
        else:
            self.start()