import streamlit as st
import matplotlib.pyplot as plt
from model3 import LeasingModel

# Pengaturan Halaman Web
st.set_page_config(page_title="Simulasi Leasing", layout="wide")

st.title("🏦 Dashboard Simulasi Risiko Gagal Bayar Leasing")
st.markdown("Gunakan panel di sebelah kiri untuk mengubah kondisi ekonomi dan kebijakan leasing, lalu lihat bagaimana dampaknya terhadap nasabah secara *real-time*.")

# --- SIDEBAR (PANEL KIRI) ---
st.sidebar.header("⚙️ Parameter Simulasi")
N = st.sidebar.number_input("Jumlah Nasabah", min_value=10, max_value=500, value=100)
bulan = st.sidebar.slider("Durasi (Bulan)", 6, 36, 12)

st.sidebar.subheader("🌍 Kondisi Lingkungan")
maks_guncangan = st.sidebar.slider("Maks. Guncangan Ekonomi (Stressor)", 0.0, 1.0, 0.5, 0.1)

st.sidebar.subheader("👤 Profil Nasabah")
maks_tabungan = st.sidebar.slider("Maks. Dana Darurat (Resilience)", 0.0, 1.0, 0.5, 0.1)
maks_boros = st.sidebar.slider("Maks. Sifat Konsumtif (Distorsi)", 1.0, 3.0, 2.0, 0.1)

st.sidebar.subheader("🏢 Kebijakan Leasing")
kekuatan_intervensi = st.sidebar.slider("Kekuatan Keringanan (CBT Protocol)", 0.0, 1.0, 0.2, 0.05)

# --- TOMBOL JALANKAN ---
if st.sidebar.button("🚀 Jalankan Simulasi", type="primary"):
    
    # Menyiapkan 2 Model sekaligus (Untuk Komparasi)
    model_pembiaran = LeasingModel(N, False, maks_guncangan, maks_tabungan, maks_boros, kekuatan_intervensi)
    model_reaktif = LeasingModel(N, True, maks_guncangan, maks_tabungan, maks_boros, kekuatan_intervensi)

    # Menjalankan loop waktu dengan progress bar
    progress_text = "Menyimulasikan dinamika nasabah..."
    my_bar = st.progress(0, text=progress_text)
    
    for i in range(bulan):
        model_pembiaran.step()
        model_reaktif.step()
        my_bar.progress((i + 1) / bulan, text=progress_text)
    
    my_bar.empty() # Hilangkan bar jika selesai

    # Mengambil Data
    data_pembiaran = model_pembiaran.datacollector.get_model_vars_dataframe()
    data_reaktif = model_reaktif.datacollector.get_model_vars_dataframe()

    # --- MEMBUAT GRAFIK ---
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(data_pembiaran["Rata_Rata_Risiko"], label="Tanpa Intervensi (Pembiaran)", color="red", marker='o', linewidth=2)
    ax.plot(data_reaktif["Rata_Rata_Risiko"], label="Dengan Intervensi (Reaktif)", color="green", marker='s', linewidth=2)
    
    ax.axhline(y=1.0, color='black', linestyle='--', label='Batas Kritis (Aset Ditarik)')
    
    ax.set_title("Perbandingan Risiko Gagal Bayar Nasabah")
    ax.set_xlabel("Bulan ke-")
    ax.set_ylabel("Rata-rata Tingkat Risiko (DR)")
    ax.set_ylim(0, 1.1)
    ax.legend()
    ax.grid(True, linestyle=':', alpha=0.7)

    # Menampilkan ke Web
    st.pyplot(fig)
    st.success("✨ Simulasi berhasil dijalankan! Coba geser slider di samping dan klik tombol lagi untuk melihat skenario yang berbeda.")