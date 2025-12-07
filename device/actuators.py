from machine import Pin, PWM, I2C
import time
import ssd1306

class Actuators:
    def __init__(self, led_pin=2, buzzer_pin=27, sda=21, scl=22):
        self.led = Pin(led_pin, Pin.OUT)
        self.buzzer = PWM(Pin(buzzer_pin))
        self.buzzer.duty(0)

        i2c = I2C(0, sda=Pin(sda), scl=Pin(scl))
        self.oled = ssd1306.SSD1306_I2C(128, 64, i2c)

    def set_led(self, on: bool):
        self.led.value(1 if on else 0)

    def beep(self, ms=200, freq=2000):
        self.buzzer.freq(freq)
        self.buzzer.duty(512)
        time.sleep_ms(ms)
        self.buzzer.duty(0)

    def show(self, d, status=""):
        self.oled.fill(0)
        self.oled.text("Weather Station", 0, 0)
        self.oled.text(f"T:{d['temp_c']:.1f}C", 0, 18)
        self.oled.text(f"H:{d['hum_pct']:.1f}%", 0, 32)
        self.oled.text(f"L:{d['light_pct']}%", 0, 46)
        if status:
            self.oled.text(status[:16], 0, 56)
        self.oled.show()
