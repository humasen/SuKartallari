import streamlit as st
import joblib
import numpy as np
import pandas as pd
import random
import time

# Sayfa Yapılandırması
st.set_page_config(page_title="Su Kartalları - Su Kalitesi İzleme", page_icon="💧", layout="wide")

# Yapay Zekâ Modelini Yükle
@st.cache_resource
def load_model():
    return joblib.load('water_model.pkl')

model = load_model()

# Session State (Bağlantı Durumu)
if 'esp32_connected' not in st.session_state:
    st.session_state.esp32_connected = False

# Arayüz Başlığı
st.title("💧 Çiğli BİLSEM Su Kartalları")
st.caption("ESP32 Destekli ve Yapay Zekâ Tabanlı Anlık Su Kalitesi Analiz Platformu")
st.markdown("---")

# Yeniden Düzenlenen 3 Panel Yapısı
tab1, tab2, tab3 = tab_1, tab_2, tab_3 = st.tabs([
    "📚 Panel 1: İdeal Parametre Rehberi", 
    "🎮 Panel 2: Manuel Test Paneli", 
    "📡 Panel 3: Canlı Sensör Paneli"
])

# ==========================================
# PANEL 1: İDEAL PARAMETRE REHBERİ (BİLGİLENDİRME)
# ==========================================
with tab1:
    st.header("📚 Su Kalitesi İdeal Parametre Standartları")
    st.write("Dünya Sağlık Örgütü (WHO) standartlarına göre içme suyunda bulunması gereken ideal aralıklar:")
    
    guide_data = {
        "Parametre": ["pH Seviyesi", "Bulanıklık (Turbidity)", "TDS (Çözünmüş Katı)", "Sıcaklık", "Çözünmüş Oksijen (DO)"],
        "İdeal Değer Aralığı": ["6.5 - 8.5", "< 5.0 NTU (İdeal < 1.0)", "< 500 ppm", "10.0 - 25.0 °C", "6.5 mg/L - 8.0 mg/L"],
        "Açıklama": [
            "Suyun asit/baz dengesini gösterir.",
            "Suyun berraklık derecesidir.",
            "Suda çözünmüş minerallerin ve tuzların toplamıdır.",
            "Suyun anlık sıcaklık değeridir.",
            "Sudaki çözünmüş oksijen miktarıdır."
        ]
    }
    st.table(pd.DataFrame(guide_data))

# ==========================================
# PANEL 2: MANUEL TEST PANELSİ
# ==========================================
with tab2:
    st.header("🎮 Manuel Test ve Simülasyon Paneli")
    st.write("Değerleri elle değiştirerek yapay zekâ modelinin çıktısını simüle edebilirsiniz.")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("⚙️ Ölçüm Değerleri")
        m_ph = st.slider("pH Değeri", 0.0, 14.0, 7.4, 0.1, key="m_ph")
        m_turbidity = st.slider("Bulanıklık (NTU)", 0.0, 10.0, 1.2, 0.1, key="m_turb")
        m_tds = st.slider("TDS / Çözünmüş Katı (ppm)", 0, 1000, 250, 10, key="m_tds")
        m_temp = st.slider("Sıcaklık (°C)", 0.0, 50.0, 22.0, 0.5, key="m_temp")
        m_do = st.slider("Çözünmüş Oksijen (DO - mg/L)", 0.0, 15.0, 7.8, 0.1, key="m_do")
    
    with col2:
        st.subheader("🤖 Yapay Zekâ Tahmini")
        input_data = np.array([[m_ph, 180.0, m_tds, 7.0, 300.0, m_tds * 1.6, 15.0, 60.0, m_turbidity]])
        
        if st.button("MANUEL DEĞERLERİ ANALİZ ET", use_container_width=True, key="btn_m"):
            pred = model.predict(input_data)
            if pred[0] == 1:
                st.success("✅ SONUÇ: SU İÇİLEBİLİR VE GÜVENLİ")
                st.balloons()
            else:
                st.error("🚨 SONUÇ: SU İÇİLEMEZ! UYGUNSUZ DEĞER TESPİT EDİLDİ")

# ==========================================
# PANEL 3: CANLI SENSÖR VERİLERİ (HEPSİ BİR ARADA + 1 SN OTOMATİK YENİLEME)
# ==========================================
with tab3:
    st.header("📡 Canlı Sensör İzleme Paneli (ESP32 DevKit V1)")
    
    # Test Amaçlı Bağlantı Anahtarı
    conn_col1, conn_col2 = st.columns([3, 1])
    with conn_col2:
        st.session_state.esp32_connected = st.checkbox("ESP32 Bağlantısını Simüle Et", value=st.session_state.esp32_connected)
    
    st.markdown("---")
    
    # Gerçek (bağlantı durumuna göre) ve Otomatik Üretilen Tüm Değerler
    if st.session_state.esp32_connected:
        val_temp_str = f"{round(random.uniform(21.5, 23.5), 1)} °C"
        val_tds_str = f"{random.randint(220, 310)} ppm"
        num_temp = float(val_temp_str.split()[0])
        num_tds = int(val_tds_str.split()[0])
    else:
        val_temp_str = "-"
        val_tds_str = "-"
        num_temp = 22.0
        num_tds = 250

    # Otomatik/İdeal Rastgele Üretilen Parametreler (Her saniye değişir)
    sim_ph = round(random.uniform(7.1, 7.5), 2)
    sim_turb = round(random.uniform(0.8, 1.1), 2)
    sim_do = round(random.uniform(7.7, 8.2), 2)
    
    # Tüm Sensör Verileri Tek Bir Bölümde (5 Kolon)
    st.subheader("📊 Anlık Sensör Ölçüm Değerleri")
    
    col_a, col_b, col_c, col_d, col_e = st.columns(5)
    
    col_a.metric(label="🌡️ Sıcaklık (DS18B20)", value=val_temp_str)
    col_b.metric(label="⚡ TDS (SEN0244)", value=val_tds_str)
    col_c.metric(label="🧪 pH Seviyesi", value=f"{sim_ph}")
    col_d.metric(label="💧 Bulanıklık", value=f"{sim_turb} NTU")
    col_e.metric(label="🫧 Oksijen (DO)", value=f"{sim_do} mg/L")
    
    if not st.session_state.esp32_connected:
        st.warning("⚠️ ESP32 Cihazından veri akışı bekleniyor... (Veri akışı şu an yok)")

    st.markdown("---")
    
    # Canlı Analiz Butonu
    if st.button("CANLI SENSÖR VERİLERİNİ ANALİZ ET", use_container_width=True, key="btn_live"):
        if not st.session_state.esp32_connected:
            st.error("❌ Hata: Gerçek sensör bağlantısı (ESP32) olmadan canlı analiz yapılamaz. Veri akışı yok.")
        else:
            live_input = np.array([[sim_ph, 180.0, num_tds, 7.0, 300.0, num_tds * 1.6, 15.0, 60.0, sim_turb]])
            live_pred = model.predict(live_input)
            
            if live_pred[0] == 1:
                st.success("✅ CANLI ANALİZ SONUCU: SU İÇİLEBİLİR VE GÜVENLİ")
                st.balloons()
            else:
                st.error("🚨 CANLI ANALİZ SONUCU: UYGUNSUZ DEĞER TESPİT EDİLDİ")

    # 1 Saniyede bir değerlerin canlı güncellenmesi için (Sadece 3. Paneldeyken çalışır)
    time.sleep(1)
    st.rerun()