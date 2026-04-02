from flask import Flask, request
import threading
import logging
from typing import Optional, Callable

class GameData:
    def __init__(self, port=3000):
        self.app = Flask(__name__)
        self.port = port
        self.data = {}

        self.on_update_callback: Optional[Callable[[dict], None]] = None
        
        # Отключаем спам Flask в консоль
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)

        # Маршрут, на который Дота шлет POST-запросы
        @self.app.route('/', methods=['POST'])
        def update():
            new_data = request.json

            self.data = new_data

            if self.on_update_callback:
                self.on_update_callback(self.data)
            
            return '', 200

    def start(self):
        """Запуск сервера в отдельном потоке"""
        server_thread = threading.Thread(target=self._run, daemon=True)
        server_thread.start()
        print(f"GSI Server started on port {self.port}")

    def _run(self):
        self.app.run(port=self.port, debug=False, use_reloader=False)

    
    @property
    def gold(self) -> int:
        return self.data.get('player', {}).get('gold', 0)

    @property
    def health_percent(self) -> int:
        # GSI отдает процент от 0 до 100
        return self.data.get('hero', {}).get('health_percent', 100)

    @property
    def is_alive(self) -> bool:
        return self.data.get('hero', {}).get('alive', True)

    @property
    def level(self) -> int:
        return self.data.get('hero', {}).get('level', 1)

    @property
    def map_name(self) -> str:
        return self.data.get('map', {}).get('name', "")

    @property
    def is_ingame(self) -> bool:
        # Проверка, находится ли игрок непосредственно в матче
        return self.map_name != ""

    @property
    def team(self) -> str:
        """Возвращает 'radiant', 'dire' или 'none'"""
        # Данные лежат в player -> team_name
        return self.data.get('player', {}).get('team_name', "none").lower()

    @property
    def is_radiant(self) -> bool:
        return self.team == "radiant"

    @property
    def is_dire(self) -> bool:
        return self.team == "dire"

    @property
    def position(self) -> tuple[float, float]:
        """Возвращает (x, y) героя на карте Доты (от -8000 до 8000)"""
        pos = self.data.get('hero', {}).get('xpos'), self.data.get('hero', {}).get('ypos')
        if pos[0] is not None:
            return float(pos[0]), float(pos[1])
        return 0.0, 0.0