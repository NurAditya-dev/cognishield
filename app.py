"""
CogniShield: Platform Analisis Risiko Kognitif Multi-Dimensi & Deteksi Astroturfing
Entry Point Streamlit (app.py) — Anti-Slop Industrial & Editorial Interface
"""

import os
import sys
import re
import html
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
# KONFIGURASI HALAMAN STREAMLIT (SESUAI SKILL.MD)
# ==============================================================================
st.set_page_config(
    page_title="CogniShield — Cognitive Risk & Astroturfing Defense",
    page_icon=":material/shield:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# ANTI-SLOP INDUSTRIAL & EDITORIAL CSS + MOTION SYSTEM
# - Monochromatic neutral palette (#0A0A0B, #121214, #EDEDEF, #A1A1AA, #71717A)
# - Hairline 1px borders at 8% opacity: rgba(255, 255, 255, 0.08)
# - Single high-weight accent color: International Signal Orange (#FF3E00)
# - Zero purple gradients, zero glassmorphism/backdrop-filter
# - Motion: cubic-bezier(0.16, 1, 0.3, 1), micro-displacement 10px, blur 4px->0px, 30ms stagger
# ==============================================================================
st.html("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

    :root {
        --bg-primary: #0A0A0B;
        --bg-panel: #121214;
        --bg-elevated: #18181B;
        --text-primary: #EDEDEF;
        --text-secondary: #A1A1AA;
        --text-muted: #71717A;
        --hairline: rgba(255, 255, 255, 0.08);
        --hairline-hover: rgba(255, 255, 255, 0.18);
        --accent: #FF3E00;
        --ease-editorial: cubic-bezier(0.16, 1, 0.3, 1);
    }

    /* Keyframes: Micro-displacement 10px + Blur entry 4px -> 0px */
    @keyframes industrialReveal {
        0% {
            opacity: 0;
            transform: translateY(10px);
            filter: blur(4px);
        }
        100% {
            opacity: 1;
            transform: translateY(0);
            filter: blur(0px);
        }
    }

    .anim-item {
        opacity: 0;
        animation: industrialReveal 520ms var(--ease-editorial) forwards;
        will-change: transform, opacity, filter;
    }

    /* Staggered delay 30ms antar item */
    .stagger-1  { animation-delay: 30ms; }
    .stagger-2  { animation-delay: 60ms; }
    .stagger-3  { animation-delay: 90ms; }
    .stagger-4  { animation-delay: 120ms; }
    .stagger-5  { animation-delay: 150ms; }
    .stagger-6  { animation-delay: 180ms; }
    .stagger-7  { animation-delay: 210ms; }
    .stagger-8  { animation-delay: 240ms; }
    .stagger-9  { animation-delay: 270ms; }
    .stagger-10 { animation-delay: 300ms; }
    .stagger-11 { animation-delay: 330ms; }
    .stagger-12 { animation-delay: 360ms; }

    /* Editorial Masthead */
    .editorial-masthead {
        background: var(--bg-panel);
        border: 1px solid var(--hairline);
        border-left: 3px solid var(--accent);
        padding: 22px 26px;
        margin-bottom: 24px;
        display: flex;
        justify-content: space-between;
        align-items: flex-end;
        flex-wrap: wrap;
        gap: 16px;
    }
    .masthead-kicker {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: var(--accent);
        margin-bottom: 8px;
    }
    .masthead-title {
        font-family: 'Inter', sans-serif;
        font-size: 1.75rem;
        font-weight: 700;
        letter-spacing: -0.03em;
        color: var(--text-primary);
        margin: 0 0 6px 0;
        line-height: 1.15;
    }
    .masthead-sub {
        font-size: 0.88rem;
        color: var(--text-secondary);
        margin: 0;
        max-width: 720px;
        line-height: 1.5;
    }
    .masthead-meta {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        color: var(--text-muted);
        text-align: right;
        line-height: 1.6;
        border-left: 1px solid var(--hairline);
        padding-left: 16px;
    }

    /* Section Index Bar */
    .index-bar {
        display: flex;
        justify-content: space-between;
        align-items: baseline;
        border-bottom: 1px solid var(--hairline);
        padding-bottom: 8px;
        margin: 24px 0 14px 0;
    }
    .index-title {
        font-family: 'Inter', sans-serif;
        font-size: 0.92rem;
        font-weight: 600;
        color: var(--text-primary);
        letter-spacing: -0.01em;
    }
    .index-code {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        color: var(--text-muted);
        letter-spacing: 0.06em;
    }

    /* Industrial Hairline Grid (KPI Strip) */
    .industrial-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        border-top: 1px solid var(--hairline);
        border-left: 1px solid var(--hairline);
        margin: 16px 0 22px 0;
        background: var(--bg-panel);
    }
    @media (max-width: 900px) {
        .industrial-grid { grid-template-columns: repeat(2, 1fr); }
    }
    .grid-cell {
        border-right: 1px solid var(--hairline);
        border-bottom: 1px solid var(--hairline);
        padding: 16px 18px;
        transition: background-color 260ms var(--ease-editorial), transform 260ms var(--ease-editorial);
    }
    .grid-cell:hover {
        background-color: var(--bg-elevated);
    }
    .cell-label {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 8px;
    }
    .cell-value {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.6rem;
        font-weight: 600;
        color: var(--text-primary);
        letter-spacing: -0.02em;
        line-height: 1.15;
    }
    .cell-value.accent {
        color: var(--accent);
    }
    .cell-foot {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        color: var(--text-secondary);
        margin-top: 6px;
    }

    /* Editorial Panel */
    .ed-panel {
        background: var(--bg-panel);
        border: 1px solid var(--hairline);
        padding: 18px 20px;
        margin-bottom: 14px;
        transition: border-color 260ms var(--ease-editorial);
    }
    .ed-panel:hover {
        border-color: var(--hairline-hover);
    }
    .ed-panel-accent {
        border-left: 3px solid var(--accent);
    }

    /* Status Readout Bar */
    .readout-bar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: var(--bg-panel);
        border: 1px solid var(--hairline);
        padding: 11px 16px;
        margin-bottom: 12px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.78rem;
    }
    .readout-bar.high-alert {
        border-left: 3px solid var(--accent);
    }
    .readout-bar.normal-alert {
        border-left: 3px solid var(--text-primary);
    }

    /* FIXED: Anti-Slop Monochromatic IOC Chips (Zero Line-Clip, Hairline 1px, Staggered Entry) */
    .ioc-rack {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        margin-top: 10px;
    }
    .ioc-pill {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: var(--bg-elevated);
        border: 1px solid var(--hairline);
        padding: 5px 10px;
        font-size: 0.8rem;
        line-height: 1.2;
        white-space: nowrap;
        transition: transform 240ms var(--ease-editorial), border-color 240ms var(--ease-editorial);
    }
    .ioc-pill:hover {
        transform: translateY(-2px);
        border-color: var(--accent);
    }
    .ioc-marker {
        width: 5px;
        height: 5px;
        background: var(--accent);
        display: inline-block;
        flex-shrink: 0;
    }
    .ioc-term {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        color: var(--text-primary);
    }
    .ioc-code {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.68rem;
        color: var(--text-muted);
        border-left: 1px solid var(--hairline);
        padding-left: 7px;
        text-transform: uppercase;
    }

    /* Annotated Text Specimen Box */
    .specimen-box {
        background: var(--bg-panel);
        border: 1px solid var(--hairline);
        padding: 18px 22px;
        font-family: 'Inter', sans-serif;
        font-size: 0.95rem;
        line-height: 1.8;
        color: var(--text-secondary);
    }
    .specimen-mark {
        background: rgba(255, 62, 0, 0.14);
        color: var(--text-primary);
        border-bottom: 1.5px solid var(--accent);
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.86rem;
        font-weight: 500;
        padding: 1px 5px;
    }

    /* Dimension Telemetry Rows */
    .dim-row {
        background: var(--bg-panel);
        border: 1px solid var(--hairline);
        padding: 12px 16px;
        margin-bottom: 8px;
        transition: border-color 240ms var(--ease-editorial);
    }
    .dim-row:hover {
        border-color: var(--hairline-hover);
    }
    .dim-top {
        display: flex;
        justify-content: space-between;
        align-items: baseline;
        margin-bottom: 8px;
    }
    .dim-label {
        font-size: 0.84rem;
        font-weight: 500;
        color: var(--text-primary);
    }
    .dim-code {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
        color: var(--text-muted);
        margin-right: 8px;
    }
    .dim-val {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.82rem;
        font-weight: 600;
        color: var(--text-primary);
    }
    .dim-track {
        width: 100%;
        height: 4px;
        background: rgba(255, 255, 255, 0.06);
        overflow: hidden;
    }
    .dim-fill {
        height: 100%;
        transition: width 600ms var(--ease-editorial);
    }

    /* Editorial Dossier Sheet (Tab 3) */
    .dossier-frame {
        background: #0D0D0F;
        border: 1px solid var(--hairline);
    }
    .dossier-head {
        border-bottom: 1px solid var(--hairline);
        padding: 10px 18px;
        display: flex;
        justify-content: space-between;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
        color: var(--text-muted);
        background: var(--bg-panel);
    }
    .dossier-body {
        padding: 20px 22px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8rem;
        line-height: 1.7;
        color: var(--text-primary);
    }
    .dossier-banner {
        border-bottom: 1px solid var(--hairline);
        padding-bottom: 12px;
        margin-bottom: 18px;
    }
    .dossier-banner-title {
        font-weight: 700;
        color: var(--text-primary);
        letter-spacing: 0.04em;
    }
    .dossier-banner-sub {
        font-size: 0.72rem;
        color: var(--text-muted);
        margin-top: 2px;
    }
    .dossier-sec {
        margin-bottom: 18px;
        padding-bottom: 14px;
        border-bottom: 1px solid var(--hairline);
    }
    .dossier-sec:last-child {
        margin-bottom: 0;
        padding-bottom: 0;
        border-bottom: none;
    }
    .dossier-sec-title {
        font-size: 0.74rem;
        font-weight: 700;
        color: var(--accent);
        letter-spacing: 0.08em;
        margin-bottom: 10px;
        text-transform: uppercase;
    }
    .dossier-kv {
        display: grid;
        grid-template-columns: 150px 1fr;
        gap: 6px 14px;
        margin-bottom: 6px;
    }
    .dossier-k {
        color: var(--text-muted);
    }
    .dossier-v {
        color: var(--text-primary);
        font-family: 'Inter', sans-serif;
        font-size: 0.85rem;
    }
    .dossier-vec-row {
        display: grid;
        grid-template-columns: 210px 130px 60px;
        align-items: center;
        gap: 12px;
        padding: 4px 0;
    }
    .dossier-step {
        display: grid;
        grid-template-columns: 24px 165px 1fr;
        gap: 8px;
        padding: 5px 0;
        border-bottom: 1px dashed rgba(255, 255, 255, 0.05);
    }
    .dossier-step:last-child {
        border-bottom: none;
    }

    /* Sidebar Telemetry Table */
    .sb-table {
        border-top: 1px solid var(--hairline);
        margin-top: 8px;
        margin-bottom: 16px;
    }
    .sb-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 7px 0;
        border-bottom: 1px solid var(--hairline);
        font-size: 0.78rem;
    }
    .sb-key {
        color: var(--text-secondary);
    }
    .sb-val {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
        color: var(--text-primary);
    }
    .sb-val.accent {
        color: var(--accent);
    }
