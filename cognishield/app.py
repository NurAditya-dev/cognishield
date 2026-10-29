"""
CogniShield: Platform Analisis Risiko Kognitif Multi-Dimensi & Deteksi Astroturfing
Entry Point Streamlit (app.py)
"""

import os
import sys
import json
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

# Pastikan direktori cognishield/ selalu masuk ke path impor modul
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from modules.preprocessing import preprocess_text
from modules.risk_scoring import CognitiveRiskScorer
from modules.astroturfing import AstroturfingDetector
from modules.ingestion import load_dataframe_from_file, detect_text_column, extract_clean_posts


# Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="CogniShield TNI-AD | Cyber Cognitive Defense",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS untuk tampilan analitis intelijen modern
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #1E3A8A 0%, #3B82F6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        color: #64748B;
        font-size: 1.05rem;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        border-radius: 10px;
        padding: 18px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .badge-safe {
        background-color: #DCFCE7;
        color: #166534;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .badge-warn {
        background-color: #FEF3C7;
        color: #92400E;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .badge-danger {
        background-color: #FEE2E2;
        color: #991B1B;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .intel-box {
        background-color: #0F172A;
        color: #F1F5F9;
        font-family: 'Courier New', Courier, monospace;
        padding: 20px;
        border-radius: 8px;
        border-left: 4px solid #38BDF8;
        white-space: pre-wrap;
    }
