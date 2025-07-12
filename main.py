import json
import re
import requests

# Carica il JSON da file
with open("data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Username da controllare
username = "blue"

headers = {
    "User-Agent": "Mozilla/5.0"  # Per evitare blocchi da alcuni siti
}

include_nsfw = False

# Funzione principale
def check_username(username):
    results = {}
    for site, info in data.items():
        try:
            if "url" not in info:
                continue  # Salta se manca l'URL
            
            # Filtra NSFW se richiesto
            if not include_nsfw and info.get("isNSFW", False):
                continue

            # RegexCheck (opzionale)
            if "regexCheck" in info:
                if not re.match(info["regexCheck"], username):
                    results[site] = "Invalid username format"
                    continue

            url = info["url"].format(username)
            r = requests.get(url, headers=headers, timeout=10)

            if info["errorType"] == "status_code":
                if r.status_code == 200:
                    results[site] = "Found ✅"
                    print("[FOUND] --> " + url)
                else:
                    results[site] = "Not found ❌"

            elif info["errorType"] == "message":
                content = r.text
                error_msgs = info["errorMsg"]
                if isinstance(error_msgs, str):
                    error_msgs = [error_msgs]

                if any(err in content for err in error_msgs):
                    results[site] = "Not found ❌"
                else:
                    results[site] = "Found ✅"

        except Exception as e:
            results[site] = f"Error: {str(e)}"

    return results

# Esegui e stampa
results = check_username(username)
for site, status in results.items():
    print(f"{site}: {status}")