</style>
""")


# ==============================================================================
# HELPER FUNCTIONS (CACHED & MODULAR SESUAI SKILL.MD)
# ==============================================================================
@st.cache_resource
def get_engines():
    """Inisialisasi singleton mesin analisis kognitif dan astroturfing."""
    return CognitiveRiskScorer(), AstroturfingDetector()


risk_scorer, astroturfing_detector = get_engines()


def get_vector_code(dim_name: str) -> dict:
    """Mengembalikan kode monospasi industrial untuk tiap dimensi risiko."""
    d = dim_name.lower()
    if "sensasional" in d or "urgensi" in d:
        return {"code": "VEC-01", "short": "URGENSI"}
    elif "provokasi" in d or "polarisasi" in d:
        return {"code": "VEC-02", "short": "PROVOKASI"}
    elif "manipulasi" in d or "konspirasi" in d:
        return {"code": "VEC-03", "short": "KONSPIRASI"}
    return {"code": "VEC-04", "short": "TOKSISITAS"}


def annotate_specimen(raw_text: str, detected_flags: list) -> str:
    """Menandai kata kunci pemicu di dalam teks narasi dengan garis bawah aksen tunggal."""
    if not raw_text:
        return ""
    escaped = html.escape(raw_text)
    if not detected_flags:
        return escaped

    sorted_flags = sorted(detected_flags, key=lambda x: len(x["keyword"]), reverse=True)
    seen = set()
    for item in sorted_flags:
        kw = item["keyword"]
        if kw.lower() in seen:
            continue
        seen.add(kw.lower())
        meta = get_vector_code(item["dimensi"])
        pattern = re.compile(rf"({re.escape(kw)})", re.IGNORECASE)
        escaped = pattern.sub(
            rf"<span class='specimen-mark' title='{meta['code']} // {item['dimensi']}'>\1</span>",
            escaped
        )
    return escaped


# ==============================================================================
# INISIALISASI SESSION STATE
# ==============================================================================
if "last_single_result" not in st.session_state:
    st.session_state.last_single_result = None
if "last_batch_result" not in st.session_state:
    st.session_state.last_batch_result = None
if "sample_input" not in st.session_state:
    st.session_state.sample_input = ""


# ==============================================================================
# SIDEBAR — INDUSTRIAL SPECIFICATIONS & PARAMETERS
# ==============================================================================
with st.sidebar:
    st.markdown("""
    <div class='anim-item stagger-1' style='padding-bottom:12px; border-bottom:1px solid rgba(255,255,255,0.08); margin-bottom:14px;'>
        <div style='font-family:JetBrains Mono,monospace; font-size:0.68rem; color:#FF3E00; letter-spacing:0.1em;'>SYS // COGNISHIELD</div>
        <div style='font-size:1.05rem; font-weight:700; color:#EDEDEF; letter-spacing:-0.02em; margin-top:2px;'>Tactical Telemetry</div>
        <div style='font-family:JetBrains Mono,monospace; font-size:0.7rem; color:#71717A; margin-top:2px;'>PUSSIBERAD × CODEPOLITAN</div>
    </div>
    """, unsafe_allow_html=True)

    st.caption("Parameter ambang batas deteksi")
    sim_threshold = st.slider(
        "Cosine similarity threshold",
        min_value=0.40,
        max_value=0.95,
        value=0.65,
        step=0.05,
        help="Skor di atas ambang ini ditandai sebagai amplifikasi narasi terkoordinasi."
    )

    st.caption("Spesifikasi modul aktif")
    st.markdown("""
    <div class='sb-table anim-item stagger-2'>
        <div class='sb-row'><span class='sb-key'>Preprocessor</span><span class='sb-val'>SLANG + NFKD</span></div>
        <div class='sb-row'><span class='sb-key'>Vectorizer</span><span class='sb-val'>TF-IDF (1,2)</span></div>
        <div class='sb-row'><span class='sb-key'>Risk Matrix</span><span class='sb-val'>4-VECTOR</span></div>
        <div class='sb-row'><span class='sb-key'>Status</span><span class='sb-val accent'>OPERATIONAL</span></div>
    </div>
    """, unsafe_allow_html=True)

    st.caption("Indeks vektor kognitif")
    st.markdown("""
    <div class='sb-table anim-item stagger-3'>
        <div class='sb-row'><span class='sb-key'>Sensasionalitas</span><span class='sb-val'>VEC-01</span></div>
        <div class='sb-row'><span class='sb-key'>Provokasi Sosial</span><span class='sb-val'>VEC-02</span></div>
        <div class='sb-row'><span class='sb-key'>Framing Konspirasi</span><span class='sb-val'>VEC-03</span></div>
        <div class='sb-row'><span class='sb-key'>Toksisitas Emosi</span><span class='sb-val'>VEC-04</span></div>
    </div>
    """, unsafe_allow_html=True)


# ==============================================================================
# EDITORIAL MASTHEAD
# ==============================================================================
st.markdown("""
<div class='editorial-masthead anim-item stagger-1'>
    <div>
        <div class='masthead-kicker'>COGNITIVE WARFARE & ASTROTURFING DEFENSE</div>
        <h1 class='masthead-title'>CogniShield Analytical Dossier</h1>
        <p class='masthead-sub'>
            Instrumen evaluasi risiko kognitif multi-dimensi dan deteksi amplifikasi narasi terkoordinasi pada jaringan informasi publik.
        </p>
    </div>
    <div class='masthead-meta'>
        <div>BUILD // 2026.10.REV4</div>
        <div>SPEC  // INDUSTRIAL-MONO</div>
        <div>MODE  // ACTIVE INSPECTION</div>
    </div>
