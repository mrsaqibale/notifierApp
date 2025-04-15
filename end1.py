import requests
import time
import os
import winsound
import sys
import ctypes
from plyer import notification
import threading

# =============== CONFIGURATION ===============
API_URL = "https://midwaykebabish.ie/api/new-orders"
CHECK_INTERVAL = 30  # Check every 30 seconds
SOUND_FILE = "play.wav"  # Your sound file (keep in same folder)
# ============================================

# Global variable to track last order ID
last_id = 0

# Hide console window immediately
def hide_console():
    if sys.executable.endswith("pythonw.exe"):
        return  # Already hidden
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

hide_console()  # Hide console on startup

# Play sound (3 beeps + notification sound)
def play_notification_sound():
    try:
        # 3 alert beeps first
        for _ in range(3):
            winsound.Beep(1000, 200)  # freq, duration
            time.sleep(0.1)
        
        # Play custom sound if available
        if os.path.exists(SOUND_FILE):
            winsound.PlaySound(SOUND_FILE, winsound.SND_FILENAME | winsound.SND_ASYNC)
    except:
        winsound.Beep(1500, 500)  # Fallback beep

# Show desktop notification
def show_notification(title, message):
    try:
        notification.notify(
            title=title,
            message=message,
            app_name="Order Notifier",
            timeout=10  # Notification stays for 10 sec
        )
    except:
        pass  # Silent fail if notification fails

# Check for new orders
def check_orders():
    global last_id
    try:
        response = requests.get(
            API_URL,
            params={"last_id": last_id},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            new_orders = data.get("orders", [])
            
            if new_orders:
                last_id = data["last_id"]
                order_count = len(new_orders)
                message = f"{order_count} new order(s) received!"
                
                # Show notification & play sound
                show_notification("📦 New Order!", message)
                play_notification_sound()
                
                # Optional: Log to file (instead of console)
                with open("order_log.txt", "a") as f:
                    f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")
                
            return True
        
        return False
        
    except:
        return False  # Silent fail on errors

# Main loop (runs in background)
def main_loop():
    while True:
        check_orders()
        time.sleep(CHECK_INTERVAL)

# Start the app
if __name__ == "__main__":
    # Start checking orders in background thread
    thread = threading.Thread(target=main_loop, daemon=True)
    thread.start()
    
    # Keep the app running (no window)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        sys.exit(0)