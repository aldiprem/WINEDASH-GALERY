# async_helpers.py
import asyncio
import threading
from functools import wraps

class AsyncLoopThread:
    """Thread yang menjalankan event loop asyncio secara terus menerus"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._started = False
        return cls._instance
    
    def start(self):
        if self._started:
            return self.loop
        
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        self._started = True
        
        # Tunggu sampai loop siap
        import time
        time.sleep(0.1)
        
        return self.loop
    
    def _run_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()
    
    def stop(self):
        if self._started:
            self.loop.call_soon_threadsafe(self.loop.stop)
            self.thread.join(timeout=5)
            self._started = False
    
    def run_coro(self, coro):
        """Jalankan coroutine di thread ini dan tunggu hasilnya"""
        if not self._started:
            self.start()
        
        future = asyncio.run_coroutine_threadsafe(coro, self.loop)
        return future.result(timeout=30)

# Singleton instance
async_loop = AsyncLoopThread()
