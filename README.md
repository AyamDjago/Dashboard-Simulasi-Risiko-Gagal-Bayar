# 🏦 Dashboard Simulasi Risiko Gagal Bayar Leasing

Repository ini berisi proyek **Pemodelan dan Simulasi Data** untuk mensimulasikan risiko gagal bayar (*default risk*) nasabah leasing menggunakan **Agent-Based Modeling (ABM)** dengan framework **Mesa** dan visualisasi dashboard interaktif berbasis **Streamlit**.

Proyek ini mensimulasikan bagaimana faktor internal nasabah (sifat konsumtif, dana darurat), faktor eksternal (guncangan ekonomi), serta kebijakan restrukturisasi dari perusahaan leasing memengaruhi tingkat risiko nasabah secara agregat dari waktu ke waktu.

---

## 🚀 Fitur Utama
1. **📈 Tren Jalur Risiko Real-Time (Tab 1)**: Membandingkan secara dinamis tingkat risiko nasabah antara skenario **Pembiaran** (tanpa intervensi) dan **Reaktif** (dengan intervensi restrukturisasi) dari bulan ke bulan secara real-time.
2. **📊 Analisis Stabilitas Monte Carlo (Tab 2)**: Menguji sensitivitas model melalui ratusan hingga ribuan iterasi acak untuk memvalidasi stabilitas dari 4 skenario "What-If" berbeda:
   - **Skenario Pembiaran**: Skenario kontrol tanpa intervensi.
   - **Skenario Reaktif**: Intervensi restrukturisasi standar ketika nasabah berstatus Restrukturisasi.
   - **Skenario Preventif**: Intervensi reaktif ditambah peningkatan ketahanan finansial awal nasabah (Buffer Dana Darurat $+0.3$).
   - **Skenario Konsumtif Tinggi**: Pengaruh peningkatan sifat konsumtif nasabah secara signifikan (Indisipliner Finansial $+1.0$).
3. **⚙️ Parameter Kustomisasi Dinamis**: Konfigurasi jumlah nasabah, durasi evaluasi, batas guncangan ekonomi, profil finansial dasar nasabah, dan kekuatan restrukturisasi langsung melalui sidebar dashboard Streamlit.

---

## 📂 Struktur Repositori

| Berkas / Direktori | Deskripsi |
| :--- | :--- |
| [app.py](file:///e:/Semester%206/Pemodelan%20dan%20Simulasi%20Data/simulasi_leasing/app.py) | Dashboard Streamlit utama yang mengintegrasikan simulasi real-time dan analisis statistik Monte Carlo. |
| [model3.py](file:///e:/Semester%206/Pemodelan%20dan%20Simulasi%20Data/simulasi_leasing/model3.py) | Definisi kelas Agen (`NasabahAgent`) dan Model (`LeasingModel`) final dengan parameterisasi dinamis dari Streamlit. |

---

## 🛠️ Logika & Formulasi Matematika Model

Model ini dijalankan secara diskret berdasarkan langkah waktu bulanan. Setiap nasabah diwakili oleh sebuah agen individual (`NasabahAgent`).

### 1. Karakteristik Agen (Nasabah)
Setiap agen memiliki tiga profil keuangan dasar yang diinisialisasi secara acak:
- **Sifat Konsumtif ($FI$)**: Menunjukkan kerentanan terhadap pengeluaran konsumtif. Nilai awal diundi dari $FI \sim U(1.0, \text{maks\_boros})$.
- **Dana Darurat ($FB$)**: Menunjukkan ketahanan finansial atau cadangan dana darurat nasabah. Nilai awal diundi dari $FB \sim U(0.0, \text{maks\_tabungan})$.
- **Tingkat Risiko ($DR$)**: Akumulasi risiko gagal bayar nasabah (*Debt Risk* / *Default Risk*). Diinisialisasi secara acak dari $DR \sim U(0.0, 0.1)$.

### 2. Dinamika Risiko Bulanan
Setiap bulan (pada setiap `step`), tingkat risiko ($DR$) diperbarui berdasarkan pengaruh lingkungan dan perilaku nasabah:
$$DR_{t} = DR_{t-1} + \max(0, (ES \times FI) - FB) - LI$$

*Di mana:*
- $ES$: Guncangan Ekonomi (*Economic Stress* / *Stressor*), diundi secara acak setiap bulan dari $ES \sim U(0.0, \text{maks\_guncangan})$.
- $LI$: Kekuatan Keringanan Restrukturisasi (*Leasing Intervention*), aktif jika model diatur menggunakan intervensi (`gunakan_intervensi=True`) dan status nasabah berada di tingkat **Restrukturisasi**.
- Nilai $DR_t$ selalu dibatasi minimal $0.0$ agar tidak negatif.

### 3. Diagram Transisi Status (*State Chart*)
Berdasarkan nilai tingkat risiko ($DR$) yang dihitung, agen akan diklasifikasikan ke dalam 4 status:
- **Lancar** ($DR < 0.3$)
- **Berisiko** ($0.3 \le DR < 0.8$)
- **Restrukturisasi** ($0.8 \le DR < 1.0$) $\rightarrow$ berhak mendapatkan diskon keringanan risiko sebesar $LI$.
- **Gagal Bayar** ($DR \ge 1.0$) $\rightarrow$ agen mengalami *default*, aset ditarik oleh perusahaan leasing, dan aktivitas/langkah pembaruan agen dihentikan.

---

## 📥 Instalasi & Persyaratan

Proyek ini memerlukan Python versi $\ge 3.8$. Anda dapat memasang paket dependensi yang diperlukan dengan perintah:

```bash
pip install mesa streamlit numpy matplotlib pandas
```

---

## 🎮 Cara Menjalankan Program

Untuk membuka dashboard visual interaktif lengkap di peramban Anda, jalankan perintah berikut di terminal:
```bash
streamlit run app.py
```

---

## 📊 Visualisasi & Analisis Dashboard (`app.py`)

- **Tab 1: Tren Jalur Risiko (Real-Time)**
  Menampilkan grafik garis perbandingan langsung pergerakan rata-rata tingkat risiko nasabah setiap bulannya antara skenario Pembiaran dan Reaktif. Grafik ini membantu melihat seberapa cepat risiko menembus batas kritis default ($1.0$) jika dibiarkan tanpa kebijakan restrukturisasi.
  
- **Tab 2: Analisis Stabilitas Monte Carlo**
  Menjalankan simulasi berulang kali (konfigurasi $50 - 1000$ iterasi) untuk merata-ratakan hasil statistik agar stabil dan valid secara akademis. Menampilkan:
  - **Metrik Risiko Akhir**: Rata-rata risiko akhir nasabah dari keempat skenario.
  - **Grafik Batang Perbandingan**: Visualisasi perbandingan nilai risiko akhir masing-masing skenario terhadap batas gagal bayar.
  - **Tabel Ringkasan Analitik**: Memuat angka detail risiko akhir, status keselamatan portfolio, dan persentase efektivitas penurunan risiko dibandingkan dengan Skenario Pembiaran.