</div>
""", unsafe_allow_html=True)


# ==============================================================================
# NAVIGATION TABS (SENTENCE CASING + MATERIAL ICONS SESUAI SKILL.MD)
# ==============================================================================
tab1, tab2, tab3 = st.tabs([
    ":material/radar: Inspeksi risiko kognitif",
    ":material/hub: Deteksi jaringan astroturfing",
    ":material/description: Lembar ringkasan intelijen"
])


# ==============================================================================
# TAB 1: SINGLE-INPUT COGNITIVE ANALYZER
# ==============================================================================
with tab1:
    st.markdown("""
    <div class='index-bar anim-item stagger-1'>
        <span class='index-title'>Inspeksi spesimen narasi tunggal</span>
        <span class='index-code'>SEC // 01 — SINGLE PAYLOAD</span>
    </div>
    """, unsafe_allow_html=True)

    # Preset skenario menggunakan st.columns dan sentence casing + Material Icons
    c_p1, c_p2, c_p3 = st.columns(3)
    if c_p1.button("Skenario kritis: provokasi & konspirasi", icon=":material/warning:", width="stretch"):
        st.session_state.sample_input = (
            "VIRALKAN SEKARANG JUGA!! Rezim antek asing ini sudah keterlaluan membodohi rakyat, "
            "semua bukti konspirasi akan kita bongkar habis!! Jangan mau dicuci otak oleh media bayaran laknat!!"
        )
        st.session_state.auto_run_single = True
    if c_p2.button("Skenario waspada: urgensi semu", icon=":material/bolt:", width="stretch"):
        st.session_state.sample_input = (
            "Waspada kawan-kawan!! Katanya ada isu rahasia yang sengaja ditutup-tutupi para elit politik. "
            "Jangan diam saja, tolong sebarkan sebelum dihapus!"
        )
        st.session_state.auto_run_single = True
    if c_p3.button("Skenario nominal: informasi netral", icon=":material/check_circle:", width="stretch"):
        st.session_state.sample_input = (
            "Badan Meteorologi mengimbau masyarakat pesisir untuk memperhatikan prakiraan pasang air laut "
            "serta menjaga kebersihan saluran drainase selama tiga hari ke depan."
        )
        st.session_state.auto_run_single = True

    user_text = st.text_area(
        "Spesimen teks unggahan atau narasi",
        value=st.session_state.get("sample_input", ""),
        height=115,
        placeholder="Tempelkan teks narasi media sosial untuk diinspeksi..."
    )

    col_act1, col_act2, _ = st.columns([1.3, 0.9, 3.8])
    analyze_btn = col_act1.button("Jalankan analisis", type="primary", icon=":material/play_arrow:", width="stretch")
    if col_act2.button("Bersihkan", icon=":material/restart_alt:", width="stretch"):
        st.session_state.sample_input = ""
        st.session_state.last_single_result = None
        st.rerun()

    should_run = analyze_btn or st.session_state.pop("auto_run_single", False) or (
        user_text and st.session_state.last_single_result is None
    )

    if should_run:
        if not user_text.strip():
            st.warning("Masukkan teks terlebih dahulu sebelum memulai analisis.", icon=":material/warning:")
        else:
            cleaned_text = preprocess_text(user_text)
            analysis = risk_scorer.analyze_text(user_text)
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
        dims = analysis["dimensions"]
        flags = analysis["detected_flags"]

        word_count = len(res["raw"].split())
        alpha_chars = [c for c in res["raw"] if c.isalpha()]
        caps_pct = round((sum(1 for c in alpha_chars if c.isupper()) / len(alpha_chars)) * 100, 1) if alpha_chars else 0.0
        dominant_dim = max(dims, key=dims.get) if max(dims.values()) > 0 else "Tidak ada"
        is_elevated = score >= 30.0

        # Industrial Hairline KPI Strip with Staggered Reveal (30ms step)
        val_cls = "cell-value accent" if score >= 65.0 else "cell-value"
        st.markdown(f"""
        <div class='industrial-grid'>
            <div class='grid-cell anim-item stagger-1'>
                <div class='cell-label'>01 // COGNITIVE RISK INDEX</div>
                <div class='{val_cls}'>{score}%</div>
                <div class='cell-foot'>STATUS: {category.upper()}</div>
            </div>
            <div class='grid-cell anim-item stagger-2'>
                <div class='cell-label'>02 // TRIGGER INDICATORS</div>
                <div class='cell-value'>{len(flags):02d}</div>
                <div class='cell-foot'>POLA LEKSIKON TERDETEKSI</div>
            </div>
            <div class='grid-cell anim-item stagger-3'>
                <div class='cell-label'>03 // PRIMARY VECTOR</div>
                <div class='cell-value' style='font-size:1.05rem; font-family:Inter,sans-serif;'>{dominant_dim}</div>
                <div class='cell-foot'>PUNCAK: {max(dims.values())}%</div>
            </div>
            <div class='grid-cell anim-item stagger-4'>
                <div class='cell-label'>04 // TYPOGRAPHIC URGENCY</div>
                <div class='cell-value'>{caps_pct}%</div>
                <div class='cell-foot'>KAPITAL ({word_count} KATA)</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Baris Utama: Gauge Monokrom + Evaluasi & IOC Pills
        col_left, col_right = st.columns([1.05, 1.95], gap="large")

        with col_left:
            bar_color = "#FF3E00" if is_elevated else "#EDEDEF"
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=score,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={
                    'text': f"INDEX READOUT // {category.upper()}",
                    'font': {'size': 11, 'color': "#A1A1AA", 'family': "JetBrains Mono"}
                },
                number={'suffix': "%", 'font': {'size': 42, 'color': "#EDEDEF", 'family': "JetBrains Mono"}},
                gauge={
                    'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "rgba(255,255,255,0.18)", 'tickfont': {'color': '#71717A', 'family': 'JetBrains Mono', 'size': 10}},
                    'bar': {'color': bar_color, 'thickness': 0.25},
                    'bgcolor': "#121214",
                    'borderwidth': 1,
                    'bordercolor': "rgba(255,255,255,0.08)",
                    'steps': [
                        {'range': [0, 30], 'color': "rgba(255, 255, 255, 0.02)"},
                        {'range': [30, 65], 'color': "rgba(255, 255, 255, 0.05)"},
                        {'range': [65, 100], 'color': "rgba(255, 62, 0, 0.10)"}
                    ],
                    'threshold': {
                        'line': {'color': "#FF3E00", 'width': 2},
                        'thickness': 0.8,
                        'value': score
                    }
                }
            ))
            fig_gauge.update_layout(
                height=255,
                margin=dict(l=20, r=20, t=48, b=16),
                paper_bgcolor="#121214",
                plot_bgcolor="#121214"
            )
            st.plotly_chart(fig_gauge, width="stretch", alt="Indikator indeks risiko kognitif")

        with col_right:
            alert_cls = "high-alert" if is_elevated else "normal-alert"
            accent_txt = "color:#FF3E00;" if is_elevated else "color:#EDEDEF;"
            st.markdown(f"""
            <div class='readout-bar {alert_cls} anim-item stagger-2'>
                <span style='{accent_txt} font-weight:600;'>KLASIFIKASI // {category.upper()}</span>
                <span style='color:#71717A;'>SCORE: {score} / 100.0</span>
            </div>
            <div class='ed-panel anim-item stagger-3'>
                <div style='font-family:JetBrains Mono,monospace; font-size:0.7rem; color:#71717A; text-transform:uppercase; letter-spacing:0.06em; margin-bottom:6px;'>Ringkasan diagnostik</div>
                <div style='font-size:0.9rem; color:#EDEDEF; line-height:1.6;'>{analysis['summary']}</div>
            </div>
            """, unsafe_allow_html=True)

            # Kata Kunci & Pola Berbahaya Terdeteksi (Staggered 30ms per item, Zero Clip)
            st.markdown("<div class='anim-item stagger-4' style='font-family:JetBrains Mono,monospace; font-size:0.72rem; color:#A1A1AA; text-transform:uppercase; letter-spacing:0.06em; margin-top:12px;'>Kata kunci & pola berbahaya terdeteksi</div>", unsafe_allow_html=True)
            if flags:
                pills_html = []
                for idx, item in enumerate(flags):
                    meta = get_vector_code(item["dimensi"])
                    stagger_cls = f"stagger-{min(12, idx + 4)}"
                    pills_html.append(
                        f"<div class='ioc-pill anim-item {stagger_cls}'>"
                        f"<span class='ioc-marker'></span>"
                        f"<span class='ioc-term'>{html.escape(item['keyword'])}</span>"
                        f"<span class='ioc-code'>{meta['code']} · {meta['short']}</span>"
                        f"</div>"
                    )
                st.markdown(f"<div class='ioc-rack'>{''.join(pills_html)}</div>", unsafe_allow_html=True)
            else:
                st.markdown(
                    "<div class='ed-panel anim-item stagger-5' style='padding:10px 14px; font-family:JetBrains Mono,monospace; font-size:0.76rem; color:#71717A;'>"
                    "00 INDICATORS // Tidak ditemukan kata kunci pemicu manipulatif."
                    "</div>",
                    unsafe_allow_html=True
                )

        # Sorotan Konteks Spesimen Teks
        st.markdown("""
        <div class='index-bar anim-item stagger-5'>
            <span class='index-title'>Sorotan pemicu pada spesimen teks</span>
            <span class='index-code'>SEC // 01.B — ANNOTATED SPECIMEN</span>
        </div>
        """, unsafe_allow_html=True)
        annotated_html = annotate_specimen(res["raw"], flags)
        st.markdown(f"<div class='specimen-box anim-item stagger-6'>{annotated_html}</div>", unsafe_allow_html=True)

        # Distribusi 4 Dimensi Kognitif
        st.markdown("""
        <div class='index-bar anim-item stagger-6'>
            <span class='index-title'>Dekomposisi vektor risiko 4-dimensi</span>
            <span class='index-code'>SEC // 01.C — VECTOR TELEMETRY</span>
        </div>
        """, unsafe_allow_html=True)

        col_radar, col_bars = st.columns([1.05, 1.95], gap="large")
        with col_radar:
            cats = list(dims.keys())
            vals = list(dims.values())
            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(
                r=vals + [vals[0]],
                theta=cats + [cats[0]],
                fill='toself',
                fillcolor='rgba(255, 62, 0, 0.14)',
                line=dict(color='#FF3E00', width=1.8),
                marker=dict(size=5, color='#FF3E00')
            ))
            fig_radar.update_layout(
                polar=dict(
                    bgcolor="#121214",
                    radialaxis=dict(visible=True, range=[0, 100], gridcolor="rgba(255,255,255,0.08)", linecolor="rgba(255,255,255,0.08)", tickfont=dict(color="#71717A", size=9, family="JetBrains Mono")),
                    angularaxis=dict(gridcolor="rgba(255,255,255,0.08)", linecolor="rgba(255,255,255,0.08)", tickfont=dict(color="#A1A1AA", size=10))
                ),
                showlegend=False,
                height=250,
                margin=dict(l=45, r=45, t=22, b=22),
                paper_bgcolor="#121214"
            )
            st.plotly_chart(fig_radar, width="stretch", alt="Grafik radar empat dimensi risiko kognitif")

        with col_bars:
            for idx, (d_name, d_val) in enumerate(dims.items()):
                meta = get_vector_code(d_name)
                fill_color = "#FF3E00" if d_val >= 50 else "#EDEDEF"
                stagger_cls = f"stagger-{min(12, idx + 7)}"
                st.markdown(f"""
                <div class='dim-row anim-item {stagger_cls}'>
                    <div class='dim-top'>
                        <span class='dim-label'><span class='dim-code'>{meta["code"]}</span>{d_name}</span>
                        <span class='dim-val'>{d_val}%</span>
                    </div>
                    <div class='dim-track'>
                        <div class='dim-fill' style='width:{min(100, max(1, d_val))}%; background:{fill_color};'></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        with st.expander("Inspeksi pra-pemrosesan teks (raw vs normalized)", icon=":material/code:"):
            c_r, c_c = st.columns(2)
            c_r.caption("Teks asli (input mentah)")
            c_r.code(res["raw"], language=None)
            c_c.caption("Teks bersih (case-folded & slang normalized)")
            c_c.code(res["cleaned"], language=None)


# ==============================================================================
# TAB 2: DETEKSI ASTROTURFING & KEMIRIPAN TEKS
# ==============================================================================
with tab2:
    st.markdown("""
    <div class='index-bar anim-item stagger-1'>
        <span class='index-title'>Deteksi amplifikasi terkoordinasi & matriks kemiripan</span>
        <span class='index-code'>SEC // 02 — ASTROTURFING MATRIX</span>
    </div>
    """, unsafe_allow_html=True)

    col_up, col_smp = st.columns([2, 1], gap="medium", vertical_alignment="bottom")
    with col_up:
        uploaded_file = st.file_uploader(
            "Unggah berkas korpus (.csv atau .json)",
            type=["csv", "json"],
            help="Dataset berisi kolom teks/narasi seperti 'text', 'content', 'komentar', atau 'tweet'."
        )
    with col_smp:
        use_sample = st.button("Muat korpus sampel (12 post)", type="primary", icon=":material/database:", width="stretch")

    df_posts = None
    if uploaded_file is not None:
        try:
            df_posts = load_dataframe_from_file(uploaded_file)
            st.caption(f"Korpus dimuat: {len(df_posts)} baris data.")
        except Exception as e:
            st.error(f"Gagal membaca berkas: {e}", icon=":material/error:")
    elif use_sample or ("use_sample_active" in st.session_state and st.session_state.use_sample_active):
        st.session_state.use_sample_active = True
        sample_path = os.path.join(os.path.dirname(__file__), "data", "sample_posts.csv")
        if os.path.exists(sample_path):
            df_posts = pd.read_csv(sample_path)

    if df_posts is not None and not df_posts.empty:
        detected_col = detect_text_column(df_posts)
        c_sel, c_prv = st.columns([1.3, 2.7], vertical_alignment="bottom")
        with c_sel:
            text_column = st.selectbox(
                "Pilih kolom narasi",
                options=df_posts.columns.tolist(),
                index=df_posts.columns.tolist().index(detected_col) if detected_col in df_posts.columns else 0
            )
        with c_prv:
            with st.expander("Lihat tabel data mentah", icon=":material/table_chart:"):
                st.dataframe(df_posts.head(12), width="stretch", height=175, alt="Pratinjau tabel korpus mentah")

        raw_posts = extract_clean_posts(df_posts, text_column)

        if len(raw_posts) < 2:
            st.warning("Korpus memerlukan minimal 2 baris teks untuk analisis kemiripan.", icon=":material/warning:")
        else:
            sim_matrix, preprocessed_posts = astroturfing_detector.fit_transform_similarity(
                raw_posts, preprocess=True
            )
            metrics = astroturfing_detector.calculate_coordination_metrics(
                sim_matrix, threshold=sim_threshold
            )
            suspicious_pairs = astroturfing_detector.find_suspicious_pairs(
                sim_matrix, raw_posts, threshold=sim_threshold
            )
            top_terms = astroturfing_detector.get_top_repetitive_keywords(
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
            status_cls = "cell-value accent" if is_astro else "cell-value"
            status_str = "COORDINATED" if is_astro else "ORGANIC"

            st.markdown(f"""
            <div class='industrial-grid'>
                <div class='grid-cell anim-item stagger-1'>
                    <div class='cell-label'>01 // TOTAL CORPUS</div>
                    <div class='cell-value'>{metrics['total_posts']:02d}</div>
                    <div class='cell-foot'>{metrics['involved_posts_count']} NODE TERLIBAT KLASTER</div>
                </div>
                <div class='grid-cell anim-item stagger-2'>
                    <div class='cell-label'>02 // DUPLICATE PAIRS (≥{int(sim_threshold*100)}%)</div>
                    <div class='cell-value'>{metrics['high_similarity_pairs_count']:02d}</div>
                    <div class='cell-foot'>PUNCAK: {round(metrics['max_pairwise_similarity']*100, 1)}%</div>
                </div>
                <div class='grid-cell anim-item stagger-3'>
                    <div class='cell-label'>03 // AMPLIFICATION RATIO</div>
                    <div class='cell-value'>{metrics['amplification_ratio']}%</div>
                    <div class='cell-foot'>PROPORSI REPLIKASI NARASI</div>
                </div>
                <div class='grid-cell anim-item stagger-4'>
                    <div class='cell-label'>04 // NETWORK REGIME</div>
                    <div class='{status_cls}' style='font-size:1.25rem;'>{status_str}</div>
                    <div class='cell-foot'>CAMPAIGN RISK: {metrics['campaign_risk_score']}%</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Heatmap Monokrom + Single High-Weight Accent (#FF3E00)
            st.markdown("""
            <div class='index-bar anim-item stagger-5'>
                <span class='index-title'>Matriks kemiripan kosinus antar-unggahan</span>
                <span class='index-code'>SEC // 02.B — PAIRWISE COSINE SIMILARITY</span>
            </div>
            """, unsafe_allow_html=True)

            labels = [f"P#{i+1:02d}: {t[:22]}..." for i, t in enumerate(raw_posts)]
            fig_heatmap = px.imshow(
                np.round(sim_matrix, 2),
                labels=dict(x="Target node", y="Source node", color="Similarity"),
                x=labels,
                y=labels,
                color_continuous_scale=[
                    [0.0, "#0A0A0B"],
                    [0.45, "#1E1E22"],
                    [0.70, "#52525B"],
                    [0.85, "#D4D4D8"],
                    [1.0, "#FF3E00"]
                ],
                zmin=0.0,
                zmax=1.0,
                aspect="auto",
                text_auto=True if len(raw_posts) <= 15 else False
            )
            fig_heatmap.update_layout(
                height=440,
                margin=dict(l=16, r=16, t=20, b=16),
                paper_bgcolor="#121214",
                plot_bgcolor="#121214",
                font=dict(color="#A1A1AA", family="JetBrains Mono", size=10)
            )
            st.plotly_chart(fig_heatmap, width="stretch", alt="Peta kalor kemiripan teks antar unggahan")

            # Tabel Pasangan Kemiripan Mencurigakan
            st.markdown(f"""
            <div class='index-bar anim-item stagger-6'>
                <span class='index-title'>Pasangan unggahan terindikasi kloning / buzzer</span>
                <span class='index-code'>SEC // 02.C — THRESHOLD ≥ {int(sim_threshold*100)}%</span>
            </div>
            """, unsafe_allow_html=True)

            if suspicious_pairs:
                pairs_display = []
                for p in suspicious_pairs:
                    pairs_display.append({
                        "Node A": f"P#{p['post_a_id']:02d}",
                        "Node B": f"P#{p['post_b_id']:02d}",
                        "Kemiripan": p["similarity_percentage"],
                        "Klasifikasi": p["coordination_level"],
                        "Spesimen A": p["text_a"],
                        "Spesimen B": p["text_b"]
                    })
                st.dataframe(
                    pd.DataFrame(pairs_display),
                    column_config={
                        "Kemiripan": st.column_config.ProgressColumn(
                            "Cosine similarity",
                            format="%.1f%%",
                            min_value=0,
                            max_value=100,
                        )
                    },
                    width="stretch",
                    hide_index=True,
                    alt="Tabel pasangan unggahan dengan kemiripan tinggi"
                )
            else:
                st.caption(f"Tidak ditemukan pasangan unggahan yang melewati ambang batas {int(sim_threshold*100)}%.")

            # Top Replicated Signatures
            if top_terms:
                st.markdown("""
                <div class='index-bar anim-item stagger-7'>
                    <span class='index-title'>Frase & slogan paling sering direplikasi</span>
                    <span class='index-code'>SEC // 02.D — REPLICATED N-GRAMS</span>
                </div>
                """, unsafe_allow_html=True)
                sigs_html = []
                for idx, (term, score_val) in enumerate(top_terms):
                    stagger_cls = f"stagger-{min(12, idx + 5)}"
                    sigs_html.append(
                        f"<div class='ioc-pill anim-item {stagger_cls}'>"
                        f"<span class='ioc-marker'></span>"
                        f"<span class='ioc-term'>{html.escape(term)}</span>"
                        f"<span class='ioc-code'>TF-IDF {score_val}</span>"
                        f"</div>"
                    )
                st.markdown(f"<div class='ioc-rack'>{''.join(sigs_html)}</div>", unsafe_allow_html=True)


# ==============================================================================
# TAB 3: LEMBAR RINGKASAN INTELIJEN TAKTIS
# ==============================================================================
with tab3:
    st.markdown("""
    <div class='index-bar anim-item stagger-1'>
        <span class='index-title'>Lembar ringkasan intelijen & protokol mitigasi</span>
        <span class='index-code'>SEC // 03 — TACTICAL DOSSIER</span>
    </div>
    """, unsafe_allow_html=True)

    batch = st.session_state.get("last_batch_result")
    single = st.session_state.get("last_single_result")

    if not batch and not single:
        st.markdown("""
        <div class='ed-panel anim-item stagger-2' style='padding:32px 24px;'>
            <div style='font-family:JetBrains Mono,monospace; font-size:0.72rem; color:#71717A; letter-spacing:0.08em; margin-bottom:6px;'>STATUS // NO BUFFERED TELEMETRY</div>
            <div style='font-size:1rem; font-weight:600; color:#EDEDEF; margin-bottom:4px;'>Belum ada data inspeksi aktif</div>
            <div style='color:#A1A1AA; font-size:0.86rem;'>
                Jalankan evaluasi teks pada <b>Inspeksi risiko kognitif</b> atau muat korpus pada <b>Deteksi jaringan astroturfing</b> untuk menyusun berkas intelijen otomatis.
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        intel_report = []
        intel_report.append("=" * 74)
        intel_report.append("  COGNISHIELD // TACTICAL THREAT INTELLIGENCE DOSSIER")
        intel_report.append("  CLASSIFICATION: RESTRICTED // INTERNAL CYBER DEFENSE UNIT")
        intel_report.append("=" * 74)
        intel_report.append("")

        intel_report.append("[01] RINGKASAN EKSEKUTIF")
        if batch:
            metrics = batch["metrics"]
            thresh = int(batch["threshold"] * 100)
            if metrics["astroturfing_detected"]:
                threat_level = "CRITICAL // COORDINATED ASTROTURFING DETECTED"
                summary_narrative = (
                    f"Teridentifikasi operasi amplifikasi narasi terkoordinasi (Astroturfing/Buzzer). "
                    f"Sebanyak {metrics['involved_posts_count']} dari {metrics['total_posts']} unggahan "
                    f"({metrics['amplification_ratio']}%) memiliki kemiripan di atas ambang batas {thresh}%, "
                    f"dengan {metrics['high_similarity_pairs_count']} pasang duplikasi template."
                )
            else:
                threat_level = "NOMINAL // ORGANIC DISTRIBUTION"
                summary_narrative = (
                    f"Distribusi narasi pada korpus ({metrics['total_posts']} unggahan) bersifat organik. "
                    f"Rasio kemiripan tinggi tercatat {metrics['amplification_ratio']}%, di bawah ambang indikasi kampanye bot."
                )
        elif single:
            cat = single["analysis"]["risk_category"]
            score = single["analysis"]["overall_risk_score"]
            threat_level = f"{cat.upper()} // COGNITIVE RISK INDEX: {score}%"
            summary_narrative = single["analysis"]["summary"]

        intel_report.append(f"Status Ancaman : {threat_level}")
        intel_report.append(f"Evaluasi       : {summary_narrative}")
        intel_report.append("")

        intel_report.append("[02] VEKTOR RISIKO & INDIKATOR LEKSIKAL")
        if single:
            dims = single["analysis"]["dimensions"]
            for d_name, d_val in dims.items():
                status_bar = "█" * int(d_val / 10) + "░" * (10 - int(d_val / 10))
                intel_report.append(f"  • {d_name:<28}: [{status_bar}] {d_val}%")
            if single["analysis"]["detected_flags"]:
                pemicu = ", ".join([f"{f['keyword']} ({f['dimensi']})" for f in single["analysis"]["detected_flags"]])
                intel_report.append(f"  • Indikator Terdeteksi        : {pemicu}")
        if batch and batch["top_terms"]:
            terms_str = ", ".join([f"'{t[0]}' ({t[1]})" for t in batch["top_terms"]])
            intel_report.append(f"  • Slogan Direplikasi          : {terms_str}")
        intel_report.append("")

        intel_report.append("[03] PROTOKOL TINDAKAN TAKTIS (COUNTERMEASURES)")
        is_high_risk = (batch and batch["metrics"]["astroturfing_detected"]) or (
            single and single["analysis"]["overall_risk_score"] >= 65
        )

        if is_high_risk:
            intel_report.append("  [DIRECTIVE: PROTOKOL MERAH — INTERVENSI AKTIF]")
            intel_report.append("  1. Audit Node      : Tandai akun dalam klaster kemiripan ≥85% untuk verifikasi bot.")
            intel_report.append("  2. Rate Limiting   : Batasi laju distribusi tagar/slogan yang direplikasi secara mekanik.")
            intel_report.append("  3. Prebunking      : Rilis klarifikasi fakta terverifikasi sebelum narasi mendominasi.")
            intel_report.append("  4. Forensik Jaringan: Simpan metadata timestamp untuk pemetaan jaringan aktor.")
        else:
            intel_report.append("  [DIRECTIVE: PROTOKOL STANDAR — PEMANTAUAN PASIF]")
            intel_report.append("  1. Telemetri Berkala: Lanjutkan pemantauan sentimen 6-12 jam ke depan.")
            intel_report.append("  2. Radar Kata Kunci : Masukkan kata kunci dominan ke daftar pantau deteksi dini.")
            intel_report.append("  3. Komunikasi Publik: Pertahankan saluran informasi resmi secara transparan.")

        intel_report.append("")
        intel_report.append("=" * 74)
        intel_report.append("  GENERATED BY COGNISHIELD ENGINE // END OF DOSSIER")
        intel_report.append("=" * 74)

        report_text = "\n".join(intel_report)

        col_meta, col_term = st.columns([1, 2], gap="large")
        with col_meta:
            panel_cls = "ed-panel ed-panel-accent anim-item stagger-2" if is_high_risk else "ed-panel anim-item stagger-2"
            dir_color = "#FF3E00" if is_high_risk else "#EDEDEF"
            dir_label = "PROTOKOL MERAH // INTERVENSI AKTIF" if is_high_risk else "PROTOKOL STANDAR // OBSERVASI PASIF"
            st.markdown(f"""
            <div class='{panel_cls}'>
                <div style='font-family:JetBrains Mono,monospace; font-size:0.7rem; color:#71717A; letter-spacing:0.06em; margin-bottom:6px;'>DIRECTIVE STATUS</div>
                <div style='font-family:JetBrains Mono,monospace; font-size:0.9rem; font-weight:700; color:{dir_color}; margin-bottom:10px;'>{dir_label}</div>
                <div style='font-size:0.86rem; color:#A1A1AA; line-height:1.6;'>{summary_narrative}</div>
            </div>
            """, unsafe_allow_html=True)

            st.download_button(
                label="Unduh berkas intelijen (.txt)",
                data=report_text,
                file_name="CogniShield_Tactical_Dossier.txt",
                mime="text/plain",
                type="primary",
                icon=":material/download:",
                width="stretch"
            )

        with col_term:
            # Bangun blok HTML terstruktur per baris agar tidak pernah tergabung jadi 1 paragraf
            vec_rows_html = []
            if single:
                dims = single["analysis"]["dimensions"]
                for d_name, d_val in dims.items():
                    filled = int(d_val / 10)
                    bar_str = "█" * filled + "░" * (10 - filled)
                    val_color = "#FF3E00" if d_val >= 50 else "#EDEDEF"
                    vec_rows_html.append(
                        f"<div class='dossier-vec-row'>"
                        f"<span style='color:#A1A1AA;'>• {html.escape(d_name)}</span>"
                        f"<span style='color:{val_color}; letter-spacing:1px;'>[{bar_str}]</span>"
                        f"<span style='color:{val_color}; font-weight:600; text-align:right;'>{d_val}%</span>"
                        f"</div>"
                    )
                if single["analysis"]["detected_flags"]:
                    pemicu = ", ".join([f"{f['keyword']} ({f['dimensi']})" for f in single["analysis"]["detected_flags"]])
                    vec_rows_html.append(
                        f"<div class='dossier-kv' style='margin-top:10px; padding-top:8px; border-top:1px dashed rgba(255,255,255,0.06);'>"
                        f"<span class='dossier-k'>Indikator Terdeteksi</span>"
                        f"<span class='dossier-v'>{html.escape(pemicu)}</span>"
                        f"</div>"
                    )
            if batch and batch["top_terms"]:
                terms_str = ", ".join([f"'{t[0]}' ({t[1]})" for t in batch["top_terms"]])
                vec_rows_html.append(
                    f"<div class='dossier-kv' style='margin-top:8px;'>"
                    f"<span class='dossier-k'>Slogan Direplikasi</span>"
                    f"<span class='dossier-v'>{html.escape(terms_str)}</span>"
                    f"</div>"
                )

            if is_high_risk:
                directive_tag = "[DIRECTIVE: PROTOKOL MERAH — INTERVENSI AKTIF]"
                steps = [
                    ("01", "Audit Node", "Tandai akun dalam klaster kemiripan ≥85% untuk verifikasi bot."),
                    ("02", "Rate Limiting", "Batasi laju distribusi tagar/slogan yang direplikasi secara mekanik."),
                    ("03", "Prebunking", "Rilis klarifikasi fakta terverifikasi sebelum narasi mendominasi."),
                    ("04", "Forensik Jaringan", "Simpan metadata timestamp untuk pemetaan jaringan aktor."),
                ]
            else:
                directive_tag = "[DIRECTIVE: PROTOKOL STANDAR — PEMANTAUAN PASIF]"
                steps = [
                    ("01", "Telemetri Berkala", "Lanjutkan pemantauan sentimen 6-12 jam ke depan."),
                    ("02", "Radar Kata Kunci", "Masukkan kata kunci dominan ke daftar pantau deteksi dini."),
                    ("03", "Komunikasi Publik", "Pertahankan saluran informasi resmi secara transparan."),
                ]

            steps_html = "".join([
                f"<div class='dossier-step'>"
                f"<span style='color:#FF3E00; font-weight:600;'>{num}.</span>"
                f"<span style='color:#EDEDEF; font-weight:600;'>{label}</span>"
                f"<span style='color:#A1A1AA; font-family:Inter,sans-serif; font-size:0.84rem;'>{desc}</span>"
                f"</div>"
                for num, label, desc in steps
            ])

            dossier_html = (
                f"<div class='dossier-frame anim-item stagger-3'>"
                f"<div class='dossier-head'>"
                f"<span>DOSSIER_OUTPUT.TXT</span>"
                f"<span>ENCODING: UTF-8 // READONLY</span>"
                f"</div>"
                f"<div class='dossier-body'>"
                f"<div class='dossier-banner'>"
                f"<div class='dossier-banner-title'>COGNISHIELD // TACTICAL THREAT INTELLIGENCE DOSSIER</div>"
                f"<div class='dossier-banner-sub'>CLASSIFICATION: RESTRICTED // INTERNAL CYBER DEFENSE UNIT</div>"
                f"</div>"
                f"<div class='dossier-sec'>"
                f"<div class='dossier-sec-title'>[01] RINGKASAN EKSEKUTIF</div>"
                f"<div class='dossier-kv'><span class='dossier-k'>Status Ancaman</span><span style='color:{dir_color}; font-weight:700;'>{html.escape(threat_level)}</span></div>"
                f"<div class='dossier-kv'><span class='dossier-k'>Evaluasi</span><span class='dossier-v'>{html.escape(summary_narrative)}</span></div>"
                f"</div>"
                f"<div class='dossier-sec'>"
                f"<div class='dossier-sec-title'>[02] VEKTOR RISIKO &amp; INDIKATOR LEKSIKAL</div>"
                f"{''.join(vec_rows_html)}"
                f"</div>"
                f"<div class='dossier-sec'>"
                f"<div class='dossier-sec-title'>[03] PROTOKOL TINDAKAN TAKTIS (COUNTERMEASURES)</div>"
                f"<div style='color:#EDEDEF; font-weight:600; font-size:0.76rem; margin-bottom:8px;'>{directive_tag}</div>"
                f"{steps_html}"
                f"</div>"
                f"<div style='padding-top:10px; border-top:1px solid rgba(255,255,255,0.08); font-size:0.7rem; color:#71717A; display:flex; justify-content:space-between;'>"
                f"<span>GENERATED BY COGNISHIELD ENGINE</span>"
                f"<span>END OF DOSSIER</span>"
                f"</div>"
                f"</div>"
                f"</div>"
            )
            st.markdown(dossier_html, unsafe_allow_html=True)
