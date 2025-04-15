import requests
import time
import platform
import subprocess
from plyer import notification
import os
import warnings

# Suppress the dbus warning
warnings.filterwarnings("ignore", message="The Python dbus package is not installed")

# Configuration
API_URL = "https://midwaykebabish.ie/api/new-orders"
CHECK_INTERVAL = 30  # seconds
SOUND_FILE = os.path.join(os.path.dirname(__file__), "play.mp3")  # Full path to sound file
last_id = 0

def install_dbus():
    """Try to install dbus if not available"""
    try:
        import dbus
    except ImportError:
        print("DBus not found. Attempting to install...")
        import requests
import time
import platform
import subprocess
from plyer import notification
import os

# Configuration
API_URL = "https://midwaykebabish.ie/api/new-orders"
CHECK_INTERVAL = 30  # seconds
SOUND_FILE = "play.wav"  # Make sure this file exists in the same directory
last_id = 0

def play_sound():
    """Play notification sound twice with better quality"""
    try:
        if platform.system() == "Windows":
            # Windows: Using ffplay from FFmpeg for better quality
            for _ in range(2):
                subprocess.run(['ffplay', '-nodisp', '-autoexit', '-volume', '100', SOUND_FILE], 
                             creationflags=subprocess.CREATE_NO_WINDOW)
                time.sleep(0.3)  # Small delay between plays
        else:
            # Linux/Mac: Using aplay/afplay with higher quality
            for _ in range(2):
                subprocess.run(["aplay", "-q", SOUND_FILE])  # Linux
                # For Mac: subprocess.run(["afplay", SOUND_FILE])
                time.sleep(0.3)
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
        try:
            if platform.system() == "Linux":
                subprocess.run(["sudo", "apt-get", "install", "python3-dbus", "-y"], check=True)
            print("DBus installed successfully")
        except subprocess.CalledProcessError:
            print("Failed to install DBus. Notifications may not work properly")

def play_sound():
    """Play notification sound twice with better quality"""
    try:
        if not os.path.exists(SOUND_FILE):
            print(f"Sound file not found at {SOUND_FILE}")
            return
            
        if platform.system() == "Windows":
            # Windows: Using ffplay from FFmpeg
            for _ in range(2):
                subprocess.run(
                    ['ffplay', '-nodisp', '-autoexit', '-volume', '100', SOUND_FILE],
                    creationflags=subprocess.CREATE_NO_WINDOW,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                time.sleep(0.3)
        else:
            # Linux: Using paplay (PulseAudio) for better compatibility
            for _ in range(2):
                subprocess.run(
                    ["play.mp3", SOUND_FILE],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                time.sleep(0.3)
    except Exception as e:
        print(f"Couldn't play sound: {e}")

def show_notification(title, message):
    """Show desktop notification with fallback"""
    try:
        notification.notify(
            title=title,
            message=message,
            app_name="Midway Kebabish Order Notifier",
            timeout=10,
            app_icon=""  # Add path to icon if desired
        )
    except Exception as e:
        print(f"Couldn't show notification: {e}")
        # Fallback to terminal bell
        print("\a\a")  # Two system beeps

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
    # Try to install dbus if needed
    if platform.system() == "Linux":
        install_dbus()
    
    print("Midway Kebabish Order Notifier")
    print(f"Checking for new orders every {CHECK_INTERVAL} seconds...")
    print(f"Sound file location: {SOUND_FILE}\n")
    
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