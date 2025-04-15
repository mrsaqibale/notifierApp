import requests
import time
import platform
import subprocess
from plyer import notification
# import winsound  # Windows only
import os

# Configuration
API_URL = "https://midwaykebabish.ie/api/new-orders"
CHECK_INTERVAL = 30  # seconds
SOUND_FILE = "/usr/share/sounds/freedesktop/stereo/message.oga"  # Linux sound path
last_id = 0

def play_sound():
    """Play notification sound based on OS"""
    try:
        if platform.system() == "Windows":
            print("e")
            # winsound.MessageBeep(winsound.MB_ICONASTERISK)
        elif os.path.exists(SOUND_FILE):
            subprocess.Popen(["play.mp3", SOUND_FILE])
    except Exception as e:
        print(f"Couldn't play sound: {e}")

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
    """Check internet connectivity"""
    try:
        requests.get("https://google.com", timeout=5)
        return True
    except:
        return False

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
                
                # Show notification and play sound
                show_notification("New Orders Alert", message)
                play_sound()
                
                # Print details to console
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
    print("Midway Kebabish Order Notifier")
    print(f"Checking for new orders every {CHECK_INTERVAL} seconds...\n")
    
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
