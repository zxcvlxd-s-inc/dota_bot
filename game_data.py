from flask import Flask, request
import threading
import logging
from typing import Optional, Callable

class DotaItem:
    def __init__(self, id_name:str):
        self.id_name = id_name

    
    def get_humanized_name(self) -> str:
        return self.id_name.replace("item_", "").replace("_", " ").title()

class GameData:
    def __init__(self, port=3000):
        self.app = Flask(__name__)
        self.port = port
        self.data = {}

        self.callbacks = []
        
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)

        @self.app.route('/', methods=['POST'])
        def update():
            new_data = request.json

            self.data = new_data


            for cb in self.callbacks:
                cb(self.data)


            return '', 200

    def start(self):
        server_thread = threading.Thread(target=self._run, daemon=True)
        server_thread.start()
        print(f"GSI Server started on port {self.port}")

    def _run(self):
        self.app.run(port=self.port, debug=False, use_reloader=False)

    def get_item(self, item_name: str) -> dict:
        for item in self.items:
            if item.get("name") == item_name:
                return item
        return {}


    def can_use_item(self, item_name: str) -> bool:
        item:dict = self.get_item(item_name)
        print(item)
        if item == {}:
            return False
        
        print(str(item.get("cooldown")))
        return item.get("cooldown") == 0
        

    @property
    def items(self) -> dict:
        return self.data.get("items", {}).values()

    @property
    def game_state(self) -> str:
        """
        - "main_menu"
        - "lobby"               → Лобби (ожидание старта)
        - "hero_selection"      → Выбор героя
        - "strategy_time"       → Время стратегии (pre-game)
        - "team_showcase"       → Показ героев
        - "pregame"             → Герои выбраны, карта загружается
        - "in_game"             → Игра идёт
        - "post_game"           → Игра закончилась
        - "unknown"             → Неизвестное состояние
        """
        map_data = self.data.get('map', {})
        game_state_raw = map_data.get('game_state', "")
        
        state_map = {
            "DOTA_GAMERULES_STATE_INIT": "main_menu",
            "DOTA_GAMERULES_STATE_HERO_SELECTION": "hero_selection",
            "DOTA_GAMERULES_STATE_STRATEGY_TIME": "strategy_time",
            "DOTA_GAMERULES_STATE_TEAM_SHOWCASE": "team_showcase",
            "DOTA_GAMERULES_STATE_PRE_GAME": "pregame",
            "DOTA_GAMERULES_STATE_GAME_IN_PROGRESS": "in_game",
            "DOTA_GAMERULES_STATE_POST_GAME": "post_game",
            "DOTA_GAMERULES_STATE_CUSTOM_GAME_SETUP": "lobby",
        }

        state = state_map.get(game_state_raw, "unknown")

        if state == "unknown":
            if not map_data.get("name"):
                return "main_menu"

        return state

    @property
    def time(self) -> int:
        return self.data.get('map', {}).get('game_time', -1)

    @property
    def hero_name(self) -> str:
        full_name = self.data.get("hero", {}).get("name", "")
        return full_name.replace("npc_dota_hero_", "") if full_name.startswith("npc_dota_hero_") else full_name

    @property
    def gold(self) -> int:
        return self.data.get('player', {}).get('gold', 0)

    @property
    def health_percent(self) -> int:
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
        return self.map_name != ""

    @property
    def team(self) -> str:
        """Возвращает 'radiant', 'dire' или 'none'"""
        return self.data.get('player', {}).get('team_name', "none").lower()

    @property
    def is_radiant(self) -> bool:
        return self.team == "radiant"

    @property
    def is_dire(self) -> bool:
        return self.team == "dire"

    @property
    def position(self) -> tuple[float, float]:
        pos = self.data.get('hero', {}).get('xpos'), self.data.get('hero', {}).get('ypos')
        if pos[0] is not None:
            return float(pos[0]), float(pos[1])
        return 0.0, 0.0