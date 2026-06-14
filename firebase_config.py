import streamlit as st
import firebase_admin
from firebase_admin import credentials, db

def init_firebase():
    if not firebase_admin._apps:
        firebase_config = {
            "type": st.secrets["firebase"]["type"],
            "project_id": st.secrets["firebase"]["project_id"],
            "private_key_id": st.secrets["firebase"]["private_key_id"],
            "private_key": st.secrets["firebase"]["private_key"],
            "client_email": st.secrets["firebase"]["client_email"],
            "client_id": st.secrets["firebase"]["client_id"],
            "auth_uri": st.secrets["firebase"]["auth_uri"],
            "token_uri": st.secrets["firebase"]["token_uri"],
            "auth_provider_x509_cert_url": st.secrets["firebase"]["auth_provider_x509_cert_url"],
            "client_x509_cert_url": st.secrets["firebase"]["client_x509_cert_url"],
            "universe_domain": st.secrets["firebase"]["universe_domain"]
        }
        
        database_url = st.secrets["firebase_config"]["database_url"]
        cred = credentials.Certificate(firebase_config)
        firebase_admin.initialize_app(cred, {"databaseURL": database_url})

def get_realtime_data():
    ref_sensor = db.reference("/data/sensor")  
    ref_relay = db.reference("/data/relay")      
    sensor_data = ref_sensor.get()
    relay_data = ref_relay.get()
    return sensor_data, relay_data

def get_history_data():
    ref_history = db.reference("/history")
    return ref_history.order_by_key().limit_to_last(50).get()
