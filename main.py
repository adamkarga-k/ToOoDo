#!/usr/bin/env python3
"""
ToOoDo (Windows Minimalist To-Do Strip)
Ultra düşük RAM (~18 MB) ve %0 CPU tüketimi ile çalışan minimalist To-Do şeridi.
"""
import sys
import os
import ctypes

# Proje dizinini ekle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bar_ui import TaskbarTodoApp

MUTEX_NAME = "Global\\ToOoDo_SingleInstance_Mutex"

def acquire_single_instance_lock():
    kernel32 = ctypes.windll.kernel32
    mutex = kernel32.CreateMutexW(None, True, MUTEX_NAME)
    ERROR_ALREADY_EXISTS = 183
    if kernel32.GetLastError() == ERROR_ALREADY_EXISTS:
        return None
    return mutex

def main():
    mutex = acquire_single_instance_lock()
    if not mutex:
        # Zaten arka planda çalışan bir kopya var, ikincisini açma
        print("Uygulama zaten çalışıyor.")
        sys.exit(0)

    app = TaskbarTodoApp()
    try:
        app.run()
    finally:
        if mutex:
            ctypes.windll.kernel32.ReleaseMutex(mutex)
            ctypes.windll.kernel32.CloseHandle(mutex)

if __name__ == "__main__":
    main()
