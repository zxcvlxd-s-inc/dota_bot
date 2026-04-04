import tkinter as tk
from custom_math import Rect, Vector


class ScreenRectSelector:
    def __init__(self):
        # Инициализируем все атрибуты
        self.callback = None
        self.selection_window = None
        self.canvas = None
        self.rect_start = None
        self.current_rect = None
        self.selected_name = None

    def select_rect(self, name: str, on_selected):
        self.selected_name = name
        self.callback = on_selected
        self.start_selection()

    def start_selection(self):
        # Убедимся, что предыдущее окно закрыто
        if self.selection_window is not None:
            self.cleanup()

        self.selection_window = tk.Toplevel()
        self.selection_window.attributes("-fullscreen", True)
        self.selection_window.attributes("-topmost", True)
        self.selection_window.overrideredirect(True)
        self.selection_window.config(bg='black')
        self.selection_window.wm_attributes("-alpha", 0.3)

        self.canvas = tk.Canvas(self.selection_window, cursor="cross", bg="white")
        self.canvas.pack(fill="both", expand=True)

        self.canvas.bind("<ButtonPress-1>", self.on_mouse_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_release)
        self.selection_window.bind("<Escape>", self.on_escape)

        self.selection_window.focus_force()

    def on_mouse_press(self, event):
        self.rect_start = (event.x, event.y)
        if self.current_rect:
            if self.canvas:
                self.canvas.delete(self.current_rect)
        self.current_rect = None  # Сбросим текущий прямоугольник

    def on_mouse_drag(self, event):
        if not self.rect_start or not self.canvas:
            return

        x1, y1 = self.rect_start
        x2, y2 = event.x, event.y

        # Удаляем старый прямоугольник
        if self.current_rect:
            self.canvas.delete(self.current_rect)

        # Рисуем новый
        self.current_rect = self.canvas.create_rectangle(
            x1, y1, x2, y2,
            outline="red", width=2, fill="lightcoral"
        )

    def on_mouse_release(self, event):
        if not self.rect_start:
            return

        x1, y1 = self.rect_start
        x2, y2 = event.x, event.y
        x1, x2 = sorted([x1, x2])
        y1, y2 = sorted([y1, y2])

        width = x2 - x1
        height = y2 - y1
        rect = Rect(Vector(x1, y1), Vector(width, height))

        if self.callback:
            self.callback(self.selected_name, rect)

        self.cleanup()

    def on_escape(self, event=None):
        self.cleanup()

    def cleanup(self):
        """Безопасная очистка — без `del`"""
        if self.selection_window:
            try:
                self.selection_window.unbind("<Escape>")
                self.selection_window.destroy()
            except tk.TclError:
                pass  # Окно уже уничтожено
            self.selection_window = None

        self.canvas = None
        self.rect_start = None
        self.current_rect = None
        self.selected_name = None
        self.callback = None
        # Не используем `del` — просто обнуляем ссылки