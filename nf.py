import requests
import time
import platform
import subprocess
from plyer import notification
import os
import warnings
import winsound  # Windows sound library

# Suppress the dbus warning
warnings.filterwarnings("ignore", message="The Python dbus package is not installed")

# Configuration
API_URL = "https://midwaykebabish.ie/api/new-orders"
CHECK_INTERVAL = 30  # seconds
SOUND_FILE = os.path.join(os.path.dirname(__file__), "play.wav")  # Using WAV for better quality with winsound
last_id = 0

def install_dependencies():
    """Check and install required dependencies"""
    try:
        if platform.system() == "Linux":
            # Check if dbus-python is installed
            try:
                import dbus
            except ImportError:
                print("Installing dbus-python...")
                subprocess.run(["sudo", "apt-get", "install", "python3-dbus", "-y"], check=True)
                
            # Check if sound utilities are installed
            try:
                subprocess.run(["paplay", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except FileNotFoundError:
                print("Installing PulseAudio utilities...")
                subprocess.run(["sudo", "apt-get", "install", "pulseaudio-utils", "-y"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Dependency installation failed: {e}")

def play_sound():
    """Play notification sound twice with optimal quality"""
    try:
        if not os.path.exists(SOUND_FILE):
            print(f"Sound file not found at {SOUND_FILE}")
            return
            
        if platform.system() == "Windows":
            # Windows: Using winsound for clean playback
            for _ in range(2):
                winsound.PlaySound(SOUND_FILE, winsound.SND_FILENAME | winsound.SND_ASYNC)
                time.sleep(0.5)  # Half second between plays
        else:
            # Linux/Mac: Using paplay with quality optimizations
            for _ in range(2):
                subprocess.run(
                    ["paplay", "--volume=65536", SOUND_FILE],  # Max volume (0-65536)
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                time.sleep(0.5)
    except Exception as e:
        print(f"Couldn't play sound: {e}")
        # Fallback to system beep
        print("\a\a")  # Two system beeps

def show_notification(title, message):
    """Show desktop notification with fallback"""
    try:
        notification.notify(
            title=title,
            message=message,
            app_name="Midway Kebabish Order Notifier",
            timeout=10,
            app_icon=os.path.join(os.path.dirname(__file__), "icon.png") if os.path.exists("icon.png") else None
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
    # Install required dependencies
    install_dependencies()
    
    print("Midway Kebabish Order Notifier")
    print(f"Checking for new orders every {CHECK_INTERVAL} seconds...")
    print(f"Sound file location: {SOUND_FILE}")
    print("Press Ctrl+C to stop\n")
    
    # Convert sound file to WAV if needed (Windows only)
    if platform.system() == "Windows" and not os.path.exists(SOUND_FILE):
        mp3_file = os.path.join(os.path.dirname(__file__), "play.mp3")
        if os.path.exists(mp3_file):
            print("Converting MP3 to WAV for better sound quality...")
            try:
                subprocess.run(
                    ["ffmpeg", "-i", mp3_file, "-acodec", "pcm_s16le", "-ar", "44100", SOUND_FILE],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    check=True
                )
            except:
                print("Failed to convert sound file. Using MP3 with reduced quality")
                SOUND_FILE = mp3_file
    
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