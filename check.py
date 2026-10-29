import os, json, requests

API = "https://fr.minecraft.wiki/api.php"
s = requests.Session()
s.headers["User-Agent"] = "notif-bridge/0.1 (perso)"

tok = s.get(API, params={"action": "query", "meta": "tokens",
    "type": "login", "format": "json"}).json()["query"]["tokens"]["logintoken"]
r = s.post(API, data={"action": "login", "lgname": os.environ["WIKI_USER"],
    "lgpassword": os.environ["WIKI_PASS"], "lgtoken": tok, "format": "json"}).json()
u = os.environ["WIKI_USER"]; p = os.environ["WIKI_PASS"]
print("user:", len(u), "caracteres,", u.count("@"), "arobase, espaces en trop:", len(u) - len(u.strip()))
print("pass:", len(p), "caracteres, espaces en trop:", len(p) - len(p.strip()))
assert r["login"]["result"] == "Success", r

d = s.get(API, params={"action": "query", "meta": "notifications",
    "notprop": "list", "notformat": "text", "notfilter": "!read",
    "notlimit": 50, "format": "json"}).json()
items = d["query"]["notifications"]["list"]

seen = set(json.load(open("seen.json"))) if os.path.exists("seen.json") else set()
for n in items:
    if str(n["id"]) in seen:
        continue
    header = n.get("*", {}).get("header") or n.get("type", "Notification")
    requests.post(f"https://ntfy.sh/{os.environ['NTFY_TOPIC']}",
        data=header.encode("utf-8"),
        headers={"Title": "Minecraft Wiki", "Click": "https://fr.minecraft.wiki/"})
    seen.add(str(n["id"]))
json.dump(sorted(seen), open("seen.json", "w"))
