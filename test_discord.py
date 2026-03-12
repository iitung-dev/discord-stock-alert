import os
import requests

DISCORD_URL = os.environ.get('DISCORD_WEBHOOK')

def send_test():
    if not DISCORD_URL:
        print("❌ ERROR: DISCORD_WEBHOOK not found in environment!")
        return

    payload = {
        "embeds": [{
            "title": "✅ Test Connection Successful",
            "color": 3066993, # Green
            "description": "If you are reading this, your GitHub Action and Discord Webhook are working perfectly!",
            "fields": [
                {"name": "Status", "value": "Operational", "inline": True},
                {"name": "Environment", "value": "GitHub Actions", "inline": True}
            ]
        }]
    }
    
    response = requests.post(DISCORD_URL, json=payload)
    if response.status_code == 204:
        print("🚀 Test message sent to Discord!")
    else:
        print(f"❌ Failed to send. Status code: {response.status_code}")

if __name__ == "__main__":
    send_test()