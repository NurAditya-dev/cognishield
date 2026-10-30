"""
CogniShield: Platform Analisis Risiko Kognitif Multi-Dimensi & Deteksi Astroturfing
Entry Point Streamlit (app.py) — Modern Cyber Intelligence Dashboard UI/UX
"""

import os
import sys
import re
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


# ==============================================================================
# KONFIGURASI HALAMAN STREAMLIT
# ==============================================================================
st.set_page_config(
    page_title="CogniShield TNI-AD | Cyber Cognitive Defense",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# CUSTOM CSS — MODERN CYBER INTELLIGENCE & GLASSMORPHISM DESIGN
# ==============================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Hero Banner */
    .hero-banner {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.92) 0%, rgba(30, 58, 138, 0.78) 55%, rgba(15, 23, 42, 0.95) 100%);
        border: 1px solid rgba(56, 189, 248, 0.25);
        border-radius: 18px;
        padding: 26px 30px;
        margin-bottom: 24px;
        box-shadow: 0 12px 32px -8px rgba(0, 0, 0, 0.35), inset 0 1px 0 0 rgba(255, 255, 255, 0.1);
        position: relative;
        overflow: hidden;
    }
    .hero-banner::before {
        content: "";
        position: absolute;
        top: -50%;
        right: -10%;
        width: 340px;
        height: 340px;
        background: radial-gradient(circle, rgba(56, 189, 248, 0.16) 0%, transparent 70%);
        pointer-events: none;
    }
    .hero-tag {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(56, 189, 248, 0.15);
        border: 1px solid rgba(56, 189, 248, 0.4);
        color: #38BDF8;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        padding: 4px 12px;
        border-radius: 999px;
        margin-bottom: 10px;
    }
    .hero-title {
        font-size: 2.05rem;
        font-weight: 800;
        color: #F8FAFC;
        margin: 0 0 6px 0;
        letter-spacing: -0.02em;
        line-height: 1.2;
    }
    .hero-title span {
        background: linear-gradient(90deg, #38BDF8 0%, #818CF8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .hero-subtitle {
        color: #94A3B8;
        font-size: 0.96rem;
        margin: 0;
        max-width: 820px;
        line-height: 1.55;
    }

    /* Section Header */
    .section-header {
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 1.15rem;
        font-weight: 700;
        margin: 18px 0 12px 0;
        padding-bottom: 8px;
        border-bottom: 1px solid rgba(148, 163, 184, 0.2);
    }

    /* Glass Card Container */
    .glass-card {
        background: rgba(30, 41, 59, 0.55);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(148, 163, 184, 0.18);
        border-radius: 16px;
        padding: 22px 24px;
        margin-bottom: 16px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .glass-card:hover {
        border-color: rgba(56, 189, 248, 0.35);
    }

    /* KPI Stat Cards */
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
        gap: 14px;
        margin: 14px 0 22px 0;
    }
    .kpi-card {
        background: linear-gradient(145deg, rgba(30, 41, 59, 0.82), rgba(15, 23, 42, 0.88));
        border: 1px solid rgba(148, 163, 184, 0.18);
        border-radius: 14px;
        padding: 18px 20px;
        position: relative;
        overflow: hidden;
        transition: all 0.22s ease;
    }
    .kpi-card:hover {
        transform: translateY(-3px);
        border-color: rgba(56, 189, 248, 0.45);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25);
    }
    .kpi-label {
        font-size: 0.78rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #94A3B8;
        margin-bottom: 6px;
    }
    .kpi-value {
        font-size: 1.65rem;
        font-weight: 800;
        color: #F8FAFC;
        line-height: 1.2;
    }
    .kpi-sub {
        font-size: 0.78rem;
        color: #64748B;
        margin-top: 4px;
    }

    /* Status Badges (Aman, Waspada, Bahaya) */
    .status-banner {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 14px 18px;
        border-radius: 12px;
        margin-bottom: 14px;
        font-weight: 700;
    }
    .status-safe {
        background: rgba(16, 185, 129, 0.14);
        border: 1px solid rgba(16, 185, 129, 0.45);
        color: #34D399;
    }
    .status-warn {
        background: rgba(245, 158, 11, 0.15);
        border: 1px solid rgba(245, 158, 11, 0.45);
        color: #FBBF24;
    }
    .status-danger {
        background: rgba(239, 68, 68, 0.16);
        border: 1px solid rgba(239, 68, 68, 0.5);
        color: #F87171;
    }

    /* FIXED: Keyword & Pattern Pills Container (Anti-Potong & High Contrast) */
    .flags-wrapper {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 10px;
        margin-bottom: 8px;
        align-items: center;
    }
    .flag-chip {
        display: inline-flex;
        align-items: center;
        gap: 7px;
        padding: 6px 13px;
        border-radius: 999px;
        font-size: 0.82rem;
        font-weight: 600;
        line-height: 1.3;
        white-space: nowrap;
        transition: all 0.18s ease;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.18);
    }
    .flag-chip:hover {
        transform: translateY(-2px) scale(1.02);
    }
    .flag-chip .dim-tag {
        font-size: 0.7rem;
        font-weight: 700;
        opacity: 0.85;
        padding: 2px 7px;
        border-radius: 999px;
        background: rgba(0, 0, 0, 0.25);
        letter-spacing: 0.02em;
    }

    /* Warna Spesifik per Dimensi Risiko */
    .chip-sensational {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.22), rgba(217, 119, 6, 0.32));
        border: 1px solid rgba(251, 191, 36, 0.55);
        color: #FDE68A;
    }
    .chip-provocation {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.24), rgba(185, 28, 28, 0.34));
        border: 1px solid rgba(248, 113, 113, 0.6);
        color: #FECACA;
    }
    .chip-conspiracy {
        background: linear-gradient(135deg, rgba(168, 85, 247, 0.24), rgba(126, 34, 206, 0.34));
        border: 1px solid rgba(192, 132, 252, 0.6);
        color: #E9D5FF;
    }
    .chip-toxicity {
        background: linear-gradient(135deg, rgba(244, 63, 94, 0.24), rgba(190, 18, 60, 0.34));
        border: 1px solid rgba(251, 113, 133, 0.6);
        color: #FFE4E6;
    }

    /* Highlighted Narrative Box */
    .annotated-box {
        background: rgba(15, 23, 42, 0.78);
        border: 1px solid rgba(148, 163, 184, 0.22);
        border-left: 4px solid #38BDF8;
        border-radius: 12px;
        padding: 16px 20px;
        font-size: 0.98rem;
        line-height: 1.75;
        color: #E2E8F0;
        margin: 10px 0 16px 0;
    }
    .hl-mark {
        padding: 2px 7px;
        border-radius: 6px;
        font-weight: 700;
        border-bottom: 2px solid;
        margin: 0 1px;
    }
    .hl-sensational { background: rgba(245, 158, 11, 0.25); color: #FDE68A; border-color: #F59E0B; }
    .hl-provocation { background: rgba(239, 68, 68, 0.28); color: #FECACA; border-color: #EF4444; }
    .hl-conspiracy  { background: rgba(168, 85, 247, 0.28); color: #E9D5FF; border-color: #A855F7; }
    .hl-toxicity    { background: rgba(244, 63, 94, 0.28); color: #FFE4E6; border-color: #F43F5E; }

    /* Dimension Progress Card */
    .dim-card {
        background: rgba(15, 23, 42, 0.65);
        border: 1px solid rgba(148, 163, 184, 0.16);
        border-radius: 12px;
        padding: 14px 16px;
        margin-bottom: 10px;
    }
    .dim-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 0.88rem;
        font-weight: 600;
        color: #E2E8F0;
        margin-bottom: 8px;
    }
    .dim-bar-bg {
        width: 100%;
        height: 9px;
        background: rgba(148, 163, 184, 0.15);
        border-radius: 999px;
        overflow: hidden;
    }
    .dim-bar-fill {
        height: 100%;
        border-radius: 999px;
        transition: width 0.5s ease;
    }

    /* Terminal Intel Box */
    .intel-box {
        background: linear-gradient(180deg, #090D16 0%, #0F172A 100%);
        color: #E2E8F0;
        font-family: 'JetBrains Mono', 'Courier New', monospace;
        font-size: 0.86rem;
        line-height: 1.65;
        padding: 24px;
        border-radius: 14px;
        border: 1px solid rgba(56, 189, 248, 0.3);
        border-left: 5px solid #38BDF8;
        white-space: pre-wrap;
        box-shadow: inset 0 2px 12px rgba(0, 0, 0, 0.6);
    }

    /* Buzzword Tag Card */
    .buzz-grid {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin-top: 10px;
    }
    .buzz-chip {
        background: linear-gradient(135deg, rgba(30, 58, 138, 0.45), rgba(15, 23, 42, 0.85));
        border: 1px solid rgba(56, 189, 248, 0.35);
        border-radius: 10px;
        padding: 8px 14px;
        display: inline-flex;
        align-items: center;
        gap: 8px;
    }
    .buzz-term {
        font-weight: 700;
        color: #F8FAFC;
        font-size: 0.9rem;
    }
    .buzz-score {
        background: rgba(56, 189, 248, 0.2);
        color: #38BDF8;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        padding: 2px 7px;
        border-radius: 6px;
        font-weight: 600;
    }

    /* Sidebar Polish */
    .sidebar-status-item {
        display: flex;
        align-items: center;
        gap: 8px;
        background: rgba(16, 185, 129, 0.1);
        border: 1px solid rgba(16, 185, 129, 0.28);
        color: #6EE7B7;
        padding: 7px 12px;
        border-radius: 8px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-bottom: 6px;
    }

    /* Custom Styling Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background: rgba(15, 23, 42, 0.5);
        padding: 6px;
        border-radius: 12px;
        border: 1px solid rgba(148, 163, 184, 0.15);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background: rgba(56, 189, 248, 0.18) !important;
        color: #38BDF8 !important;
    }
</style>
""", unsafe_allow_html=True)


# ==============================================================================
# HELPER FUNCTIONS UNTUK VISUALISASI UI/UX
# ==============================================================================
def get_dimension_style(dim_name: str) -> dict:
    """Mengembalikan konfigurasi ikon, kelas CSS, dan warna berdasarkan nama dimensi."""
    dim_lower = dim_name.lower()
    if "sensasional" in dim_lower or "urgensi" in dim_lower:
        return {
            "chip_class": "chip-sensational",
            "hl_class": "hl-sensational",
            "icon": "⚡",
            "short": "Sensasionalitas",
            "color": "#F59E0B"
        }
    elif "provokasi" in dim_lower or "polarisasi" in dim_lower:
        return {
            "chip_class": "chip-provocation",
            "hl_class": "hl-provocation",
            "icon": "🔥",
            "short": "Provokasi",
            "color": "#EF4444"
        }
    elif "manipulasi" in dim_lower or "konspirasi" in dim_lower:
        return {
            "chip_class": "chip-conspiracy",
            "hl_class": "hl-conspiracy",
            "icon": "🕵️",
            "short": "Konspirasi",
            "color": "#A855F7"
        }
    else:
        return {
            "chip_class": "chip-toxicity",
            "hl_class": "hl-toxicity",
            "icon": "☣️",
            "short": "Toksisitas",
            "color": "#F43F5E"
        }


def highlight_text_with_flags(raw_text: str, detected_flags: list) -> str:
    """Mewarnai kata kunci berbahaya langsung di dalam teks asli secara aman."""
    if not raw_text:
        return ""
    import html
    escaped_text = html.escape(raw_text)
    if not detected_flags:
        return escaped_text

    # Urutkan berdasarkan panjang keyword (terpanjang dulu agar frase multi-kata ter-highlight utuh)
    sorted_flags = sorted(detected_flags, key=lambda x: len(x["keyword"]), reverse=True)
    seen_keywords = set()

    for item in sorted_flags:
        kw = item["keyword"]
        if kw.lower() in seen_keywords:
            continue
        seen_keywords.add(kw.lower())
        style = get_dimension_style(item["dimensi"])
        pattern = re.compile(rf"({re.escape(kw)})", re.IGNORECASE)
        escaped_text = pattern.sub(
            rf"<span class='hl-mark {style['hl_class']}' title='{item['dimensi']}'>{style['icon']} \1</span>",
            escaped_text
        )
    return escaped_text


# ==============================================================================
# INISIALISASI STATE SESSION STREAMLIT
# ==============================================================================
if "risk_scorer" not in st.session_state:
    st.session_state.risk_scorer = CognitiveRiskScorer()
if "astroturfing_detector" not in st.session_state:
    st.session_state.astroturfing_detector = AstroturfingDetector()
if "last_single_result" not in st.session_state:
    st.session_state.last_single_result = None
if "last_batch_result" not in st.session_state:
    st.session_state.last_batch_result = None


# ==============================================================================
# SIDEBAR NAVIGATION & TELEMETRY
# ==============================================================================
with st.sidebar:
    st.markdown("""
    <div style='display:flex; align-items:center; gap:12px; margin-bottom:8px;'>
        <div style='font-size:2.2rem; background:rgba(56,189,248,0.15); border:1px solid rgba(56,189,248,0.4); width:52px; height:52px; display:flex; align-items:center; justify-content:center; border-radius:12px;'>🛡️</div>
        <div>
            <div style='font-weight:800; font-size:1.15rem; color:#F8FAFC; line-height:1.2;'>CogniShield</div>
            <div style='font-size:0.75rem; color:#38BDF8; font-weight:600;'>TNI-AD • CYBER DEFENSE</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.caption("Sistem Pertahanan Siber Sosial & Deteksi Astroturfing Terkoordinasi\nPUSSIBERAD × CODEPOLITAN 2026")
    st.markdown("---")

    st.markdown("#### ⚙️ Parameter Deteksi")
    sim_threshold = st.slider(
        "Ambang Batas Kemiripan Buzzer (Similarity Threshold):",
        min_value=0.40,
        max_value=0.95,
        value=0.65,
        step=0.05,
        help="Pasangan unggahan dengan skor Cosine Similarity di atas nilai ini diklasifikasikan sebagai terkoordinasi / astroturfing."
    )

    st.markdown("---")
    st.markdown("#### 📡 Status Pipeline NLP")
    st.markdown("""
    <div class='sidebar-status-item'>🟢 Case Folding & Slang Normalizer</div>
    <div class='sidebar-status-item'>🟢 TF-IDF N-Gram (1,2) Engine</div>
    <div class='sidebar-status-item'>🟢 4D Cognitive Risk Scorer</div>
    <div class='sidebar-status-item'>🟢 Auto Threat Briefing Ready</div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### 🎨 Legenda Vektor Risiko")
    st.markdown("""
    <div style='font-size:0.8rem; line-height:1.8; color:#CBD5E1;'>
        <div>⚡ <b style='color:#FBBF24;'>Sensasionalitas</b>: Clickbait & urgensi semu</div>
        <div>🔥 <b style='color:#F87171;'>Provokasi</b>: Polarisasi & ujaran pemecah</div>
        <div>🕵️ <b style='color:#C084FC;'>Konspirasi</b>: Framing manipulatif</div>
        <div>☣️ <b style='color:#FB7185;'>Toksisitas</b>: Agresi & makian emosional</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.caption("Kartika Cyber Hackathon 2026 • Siber Sosial")


# ==============================================================================
# HERO BANNER UTAMA
# ==============================================================================
st.markdown("""
<div class='hero-banner'>
    <div class='hero-tag'>🛡️ COGNITIVE WARFARE & ASTROTURFING DEFENSE SYSTEM</div>
    <h1 class='hero-title'>CogniShield TNI-AD: <span>Deteksi Dini Disinformasi & Buzzer</span></h1>
    <p class='hero-subtitle'>
        Platform intelijen siber sosial berbasis NLP untuk mengukur indeks risiko manipulasi kognitif 4-dimensi,
        menyorot pola bahasa provokatif, serta memetakan jaringan amplifikasi narasi terkoordinasi secara <i>real-time</i>.
    </p>
</div>
""", unsafe_allow_html=True)


# ==============================================================================
# TAB MENU HORIZONTAL (3 FITUR UTAMA MVP)
# ==============================================================================
tab1, tab2, tab3 = st.tabs([
    "🔍 Tab 1: Single-Input Cognitive Analyzer",
    "🤖 Tab 2: Deteksi Jaringan Astroturfing",
    "📋 Tab 3: Lembar Ringkasan Intelijen"
])


# ==============================================================================
# TAB 1: SINGLE-INPUT ANALYZER
# ==============================================================================
with tab1:
    st.markdown("<div class='section-header'>🎯 Evaluasi Risiko Kognitif Narasi Tunggal</div>", unsafe_allow_html=True)
    st.caption("Uji teks unggahan media sosial atau berita untuk mendeteksi pemicu emosional, provokasi polarisasi, pembingkaian konspirasi, dan urgensi semu.")

    # Preset contoh teks untuk demo cepat
    st.markdown("**⚡ Uji Cepat dengan Skenario Narasi:**")
    col_preset1, col_preset2, col_preset3 = st.columns(3)
    if col_preset1.button("🚨 Skenario Bahaya (Provokasi & Konspirasi)", use_container_width=True):
        st.session_state.sample_input = (
            "VIRALKAN SEKARANG JUGA!! Rezim antek asing ini sudah keterlaluan membodohi rakyat, "
            "semua bukti konspirasi akan kita bongkar habis!! Jangan mau dicuci otak oleh media bayaran laknat!!"
        )
        st.session_state.auto_run_single = True
    if col_preset2.button("⚠️ Skenario Waspada (Sensasional & Clickbait)", use_container_width=True):
        st.session_state.sample_input = (
            "Waspada kawan-kawan!! Katanya ada isu rahasia yang sengaja ditutup-tutupi para elit politik. "
            "Jangan diam saja, tolong sebarkan sebelum dihapus!"
        )
        st.session_state.auto_run_single = True
    if col_preset3.button("✅ Skenario Aman (Informasi Publik Netral)", use_container_width=True):
        st.session_state.sample_input = (
            "Badan Meteorologi mengimbau masyarakat pesisir untuk memperhatikan prakiraan pasang air laut "
            "serta menjaga kebersihan saluran drainase selama tiga hari ke depan."
        )
        st.session_state.auto_run_single = True

    user_text = st.text_area(
        "Masukkan teks unggahan / narasi media sosial yang ingin diinspeksi:",
        value=st.session_state.get("sample_input", ""),
        height=125,
        placeholder="Ketik atau tempel teks narasi di sini (mendukung bahasa gaul/slang Indonesia)..."
    )

    col_btn, col_clear, _ = st.columns([1.4, 1, 3.6])
    analyze_btn = col_btn.button("🚀 Analisis Risiko Kognitif", type="primary", use_container_width=True)
    if col_clear.button("🧹 Bersihkan", use_container_width=True):
        st.session_state.sample_input = ""
        st.session_state.last_single_result = None
        st.rerun()

    should_run = analyze_btn or st.session_state.pop("auto_run_single", False) or (
        user_text and st.session_state.last_single_result is None
    )

    if should_run:
        if not user_text.strip():
            st.warning("Silakan masukkan teks terlebih dahulu untuk dianalisis.")
        else:
            with st.spinner("Menganalisis struktur leksikal & menghitung Multi-Dimensional Cognitive Risk Index..."):
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
        dims = analysis["dimensions"]
        flags = analysis["detected_flags"]

        # Hitung jumlah kata & huruf kapital untuk telemetri
        word_count = len(res["raw"].split())
        alpha_chars = [c for c in res["raw"] if c.isalpha()]
        caps_pct = round((sum(1 for c in alpha_chars if c.isupper()) / len(alpha_chars)) * 100, 1) if alpha_chars else 0.0

        # KPI Summary Strip
        st.markdown(f"""
        <div class='kpi-grid'>
            <div class='kpi-card' style='border-left: 4px solid {color};'>
                <div class='kpi-label'>Indeks Risiko Kognitif</div>
                <div class='kpi-value' style='color:{color};'>{score}%</div>
                <div class='kpi-sub'>Kategori: <b>{category.upper()}</b></div>
            </div>
            <div class='kpi-card'>
                <div class='kpi-label'>Pemicu Terdeteksi</div>
                <div class='kpi-value'>{len(flags)} <span style='font-size:0.95rem; font-weight:500; color:#94A3B8;'>Frase/Kata</span></div>
                <div class='kpi-sub'>Indikator leksikon manipulatif</div>
            </div>
            <div class='kpi-card'>
                <div class='kpi-label'>Dimensi Paling Dominan</div>
                <div class='kpi-value' style='font-size:1.15rem;'>{max(dims, key=dims.get) if max(dims.values()) > 0 else "Tidak Ada"}</div>
                <div class='kpi-sub'>Skor puncak: <b>{max(dims.values())}%</b></div>
            </div>
            <div class='kpi-card'>
                <div class='kpi-label'>Intensitas Tipografi</div>
                <div class='kpi-value'>{caps_pct}% <span style='font-size:0.95rem; font-weight:500; color:#94A3B8;'>Huruf Kapital</span></div>
                <div class='kpi-sub'>{word_count} kata ({len(res['raw'])} karakter)</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Baris Utama: Gauge Indicator + Evaluasi & Chip Kata Kunci
        col_gauge, col_info = st.columns([1.15, 1.85], gap="large")

        with col_gauge:
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=score,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={
                    'text': f"<b>COGNITIVE RISK INDEX</b><br><span style='font-size:0.82em;color:{color}'>Status: {category.upper()}</span>",
                    'font': {'size': 16, 'color': "#E2E8F0"}
                },
                number={'suffix': "%", 'font': {'size': 42, 'color': color}},
                gauge={
                    'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#64748B", 'tickfont': {'color': '#94A3B8'}},
                    'bar': {'color': color, 'thickness': 0.32},
                    'bgcolor': "rgba(15, 23, 42, 0.6)",
                    'borderwidth': 1,
                    'bordercolor': "rgba(148, 163, 184, 0.25)",
                    'steps': [
                        {'range': [0, 30], 'color': "rgba(16, 185, 129, 0.18)"},
                        {'range': [30, 65], 'color': "rgba(245, 158, 11, 0.18)"},
                        {'range': [65, 100], 'color': "rgba(239, 68, 68, 0.22)"}
                    ],
                    'threshold': {
                        'line': {'color': "#F8FAFC", 'width': 3},
                        'thickness': 0.82,
                        'value': score
                    }
                }
            ))
            fig_gauge.update_layout(
                height=295,
                margin=dict(l=24, r=24, t=55, b=18),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font={'family': "Plus Jakarta Sans, sans-serif"}
            )
            st.plotly_chart(fig_gauge, use_container_width=True)

        with col_info:
            if category == "Aman":
                status_cls, status_icon = "status-safe", "🟢 STATUS: AMAN — Risiko Kognitif Rendah"
            elif category == "Waspada":
                status_cls, status_icon = "status-warn", "🟡 STATUS: WASPADA — Indikasi Pembingkaian / Sensasional"
            else:
                status_cls, status_icon = "status-danger", "🔴 STATUS: BAHAYA — Risiko Manipulasi Kognitif Tinggi!"

            st.markdown(f"""
            <div class='status-banner {status_cls}'>
                <span>{status_icon}</span>
                <span style='font-size:0.85rem; opacity:0.9;'>Skor: {score}/100</span>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"**📋 Ringkasan Diagnostik:**\n\n{analysis['summary']}")

            # BAGIAN YANG DIPERBAIKI: Kata Kunci & Pola Berbahaya Terdeteksi (Flexbox Pill Anti-Potong)
            st.markdown("<div style='margin-top:14px; font-weight:700; font-size:0.95rem; color:#F8FAFC;'>🚩 Kata Kunci & Pola Berbahaya Terdeteksi:</div>", unsafe_allow_html=True)
            if flags:
                chips_list = []
                for item in flags:
                    style = get_dimension_style(item["dimensi"])
                    chips_list.append(
                        f"<div class='flag-chip {style['chip_class']}'>"
                        f"<span>{style['icon']} {item['keyword']}</span>"
                        f"<span class='dim-tag'>{style['short']}</span>"
                        f"</div>"
                    )
                st.markdown(f"<div class='flags-wrapper'>{''.join(chips_list)}</div>", unsafe_allow_html=True)
            else:
                st.markdown(
                    "<div style='padding:10px 14px; border-radius:10px; background:rgba(16,185,129,0.1); border:1px solid rgba(16,185,129,0.3); color:#6EE7B7; font-size:0.88rem; margin-top:6px;'>"
                    "✔ Tidak ditemukan kata kunci provokatif, konspirasi, atau sensasionalitas berlebih."
                    "</div>",
                    unsafe_allow_html=True
                )

        # Sorotan Teks Interaktif (Annotated Narrative Highlight)
        st.markdown("<div class='section-header'>🖍️ Sorotan Pemicu Kognitif pada Teks (Annotated Narrative)</div>", unsafe_allow_html=True)
        annotated_html = highlight_text_with_flags(res["raw"], flags)
        st.markdown(f"<div class='annotated-box'>{annotated_html}</div>", unsafe_allow_html=True)

        # Breakdown 4 Dimensi Kognitif: Radar Chart + Custom Progress Cards
        st.markdown("<div class='section-header'>📊 Profil Multi-Dimensional Cognitive Risk Index</div>", unsafe_allow_html=True)
        col_radar, col_bars = st.columns([1.15, 1.85], gap="large")

        with col_radar:
            categories_radar = list(dims.keys())
            values_radar = list(dims.values())
            # Tutup poligon radar
            categories_closed = categories_radar + [categories_radar[0]]
            values_closed = values_radar + [values_radar[0]]

            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(
                r=values_closed,
                theta=categories_closed,
                fill='toself',
                fillcolor='rgba(56, 189, 248, 0.22)',
                line=dict(color='#38BDF8', width=2.5),
                marker=dict(size=7, color='#38BDF8'),
                name='Profil Risiko'
            ))
            fig_radar.update_layout(
                polar=dict(
                    bgcolor="rgba(15, 23, 42, 0.55)",
                    radialaxis=dict(visible=True, range=[0, 100], gridcolor="rgba(148, 163, 184, 0.2)", tickfont=dict(color="#94A3B8", size=10)),
                    angularaxis=dict(gridcolor="rgba(148, 163, 184, 0.2)", tickfont=dict(color="#E2E8F0", size=11))
                ),
                showlegend=False,
                height=290,
                margin=dict(l=45, r=45, t=25, b=25),
                paper_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig_radar, use_container_width=True)

        with col_bars:
            for d_name, d_val in dims.items():
                style = get_dimension_style(d_name)
                st.markdown(f"""
                <div class='dim-card'>
                    <div class='dim-header'>
                        <span>{style['icon']} {d_name}</span>
                        <span style='color:{style["color"]}; font-weight:800;'>{d_val}%</span>
                    </div>
                    <div class='dim-bar-bg'>
                        <div class='dim-bar-fill' style='width:{min(100, max(2, d_val))}%; background:{style["color"]};'></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        with st.expander("🔎 Inspeksi Detail Pra-Pemrosesan Teks (NLP Preprocessing Normalization)"):
            c_raw, c_clean = st.columns(2)
            c_raw.markdown("**📝 Teks Asli (Input Mentah):**")
            c_raw.code(res["raw"], language=None)
            c_clean.markdown("**✨ Teks Bersih (Normalized, Slang-Cleaned, Case-Folded):**")
            c_clean.code(res["cleaned"], language=None)


# ==============================================================================
# TAB 2: DETEKSI ASTROTURFING & KEMIRIPAN TEKS
# ==============================================================================
with tab2:
    st.markdown("<div class='section-header'>🤖 Deteksi Kampanye Astroturfing & Amplifikasi Buzzer</div>", unsafe_allow_html=True)
    st.caption("Unggah dataset CSV/JSON postingan media sosial untuk memetakan kesamaan naratif antar-akun secara instan menggunakan vektor TF-IDF dan Cosine Similarity.")

    col_upload, col_sample = st.columns([2, 1], gap="medium")

    with col_upload:
        uploaded_file = st.file_uploader(
            "Unggah Berkas CSV / JSON Narasi Medsos:",
            type=["csv", "json"],
            help="Berkas berisi kolom narasi/teks seperti 'text', 'content', 'komentar', atau 'tweet'."
        )

    with col_sample:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        use_sample = st.button("📁 Gunakan Dataset Sampel (12 Postingan Buzzer)", type="primary", use_container_width=True)

    df_posts = None
    if uploaded_file is not None:
        try:
            df_posts = load_dataframe_from_file(uploaded_file)
            st.success(f"✔ Berkas berhasil dimuat: {len(df_posts)} baris data.")
        except Exception as e:
            st.error(f"Gagal membaca file: {e}")
    elif use_sample or ("use_sample_active" in st.session_state and st.session_state.use_sample_active):
        st.session_state.use_sample_active = True
        sample_path = os.path.join(os.path.dirname(__file__), "data", "sample_posts.csv")
        if os.path.exists(sample_path):
            df_posts = pd.read_csv(sample_path)
            st.info("📌 Menggunakan dataset sampel bawaan CogniShield (`data/sample_posts.csv`).")

    if df_posts is not None and not df_posts.empty:
        detected_col = detect_text_column(df_posts)
        col_sel, col_preview = st.columns([1.5, 2.5])
        with col_sel:
            text_column = st.selectbox(
                "Pilih kolom teks yang dianalisis:",
                options=df_posts.columns.tolist(),
                index=df_posts.columns.tolist().index(detected_col) if detected_col in df_posts.columns else 0
            )
        with col_preview:
            with st.expander("👁️ Pratinjau Tabel Dataset Mentah"):
                st.dataframe(df_posts.head(10), use_container_width=True, height=180)

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

                st.session_state.last_batch_result = {
                    "df": df_posts,
                    "raw_posts": raw_posts,
                    "sim_matrix": sim_matrix,
                    "metrics": metrics,
                    "suspicious_pairs": suspicious_pairs,
                    "top_terms": top_terms,
                    "threshold": sim_threshold
                }

            is_astro = metrics["astroturfing_detected"]
            astro_color = "#EF4444" if is_astro else "#10B981"
            astro_text = "TERDETEKSI" if is_astro else "ORGANIK"

            # KPI Cards Modern
            st.markdown(f"""
            <div class='kpi-grid'>
                <div class='kpi-card'>
                    <div class='kpi-label'>Total Unggahan Dianalisis</div>
                    <div class='kpi-value'>{metrics['total_posts']} <span style='font-size:0.95rem; color:#94A3B8;'>Post</span></div>
                    <div class='kpi-sub'>{metrics['involved_posts_count']} post terindikasi terkoordinasi</div>
                </div>
                <div class='kpi-card'>
                    <div class='kpi-label'>Pasangan Duplikasi (≥{int(sim_threshold*100)}%)</div>
                    <div class='kpi-value' style='color:#FBBF24;'>{metrics['high_similarity_pairs_count']} <span style='font-size:0.95rem; color:#94A3B8;'>Pasang</span></div>
                    <div class='kpi-sub'>Kemiripan maks: <b>{round(metrics['max_pairwise_similarity']*100, 1)}%</b></div>
                </div>
                <div class='kpi-card'>
                    <div class='kpi-label'>Rasio Amplifikasi Buzzer</div>
                    <div class='kpi-value' style='color:#38BDF8;'>{metrics['amplification_ratio']}%</div>
                    <div class='kpi-sub'>Proporsi narasi non-organik</div>
                </div>
                <div class='kpi-card' style='border-left: 4px solid {astro_color};'>
                    <div class='kpi-label'>Status Jaringan</div>
                    <div class='kpi-value' style='color:{astro_color}; font-size:1.45rem;'>{astro_text}</div>
                    <div class='kpi-sub'>Skor Risiko Kampanye: <b>{metrics['campaign_risk_score']}%</b></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Heatmap Matriks Kemiripan Teks
            st.markdown("<div class='section-header'>🗺️ Peta Kalor Kemiripan Antar-Unggahan (Cosine Similarity Matrix)</div>", unsafe_allow_html=True)
            st.caption("Skor 1.0 mengindikasikan duplikasi identik (copy-paste bot); skor mendekati 0.0 menunjukkan narasi organik yang berbeda.")

            labels = [f"P#{i+1}: {t[:24]}..." for i, t in enumerate(raw_posts)]
            fig_heatmap = px.imshow(
                np.round(sim_matrix, 2),
                labels=dict(x="Unggahan Target", y="Unggahan Asal", color="Similarity"),
                x=labels,
                y=labels,
                color_continuous_scale=["#0F172A", "#1E3A8A", "#D97706", "#DC2626"],
                zmin=0.0,
                zmax=1.0,
                aspect="auto",
                text_auto=True if len(raw_posts) <= 15 else False
            )
            fig_heatmap.update_layout(
                height=460,
                margin=dict(l=20, r=20, t=25, b=20),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#E2E8F0")
            )
            st.plotly_chart(fig_heatmap, use_container_width=True)

            # Tabel Pasangan Kemiripan Mencurigakan
            st.markdown(f"<div class='section-header'>🚨 Pasangan Unggahan Terkoordinasi (Similarity ≥ {int(sim_threshold*100)}%)</div>", unsafe_allow_html=True)
            if suspicious_pairs:
                pairs_display = []
                for p in suspicious_pairs:
                    pairs_display.append({
                        "Post A": f"#{p['post_a_id']}",
                        "Post B": f"#{p['post_b_id']}",
                        "Kemiripan (%)": p["similarity_percentage"],
                        "Klasifikasi Koordinasi": p["coordination_level"],
                        "Cuplikan Narasi A": p["text_a"],
                        "Cuplikan Narasi B": p["text_b"]
                    })
                st.dataframe(
                    pd.DataFrame(pairs_display),
                    column_config={
                        "Kemiripan (%)": st.column_config.ProgressColumn(
                            "Tingkat Kemiripan",
                            help="Persentase kemiripan Cosine Similarity",
                            format="%.1f%%",
                            min_value=0,
                            max_value=100,
                        )
                    },
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.success(f"✔ Tidak ada pasangan postingan yang melampaui ambang batas kemiripan ({int(sim_threshold*100)}%). Pola unggahan tampak organik.")

            # Top Replicated Buzzwords
            if top_terms:
                st.markdown("<div class='section-header'>📢 Kata Kunci & Slogan Paling Banyak Direplikasi (Top Buzzwords)</div>", unsafe_allow_html=True)
                buzz_html = "".join([
                    f"<div class='buzz-chip'><span class='buzz-term'>#{term}</span><span class='buzz-score'>TF-IDF {score}</span></div>"
                    for term, score in top_terms
                ])
                st.markdown(f"<div class='buzz-grid'>{buzz_html}</div>", unsafe_allow_html=True)


# ==============================================================================
# TAB 3: LEMBAR RINGKASAN INTELIJEN & REKOMENDASI TAKTIS
# ==============================================================================
with tab3:
    st.markdown("<div class='section-header'>📋 Lembar Ringkasan Intelijen (Automated Threat Briefing)</div>", unsafe_allow_html=True)
    st.caption("Laporan taktis terotomatisasi berbasis aturan yang menyintesis temuan risiko kognitif dan operasi astroturfing beserta rekomendasi mitigasi.")

    batch = st.session_state.get("last_batch_result")
    single = st.session_state.get("last_single_result")

    if not batch and not single:
        st.markdown("""
        <div class='glass-card' style='text-align:center; padding:40px 24px;'>
            <div style='font-size:2.6rem; margin-bottom:10px;'>📡</div>
            <div style='font-size:1.15rem; font-weight:700; color:#F8FAFC; margin-bottom:6px;'>Belum Ada Telemetri Analisis Aktif</div>
            <div style='color:#94A3B8; font-size:0.92rem; max-width:540px; margin:0 auto;'>
                Silakan jalankan inspeksi teks pada <b>Tab 1 (Single-Input Analyzer)</b> atau muat dataset kampanye pada
                <b>Tab 2 (Deteksi Astroturfing)</b> untuk menghasilkan lembar ringkasan intelijen secara otomatis.
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        intel_report = []
        intel_report.append("=" * 72)
        intel_report.append("  COGNISHIELD THREAT INTELLIGENCE SUMMARY REPORT")
        intel_report.append("  Klasifikasi: SENSITIF - INTERNAL CYBER RESPONSE UNIT")
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

        # 3. Rekomendasi Tindakan Taktis
        intel_report.append("[3] REKOMENDASI TINDAKAN TAKTIS (COUNTERMEASURE PROTOCOLS)")
        is_high_risk = False
        if batch and batch["metrics"]["astroturfing_detected"]:
            is_high_risk = True
        elif single and single["analysis"]["overall_risk_score"] >= 65:
            is_high_risk = True

        if is_high_risk:
            intel_report.append("  [PROTOKOL MERAH - ESKALASI & INTERVENSI CEPAT]")
            intel_report.append("  1. Platform Moderation: Tandai (flagging) akun sumber narasi kemiripan ≥85% untuk audit bot.")
            intel_report.append("  2. Rate-Limiting Narasi: Batasi laju distribusi tagar/slogan yang direplikasi secara mekanik.")
            intel_report.append("  3. Counter-Messaging (Prebunking): Rilis klarifikasi fakta resmi sebelum narasi manipulatif mendominasi.")
            intel_report.append("  4. Cyber Threat Intel Escalation: Amankan artefak digital & petakan klaster jaringan buzzer.")
        else:
            intel_report.append("  [PROTOKOL HIJAU/KUNING - MONITORING & MITIGASI PASIF]")
            intel_report.append("  1. Continuous Telemetry: Lanjutkan pemantauan dinamika sentimen 6-12 jam ke depan.")
            intel_report.append("  2. Algorithmic Watchlist: Daftarkan kata kunci terkait dalam radar deteksi dini.")
            intel_report.append("  3. Edukasi Literasi Kognitif: Dorong saluran informasi resmi untuk menjaga transparansi publik.")

        intel_report.append("")
        intel_report.append("=" * 72)
        intel_report.append("  Dihasilkan secara otomatis oleh CogniShield Security Engine")
        intel_report.append("=" * 72)

        report_text = "\n".join(intel_report)

        # Visual Tactical Cards + Terminal Output
        col_proto, col_term = st.columns([1.05, 1.95], gap="large")
        with col_proto:
            proto_color = "#EF4444" if is_high_risk else "#10B981"
            proto_badge = "🔴 PROTOKOL MERAH (INTERVENSI AKTIF)" if is_high_risk else "🟢 PROTOKOL HIJAU/KUNING (MONITORING)"
            st.markdown(f"""
            <div class='glass-card' style='border-top: 4px solid {proto_color};'>
                <div style='font-size:0.78rem; font-weight:700; color:{proto_color}; letter-spacing:0.06em; margin-bottom:6px;'>STATUS RESPON TAKTIS</div>
                <div style='font-size:1.15rem; font-weight:800; color:#F8FAFC; margin-bottom:12px;'>{proto_badge}</div>
                <div style='font-size:0.88rem; color:#CBD5E1; line-height:1.6;'>
                    {summary_narrative}
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.download_button(
                label="📥 Unduh Dokumen Intelijen (.TXT)",
                data=report_text,
                file_name="CogniShield_Intelligence_Summary.txt",
                mime="text/plain",
                type="primary",
                use_container_width=True
            )

        with col_term:
            st.markdown(f"<div class='intel-box'>{report_text}</div>", unsafe_allow_html=True)
