import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import json

def init_firebase():
    if not firebase_admin._apps:
        # Ambil dari secrets (format simple)
        firebase_config = {
            "type": st.secrets["firebase_type"],
            "project_id": st.secrets["firebase_project"],
            "private_key": st.secrets["firebase_key"],
            "client_email": st.secrets["firebase_email"],
            "client_id": st.secrets["firebase_client_id"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40skripsi-151e5.iam.gserviceaccount.com"
        }
        
        database_url = st.secrets["firebase_config"]["database_url"]
        
        cred = credentials.Certificate(firebase_config)
        firebase_admin.initialize_app(cred, {"databaseURL": database_url})

def get_realtime_data():
    ref_sensor = db.reference("/sensor_data")
    ref_relay = db.reference("/relay_status")
    return ref_sensor.get(), ref_relay.get()

def get_history_data():
    ref_history = db.reference("/history")
    return ref_history.order_by_key().limit_to_last(50).get()
