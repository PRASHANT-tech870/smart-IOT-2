import paho.mqtt.client as mqtt
import firebase_admin
from firebase_admin import credentials, db, firestore
import json

# Firebase setup
cred = credentials.Certificate('/home/vboxuser/Downloads/EL/server2/serviceAccountKey.json')

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://esp32-d27db-default-rtdb.asia-southeast1.firebasedatabase.app/'
    })

# Initialize Firestore
firestore_db = firestore.client()

# Initialize Realtime Database
realtime_db = db

# MQTT setup
mqtt_broker = "localhost"  # Replace with your MQTT broker address
mqtt_port = 1883
mqtt_topic = "sensor/combined"

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe(mqtt_topic)

def on_message(client, userdata, msg):
    print(f"Topic: {msg.topic}\nMessage: {msg.payload.decode()}")
    data = msg.payload.decode()

    try:
        # Extract sensor values
        parts = data.split(',')
        mq_value = int(parts[0].split(':')[1].strip())
        temperature = float(parts[1].split(':')[1].strip().split()[0])  # Extract temperature value
        humidity = float(parts[2].split(':')[1].strip().split()[0])  # Extract humidity value

    except (IndexError, ValueError) as e:
        print("Error parsing message:", e)
        return

    # Prepare data for Firebase Realtime Database
    realtime_data = {
        "mq_value": mq_value,
        "temperature": temperature,
        "humidity": humidity
    }

    # Debugging output
    print("Sending data to Firebase Realtime Database:", realtime_data)

    try:
        # Send data to Firebase Realtime Database
        realtime_db.reference('/CombinedSensorData').update(realtime_data)  # Use update instead of set
        print("Data sent to Firebase Realtime Database")
    except Exception as e:
        print("Error sending data to Firebase Realtime Database:", e)

    # Prepare data for Firestore
    firestore_data = {
        "mq_value": mq_value,
        "temperature": temperature,
        "humidity": humidity
    }

    # Debugging output
    print("Sending data to Firestore:", firestore_data)

    try:
        # Send data to Firestore
        firestore_db.collection('combined_sensor_data').add(firestore_data)
        print("Data sent to Firebase Firestore")
    except Exception as e:
        print("Error sending data to Firebase Firestore:", e)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(mqtt_broker, mqtt_port, 60)
client.loop_forever()
