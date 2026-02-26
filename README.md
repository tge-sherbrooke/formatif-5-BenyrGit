# Formatif F5 — Publication MQTT avec Adafruit IO

**Cours** : 243-413-SH — Introduction aux objets connectes
**Semaine** : 5
**Type** : Formative (non notee)
**Retries** : Illimites - poussez autant de fois que necessaire!

---

> **Pratique autonome** -- Ce formatif est une evaluation formative (non notee). Contrairement au laboratoire guide, vous devez completer les taches de maniere autonome. Les tests automatiques vous donnent une retroaction immediate a chaque push.

## Ce que vous avez appris en labo

Le laboratoire de la semaine 5 vous a guide a travers :

- Configuration d'un compte Adafruit IO et recuperation de la cle API
- Publication de donnees de capteur vers Adafruit IO via MQTT
- Organisation des donnees en feeds separes (temperature, humidite)
- Implementation d'une reconnexion robuste avec backoff exponentiel

Ce formatif vous demande d'appliquer ces competences de maniere autonome.

---

## Progressive Milestones

Ce formatif utilise des **jalons progressifs** avec retroaction detaillee:

| Jalon | Points | Verification |
|-------|--------|-------------|
| **Milestone 1** | 25 pts | Script existe, import Adafruit IO, credentials, PAS DE CLES API! |
| **Milestone 2** | 35 pts | Client MQTT, fonction publish, multiple feeds |
| **Milestone 3** | 40 pts | Reconnexion, constantes backoff, buffering, loop non-bloquant |

**Chaque test echoue vous dit**:
- Ce qui etait attendu
- Ce qui a ete trouve
- Une suggestion pour corriger

---

## IMPORTANT: Securite des cles API

**NE COMMITTEZ JAMAIS VOS CLES API!**

Utilisez des variables d'environnement:

```bash
# Sur votre Raspberry Pi:
export ADAFRUIT_IO_USERNAME='votre_username'
export ADAFRUIT_IO_KEY='aio_xxxxx'

# Dans votre code:
import os
ADAFRUIT_IO_USERNAME = os.environ.get('ADAFRUIT_IO_USERNAME')
ADAFRUIT_IO_KEY = os.environ.get('ADAFRUIT_IO_KEY')
```

---

## Objectif

Ce formatif vise a verifier que vous etes capable de:
1. Configurer un client MQTT Adafruit IO
2. Publier des donnees de capteurs vers plusieurs feeds
3. Implementer une reconnexion robuste avec backoff exponentiel
4. Gerer les deconnexions avec buffering des donnees

---

## Workflow de soumission

```
+-------------------------------------------------------------+
|                    WORKFLOW FORMATIF F5                     |
+-------------------------------------------------------------+
|                                                             |
|  1. Creer un compte Adafruit IO                             |
|     +-- https://io.adafruit.com                             |
|     +-- Obtenir votre username et API key                   |
|     +-- NE PAS commiter la cle!                             |
|                                                             |
|  2. Creer mqtt_publisher.py                                 |
|     +-- Import Adafruit_IO                                  |
|     +-- Credentials via env vars                            |
|     +-- Client MQTT + loop_background()                     |
|     +-- Publish vers multiple feeds                         |
|     +-- Reconnexion avec backoff                            |
|                                                             |
|  3. Creer les feeds sur Adafruit IO                         |
|     +-- temperature (lowercase!)                            |
|     +-- humidity                                            |
|                                                             |
|  4. Tester sur Raspberry Pi                                 |
|     +-- export ADAFRUIT_IO_USERNAME='...'                   |
|     +-- export ADAFRUIT_IO_KEY='...'                        |
|     +-- python3 validate_pi.py                              |
|                                                             |
|  5. Pousser vers GitHub (SANS les cles!)                    |
|                                                             |
+-------------------------------------------------------------+
```

---

## Structure de code recommandee

```python
# /// script
# requires-python = ">=3.9"
# dependencies = ["adafruit-io"]
# ///
"""Publication MQTT vers Adafruit IO avec reconnexion robuste."""

import os
import time
from Adafruit_IO import MQTTClient

# Configuration - NE PAS HARDCODER LES CLES!
ADAFRUIT_IO_USERNAME = os.environ.get('ADAFRUIT_IO_USERNAME')
ADAFRUIT_IO_KEY = os.environ.get('ADAFRUIT_IO_KEY')

# Backoff constants
MIN_DELAY = 1    # 1 seconde initial
MAX_DELAY = 120  # 2 minutes max

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
        # Lire capteurs (exemple)
        temperature = 22.5
        humidity = 45.0

        publish_or_buffer(client, 'temperature', temperature)
        publish_or_buffer(client, 'humidity', humidity)

        time.sleep(3)  # Minimum 3s entre publications (rate limit!)


if __name__ == "__main__":
    main()
```

---

## Points cles

### Feed Key vs Feed Name

Adafruit IO a deux identifiants pour chaque feed:
- **Name**: Nom affiche (ex: "Temperature Sensor")
- **Key**: Identifiant API (ex: "temperature-sensor")

**Dans votre code, utilisez toujours le KEY (lowercase, pas d'espaces)!**

```python
client.publish('temperature', value)       # CORRECT - utilise le key
client.publish('Temperature', value)       # ERREUR 404!
client.publish('Temperature Sensor', value)  # ERREUR 404!
```

### Rate Limiting

Adafruit IO gratuit: 30 publications/minute max.
Minimum 2-3 secondes entre chaque publication.

### Backoff Exponentiel

Quand la connexion echoue, doublez le delai a chaque tentative:
- 1s -> 2s -> 4s -> 8s -> 16s -> 32s -> 64s -> 120s (max)

Cela evite de surcharger le serveur pendant les pannes.

### loop_background()

`loop_background()` execute la boucle MQTT dans un thread separe.
Cela permet a votre code de continuer a s'executer (lecture capteurs, etc.).

---

## Livrables

Dans ce depot, vous devez avoir:

- [ ] `mqtt_publisher.py` — Script de publication MQTT
- [ ] `.test_markers/` — Dossier cree par `validate_pi.py`
- [ ] **PAS DE CLES API DANS LE CODE!**

---

Bonne chance!
