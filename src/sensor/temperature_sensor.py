import random

class TemperatureSensor:
    def read_value(self):
        return round(random.uniform(20.0, 35.0), 2)
