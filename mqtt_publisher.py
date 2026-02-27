# /// script
# requires-python = ">=3.9"
# dependencies = ["adafruit-io", "adafruit-circuitpython-ahtx0", "adafruit-blinka", "rpi-gpio>=0.7.1"]
# ///
"""Publication MQTT vers Adafruit IO avec reconnexion robuste."""

import os
import time
import board
import adafruit_ahtx0
from Adafruit_IO import MQTTClient

# Configuration - NE PAS HARDCODER LES CLES!
ADAFRUIT_IO_USERNAME = os.environ.get('ADAFRUIT_IO_USERNAME')
ADAFRUIT_IO_KEY = os.environ.get('ADAFRUIT_IO_KEY')

# Backoff constants
MIN_DELAY = 1    # 1 seconde initial
MAX_DELAY = 120  # 2 minutes max
# nombre de tentative de lecture du capteur
MAX_RETRIES = 3  

# Buffer pour les donnees pendant deconnexion
data_buffer = []
is_connected = False


def connected(client):
    """Callback quand connecte."""
    global is_connected
    is_connected = True
    print("Connecte a Adafruit IO!")
    flush_buffer(client)


def disconnected(client):
    """Callback quand deconnecte."""
    global is_connected
    is_connected = False
    print("Deconnecte - tentative de reconnexion...")


def flush_buffer(client):
    """Envoie les donnees bufferisees."""
    global data_buffer
    for feed, value in data_buffer:
        client.publish(feed, value)
    data_buffer = []


def publish_or_buffer(client, feed, value):
    """Publie ou buffer si deconnecte."""
    if is_connected:
        client.publish(feed, value)
    else:
        data_buffer.append((feed, value))


def reconnect_with_backoff(client):
    """Reconnexion avec backoff exponentiel."""
    delay = MIN_DELAY
    while not is_connected:
        try:
            client.connect()
            return
        except Exception as e:
            print(f"Echec connexion: {e}")
            print(f"Nouvelle tentative dans {delay}s...")
            time.sleep(delay)
            delay = min(delay * 2, MAX_DELAY)

def read_aht20():
    """Lit le capteur AHT20 avec retry en cas d'erreur."""
    i2c = board.I2C()
    sensor = adafruit_ahtx0.AHTx0(i2c)

    for attempt in range(MAX_RETRIES):
        try:
            temperature = round(sensor.temperature, 1)
            humidity = round(sensor.relative_humidity, 1)
            return temperature, humidity
        except Exception as e:
            print(f"Tentative {attempt + 1}/{MAX_RETRIES}: {e}")
            time.sleep(1)

    raise RuntimeError(f"Echec apres {MAX_RETRIES} tentatives")

def main():
    if not ADAFRUIT_IO_USERNAME or not ADAFRUIT_IO_KEY:
        print("Erreur: Variables d'environnement non definies!")
        print("  export ADAFRUIT_IO_USERNAME='...'")
        print("  export ADAFRUIT_IO_KEY='...'")
        return

    client = MQTTClient(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)
    client.on_connect = connected
    client.on_disconnect = disconnected

    client.connect()
    client.loop_background()  # Non-bloquant!

    # Exemple de publication
    while True:
        temperature, humidity = read_aht20()

        publish_or_buffer(client, 'temperature', temperature)
        publish_or_buffer(client, 'humidity', humidity)

        time.sleep(3)  # Minimum 3s entre publications (rate limit!)


if __name__ == "__main__":
    main()