from machine import Pin, PWM, I2C   # Librerías para controlar pines, sonidos y comunicación con pantalla.
import time                         # Librería para manejar tiempos y pausas.
import ssd1306                      # Librería para controlar pantallas OLED modelo SSD1306.

# ------------------------------------------------------------
# Clase Actuators: agrupa todo lo que el dispositivo puede "hacer"
# (encender LED, sonar buzzer, mostrar en pantalla).
# ------------------------------------------------------------
class Actuators:
    def __init__(self, led_pin=2, buzzer_pin=27, sda=21, scl=22):
        # Esta función se ejecuta al crear un nuevo objeto Actuators.
        # Configuramos los pines del LED, buzzer y pantalla OLED.

        self.led = Pin(led_pin, Pin.OUT)   # LED conectado al pin indicado (por defecto pin 2).
        self.buzzer = PWM(Pin(buzzer_pin)) # Buzzer conectado al pin indicado (por defecto pin 27).
        self.buzzer.duty(0)                # Inicialmente apagamos el buzzer.

        # Configuramos la comunicación I2C para la pantalla OLED.
        i2c = I2C(0, sda=Pin(sda), scl=Pin(scl))
        self.oled = ssd1306.SSD1306_I2C(128, 64, i2c)   # Pantalla OLED de 128x64 píxeles.

    def set_led(self, on: bool):
        # Esta función sirve para ENCENDER o APAGAR el LED.
        # Si "on" es True → LED encendido. Si es False → LED apagado.
        self.led.value(1 if on else 0)

    def beep(self, ms=200, freq=2000):
        # Esta función hace sonar el buzzer.
        # ms = duración del sonido en milisegundos (por defecto 200 ms).
        # freq = frecuencia del sonido en Hz (por defecto 2000 Hz).
        self.buzzer.freq(freq)     # Ajustamos la frecuencia del sonido.
        self.buzzer.duty(512)      # Activamos el buzzer (volumen medio).
        time.sleep_ms(ms)          # Esperamos el tiempo indicado.
        self.buzzer.duty(0)        # Apagamos el buzzer.

    def show(self, d, status=""):
        # Esta función muestra información en la pantalla OLED.
        # d = diccionario con datos de sensores (temp_c, hum_pct, light_pct).
        # status = texto opcional para mostrar un estado o mensaje.

        self.oled.fill(0)   # Limpiamos la pantalla.
        self.oled.text("Weather Station", 0, 0)   # Título en la parte superior.
        self.oled.text(f"T:{d['temp_c']:.1f}C", 0, 18)   # Temperatura.
        self.oled.text(f"H:{d['hum_pct']:.1f}%", 0, 32)  # Humedad.
        self.oled.text(f"L:{d['light_pct']}%", 0, 46)    # Luz.
        if status:
            self.oled.text(status[:16], 0, 56)   # Mensaje de estado (máx. 16 caracteres).
        self.oled.show()   # Actualizamos la pantalla para mostrar todo.
