# async_helpers.py
import asyncio
import threading
from concurrent.futures import TimeoutError

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
                    cls._instance._loop = None
                    cls._instance._thread = None
        return cls._instance
    
    def start(self):
        if self._started and self._loop and self._loop.is_running():
            return self._loop
        
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._run_loop, daemon=True, name="AsyncLoopThread")
        self._thread.start()
        self._started = True
        
        # Tunggu sampai loop siap
        import time
        timeout = 5
        start_time = time.time()
        while not self._loop.is_running() and time.time() - start_time < timeout:
            time.sleep(0.1)
        
        if not self._loop.is_running():
            raise RuntimeError("Failed to start async loop thread")
        
        return self._loop
    
    def _run_loop(self):
        asyncio.set_event_loop(self._loop)
        try:
            self._loop.run_forever()
        except Exception as e:
            print(f"Async loop error: {e}")
        finally:
            self._loop.close()
    
    def stop(self):
        if self._started and self._loop:
            self._loop.call_soon_threadsafe(self._loop.stop)
            if self._thread:
                self._thread.join(timeout=5)
            self._started = False
            self._loop = None
            self._thread = None
    
    def run_coro(self, coro, timeout=30):
        """Jalankan coroutine di thread ini dan tunggu hasilnya"""
        if not self._started:
            self.start()
        
        if not self._loop or not self._loop.is_running():
            raise RuntimeError("Async loop is not running")
        
        future = asyncio.run_coroutine_threadsafe(coro, self._loop)
        try:
            return future.result(timeout=timeout)
        except TimeoutError:
            future.cancel()
            raise TimeoutError(f"Coroutine timed out after {timeout} seconds")
        except Exception as e:
            raise e

# Singleton instance
async_loop = AsyncLoopThread()