</style>
""", unsafe_allow_html=True)


# Inisialisasi State Session Streamlit
if "risk_scorer" not in st.session_state:
    st.session_state.risk_scorer = CognitiveRiskScorer()
if "astroturfing_detector" not in st.session_state:
    st.session_state.astroturfing_detector = AstroturfingDetector()
if "last_single_result" not in st.session_state:
    st.session_state.last_single_result = None
if "last_batch_result" not in st.session_state:
    st.session_state.last_batch_result = None


# Sidebar Navigation & System Info
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/shield.png", width=64)
    st.markdown("### 🛡️ CogniShield TNI-AD")
    st.caption("Sistem Pertahanan Siber Sosial & Deteksi Astroturfing\nPUSSIBERAD x CODEPOLITAN 2026")
    st.markdown("---")
    
    st.markdown("#### ⚙️ Pengaturan Mesin")
    sim_threshold = st.slider(
        "Ambang Batas Kemiripan Buzzer (Similarity Threshold):",
        min_value=0.40,
        max_value=0.95,
        value=0.65,
        step=0.05,
        help="Skor di atas nilai ini diidentifikasi sebagai koordinasi atau pengulangan narasi astroturfing."
    )
    
    st.markdown("---")
    st.markdown("#### 📌 Status Pipeline NLP")
    st.success("✔ Case Folding & Slang Normalizer Aktif")
    st.success("✔ TF-IDF N-gram (1,2) Ready")
    st.success("✔ Multi-Dimensional Risk Index Ready")
    
    st.markdown("---")
    st.caption("Kartika Cyber Hackathon 2026 • Siber Sosial")


# Main Page Header
st.markdown("<div class='main-header'>CogniShield TNI-AD: Deteksi Dini Disinformasi & Astroturfing</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-header'>Prototype Sistem Deteksi Dini Disinformasi, Risiko Kognitif, dan Kampanye Narasi Terkoordinasi (Buzzer/Bot) Media Sosial.</div>", unsafe_allow_html=True)


# Tab Menu Horizontal Sesuai Spesifikasi (3 Fitur MVP)
tab1, tab2, tab3 = st.tabs([
    "🔍 Tab 1: Single-Input Analyzer",
    "🤖 Tab 2: Deteksi Astroturfing",
    "📋 Tab 3: Lembar Ringkasan Intelijen"
])


# ==============================================================================
# TAB 1: SINGLE-INPUT ANALYZER
# ==============================================================================
with tab1:
    st.subheader("Analisis Risiko Kognitif Tunggal (Single-Input Analyzer)")
    st.markdown("Evaluasi konten unggahan tunggal terhadap potensi provokasi, manipulasi naratif konspirasi, dan sensasionalitas semu.")

    # Preset contoh teks untuk demo cepat
    col_preset1, col_preset2, col_preset3 = st.columns(3)
    sample_text = ""
    if col_preset1.button("📌 Contoh Teks Berbahaya / Provokasi", use_container_width=True):
        st.session_state.sample_input = "VIRALKAN SEKARANG JUGA!! Rezim antek asing ini sudah keterlaluan membodohi rakyat, semua bukti konspirasi akan kita bongkar habis!! Jangan mau dicuci otak oleh media bayaran laknat!!"
    if col_preset2.button("⚠️ Contoh Teks Waspada / Sensasional", use_container_width=True):
        st.session_state.sample_input = "Waspada kawan-kawan!! Katanya ada isu rahasia yang sengaja ditutup-tutupi para elit politik. Tolong sebarkan sebelum dihapus!"
    if col_preset3.button("✅ Contoh Teks Netral / Berita Aman", use_container_width=True):
        st.session_state.sample_input = "Badan Meteorologi mengimbau masyarakat pesisir untuk memperhatikan prakiraan pasang air laut selama tiga hari ke depan."

    user_text = st.text_area(
        "Masukkan teks unggahan / narasi media sosial:",
        value=st.session_state.get("sample_input", ""),
        height=140,
        placeholder="Ketik atau tempel teks narasi di sini..."
    )

    col_btn, _ = st.columns([1, 4])
    analyze_btn = col_btn.button("🚀 Mulai Analisis Kognitif", type="primary", use_container_width=True)

    if analyze_btn or (user_text and st.session_state.last_single_result is None):
        if not user_text.strip():
            st.warning("Silakan masukkan teks terlebih dahulu untuk dianalisis.")
        else:
            with st.spinner("Memproses pra-pemrosesan teks & menghitung Multi-Dimensional Cognitive Risk Index..."):
                cleaned_text = preprocess_text(user_text)
                analysis = st.session_state.risk_scorer.analyze_text(user_text)
                st.session_state.last_single_result = {
                    "raw": user_text,
                    "cleaned": cleaned_text,
                    "analysis": analysis
                }

    if st.session_state.last_single_result:
        res = st.session_state.last_single_result
        analysis = res["analysis"]
        score = analysis["overall_risk_score"]
        category = analysis["risk_category"]
        color = analysis["risk_color"]

        st.markdown("---")
        
        # Grid Atas: Gauge Chart & Penilaian Kategori
        col_gauge, col_info = st.columns([1.2, 1.8])

        with col_gauge:
            # Plotly Indicator Gauge
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=score,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': f"Cognitive Risk Index<br><span style='font-size:0.8em;color:{color}'><b>Status: {category.upper()}</b></span>", 'font': {'size': 20}},
                number={'suffix': "%", 'font': {'size': 36, 'color': color}},
                gauge={
                    'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#475569"},
                    'bar': {'color': color, 'thickness': 0.28},
                    'bgcolor': "white",
                    'borderwidth': 1,
                    'bordercolor': "#CBD5E1",
                    'steps': [
                        {'range': [0, 35], 'color': "rgba(40, 167, 69, 0.2)"},
                        {'range': [35, 70], 'color': "rgba(253, 126, 20, 0.2)"},
                        {'range': [70, 100], 'color': "rgba(220, 53, 69, 0.2)"}
                    ],
                    'threshold': {
                        'line': {'color': "black", 'width': 3},
                        'thickness': 0.8,
                        'value': score
                    }
                }
            ))
            fig_gauge.update_layout(height=280, margin=dict(l=20, r=20, t=50, b=20))
            st.plotly_chart(fig_gauge, use_container_width=True)

        with col_info:
            st.markdown("#### 🎯 Hasil Evaluasi Risiko")
            if category == "Aman":
                st.markdown("<span class='badge-safe'>STATUS: AMAN (Risiko Rendah)</span>", unsafe_allow_html=True)
            elif category == "Waspada":
                st.markdown("<span class='badge-warn'>STATUS: WASPADA (Risiko Sedang)</span>", unsafe_allow_html=True)
            else:
                st.markdown("<span class='badge-danger'>STATUS: BAHAYA (Risiko Kognitif Tinggi)</span>", unsafe_allow_html=True)

            st.write("")
            st.info(f"**Ringkasan Diagnostik:**\n{analysis['summary']}")

            # Tampilkan kata kunci pemicu yang terdeteksi
            if analysis["detected_flags"]:
                st.markdown("**Kata Kunci & Pola Berbahaya Terdeteksi:**")
                flags_html = " ".join([
                    f"<span style='background-color:#E2E8F0; padding:3px 8px; border-radius:12px; font-size:0.85rem; margin-right:4px;'>⚠️ {item['keyword']} ({item['dimensi']})</span>"
                    for item in analysis["detected_flags"]
                ])
                st.markdown(flags_html, unsafe_allow_html=True)
            else:
                st.caption("Tidak ditemukan kata kunci indikator risiko manipulatif.")

        # Breakdown 4 Dimensi Kognitif
        st.markdown("#### 📊 Profil Multi-Dimensional Cognitive Risk Index")
        dims = analysis["dimensions"]
        dim_df = pd.DataFrame({
            "Dimensi Risiko": list(dims.keys()),
            "Skor (0-100)": list(dims.values())
        })

        fig_bar = px.bar(
            dim_df,
            x="Skor (0-100)",
            y="Dimensi Risiko",
            orientation='h',
            text="Skor (0-100)",
            color="Skor (0-100)",
            color_continuous_scale=["#28a745", "#fd7e14", "#dc3545"],
            range_x=[0, 100]
        )
        fig_bar.update_layout(height=240, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig_bar, use_container_width=True)

        with st.expander("🔎 Lihat Detail Pra-Pemrosesan Teks (Preprocessing Normalization)"):
            c_raw, c_clean = st.columns(2)
            c_raw.markdown("**Teks Asli (Input Mentah):**")
            c_raw.code(res["raw"])
            c_clean.markdown("**Teks Bersih (Normalized, Slang-Cleaned, Case-Folded):**")
            c_clean.code(res["cleaned"])


# ==============================================================================
# TAB 2: DETEKSI ASTROTURFING & KEMIRIPAN TEKS
# ==============================================================================
with tab2:
    st.subheader("Deteksi Astroturfing & Amplifikasi Terkoordinasi")
    st.markdown("Unggah berkas data CSV/JSON postingan media sosial untuk memetakan kesamaan teks antar-unggahan secara instan menggunakan TF-IDF dan Cosine Similarity.")

    col_upload, col_sample = st.columns([2, 1])
    
    with col_upload:
        uploaded_file = st.file_uploader(
            "Unggah Berkas CSV / JSON Narasi Medsos:",
            type=["csv", "json"],
            help="Berkas berisi kolom narasi/teks seperti 'text', 'content', 'komentar', atau 'tweet'."
        )

    with col_sample:
        st.write("")
        st.write("")
        use_sample = st.button("📁 Gunakan Sampel Bawaan (12 Postingan Buzzer)", use_container_width=True)

    df_posts = None
    if uploaded_file is not None:
        try:
            df_posts = load_dataframe_from_file(uploaded_file)
            st.success(f"Berkas berhasil dimuat: {len(df_posts)} baris data.")
        except Exception as e:
            st.error(f"Gagal membaca file: {e}")
    elif use_sample or ("use_sample_active" in st.session_state and st.session_state.use_sample_active):
        st.session_state.use_sample_active = True
        sample_path = os.path.join(os.path.dirname(__file__), "data", "sample_posts.csv")
        if os.path.exists(sample_path):
            df_posts = pd.read_csv(sample_path)
            st.info("Memakai dataset sampel bawaan CogniShield (`sample_posts.csv`).")

    if df_posts is not None and not df_posts.empty:
        # Pilih kolom teks
        detected_col = detect_text_column(df_posts)
        text_column = st.selectbox(
            "Pilih kolom teks yang akan dianalisis:",
            options=df_posts.columns.tolist(),
            index=df_posts.columns.tolist().index(detected_col) if detected_col in df_posts.columns else 0
        )

        raw_posts = extract_clean_posts(df_posts, text_column)

        if len(raw_posts) < 2:
            st.warning("Data membutuhkan minimal 2 baris teks untuk memetakan kesamaan antar-unggahan.")
        else:
            with st.spinner("Mengekstrak fitur TF-IDF dan menghitung Cosine Similarity Matrix..."):
                sim_matrix, preprocessed_posts = st.session_state.astroturfing_detector.fit_transform_similarity(
                    raw_posts, preprocess=True
                )
                metrics = st.session_state.astroturfing_detector.calculate_coordination_metrics(
                    sim_matrix, threshold=sim_threshold
                )
                suspicious_pairs = st.session_state.astroturfing_detector.find_suspicious_pairs(
                    sim_matrix, raw_posts, threshold=sim_threshold
                )
                top_terms = st.session_state.astroturfing_detector.get_top_repetitive_keywords(
                    raw_posts, top_n=8
                )

                # Simpan ke session untuk Tab 3
                st.session_state.last_batch_result = {
                    "df": df_posts,
                    "raw_posts": raw_posts,
                    "sim_matrix": sim_matrix,
                    "metrics": metrics,
                    "suspicious_pairs": suspicious_pairs,
                    "top_terms": top_terms,
                    "threshold": sim_threshold
                }

            # KPI Metrics Cards
            st.markdown("---")
            m_col1, m_col2, m_col3, m_col4 = st.columns(4)
            m_col1.metric("Total Unggahan", f"{metrics['total_posts']} Post")
            m_col2.metric("Pasangan Terkoordinasi", f"{metrics['high_similarity_pairs_count']} Pasang")
            m_col3.metric("Rasio Amplifikasi Buzzer", f"{metrics['amplification_ratio']}%")
            
            risk_label = "TERDETEKSI" if metrics["astroturfing_detected"] else "ORGANIK / MINIMAL"
            m_col4.metric("Status Astroturfing", risk_label)

            # Heatmap Matriks Kemiripan Teks
            st.markdown("#### 🗺️ Matriks Kemiripan Teks (Cosine Similarity Matrix)")
            st.caption("Nilai 1.0 = teks identik; nilai mendekati 0.0 = narasi berbeda total.")

            labels = [f"P#{i+1}: {t[:25]}..." for i, t in enumerate(raw_posts)]
            fig_heatmap = px.imshow(
                sim_matrix,
                labels=dict(x="ID Unggahan Target", y="ID Unggahan Asal", color="Cosine Similarity"),
                x=labels,
                y=labels,
                color_continuous_scale="Reds",
                zmin=0.0,
                zmax=1.0,
                aspect="auto"
            )
            fig_heatmap.update_layout(height=450, margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig_heatmap, use_container_width=True)

            # Tabel Pasangan Kemiripan Mencurigakan
            st.markdown(f"#### 🚨 Pasangan Unggahan Mencurigakan (Similarity ≥ {int(sim_threshold*100)}%)")
            if suspicious_pairs:
                pairs_display = []
                for p in suspicious_pairs:
                    pairs_display.append({
                        "Post A": f"#{p['post_a_id']}",
                        "Post B": f"#{p['post_b_id']}",
                        "Tingkat Kemiripan": f"{p['similarity_percentage']}%",
                        "Klasifikasi": p["coordination_level"],
                        "Cuplikan Post A": p["text_a"],
                        "Cuplikan Post B": p["text_b"]
                    })
                st.dataframe(pd.DataFrame(pairs_display), use_container_width=True)
            else:
                st.success(f"Tidak ada pasangan postingan yang melampaui ambang batas kemiripan ({int(sim_threshold*100)}%). Pola unggahan tampak organik.")

            # Top Replicated Buzzwords
            if top_terms:
                st.markdown("#### 📢 Kata Kunci / Slogan Paling Banyak Direplikasi")
                kw_cols = st.columns(len(top_terms))
                for idx, (term, score) in enumerate(top_terms):
                    kw_cols[idx].markdown(f"**`{term}`**<br><small>TF-IDF: {score}</small>", unsafe_allow_html=True)


# ==============================================================================
# TAB 3: LEMBAR RINGKASAN INTELIJEN & REKOMENDASI TAKTIS
# ==============================================================================
with tab3:
    st.subheader("Lembar Ringkasan Intelijen (Intelligence Briefing Sheet)")
    st.markdown("Laporan taktis terotomatisasi berbasis aturan yang merangkum hasil temuan dari analisis risiko kognitif dan operasi astroturfing serta memberikan langkah aksi taktis.")

    batch = st.session_state.get("last_batch_result")
    single = st.session_state.get("last_single_result")

    if not batch and not single:
        st.info("💡 Belum ada data analisis. Silakan jalankan analisis di **Tab 1** (Single-Input) atau unggah berkas di **Tab 2** (Astroturfing) untuk menghasilkan lembar intelijen otomatis.")
    else:
        # Konstruksi Laporan Otomatis Berbasis Aturan
        intel_report = []
        intel_report.append("=" * 72)
        intel_report.append("  COGNISHIELD THREAT INTELLIGENCE SUMMARY REPORT")
        intel_report.append("  Klasifikasi: SENSITIF - INTERNAL RESPONSE UNIT")
        intel_report.append("=" * 72)
        intel_report.append("")

        # 1. Executive Summary
        intel_report.append("[1] RINGKASAN EKSEKUTIF")
        if batch:
            metrics = batch["metrics"]
            thresh = int(batch["threshold"] * 100)
            if metrics["astroturfing_detected"]:
                threat_level = "TINGGI (COORDINATED ASTROTURFING ATTACK DETECTED)"
                summary_narrative = (
                    f"Teridentifikasi aktivitas amplifikasi narasi artifisial terkoordinasi (Astroturfing/Buzzer). "
                    f"Sebanyak {metrics['involved_posts_count']} dari {metrics['total_posts']} unggahan "
                    f"({metrics['amplification_ratio']}%) menunjukkan duplikasi narasi melebihi ambang batas {thresh}%. "
                    f"Ditemukan {metrics['high_similarity_pairs_count']} pasang narasi template yang direplikasi secara sistematis."
                )
            else:
                threat_level = "RENDAH - SEDANG (ORGANIK / SPORADIK)"
                summary_narrative = (
                    f"Pola persebaran narasi dalam sampel ({metrics['total_posts']} unggahan) cenderung organik. "
                    f"Rasio kemiripan ekstrem berada pada {metrics['amplification_ratio']}%, tidak menunjukkan adanya "
                    "infrastruktur bot terorkestrasi berskala besar."
                )
        elif single:
            cat = single["analysis"]["risk_category"]
            score = single["analysis"]["overall_risk_score"]
            threat_level = f"{cat.upper()} (RISIKO KOGNITIF: {score}%)"
            summary_narrative = single["analysis"]["summary"]
        
        intel_report.append(f"Status Ancaman: {threat_level}")
        intel_report.append(f"Ringkasan     : {summary_narrative}")
        intel_report.append("")

        # 2. Vektor & Dimensi Ancaman
        intel_report.append("[2] VEKTOR DAN DIMENSI ANCAMAN KOGNITIF")
        if single:
            dims = single["analysis"]["dimensions"]
            for d_name, d_val in dims.items():
                status_bar = "■" * int(d_val / 10) + "□" * (10 - int(d_val / 10))
                intel_report.append(f"  • {d_name:<28}: [{status_bar}] {d_val}%")
            if single["analysis"]["detected_flags"]:
                pemicu = ", ".join([f"{f['keyword']} ({f['dimensi']})" for f in single["analysis"]["detected_flags"]])
                intel_report.append(f"  • Pemicu Khusus Terdeteksi : {pemicu}")
        if batch and batch["top_terms"]:
            terms_str = ", ".join([f"'{t[0]}' (skor: {t[1]})" for t in batch["top_terms"]])
            intel_report.append(f"  • Slogan/Frase Utama Direplikasi: {terms_str}")
        intel_report.append("")

        # 3. Rekomendasi Tindakan Taktis (Rule-based Decision Matrix)
        intel_report.append("[3] REKOMENDASI TINDAKAN TAKTIS (COUNTERMEASURE PROTOCOLS)")
        
        is_high_risk = False
        if batch and batch["metrics"]["astroturfing_detected"]:
            is_high_risk = True
        elif single and single["analysis"]["overall_risk_score"] >= 70:
            is_high_risk = True

        if is_high_risk:
            intel_report.append("  [PROTOKOL MERAH - ESKALASI & INTERVENSI CEPAT]")
            intel_report.append("  1. Platform Moderation: Lakukan penandaan (flagging) akun sumber narasi kemiripan ≥85% untuk verifikasi bot.")
            intel_report.append("  2. Rate-Limiting Narasi: Batasi laju distribusi tagar/slogan yang direplikasi secara mekanik.")
            intel_report.append("  3. Counter-Messaging (Prebunking): Rilis klarifikasi fakta terverifikasi sebelum narasi manipulatif mendominasi ruang publik.")
            intel_report.append("  4. Cyber Threat Intel Escalation: Simpan jejak timestamp untuk pemetaan jaringan afiliasi buzzer.")
        else:
            intel_report.append("  [PROTOKOL HIJAU/KUNING - MONITORING & MITIGASI PASIF]")
            intel_report.append("  1. Continuous Telemetry: Lanjutkan pemantauan dinamika sentimen 6-12 jam ke depan.")
            intel_report.append("  2. Algorithmic Watchlist: Daftarkan kata kunci terkait dalam radar deteksi dini bila terjadi lonjakan volume tiba-tiba.")
            intel_report.append("  3. Edukasi Literasi Kognitif: Dorong saluran informasi resmi untuk menjaga transparansi data publik.")
        
        intel_report.append("")
        intel_report.append("=" * 72)
        intel_report.append("  Dihasilkan secara otomatis oleh CogniShield Security Engine")
        intel_report.append("=" * 72)

        report_text = "\n".join(intel_report)

        # Tampilkan Laporan dalam Format Terminal Intelijen
        st.markdown(f"<div class='intel-box'>{report_text}</div>", unsafe_allow_html=True)
        st.write("")

        # Tombol Download Laporan
        st.download_button(
            label="📥 Unduh Ringkasan Intelijen (.TXT)",
            data=report_text,
            file_name="CogniShield_Intelligence_Summary.txt",
            mime="text/plain"
        )
