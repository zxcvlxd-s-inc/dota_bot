import time
import threading
from typing import Callable, Optional

class Timer:
    def __init__(self):
        self.timeout: Optional[Callable] = None
        self.tick: Optional[Callable] = None
        self.started: Optional[Callable] = None
        self.stopped: Optional[Callable] = None
        
        self._duration:float = 0.0
        self._remaining:float = 0.0
        self._running:bool = False
        self._paused:bool = False
        self.one_shot:bool = False
        self._thread: Optional[threading.Thread] = None
        self._tick_interval = 0.1
    
    def start(self) -> None:
        if self._running:
            self.stop()
        
        self._duration
        self._remaining = self._duration
        self._running = True
        self._paused = False
        
        if self.started:
            self.started()
        
        self._thread = threading.Thread(target=self._countdown, daemon=True)
        self._thread.start()
    
    def stop(self) -> None:
        was_running = self._running
        self._running = False
        self._paused = False
        
        if was_running and self.stopped:
            self.stopped()
        
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)
    
    def connect(self, signal_name: str, callable_obj: Callable) -> bool:
        if signal_name == "timeout":
            self.timeout = callable_obj
            return True
        elif signal_name == "tick":
            self.tick = callable_obj
            return True
        elif signal_name == "started":
            self.started = callable_obj
            return True
        elif signal_name == "stopped":
            self.stopped = callable_obj
            return True
        return False
    
    def disconnect(self, signal_name: str) -> None:
        if signal_name == "timeout":
            self.timeout = None
        elif signal_name == "tick":
            self.tick = None
        elif signal_name == "started":
            self.started = None
        elif signal_name == "stopped":
            self.stopped = None
    
    def _countdown(self) -> None:
        start_time = time.time()
        target_time = start_time + self._duration
        last_tick_time = start_time
        
        while self._running and time.time() < target_time:
            current_time = time.time()
            
            if not self._paused:
                self._remaining = max(0, target_time - current_time)
                
                if self.tick and current_time - last_tick_time >= self._tick_interval:
                    self.tick(self._remaining)
                    last_tick_time = current_time
                
                time.sleep(0.01)
            else:
                time.sleep(0.1)
        
        if self._running and time.time() >= target_time:
            self._remaining = 0
            self._running = False
            if self.timeout:
                self.timeout()
            if not self.one_shot:
                self.start()
