import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from firebase_config import init_firebase, get_realtime_data
import os

# ===== KONFIGURASI HALAMAN =====
st.set_page_config(
    page_title="Monitoring Kendali Daya Berbasis Waktu",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===== TARIF LISTRIK =====
TARIF_PER_KWH = 1444

# ===== CSS KUSTOM =====
st.markdown("""
    <style>
        .metric-card {
            background-color: #1e1e2e;
            border-radius: 16px;
            padding: 24px 20px;
            text-align: center;
            border: 1px solid #313244;
            height: 100%;
        }
        .metric-label {
            font-size: 15px;
            color: #a6adc8;
            margin-bottom: 8px;
            font-weight: 500;
        }
        .metric-value {
            font-size: 36px;
            font-weight: bold;
            color: #cdd6f4;
            line-height: 1.2;
        }
        .metric-unit {
            font-size: 14px;
            color: #a6adc8;
            margin-top: 4px;
        }
        .status-on {
            background-color: #a6e3a1;
            color: #1e1e2e;
            padding: 6px 16px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 16px;
        }
        .status-off {
            background-color: #f38ba8;
            color: #1e1e2e;
            padding: 6px 16px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 16px;
        }
        .header-title {
            font-size: 32px;
            font-weight: bold;
            color: #cdd6f4;
            text-align: center;
            margin-bottom: 8px;
        }
        .section-title {
            font-size: 20px;
            font-weight: bold;
            color: #89b4fa;
            margin-bottom: 12px;
            margin-top: 16px;
        }
    </style>
""", unsafe_allow_html=True)

# ===== INISIALISASI FIREBASE =====
try:
    init_firebase()
except Exception as e:
    st.error(f"Gagal terhubung ke Firebase: {e}")
    st.stop()

# ===== INISIALISASI SESSION STATE UNTUK GRAFIK REAL-TIME =====
if "realtime_log" not in st.session_state:
    st.session_state.realtime_log = []

# ===== SIDEBAR =====
with st.sidebar:
    logo_path = "uny_logo.png"
    if os.path.exists(logo_path):
        st.image(logo_path, width=200)
    else:
        st.markdown("### 🎓 UNY")
        st.caption("Universitas Negeri Yogyakarta")

    st.markdown("### ⚡ Monitoring Daya")
    st.markdown("**Praktik Elektronika Daya**")
    st.markdown("Departemen Pendidikan Teknik Elektro")
    st.markdown("Fakultas Teknik UNY")
    st.divider()

    st.markdown("### 💡 Informasi Tarif")
    tarif_input = st.number_input(
        "Tarif Listrik (Rp/kWh)",
        min_value=500,
        max_value=5000,
        value=TARIF_PER_KWH,
        step=10
    )
    st.caption("Sesuaikan tarif dengan golongan listrik yang digunakan")

    st.divider()
    st.markdown("### 🔄 Manual Refresh")
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.rerun()

    if st.button("🗑️ Reset Grafik", use_container_width=True):
        st.session_state.realtime_log = []
        st.rerun()

    st.divider()
    st.caption(f"🕐 Update: {datetime.now().strftime('%H:%M:%S')}")

# ===== FUNGSI HELPER =====
def make_metric_card(label, value, unit, color="#cdd6f4"):
    return f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value" style="color:{color};">{value}</div>
        <div class="metric-unit">{unit}</div>
    </div>
    """

def make_gauge(value, title, min_val, max_val, unit, color):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={"text": f"{title} ({unit})", "font": {"size": 16, "color": "#a6adc8"}},
        number={"font": {"size": 28, "color": "#cdd6f4"}, "suffix": f" {unit}"},
        gauge={
            "axis": {"range": [min_val, max_val], "tickcolor": "#a6adc8"},
            "bar": {"color": color},
            "bgcolor": "#1e1e2e",
            "bordercolor": "#313244",
            "threshold": {
                "line": {"color": "#f38ba8", "width": 2},
                "thickness": 0.75,
                "value": max_val * 0.85
            }
        }
    ))
    fig.update_layout(
        height=220,
        paper_bgcolor="#1e1e2e",
        plot_bgcolor="#1e1e2e",
        margin=dict(l=20, r=20, t=50, b=20),
        font={"color": "#cdd6f4"}
    )
    return fig

# ===== AMBIL DATA DARI FIREBASE =====
try:
    sensor_data, relay_data = get_realtime_data()
except Exception as e:
    st.error(f"Terjadi kesalahan saat mengambil data: {e}")
    sensor_data = None
    relay_data = None

# ===== NILAI DEFAULT =====
if sensor_data is None:
    sensor_data = {"tegangan": 0.0, "arus": 0.0, "daya": 0.0, "energi": 0.0, "frekuensi": 0.0, "faktor_daya": 0.0, "timestamp": "-"}

if relay_data is None:
    relay_data = {"relay1": 0, "relay2": 0, "relay3": 0, "relay4": 0, "jadwal_aktif": "-"}

# ===== SIMPAN DATA KE LOG REAL-TIME =====
timestamp_now = sensor_data.get("timestamp", datetime.now().strftime("%H:%M:%S"))
if sensor_data.get("tegangan", 0) > 0:
    st.session_state.realtime_log.append({
        "Waktu": timestamp_now,
        "Daya (W)": sensor_data.get("daya", 0),
        "Energi (kWh)": sensor_data.get("energi", 0),
        "Tegangan (V)": sensor_data.get("tegangan", 0),
        "Arus (A)": sensor_data.get("arus", 0),
        "Frekuensi (Hz)": sensor_data.get("frekuensi", 0),
        "Faktor Daya": sensor_data.get("faktor_daya", 0),
    })
    # Batasi log maksimal 100 data terakhir
    if len(st.session_state.realtime_log) > 100:
        st.session_state.realtime_log = st.session_state.realtime_log[-100:]

estimasi_biaya = sensor_data.get("energi", 0) * tarif_input

# ===== HEADER UTAMA =====
st.markdown('<p class="header-title">⚡ Dashboard Monitoring Kendali Daya Berbasis Waktu</p>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; font-size: 16px; color: #a6adc8; margin-bottom: 16px;">Pengembangan Perangkat Kendali Daya Berbasis Waktu — Ilham Rizki Maulana — UNY 2026</p>', unsafe_allow_html=True)
st.divider()

# ===== STATUS RELAY =====
st.markdown('<p class="section-title">🔌 Status 4 Relay</p>', unsafe_allow_html=True)

relay1 = relay_data.get("relay1", 0)
relay2 = relay_data.get("relay2", 0)
relay3 = relay_data.get("relay3", 0)
relay4 = relay_data.get("relay4", 0)

col_r1, col_r2, col_r3, col_r4 = st.columns(4)

def show_relay_status(col, relay_num, status):
    status_label = "ON" if status else "OFF"
    status_class = "status-on" if status else "status-off"
    with col:
        st.markdown(f"""
            <div style="padding: 16px; background: #1e1e2e; border-radius: 16px; border: 1px solid #313244; text-align: center;">
                <div class="metric-label">Relay {relay_num}</div>
                <span class="{status_class}">{status_label}</span>
            </div>
        """, unsafe_allow_html=True)

show_relay_status(col_r1, 1, relay1)
show_relay_status(col_r2, 2, relay2)
show_relay_status(col_r3, 3, relay3)
show_relay_status(col_r4, 4, relay4)

st.markdown("<br>", unsafe_allow_html=True)

# ===== PARAMETER UTAMA =====
st.markdown('<p class="section-title">📊 Parameter Kelistrikan Real-Time</p>', unsafe_allow_html=True)

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(make_metric_card("🔌 Tegangan", f"{sensor_data.get('tegangan', 0):.1f}", "Volt", "#89b4fa"), unsafe_allow_html=True)
with col2:
    st.markdown(make_metric_card("⚡ Arus", f"{sensor_data.get('arus', 0):.2f}", "Ampere", "#a6e3a1"), unsafe_allow_html=True)
with col3:
    st.markdown(make_metric_card("💡 Daya Aktif", f"{sensor_data.get('daya', 0):.1f}", "Watt", "#fab387"), unsafe_allow_html=True)
with col4:
    st.markdown(make_metric_card("🔄 Frekuensi", f"{sensor_data.get('frekuensi', 0):.1f}", "Hz", "#cba6f7"), unsafe_allow_html=True)
with col5:
    st.markdown(make_metric_card("📐 Faktor Daya", f"{sensor_data.get('faktor_daya', 0):.2f}", "PF", "#f9e2af"), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ===== ENERGI DAN BIAYA =====
st.markdown('<p class="section-title">🔋 Konsumsi Energi dan Estimasi Biaya</p>', unsafe_allow_html=True)

col_e1, col_e2, col_e3 = st.columns(3)

with col_e1:
    st.markdown(make_metric_card("⚡ Total Energi", f"{sensor_data.get('energi', 0):.5f}", "kWh", "#89dceb"), unsafe_allow_html=True)
with col_e2:
    st.markdown(make_metric_card("💰 Estimasi Biaya", f"Rp {estimasi_biaya:,.0f}", f"@ Rp {tarif_input:,}/kWh", "#a6e3a1"), unsafe_allow_html=True)
with col_e3:
    daya_semu = sensor_data.get("tegangan", 0) * sensor_data.get("arus", 0)
    st.markdown(make_metric_card("📡 Daya Semu", f"{daya_semu:.1f}", "VA", "#f38ba8"), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ===== GAUGE CHARTS =====
st.markdown('<p class="section-title">🎛️ Indikator Visual</p>', unsafe_allow_html=True)

col_g1, col_g2, col_g3 = st.columns(3)

with col_g1:
    st.plotly_chart(make_gauge(sensor_data.get("tegangan", 0), "Tegangan", 0, 260, "V", "#89b4fa"), use_container_width=True)
with col_g2:
    st.plotly_chart(make_gauge(sensor_data.get("arus", 0), "Arus", 0, 100, "A", "#a6e3a1"), use_container_width=True)
with col_g3:
    st.plotly_chart(make_gauge(sensor_data.get("faktor_daya", 0), "Faktor Daya", 0, 1, "PF", "#f9e2af"), use_container_width=True)

# ===== GRAFIK REAL-TIME =====
st.markdown('<p class="section-title">📈 Grafik Daya vs Waktu (Sesi Ini)</p>', unsafe_allow_html=True)

if st.session_state.realtime_log:
    df = pd.DataFrame(st.session_state.realtime_log)

    fig_daya = go.Figure()
    fig_daya.add_trace(go.Scatter(
        x=df["Waktu"], y=df["Daya (W)"],
        mode="lines+markers", name="Daya Aktif",
        line=dict(color="#fab387", width=2),
        marker=dict(size=4),
        fill="tozeroy", fillcolor="rgba(250, 179, 135, 0.15)"
    ))
    fig_daya.update_layout(
        title="Daya Aktif terhadap Waktu", xaxis_title="Waktu", yaxis_title="Daya (Watt)",
        height=320, paper_bgcolor="#1e1e2e", plot_bgcolor="#1e1e2e",
        font={"color": "#cdd6f4", "size": 14}, title_font={"size": 18},
        xaxis=dict(gridcolor="#313244"), yaxis=dict(gridcolor="#313244"),
        margin=dict(l=20, r=20, t=50, b=30)
    )
    st.plotly_chart(fig_daya, use_container_width=True)

    fig_energi = go.Figure()
    fig_energi.add_trace(go.Scatter(
        x=df["Waktu"], y=df["Energi (kWh)"],
        mode="lines+markers", name="Energi",
        line=dict(color="#89dceb", width=2),
        marker=dict(size=4),
        fill="tozeroy", fillcolor="rgba(137, 220, 235, 0.15)"
    ))
    fig_energi.update_layout(
        title="Akumulasi Energi terhadap Waktu", xaxis_title="Waktu", yaxis_title="Energi (kWh)",
        height=320, paper_bgcolor="#1e1e2e", plot_bgcolor="#1e1e2e",
        font={"color": "#cdd6f4", "size": 14}, title_font={"size": 18},
        xaxis=dict(gridcolor="#313244"), yaxis=dict(gridcolor="#313244"),
        margin=dict(l=20, r=20, t=50, b=30)
    )
    st.plotly_chart(fig_energi, use_container_width=True)

else:
    st.info("📭 Belum ada data. Tekan Refresh Data untuk mulai merekam.")

# ===== TABEL DATA TERKINI =====
st.markdown('<p class="section-title">📋 Tabel Data Terkini</p>', unsafe_allow_html=True)

if st.session_state.realtime_log:
    df_table = pd.DataFrame(st.session_state.realtime_log)
    st.dataframe(df_table.tail(10), use_container_width=True, hide_index=True)
else:
    st.info("Belum ada data.")

# ===== CATATAN =====
st.divider()
st.caption("⚠️ Estimasi biaya dihitung berdasarkan tarif yang dimasukkan di sidebar dan bersifat perkiraan. Grafik merekam data selama sesi ini (maks. 100 data). Tekan 'Reset Grafik' untuk menghapus riwayat grafik.")
