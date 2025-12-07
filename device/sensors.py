import time
import dht
from machine import Pin, ADC

class Sensors:
    def __init__(self, dht_pin=15, adc_pin=34):
        self.dht = dht.DHT22(Pin(dht_pin))
        self.adc = ADC(Pin(adc_pin))
        self.adc.atten(ADC.ATTN_11DB)

    def read(self):
        self.dht.measure()
        temp = self.dht.temperature()
        hum = self.dht.humidity()
        raw = self.adc.read()  # 0..4095
        light_pct = int((raw / 4095) * 100)

        return {
            "ts": int(time.time()),
            "temp_c": float(temp),
            "hum_pct": float(hum),
            "light_pct": int(light_pct)
        }
