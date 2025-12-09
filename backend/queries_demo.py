# Importamos las funciones que nos permiten leer datos de la base de datos.
from db import get_last_readings, get_last_commands, get_last_events

# ---------------- CONSULTAS DE DEMOSTRACIÓN ----------------

# 1. Mostrar las últimas 10 lecturas de sensores.
print("\n--- Últimas 10 lecturas ---")
for r in get_last_readings(10):   # Pedimos las 10 lecturas más recientes.
    # Mostramos la hora (ts), temperatura, humedad y luz.
    print((r["ts"], r["temp_c"], r["hum_pct"], r["light_pct"]))

# 2. Mostrar los últimos 10 comandos enviados al dispositivo.
print("\n--- Últimos 10 comandos ---")
for c in get_last_commands(10):   # Pedimos los 10 comandos más recientes.
    # Mostramos la hora, el texto del comando y su estado.
    print((c["ts"], c["command_string"], c["status"]))

# 3. Mostrar los últimos 10 eventos registrados.
print("\n--- Últimos 10 eventos ---")
for e in get_last_events(10):   # Pedimos los 10 eventos más recientes.
    # Mostramos la hora, el tipo de evento y los detalles (payload).
    print((e["ts"], e["event_type"], e["payload"]))
