-- Tabla para guardar las lecturas de los sensores.
CREATE TABLE IF NOT EXISTS sensor_readings (
  id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Número único que se asigna automáticamente a cada lectura.
  ts INTEGER NOT NULL,                   -- Momento exacto en que se tomó la lectura (en formato de tiempo).
  temp_c REAL,                           -- Temperatura en grados Celsius.
  hum_pct REAL,                          -- Humedad en porcentaje (%).
  light_pct INTEGER                      -- Nivel de luz en porcentaje (%).
);

-- Tabla para guardar los comandos enviados al dispositivo.
CREATE TABLE IF NOT EXISTS command_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Número único para cada comando.
  ts INTEGER NOT NULL,                   -- Momento en que se envió el comando.
  command_string TEXT NOT NULL,          -- El texto del comando (ejemplo: "ENCENDER LED").
  status TEXT NOT NULL                   -- Estado del comando (ejemplo: "ejecutado", "fallido").
);

-- Tabla para guardar los eventos que ocurren en el dispositivo.
CREATE TABLE IF NOT EXISTS event_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Número único para cada evento.
  ts INTEGER NOT NULL,                   -- Momento en que ocurrió el evento.
  event_type TEXT,                       -- Tipo de evento (ejemplo: "INFO", "ERROR", "ALERTA").
  payload TEXT                           -- Detalles del evento en formato texto (JSON).
);
