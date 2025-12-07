import sqlite3
import json
import os

BASE_DIR = os.path.dirname(__file__)
DB = os.path.join(BASE_DIR, "iot_weather.db")

def init_db():
    con = sqlite3.connect(DB)
    schema_path = os.path.join(BASE_DIR, "schema.sql")
    with open(schema_path, "r", encoding="utf-8") as f:
        con.executescript(f.read())
    con.commit()
    con.close()

def insert_reading(d):
    con = sqlite3.connect(DB)
    con.execute(
        "INSERT INTO sensor_readings (ts,temp_c,hum_pct,light_pct) VALUES (?,?,?,?)",
        (int(d["ts"]), d.get("temp_c"), d.get("hum_pct"), d.get("light_pct"))
    )
    con.commit()
    con.close()

def log_command(cmd_str, status):
    import time
    con = sqlite3.connect(DB)
    con.execute(
        "INSERT INTO command_log (ts,command_string,status) VALUES (?,?,?)",
        (int(time.time()), cmd_str, status)
    )
    con.commit()
    con.close()

def insert_event(ts, event_type, payload_dict):
    con = sqlite3.connect(DB)
    payload_str = json.dumps(payload_dict)
    con.execute(
        "INSERT INTO event_log (ts, event_type, payload) VALUES (?,?,?)",
        (int(ts), event_type, payload_str)
    )
    con.commit()
    con.close()

def get_last_readings(limit=10):
    con = sqlite3.connect(DB)
    cur = con.execute(
        "SELECT ts,temp_c,hum_pct,light_pct FROM sensor_readings ORDER BY ts DESC LIMIT ?",
        (int(limit),)
    )
    rows = cur.fetchall()
    con.close()
    return [
        {"ts": r[0], "temp_c": r[1], "hum_pct": r[2], "light_pct": r[3]}
        for r in rows
    ]

def get_last_commands(limit=10):
    con = sqlite3.connect(DB)
    cur = con.execute(
        "SELECT ts,command_string,status FROM command_log ORDER BY ts DESC LIMIT ?",
        (int(limit),)
    )
    rows = cur.fetchall()
    con.close()
    return [
        {"ts": r[0], "command_string": r[1], "status": r[2]}
        for r in rows
    ]

def get_last_events(limit=10):
    con = sqlite3.connect(DB)
    cur = con.execute(
        "SELECT ts,event_type,payload FROM event_log ORDER BY ts DESC LIMIT ?",
        (int(limit),)
    )
    rows = cur.fetchall()
    con.close()
    return [
        {"ts": r[0], "event_type": r[1], "payload": r[2]}
        for r in rows
    ]
