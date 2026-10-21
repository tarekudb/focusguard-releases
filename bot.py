import os
import time
import requests
import json
import base64

BOT_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
GH_TOKEN = os.environ.get('GH_PAT')
REPO = "tarekudb/focusguard-releases"
PREMIUM_FILE = "premium.json"
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"

try:
    requests.get(f"{API_URL}deleteWebhook?drop_pending_updates=true", timeout=10)
except Exception as e:
    print(f"Webhook delete error: {e}")

def get_premium_data():
    headers = {"Authorization": f"token {GH_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    url = f"https://api.github.com/repos/{REPO}/contents/{PREMIUM_FILE}"
    r = requests.get(url, headers=headers, timeout=10)
    if r.status_code == 200:
        data = r.json()
        content = base64.b64decode(data['content']).decode('utf-8')
        return json.loads(content), data['sha']
    return {"users": []}, None

def update_premium(device_id):
    data, sha = get_premium_data()
    if device_id in data.get("users", []):
        return True
    
    data.setdefault("users", []).append(device_id)
    content_encoded = base64.b64encode(json.dumps(data, indent=2).encode('utf-8')).decode('utf-8')
    headers = {"Authorization": f"token {GH_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    url = f"https://api.github.com/repos/{REPO}/contents/{PREMIUM_FILE}"
    payload = {
        "message": f"Add premium user {device_id[:6]}",
        "content": content_encoded,
        "branch": "main"
    }
    if sha:
        payload["sha"] = sha
    
    r = requests.put(url, headers=headers, json=payload, timeout=10)
    return r.status_code in [200, 201]

def main():
    print("Bot started successfully. Waiting for messages...", flush=True)
    last_update_id = 0
    
    while True:
        try:
            url = f"{API_URL}getUpdates?offset={last_update_id + 1}&timeout=20"
            r = requests.get(url, timeout=25)
            
            if r.status_code == 200:
                updates = r.json().get('result', [])
                for update in updates:
                    last_update_id = update['update_id']
                    if 'callback_query' in update:
                        cb = update['callback_query']
                        data = cb['data']
                        msg_id = cb['message']['message_id']
                        
                        if data.startswith("approve_"):
                            # ১. টেলিগ্রামের লোডিং বন্ধ করা (সাথে সাথে উত্তর দেওয়া)
                            requests.post(f"{API_URL}answerCallbackQuery", json={"callback_query_id": cb['id'], "text": "✅ Approved!"}, timeout=10)
                            
                            # ২. গিটহাবে ডেটা পাঠানো
                            device_id = data.replace("approve_", "")
                            update_premium(device_id)
                            
                            # ৩. মেসেজ পরিবর্তন করা
                            requests.post(f"{API_URL}editMessageText", json={
                                "chat_id": CHAT_ID,
                                "message_id": msg_id,
                                "text": f"✅ Approved Premium for Device: {device_id}",
                                "reply_markup": {"inline_keyboard": []}
                            }, timeout=10)
                            
                        elif data.startswith("reject_"):
                            requests.post(f"{API_URL}answerCallbackQuery", json={"callback_query_id": cb['id'], "text": "❌ Rejected"}, timeout=10)
                            requests.post(f"{API_URL}editMessageText", json={
                                "chat_id": CHAT_ID,
                                "message_id": msg_id,
                                "text": f"❌ Rejected Payment",
                                "reply_markup": {"inline_keyboard": []}
                            }, timeout=10)
            time.sleep(1)
        except Exception as e:
            print(f"Error: {e}", flush=True)
            time.sleep(5)

if __name__ == "__main__":
    main()
