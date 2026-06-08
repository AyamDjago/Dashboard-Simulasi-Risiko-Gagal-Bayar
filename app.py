import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from model3 import LeasingModel

# Pengaturan Halaman Web
st.set_page_config(page_title="Dashboard Simulasi Leasing", layout="wide")

st.title("🏦 Dashboard Akhir Simulasi Risiko Gagal Bayar Leasing")
st.markdown("Aplikasi ini menggabungkan simulasi real-time jalur risiko dan uji validitas statistik menggunakan metode Monte Carlo.")

# --- SIDEBAR (PANEL KIRI UNTUK KONTROL) ---
st.sidebar.header("⚙️ Parameter Umum")
N = st.sidebar.number_input("Jumlah Nasabah per Simulasi", min_value=10, max_value=500, value=100)
bulan = st.sidebar.slider("Durasi Evaluasi (Bulan)", 6, 36, 12)

st.sidebar.subheader("🌍 Kondisi Lingkungan & Profil Dasar")
maks_guncangan = st.sidebar.slider("Maks. Guncangan Ekonomi (ES)", 0.0, 1.0, 0.5, 0.1)
maks_tabungan_dasar = st.sidebar.slider("Maks. Dana Darurat Standar (FB)", 0.0, 1.0, 0.5, 0.1)
maks_boros_dasar = st.sidebar.slider("Maks. Sifat Konsumtif Standar (FI)", 1.0, 3.0, 2.0, 0.1)

st.sidebar.subheader("🏢 Kebijakan Leasing")
kekuatan_intervensi = st.sidebar.slider("Kekuatan Keringanan Restrukturisasi (LI)", 0.0, 1.0, 0.2, 0.05)


# --- PEMBAGIAN TAB DI DASHBOARD ---
tab1, tab2 = st.tabs(["📈 Tren Jalur Risiko (Real-Time)", "📊 Analisis Stabilitas Monte Carlo"])

# ====================================================================
# TAB 1: TREN JALUR RISIKO REAL-TIME
# ====================================================================
with tab1:
    st.subheader("Analisis Perbandingan Jalur Risiko Bulanan")
    st.markdown("Klik tombol di bawah untuk melihat perbandingan langsung antara skenario Pembiaran dan Reaktif secara real-time.")
    
    if st.button("Jalankan Simulasi Jalur", type="primary"):
        # Jalankan model tunggal
        model_pembiaran = LeasingModel(N, False, maks_guncangan, maks_tabungan_dasar, maks_boros_dasar, kekuatan_intervensi)
        model_reaktif = LeasingModel(N, True, maks_guncangan, maks_tabungan_dasar, maks_boros_dasar, kekuatan_intervensi)

        for i in range(bulan):
            model_pembiaran.step()
            model_reaktif.step()

        data_pembiaran = model_pembiaran.datacollector.get_model_vars_dataframe()
        data_reaktif = model_reaktif.datacollector.get_model_vars_dataframe()

        # Visualisasi
        fig1, ax1 = plt.subplots(figsize=(10, 4))
        ax1.plot(data_pembiaran["Rata_Rata_Risiko"], label="Tanpa Intervensi (Pembiaran)", color="red", marker='o')
        ax1.plot(data_reaktif["Rata_Rata_Risiko"], label="Dengan Intervensi (Reaktif)", color="green", marker='s')
        ax1.axhline(y=1.0, color='black', linestyle='--', label='Batas Default (Aset Ditarik)')
        ax1.set_xlabel("Bulan ke-")
        ax1.set_ylabel("Rata-rata Tingkat Risiko (DR)")
        ax1.set_ylim(0, 1.2)
        ax1.legend()
        ax1.grid(True, linestyle=':')
        
        st.pyplot(fig1)
        st.success("Tren bulanan berhasil diperbarui!")

