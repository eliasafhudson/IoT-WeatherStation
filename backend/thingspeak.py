import requests   # Librería que permite enviar y recibir información de páginas web o servicios en la nube.


# Función para ENVIAR datos de sensores a ThingSpeak.
def write_channel(write_key, d):
    # Hacemos una petición POST (enviar datos) a la dirección de ThingSpeak.
    r = requests.post(
        "https://api.thingspeak.com/update.json",
        data={
            "api_key": write_key,        # Clave secreta para identificar nuestro canal en ThingSpeak.
            "field1": d.get("temp_c"),   # Enviamos la temperatura.
            "field2": d.get("hum_pct"),  # Enviamos la humedad.
            "field3": d.get("light_pct") # Enviamos el nivel de luz.
        },
        timeout=10   # Tiempo máximo de espera (10 segundos).
    )
    r.raise_for_status()   # Si hubo un error en la petición, aquí se detiene y muestra el error.
    return r.json()        # Devolvemos la respuesta de ThingSpeak en formato JSON (texto con estructura).


# Función para LEER comandos desde TalkBack en ThingSpeak.
def execute_talkback(talkback_id, talkback_key):
    # Creamos la dirección (URL) para pedir el próximo comando de TalkBack.
    url = f"https://api.thingspeak.com/talkbacks/{talkback_id}/commands/execute.json"
    # Hacemos una petición POST para ejecutar el comando pendiente.
    r = requests.post(url, data={"api_key": talkback_key}, timeout=10)
    r.raise_for_status()   # Si hubo un error en la petición, aquí se detiene y muestra el error.
    return r.json()        # Devolvemos el comando en formato JSON. Si no hay comandos, devuelve {} (vacío).
