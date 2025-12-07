# 🌦 IoT Weather Station – ESP32 + Wokwi + MQTT + ThingSpeak + SQLite

Proyecto desarrollado para simular una **estación meteorológica IoT completa** usando:

- ESP32 con MicroPython (simulado en Wokwi)
- Sensores: DHT22 (temp/humedad) + LDR (luz)
- Actuadores: LED + Buzzer + Pantalla OLED
- Comunicación MQTT (broker EMQX)
- Plataforma Cloud: ThingSpeak (telemetría + TalkBack)
- Base de datos local: SQLite (histórico y eventos)
- Backend Python (procesamiento, guardado y control)

El sistema permite:

✔ Lectura de sensores en tiempo real  
✔ Publicación de telemetría vía MQTT  
✔ Control remoto desde la nube (LED, BEEP)  
✔ Registros de histórico en base de datos  
✔ Dashboard en ThingSpeak con gráficas en tiempo real  
✔ Ejecución automática de comandos desde TalkBack  

---

# 📡 Arquitectura General del Sistema

┌─────────────┐ MQTT ┌──────────────┐
│ ESP32 │ ─────────────────▶│ EMQX Cloud │
│ Wokwi IoT │◀──────────────────│ (broker MQTT) │
└──────┬──────┘ └──────────────┘
│ Telemetría │
│ ▼
│ ┌──────────────┐
│ │ Backend │
│ │ Python + DB │
│ └──────┬───────┘
│ │
▼ │
┌──────────────┐ ┌──────────▼─────────┐
│ ThingSpeak │◀──────────────│ SQLite (histórico) │
│ Canal + │──────────────▶│ Guardado local │
│ TalkBack │ comandos └────────────────────┘
└──────────────┘

IoT-WeatherStation/
│
├── backend/
│ ├── main.py
│ ├── db.py
│ ├── thingspeak.py
│ ├── requirements.txt
│ ├── weather.db (generado automáticamente)
│ └── .env
│
├── device/
│ ├── main.py
│ ├── sensors.py
│ ├── actuators.py
│ ├── wifi_mgr.py
│ ├── mqtt_mgr.py
│ ├── config.py
│ └── libs (opcional)
│
├── wokwi/
│ └── diagram.json
│
├── docs/
│ ├── arquitectura_iot.md
│ ├── flujo_datos.png
│ └── configuracion_cloud.md
│
└── README.md


---

# ⚙️ Configuración de la Plataforma Cloud (ThingSpeak)

## 1️⃣ Crear un canal en ThingSpeak

1. Entrar a: https://thingspeak.com
2. Create New Channel
3. Activar:
   - Field 1 → Temperature
   - Field 2 → Humidity
   - Field 3 → Light %

4. Guardar el **WRITE API KEY**  
   Lo usará el backend.

---

## 2️⃣ Crear TalkBack para comandos

1. MENÚ → Apps → TalkBack → New TalkBack  
2. Guardar:
   - `TalkBack ID`
   - `TalkBack API KEY`
3. Agregar comandos de ejemplo:
   - `LED=1`
   - `LED=0`
   - `BEEP=300`

---

## 3️⃣ Backend escribe telemetría con:

POST https://api.thingspeak.com/update.json


## 4️⃣ Backend extrae comandos con:

POST https://api.thingspeak.com/talkbacks/{ID}/commands/execute


El backend los publica al ESP32 por MQTT.

---

# 🔄 Diagrama de Flujo de Datos (explicado)

ESP32 (MicroPython)
│
│ Lectura sensores cada 1 seg.
│ Publica telemetría MQTT → topic: iot/weather/.../telemetry
▼
Broker MQTT (EMQX)
│
│ Recibe telemetría del ESP32
│ Entrega mensajes al backend
▼
Backend Python
│ Guarda en SQLite
│ Procesa alertas (HOT, DARK)
│ Envía datos a ThingSpeak cada 16 s
│ Consulta TalkBack cada 5 s
│ Publica comandos MQTT → topic: .../cmd
▼
ESP32
│ Recibe comandos:
│ LED=1 → enciende LED
│ LED=0 → apaga LED
│ BEEP=300 → suena buzzer
│ Muestra estado en OLED
▼
Usuario observa dashboard en ThingSpeak


---

# 🌐 Conexión MQTT

### Topics del sistema:

| Propósito | Topic |
|----------|--------|
| Telemetría | `iot/weather/ws-esp32-001/telemetry` |
| Comandos al ESP32 | `iot/weather/ws-esp32-001/cmd` |
| Eventos desde el dispositivo | `iot/weather/ws-esp32-001/event` |

Broker:

broker.emqx.io
port: 1883


---

# 🗄 Base de Datos (SQLite)

El backend crea **weather.db** con tablas automáticas:

### Tabla readings (telemetría)
```sql
CREATE TABLE readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts INTEGER,
    temp REAL,
    humidity REAL,
    light INTEGER
);

Tabla commands (registro de comandos)
CREATE TABLE commands (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts INTEGER,
    command TEXT,
    status TEXT
);

Tabla events (eventos enviados por ESP32)

CREATE TABLE events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts INTEGER,
    type TEXT,
    data TEXT
);

