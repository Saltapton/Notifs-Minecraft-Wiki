import os, json, requests

API = "https://fr.minecraft.wiki/api.php"
s = requests.Session()
s.headers["User-Agent"] = "notif-bridge/0.1 (perso)"

u = os.environ["WIKI_USER"].strip()
p = os.environ["WIKI_PASS"].strip()

tok = s.get(API, params={"action": "query", "meta": "tokens",
    "type": "login", "format": "json"}).json()["query"]["tokens"]["logintoken"]
r = s.post(API, data={"action": "login", "lgname": u,
    "lgpassword": p, "lgtoken": tok, "format": "json"}).json()
assert r["login"]["result"] == "Success", r

d = s.get(API, params={"action": "query", "meta": "notifications",
    "notprop": "list", "notformat": "flyout", "notfilter": "!read",
    "notlimit": 50, "notwikis": "*", "format": "json"}).json()
if "query" not in d:
    raise SystemExit(f"Erreur API: {d}")
items = d["query"]["notifications"]["list"]

seen = set(json.load(open("seen.json"))) if os.path.exists("seen.json") else set()
for n in items:
    wiki = n.get("wiki", "")
    key = f"{wiki}:{n['id']}"
    if key in seen or str(n["id"]) in seen:
        continue
    star = n.get("*", "")
    raw = (star.get("header", "") if isinstance(star, dict) else star) or n.get("type", "Notification")
    lines = [l.strip() for l in html.unescape(re.sub(r"<[^>]+>", "\n", raw)).split("\n")]
    header = next((l for l in lines if l), "Notification")
    requests.post("https://ntfy.sh/", json={
        "topic": os.environ["NTFY_TOPIC"],
        "title": f"⛏️ {wiki or 'Minecraft Wiki'}",
        "message": header,
        "click": "https://fr.minecraft.wiki/",
    })
    seen.add(key)
json.dump(sorted(seen), open("seen.json", "w"))
