import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import json

def init_firebase():
    if not firebase_admin._apps:
        # Ambil dari secrets sebagai JSON string
        firebase_json = st.secrets["firebase_json"]
        
        # Parse JSON
        firebase_config = json.loads(firebase_json)
        
        cred = credentials.Certificate(firebase_config)
        
        database_url = st.secrets["firebase_config"]["database_url"]
        
        firebase_admin.initialize_app(cred, {
            "databaseURL": database_url
        })

def get_realtime_data():
    ref_sensor = db.reference("/sensor_data")
    ref_relay = db.reference("/relay_status")
    sensor_data = ref_sensor.get()
    relay_data = ref_relay.get()
    return sensor_data, relay_data

def get_history_data():
    ref_history = db.reference("/history")
    history_data = ref_history.order_by_key().limit_to_last(50).get()
    return history_data