# ====================================================================
# TAB 2: ANALISIS MONTE CARLO
# ====================================================================
with tab2:
    st.subheader("Uji Validitas 4 Skenario 'What-If' (Metode Monte Carlo)")
    st.markdown("Menjalankan simulasi berulang kali untuk mendapatkan rata-rata statistik yang stabil dari 4 skenario berbeda.")
    
    # Beri slider jumlah iterasi agar web tidak crash/freeze jika laptop berat
    iterasi = st.slider("Jumlah Iterasi Monte Carlo", min_value=50, max_value=1000, value=200, step=50, 
                        help="Untuk sidang/final gunakan 1000. Untuk testing cepat gunakan 200.")
    
    if st.button("Mulai Perhitungan Monte Carlo", type="secondary"):
        
        # Fungsi internal Monte Carlo
        def run_mc_core(nama_skenario, gunakan_intervensi, maks_tabungan, maks_boros, p_bar, progress_start, progress_end):
            hasil_akhir_dr = []
            steps_per_run = iterasi
            
            for i in range(iterasi):
                model = LeasingModel(N=N, gunakan_intervensi=gunakan_intervensi, maks_guncangan=maks_guncangan, maks_tabungan=maks_tabungan, maks_boros=maks_boros)
                for _ in range(bulan):
                    model.step()
                
                data = model.datacollector.get_model_vars_dataframe()
                hasil_akhir_dr.append(data["Rata_Rata_Risiko"].iloc[-1])
                
                # Update progress bar secara halus
                current_prog = progress_start + ((i / iterasi) * (progress_end - progress_start))
                p_bar.progress(min(current_prog, 1.0), text=f"Menghitung {nama_skenario}... ({i+1}/{iterasi})")
                
            return np.mean(hasil_akhir_dr)

        # Progress bar tunggal untuk semua skenario
        progress_bar = st.progress(0.0, text="Menyiapkan simulasi...")
        
        # Eksekusi 4 skenario berurutan dengan membagi jatah progress bar (masing-masing 25%)
        dr_pembiaran = run_mc_core("Skenario Pembiaran", False, maks_tabungan_dasar, maks_boros_dasar, progress_bar, 0.0, 0.25)
        dr_reaktif = run_mc_core("Skenario Reaktif", True, maks_tabungan_dasar, maks_boros_dasar, progress_bar, 0.25, 0.50)
        dr_preventif = run_mc_core("Skenario Preventif", True, maks_tabungan_dasar + 0.3, maks_boros_dasar, progress_bar, 0.50, 0.75)
        dr_konsumtif = run_mc_core("Skenario Konsumtif Tinggi", True, maks_tabungan_dasar, maks_boros_dasar + 1.0, progress_bar, 0.75, 1.0)
        
        progress_bar.empty() # Hapus jika selesai

        # Tampilkan Angka Hasil Perhitungan di Dashboard
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("DR Pembiaran", f"{dr_pembiaran:.3f}")
        col2.metric("DR Reaktif", f"{dr_reaktif:.3f}")
        col3.metric("DR Preventif", f"{dr_preventif:.3f}")
        col4.metric("DR Konsumtif Tinggi", f"{dr_konsumtif:.3f}")

        # Membuat Grafik Batang Monte Carlo
        fig2, ax2 = plt.subplots(figsize=(10, 5))
        skenarios = ['Pembiaran', 'Reaktif', 'Preventif (Buffer +)', 'Konsumtif Tinggi (Indiscipline +)']
        nilai_drs = [dr_pembiaran, dr_reaktif, dr_preventif, dr_konsumtif]
        warna = ['#ff4b4b', '#00bc7c', '#1c83e1', '#fca311']

        ax2.bar(skenarios, nilai_drs, color=warna)
        ax2.axhline(y=1.0, color='black', linestyle='--', label='Batas Gagal Bayar (Default)')
        ax2.set_ylabel("Rata-rata Risiko Akhir (DR)")
        ax2.set_ylim(0, 1.2)
        ax2.legend()
        ax2.grid(axis='y', linestyle=':', alpha=0.7)
        
        st.pyplot(fig2)
        
        # --- TABEL RINGKASAN ANALITIK ---
        st.markdown("### Tabel Ringkasan Analitik")
        
        # Membuat tabel data menggunakan Pandas
        import pandas as pd
        df_analitik = pd.DataFrame({
            "Skenario": skenarios,
            "Rata-rata Risiko Akhir (DR)": [round(x, 3) for x in nilai_drs],
            "Status Keselamatan": [
                "Gagal Bayar Mayoritas" if x >= 1.0 else "Restrukturisasi/Aman" for x in nilai_drs
            ]
        })
        
        # Menghitung persentase penurunan risiko dibandingkan Pembiaran
        dr_base = df_analitik.loc[0, "Rata-rata Risiko Akhir (DR)"]
        df_analitik["Efektivitas Penurunan Risiko"] = [
            "0%" if i == 0 else f"{round(((dr_base - val) / dr_base) * 100, 1)}%" 
            for i, val in enumerate(df_analitik["Rata-rata Risiko Akhir (DR)"])
        ]
        
        # Menampilkan tabel yang interaktif di Streamlit
        st.dataframe(df_analitik, use_container_width=True)