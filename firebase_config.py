import firebase_admin
from firebase_admin import credentials, db

def init_firebase():
    """
    Inisialisasi koneksi ke Firebase Realtime Database.
    Pastikan file serviceAccountKey.json sudah ada di folder yang sama.
    """
    if not firebase_admin._apps:
        cred = credentials.Certificate("serviceAccountKey.json")
        firebase_admin.initialize_app(cred, {
            "databaseURL": "https://skripsi-151e5-default-rtdb.asia-southeast1.firebasedatabase.app/"
            # Ganti YOUR-PROJECT-ID dengan ID project Firebase kamu 
        })

def get_realtime_data():
    """
    Mengambil data sensor terbaru dari Firebase Realtime Database.
    Struktur data di Firebase:
    /sensor_data/
        tegangan: float
        arus: float
        daya: float
        energi: float
        frekuensi: float
        faktor_daya: float
        timestamp: string
    /relay_status/
        status: bool
        jadwal_aktif: string
    """
    ref_sensor = db.reference("/sensor_data")
    ref_relay = db.reference("/relay_status")

    sensor_data = ref_sensor.get()
    relay_data = ref_relay.get()

    return sensor_data, relay_data

def get_history_data():
    """
    Mengambil data riwayat dari Firebase untuk ditampilkan di grafik.
    Struktur data di Firebase:
    /history/
        timestamp_1/
            daya: float
            energi: float
            timestamp: string
        timestamp_2/
            ...
    """
    ref_history = db.reference("/history")
    history_data = ref_history.order_by_key().limit_to_last(50).get()
    return history_data
