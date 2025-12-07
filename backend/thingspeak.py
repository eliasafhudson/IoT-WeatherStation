import requests

def write_channel(write_key, d):
    r = requests.post(
        "https://api.thingspeak.com/update.json",
        data={
            "api_key": write_key,
            "field1": d.get("temp_c"),
            "field2": d.get("hum_pct"),
            "field3": d.get("light_pct"),
        },
        timeout=10
    )
    r.raise_for_status()
    return r.json()

def execute_talkback(talkback_id, talkback_key):
    url = f"https://api.thingspeak.com/talkbacks/{talkback_id}/commands/execute.json"
    r = requests.post(url, data={"api_key": talkback_key}, timeout=10)
    r.raise_for_status()
    return r.json()  # {} si no hay comandos (comportamiento típico)
