import requests
import time
import winsound
from plyer import notification
import os
import sys

# Configuration
API_URL = "https://midwaykebabish.ie/api/new-orders"
CHECK_INTERVAL = 30  # seconds
SOUND_FILE = os.path.join(os.path.dirname(__file__), "play.wav")  # Must be WAV format
last_id = 0

def play_sound():
    """Play WAV file twice using winsound"""
    try:
        if not os.path.exists(SOUND_FILE):
            print(f"Sound file not found at {SOUND_FILE}")
            return
            
        for _ in range(2):
            winsound.PlaySound(SOUND_FILE, winsound.SND_FILENAME | winsound.SND_ASYNC)
            time.sleep(0.5)  # Half second between plays
    except Exception as e:
        print(f"Couldn't play sound: {e}")
        # Fallback to system beep
        winsound.Beep(1000, 200)  # Frequency 1000Hz, duration 200ms

def show_notification(title, message):
    """Show desktop notification"""
    try:
        notification.notify(
            title=title,
            message=message,
            app_name="Midway Kebabish Order Notifier",
            timeout=10
        )
    except Exception as e:
        print(f"Couldn't show notification: {e}")

def check_internet():
    """Check internet connectivity with multiple attempts"""
    attempts = 3
    for _ in range(attempts):
        try:
            requests.get("https://google.com", timeout=5)
            return True
        except:
            time.sleep(2)
    return False

def check_orders():
    global last_id
    try:
        response = requests.get(
            API_URL,
            params={"last_id": last_id},
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            new_orders = data.get("orders", [])
            
            if new_orders:
                last_id = data["last_id"]
                order_count = len(new_orders)
                message = f"{order_count} new order(s) received!"
                
                show_notification("New Orders Alert", message)
                play_sound()
                
                print(f"\n🔔 {message}")
                for order in new_orders:
                    print(f"\nOrder ID: {order['id']}")
                    print(f"Customer: {order.get('user_name', {}).get('name', 'N/A')}")
                    print(f"Status: {order.get('order_status', 'N/A')}")
                    print(f"Amount: {order.get('total_amount', 'N/A')}")
            
            return True
        
        print(f"API Error: HTTP {response.status_code}")
        return False
        
    except requests.exceptions.RequestException as e:
        print(f"Connection Error: {e}")
        return False

def main():
    # Hide console window
    if sys.platform == 'win32':
        import ctypes
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    
    print("Midway Kebabish Order Notifier")
    print(f"Checking for new orders every {CHECK_INTERVAL} seconds...")
    print(f"Sound file location: {SOUND_FILE}")
    print("Running in background - close from Task Manager to stop\n")
    
    # Verify sound file exists and is WAV format
    if not os.path.exists(SOUND_FILE):
        print(f"Error: Sound file not found at {SOUND_FILE}")
        print("Please place a 'play.wav' file in the same directory")
        return
    
    while True:
        if check_internet():
            check_orders()
        else:
            print("⚠️ No internet connection - retrying in 30 seconds")
            show_notification("Connection Lost", "No internet connection detected")
        
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopping order notifier...")
    except Exception as e:
        print(f"Fatal error: {e}")