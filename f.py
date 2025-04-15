import requests

# API URL (replace with your actual domain)
API_URL = "https://midwaykebabish.ie/api/new-orders"

# Optional query parameter (last_id)
params = {
    "last_id": 0  # Change this if testing pagination
}

try:
    # Make GET request
    response = requests.get(API_URL, params=params)
    
    # Check if request was successful (HTTP 200)
    if response.status_code == 200:
        data = response.json()
        
        print("✅ API is working!")
        print(f"Total new orders: {data['count']}")
        print(f"Last order ID: {data['last_id']}")
        
        # Print first order details (if available)
        if data["orders"]:
            first_order = data["orders"][0]
            print("\n📦 First order details:")
            print(f"Order ID: {first_order['id']}")
            print(f"Status: {first_order['order_status']}")
            print(f"User: {first_order['user_name']['name']}")  # Assuming 'userName' relation exists
        else:
            print("No new orders found.")
    else:
        print(f"❌ API returned an error (HTTP {response.status_code})")
        print(response.text)

except requests.exceptions.RequestException as e:
    print(f"❌ Failed to connect to the API: {e}")
