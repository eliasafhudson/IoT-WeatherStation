# Arquitectura IoT – Weather Station ESP32

## Resumen
- Dispositivo ESP32 (MicroPython/Wokwi) lee sensores DHT22 y LDR y controla LED/Buzzer/OLED.
- Comunicación mediante MQTT con broker EMQX (`broker.emqx.io`).
- Backend Python recibe telemetría y eventos, guarda en SQLite y envía datos a ThingSpeak.
- ThingSpeak visualiza en tiempo real y entrega comandos por TalkBack al backend.
- Backend publica comandos MQTT que el ESP32 ejecuta y reporta como eventos.

## Componentes
- Dispositivo IoT (ESP32): `device/main.py`, `device/sensors.py`, `device/actuators.py`, `device/mqtt_mgr.py`, `device/config.py`.
- Broker MQTT (EMQX): servicio público `broker.emqx.io:1883`.
- Backend Python: `backend/main.py`, `backend/db.py`, `backend/thingspeak.py`.
- Base de datos local: SQLite (`backend/iot_weather.db`) con esquema en `backend/schema.sql`.
- Plataforma Cloud: ThingSpeak (canal de telemetría, TalkBack para comandos).

## Flujo de Datos
1. ESP32 mide temperatura/humedad/luz cada segundo: `device/sensors.py:12-23`.
2. Publica telemetría cada `TELE_INTERVAL_SEC`: `device/main.py:89-96`.
3. Broker EMQX entrega telemetría y eventos al backend: `backend/main.py:27-31`.
4. Backend guarda lecturas/eventos en SQLite: `backend/main.py:38-52`.
5. Backend envía lecturas a ThingSpeak cada ~16s: `backend/main.py:85-93`.
6. Backend consulta TalkBack y publica comandos MQTT: `backend/main.py:95-105`.
7. ESP32 recibe comandos, actúa y reporta evento: `device/main.py:43-60`.

```
ESP32 ──telemetry/event──▶ EMQX MQTT ──▶ Backend ──HTTP──▶ ThingSpeak
  ▲                                   │         ▲           TalkBack
  └─────────────── cmd (MQTT) ────────┘         └── cmd ────┘
```

## MQTT Topics y Payloads
- Telemetría: `iot/weather/ws-esp32-001/telemetry`
  - `{"ts": 1765..., "temp_c": 24.7, "hum_pct": 58.2, "light_pct": 42}`
- Comandos al dispositivo: `iot/weather/ws-esp32-001/cmd`
  - `{"value": "LED=1"}` o `{"value": "BEEP=300"}`
- Eventos del dispositivo: `iot/weather/ws-esp32-001/event`
  - `{"type": "EVENT", "cmd": "LED", "val": "1", "ts": 1765...}`

## Base de Datos (SQLite)
Tablas creadas por `backend/schema.sql`:
- `sensor_readings(ts, temp_c, hum_pct, light_pct)`
- `command_log(ts, command_string, status)`
- `event_log(ts, event_type, payload)`

Helpers de consultas: `backend/db.py:45-82`.
- Últimas lecturas: `get_last_readings(limit)`
- Últimos comandos: `get_last_commands(limit)`
- Últimos eventos: `get_last_events(limit)`

## ThingSpeak
- Escritura de canal: `backend/thingspeak.py:1-14` (`field1=Temp`, `field2=Hum`, `field3=Light`).
- TalkBack (comandos): `backend/thingspeak.py:16-21`.
- Variables en `backend/.env`:
  - `THINGSPEAK_WRITE_KEY`, `TALKBACK_ID`, `TALKBACK_API_KEY`.

## Configuración
- Dispositivo: `device/config.py:7-14` (broker/port/topics, intervalo).
- Backend: carga `.env` desde `backend/main.py:10` y usa `DEVICE_ID/MQTT_HOST/MQTT_PORT`.
- Broker: por defecto EMQX (`broker.emqx.io:1883`).

## Seguridad y Buenas Prácticas
- No subir `.env` ni bases de datos al repositorio (`.gitignore` en raíz).
- Si usas broker cloud con credenciales/TLS (HiveMQ/AWS/Azure), parametrizar host/puerto/certs.
- Validar payloads y restringir comandos aceptados (`LED`, `BEEP`).

## Operación
- Backend: `pip install -r backend/requirements.txt` y `python backend/main.py`.
- Dispositivo (Wokwi): abrir `device/diagram.json`, cargar archivos MicroPython, ejecutar.
- Consultas: `python backend/queries_demo.py`.

## Alternativas de Plataforma
- Adafruit IO: feeds y dashboards MQTT; requiere usuario/API Key y nuevos topics.
- AWS IoT Core/Azure IoT Hub: producción, reglas y almacenamiento gestionado.
- EMQX Cloud + Grafana: broker gestionado + visualización DIY.

## Solución de Problemas
- Sin gráficos en ThingSpeak: verificar `THINGSPEAK_WRITE_KEY` y límite de 15s.
- Sin comandos: confirmar `TALKBACK_ID`/`API KEY` y que haya comandos en TalkBack.
- MQTT desconectado: revisar firewall/puerto 1883 y `MQTT_HOST`.

