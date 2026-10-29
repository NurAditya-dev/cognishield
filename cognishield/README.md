# CogniShield 🛡️

**Cognitive Risk & Astroturfing Defense System**  
Platform Analisis Risiko Kognitif Multi-Dimensi & Deteksi Amplifikasi Narasi Terkoordinasi (Buzzer/Bot) Media Sosial.

---

## 📂 Struktur Direktori Proyek

```plaintext
cognishield/
├── app.py                  # Entry point antarmuka Streamlit
├── modules/
│   ├── ingestion.py        # Pengolahan input teks / file CSV & JSON
│   ├── preprocessing.py    # Pembersihan URL, emoji, karakter khusus & normalisasi slang
│   ├── risk_scoring.py     # Logika Multi-Dimensional Cognitive Risk Index (0-100%)
│   └── astroturfing.py     # Deteksi kemiripan teks (TF-IDF & Cosine Similarity)
├── data/
│   └── sample_posts.csv    # Sampel dataset postingan buzzer & akun organik
├── requirements.txt        # Daftar dependensi utama
└── test_backend.py         # Skrip verifikasi unit modul backend
```

---

## 🚀 Cara Menjalankan Aplikasi

1. **Aktifkan Virtual Environment**:
   - Di PowerShell:
     ```powershell
     .\.venv\Scripts\Activate.ps1
     ```
   - Atau langsung gunakan Python/Streamlit dari `.venv`:
     ```powershell
     .\.venv\Scripts\streamlit.exe run cognishield/app.py
     ```

2. **Buka di Peramban Web**:
   Kunjungi [http://localhost:8501](http://localhost:8501).

---

## 🎯 3 Fitur Utama (MVP)

### 1. Tab 1 - Single-Input Analyzer
* **Input**: Masukan teks narasi bebas atau gunakan tombol preset pengujian.
* **Gauge Indicator**: Visualisasi dinamis skor risiko (0–100%) dengan kategori:
  * 🟢 **Aman** (< 30%)
  * 🟡 **Waspada** (30% – 65%)
  * 🔴 **Bahaya** (≥ 65%)
* **Multi-Dimensional Profile**: Menampilkan 4 dimensi kognitif:
  1. *Sensasionalitas & Urgensi Semu*
  2. *Provokasi & Polarisasi Sosial*
  3. *Pembingkaian Konspirasi & Manipulasi Naratif*
  4. *Toksisitas Emosional & Agresi*
* **Keyword Flags & Normalisasi**: Perbandingan teks asli vs hasil pembersihan slang, emoji, dan tautan.

### 2. Tab 2 - Deteksi Astroturfing
* **File Uploader**: Unggah berkas CSV atau JSON (tersedia opsi pakai sampel bawaan 12 data postingan).
* **Cosine Similarity Matrix**: Heatmap interaktif Plotly yang memetakan korelasi leksikal dan semantik antar-postingan.
* **Tabel Deteksi Buzzer**: Daftar pasangan postingan dengan kemiripan tinggi (≥ threshold), klasifikasi kloning bot, dan frase/slogan dominan yang direplikasi secara artifisial.

### 3. Tab 3 - Lembar Ringkasan Intelijen
* **Automated Threat Report**: Laporan taktis berbasis aturan (*rule-based intelligence summary*) dengan klasifikasi tingkat ancaman.
* **Rekomendasi Tindakan Taktis**: Protokol mitigasi platform (penandaan akun, pembatasan laju sebaran), strategi komunikasi (*prebunking* / *counter-messaging*), dan eskalasi keamanan siber.
* **Exporting**: Opsi unduh laporan ringkasan taktis dalam format `.txt`.
