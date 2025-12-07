from db import get_last_readings, get_last_commands, get_last_events

print("\n--- Últimas 10 lecturas ---")
for r in get_last_readings(10):
    print((r["ts"], r["temp_c"], r["hum_pct"], r["light_pct"]))

print("\n--- Últimos 10 comandos ---")
for c in get_last_commands(10):
    print((c["ts"], c["command_string"], c["status"]))

print("\n--- Últimos 10 eventos ---")
for e in get_last_events(10):
    print((e["ts"], e["event_type"], e["payload"]))
