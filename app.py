"""
CogniShield: Sistem Analisis Risiko Kognitif & Deteksi Astroturfing
Antarmuka Streamlit Native — Disiplin Editorial & Tanpa Dekorasi Buatan
"""

import os
import sys
import re
import pandas as pd
import altair as alt
import streamlit as st

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from modules.preprocessing import preprocess_text
from modules.risk_scoring import CognitiveRiskScorer
from modules.astroturfing import AstroturfingDetector
from modules.ingestion import load_dataframe_from_file, detect_text_column, extract_clean_posts


# ==============================================================================
# KONFIGURASI HALAMAN STREAMLIT
# ==============================================================================
st.set_page_config(
    page_title="CogniShield — Analisis Risiko Kognitif & Astroturfing",
    page_icon=":material/shield:",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ==============================================================================
# CACHED ENGINES & HELPER FUNCTIONS
# ==============================================================================
@st.cache_resource
def get_engines(_version: str = "2.1") -> tuple[CognitiveRiskScorer, AstroturfingDetector]:
    """Menginisialisasi mesin penilaian risiko kognitif dan detektor astroturfing."""
    return CognitiveRiskScorer(), AstroturfingDetector()


@st.cache_data(ttl="30m", max_entries=10)
def load_sample_dataset(path: str) -> pd.DataFrame:
    """Memuat dataset sampel dari disk dengan caching."""
    return pd.read_csv(path)


risk_scorer, astroturfing_detector = get_engines()

PRESET_TEXTS = {
    "Kritis (provokasi & konspirasi)": (
        "VIRALKAN SEKARANG JUGA!! Rezim antek asing ini sudah keterlaluan membodohi rakyat, "
        "semua bukti konspirasi akan kita bongkar habis!! Jangan mau dicuci otak oleh media bayaran laknat!!"
    ),
    "Waspada (urgensi semu)": (
        "Waspada kawan-kawan!! Katanya ada isu rahasia yang sengaja ditutup-tutupi para elit politik. "
        "Jangan diam saja, tolong sebarkan sebelum dihapus!"
    ),
    "Nominal (informasi publik)": (
        "Badan Meteorologi mengimbau masyarakat pesisir untuk memperhatikan prakiraan pasang air laut "
        "serta menjaga kebersihan saluran drainase selama tiga hari ke depan."
    ),
}


def highlight_triggers_markdown(raw_text: str, detected_flags: list[dict]) -> str:
    """Menyorot kata kunci pemicu di dalam teks menggunakan sintaks Markdown native Streamlit."""
    if not raw_text:
        return ""
    result = raw_text
    if not detected_flags:
        return result

    sorted_flags = sorted(detected_flags, key=lambda x: len(x["keyword"]), reverse=True)
    seen = set()
    for item in sorted_flags:
        kw = item["keyword"]
        if kw.lower() in seen:
            continue
        seen.add(kw.lower())
        pattern = re.compile(rf"\b({re.escape(kw)})\b" if " " not in kw else rf"({re.escape(kw)})", re.IGNORECASE)
        result = pattern.sub(r":primary-background[**\1**]", result)
    return result


def format_plain_dossier(single_res: dict | None, batch_res: dict | None) -> str:
    """Menyusun berkas laporan teks murni (.txt) untuk diunduh."""
    lines = [
        "COGNISHIELD — LEMBAR RINGKASAN INTELIJEN & PROTOKOL MITIGASI",
        "Klasifikasi: Internal // Pertahanan Siber Sosial",
        "-" * 68,
        "",
        "1. RINGKASAN EKSEKUTIF",
    ]
    if batch_res:
        m = batch_res["metrics"]
        thresh = int(batch_res["threshold"] * 100)
        status = "KRITIS (Kampanye Astroturfing Terdeteksi)" if m["astroturfing_detected"] else "NOMINAL (Sebaran Organik)"
        summary = (
            f"Terdeteksi {m['involved_posts_count']} dari {m['total_posts']} unggahan ({m['amplification_ratio']}%) "
            f"memiliki kemiripan di atas ambang {thresh}% ({m['high_similarity_pairs_count']} pasang duplikasi)."
            if m["astroturfing_detected"]
            else f"Sebaran {m['total_posts']} unggahan bersifat organik (rasio duplikasi {m['amplification_ratio']}%)."
        )
    elif single_res:
        a = single_res["analysis"]
        status = f"{a['risk_category'].upper()} (Indeks Risiko Kognitif: {a['overall_risk_score']}%)"
        summary = a["summary"]
    else:
        status = "Tidak ada data"
        summary = "-"

    lines.append(f"Status ancaman : {status}")
    lines.append(f"Evaluasi       : {summary}")
    lines.append("")
    lines.append("2. VEKTOR RISIKO & INDIKATOR")

    if single_res:
        for d_name, d_val in single_res["analysis"]["dimensions"].items():
            lines.append(f"- {d_name:<28}: {d_val}%")
        flags = single_res["analysis"]["detected_flags"]
        if flags:
            lines.append(f"- Indikator terdeteksi        : {', '.join(f['keyword'] for f in flags)}")
    if batch_res and batch_res["top_terms"]:
        lines.append(
            f"- Frase direplikasi           : {', '.join(f'{t[0]} ({t[1]})' for t in batch_res['top_terms'])}"
        )

    lines.append("")
    lines.append("3. PROTOKOL TINDAKAN TAKTIS")
    is_high = (batch_res and batch_res["metrics"]["astroturfing_detected"]) or (
        single_res and single_res["analysis"]["overall_risk_score"] >= 65
    )
    if is_high:
        lines.extend([
            "[Protokol Merah — Intervensi Aktif]",
            "1. Audit akun pada klaster kemiripan >= 85% untuk pemeriksaan otomasi/bot.",
            "2. Batasi laju amplifikasi pada slogan atau tagar yang terduplikasi secara mekanik.",
            "3. Terbitkan klarifikasi berbasis data resmi (prebunking) sebelum narasi meluas.",
            "4. Arsipkan metadata waktu dan keterkaitan antar-unggah untuk pemetaan jaringan.",
        ])
    else:
        lines.extend([
            "[Protokol Standar — Pemantauan Pasif]",
            "1. Pantau tren sentimen dan volume kata kunci selama 6-12 jam ke depan.",
            "2. Daftarkan frase dominan ke dalam radar deteksi dini.",
            "3. Pertahankan keterbukaan informasi pada kanal komunikasi resmi.",
        ])

    return "\n".join(lines)


# ==============================================================================
# INISIALISASI SESSION STATE
# ==============================================================================
st.session_state.setdefault("last_single_result", None)
st.session_state.setdefault("last_batch_result", None)
st.session_state.setdefault("input_text_area", PRESET_TEXTS["Kritis (provokasi & konspirasi)"])


# ==============================================================================
# SIDEBAR — HANYA FILTER GLOBAL & INFO RINGKAS (SESUAI SKILL.MD)
# ==============================================================================
with st.sidebar:
    st.markdown("### :material/shield: CogniShield")
    st.caption("Analisis risiko kognitif multi-dimensi dan deteksi amplifikasi terkoordinasi.")

    sim_threshold = st.slider(
        "Ambang kemiripan kosinus",
        min_value=0.35,
        max_value=0.90,
        value=0.55,
        step=0.05,
        help="Pasangan unggahan dengan skor kemiripan leksikal & konteks di atas nilai ini ditandai sebagai terkoordinasi.",
    )

    st.caption("PUSSIBERAD × CODEPOLITAN · 2026")


# ==============================================================================
# HEADER HALAMAN UTAMA
# ==============================================================================
st.title("CogniShield")
st.caption(
    "Evaluasi indeks risiko manipulasi kognitif 4-dimensi dan pemetaan jaringan astroturfing media sosial."
)


# ==============================================================================
# NAVIGASI TAB
# ==============================================================================
tab1, tab2, tab3 = st.tabs([
    ":material/radar: Inspeksi risiko kognitif",
    ":material/hub: Deteksi jaringan astroturfing",
    ":material/description: Lembar ringkasan intelijen",
])


# ==============================================================================
# TAB 1: SINGLE-INPUT COGNITIVE ANALYZER
# ==============================================================================
with tab1:
    def on_preset_change():
        choice = st.session_state.get("preset_selector")
        if choice and choice in PRESET_TEXTS:
            st.session_state.input_text_area = PRESET_TEXTS[choice]

    st.segmented_control(
        "Contoh skenario",
        options=list(PRESET_TEXTS.keys()),
        default="Kritis (provokasi & konspirasi)",
        key="preset_selector",
        on_change=on_preset_change,
    )

    user_text = st.text_area(
        "Teks unggahan atau narasi",
        key="input_text_area",
        height=110,
        placeholder="Tempelkan teks narasi media sosial untuk dianalisis...",
    )

    with st.container(horizontal=True):
        analyze_btn = st.button("Analisis teks", type="primary", icon=":material/analytics:")
        clear_btn = st.button("Bersihkan", icon=":material/restart_alt:")

    if clear_btn:
        st.session_state.input_text_area = ""
        st.session_state.last_single_result = None
        st.rerun()

    if analyze_btn or (user_text.strip() and st.session_state.last_single_result is None):
        if not user_text.strip():
            st.warning("Masukkan teks terlebih dahulu untuk dianalisis.", icon=":material/warning:")
        else:
            cleaned_text = preprocess_text(user_text)
            analysis = risk_scorer.analyze_text(user_text)
            st.session_state.last_single_result = {
                "raw": user_text,
                "cleaned": cleaned_text,
                "analysis": analysis,
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

        # Baris KPI menggunakan native st.metric dengan border=True dan height="stretch"
        m1, m2, m3, m4 = st.columns(4)
        m1.metric(
            "Indeks risiko kognitif",
            f"{score}%",
            delta=category,
            delta_color="inverse" if score >= 30 else "normal",
            border=True,
            height="stretch",
        )
        m2.metric(
            "Indikator terdeteksi",
            f"{len(flags)} kata",
            delta=0,
            delta_description="pemicu leksikon aktif",
            border=True,
            height="stretch",
        )
        m3.metric(
            "Dimensi tertinggi",
            f"{max(dims.values())}%",
            delta=0,
            delta_description=dominant_dim,
            border=True,
            height="stretch",
        )
        m4.metric(
            "Proporsi huruf kapital",
            f"{caps_pct}%",
            delta=0,
            delta_description=f"dari {word_count} kata",
            border=True,
            height="stretch",
        )

        col_eval, col_chart = st.columns([1.15, 1.35], gap="medium")

        with col_eval:
            with st.container(border=True, height="stretch"):
                badge_color = "red" if category == "Bahaya" else ("orange" if category == "Waspada" else "green")
                badge_icon = ":material/error:" if category == "Bahaya" else (":material/warning:" if category == "Waspada" else ":material/check_circle:")

                with st.container(horizontal=True, vertical_alignment="center"):
                    st.subheader("Evaluasi diagnostik")
                    st.badge(f"Status: {category}", icon=badge_icon, color=badge_color)

                st.markdown(analysis["summary"])

                st.caption("Sorotan pemicu pada teks")
                st.markdown(f"> {highlight_triggers_markdown(res['raw'], flags)}")

                st.caption("Kata kunci & pola berbahaya terdeteksi")
                if flags:
                    badges_md = " ".join([
                        f":primary-badge[:material/flag: {item['keyword']} · {item['dimensi']}]"
                        for item in flags
                    ])
                    st.markdown(badges_md)
                else:
                    st.caption("Tidak ditemukan indikator kata kunci manipulatif.")

        with col_chart:
            with st.container(border=True, height="stretch"):
                st.subheader("Profil empat dimensi risiko")
                st.caption("Skor intensitas leksikal per dimensi (skala 0–100%).")

                dim_df = pd.DataFrame({
                    "Dimensi": list(dims.keys()),
                    "Skor": list(dims.values()),
                })

                bar_chart = (
                    alt.Chart(dim_df)
                    .mark_bar(height=22, cornerRadiusEnd=2)
                    .encode(
                        x=alt.X("Skor:Q", scale=alt.Scale(domain=[0, 100]), title="Skor risiko (%)"),
                        y=alt.Y("Dimensi:N", sort=None, title=None),
                        color=alt.condition(
                            alt.datum.Skor >= 50,
                            alt.value("#FF3E00"),
                            alt.value("#A1A1AA"),
                        ),
                        tooltip=[
                            alt.Tooltip("Dimensi:N", title="Dimensi"),
                            alt.Tooltip("Skor:Q", title="Skor (%)"),
                        ],
                    )
                    .properties(height=220)
                )
                text_labels = (
                    alt.Chart(dim_df)
                    .mark_text(align="left", baseline="middle", dx=6, color="#EDEDEF", font="JetBrains Mono")
                    .encode(
                        x=alt.X("Skor:Q"),
                        y=alt.Y("Dimensi:N", sort=None),
                        text=alt.Text("Skor:Q", format=".1f"),
                    )
                )
                st.altair_chart(
                    bar_chart + text_labels,
                    alt="Grafik batang horizontal empat dimensi risiko kognitif",
                )

        with st.expander("Detail pra-pemrosesan teks (mentah vs ternormalisasi)", icon=":material/code:"):
            c_raw, c_clean = st.columns(2)
            with c_raw:
                st.caption("Teks asli")
                st.code(res["raw"], language=None)
            with c_clean:
                st.caption("Hasil normalisasi (case-folded & kamus slang)")
                st.code(res["cleaned"], language=None)


# ==============================================================================
# TAB 2: DETEKSI JARINGAN ASTROTURFING
# ==============================================================================
with tab2:
    data_source = st.segmented_control(
        "Sumber data korpus",
        options=["Dataset sampel (12 unggahan)", "Unggah berkas (.csv / .json)"],
        default="Dataset sampel (12 unggahan)",
    )

    df_posts = None
    if data_source == "Unggah berkas (.csv / .json)":
        uploaded_file = st.file_uploader(
            "Pilih berkas CSV atau JSON",
            type=["csv", "json"],
            help="Berkas harus memiliki kolom teks seperti 'text', 'content', 'komentar', atau 'tweet'.",
        )
        if uploaded_file is not None:
            try:
                df_posts = load_dataframe_from_file(uploaded_file)
            except Exception as e:
                st.error(f"Gagal membaca berkas: {e}", icon=":material/error:")
    else:
        sample_path = os.path.join(os.path.dirname(__file__), "data", "sample_posts.csv")
        if os.path.exists(sample_path):
            df_posts = load_sample_dataset(sample_path)

    if df_posts is not None and not df_posts.empty:
        detected_col = detect_text_column(df_posts)
        col_sel, col_exp = st.columns([1, 2], vertical_alignment="bottom")
        with col_sel:
            text_column = st.selectbox(
                "Kolom teks yang dianalisis",
                options=df_posts.columns.tolist(),
                index=df_posts.columns.tolist().index(detected_col) if detected_col in df_posts.columns else 0,
            )
        with col_exp:
            with st.expander(f"Pratinjau dataset ({len(df_posts)} baris)", icon=":material/table_chart:"):
                st.dataframe(df_posts, height=200, hide_index=True, alt="Tabel pratinjau dataset unggahan")

        raw_posts = extract_clean_posts(df_posts, text_column)

        if len(raw_posts) < 2:
            st.warning("Dataset memerlukan minimal 2 baris teks untuk menghitung kemiripan.", icon=":material/warning:")
        else:
            sim_matrix, _ = astroturfing_detector.fit_transform_similarity(raw_posts, preprocess=True)
            metrics = astroturfing_detector.calculate_coordination_metrics(sim_matrix, threshold=sim_threshold)
            suspicious_pairs = astroturfing_detector.find_suspicious_pairs(sim_matrix, raw_posts, threshold=sim_threshold)
            top_terms = astroturfing_detector.get_top_repetitive_keywords(raw_posts, top_n=8)

            st.session_state.last_batch_result = {
                "df": df_posts,
                "raw_posts": raw_posts,
                "sim_matrix": sim_matrix,
                "metrics": metrics,
                "suspicious_pairs": suspicious_pairs,
                "top_terms": top_terms,
                "threshold": sim_threshold,
            }

            is_astro = metrics["astroturfing_detected"]

            k1, k2, k3, k4 = st.columns(4)
            k1.metric(
                "Total unggahan",
                f"{metrics['total_posts']}",
                delta=0,
                delta_description=f"{metrics.get('hostile_posts_count', metrics['involved_posts_count'])} bermuatan pemicu ({metrics.get('hostile_ratio', metrics['amplification_ratio'])}%)",
                border=True,
                height="stretch",
            )
            k2.metric(
                f"Pasangan terkoordinasi (≥{int(sim_threshold * 100)}%)",
                f"{metrics['high_similarity_pairs_count']}",
                delta=0,
                delta_description=f"maksimum {round(metrics['max_pairwise_similarity'] * 100, 1)}%",
                border=True,
                height="stretch",
            )
            k3.metric(
                "Rasio amplifikasi & buzzer",
                f"{metrics['amplification_ratio']}%",
                delta=0,
                delta_description=f"vektor: {metrics.get('dominant_campaign_vector', 'Campuran')}",
                border=True,
                height="stretch",
            )
            k4.metric(
                "Status jaringan",
                "Terkoordinasi" if is_astro else "Organik",
                delta=f"Risiko {metrics['campaign_risk_score']}%",
                delta_color="inverse" if is_astro else "normal",
                border=True,
                height="stretch",
            )

            if is_astro and metrics.get("detection_reason"):
                st.warning(
                    metrics["detection_reason"],
                    title="Indikasi kampanye buzzer / astroturfing terdeteksi",
                    icon=":material/gpp_maybe:",
                )

            col_heat, col_terms = st.columns([1.65, 0.85], gap="medium")

            with col_heat:
                with st.container(border=True, height="stretch"):
                    st.subheader("Matriks kemiripan kosinus antar-unggahan")
                    st.caption("Skor 1.0 menunjukkan duplikasi identik; 0.0 menunjukkan narasi berbeda.")

                    n_posts = len(raw_posts)
                    heat_records = []
                    for i in range(n_posts):
                        for j in range(n_posts):
                            heat_records.append({
                                "Unggahan A": f"P{i + 1:02d}",
                                "Unggahan B": f"P{j + 1:02d}",
                                "Kemiripan": round(float(sim_matrix[i, j]), 2),
                                "Cuplikan A": raw_posts[i][:60],
                                "Cuplikan B": raw_posts[j][:60],
                            })
                    heat_df = pd.DataFrame(heat_records)

                    heatmap = (
                        alt.Chart(heat_df)
                        .mark_rect(stroke="#0A0A0B", strokeWidth=1)
                        .encode(
                            x=alt.X("Unggahan B:O", title="Unggahan target"),
                            y=alt.Y("Unggahan A:O", title="Unggahan asal"),
                            color=alt.Color(
                                "Kemiripan:Q",
                                scale=alt.Scale(
                                    domain=[0.0, 0.5, 0.75, 1.0],
                                    range=["#121214", "#27272A", "#A1A1AA", "#FF3E00"],
                                ),
                                title="Similarity",
                            ),
                            tooltip=[
                                alt.Tooltip("Unggahan A:O"),
                                alt.Tooltip("Unggahan B:O"),
                                alt.Tooltip("Kemiripan:Q", format=".2f"),
                                alt.Tooltip("Cuplikan A:N"),
                                alt.Tooltip("Cuplikan B:N"),
                            ],
                        )
                        .properties(height=340)
                    )
                    st.altair_chart(heatmap, alt="Peta kalor kemiripan teks antar unggahan")

            with col_terms:
                with st.container(border=True, height="stretch"):
                    st.subheader("Frase paling sering direplikasi")
                    st.caption("Kata kunci atau n-gram dengan bobot TF-IDF rata-rata tertinggi.")
                    if top_terms:
                        terms_df = pd.DataFrame(top_terms, columns=["Frase / kata kunci", "Bobot TF-IDF"])
                        st.dataframe(
                            terms_df,
                            column_config={
                                "Bobot TF-IDF": st.column_config.ProgressColumn(
                                    "Bobot TF-IDF",
                                    format="%.3f",
                                    min_value=0.0,
                                    max_value=float(max(s for _, s in top_terms)) * 1.15,
                                )
                            },
                            hide_index=True,
                            alt="Tabel frase yang paling sering direplikasi",
                        )
                    else:
                        st.caption("Tidak ada frase berulang yang signifikan.")

            with st.container(border=True):
                st.subheader(f"Pasangan unggahan terindikasi terkoordinasi (kemiripan ≥ {int(sim_threshold * 100)}%)")
                if suspicious_pairs:
                    pairs_df = pd.DataFrame([
                        {
                            "Pasangan": f"P{p['post_a_id']:02d} ↔ P{p['post_b_id']:02d}",
                            "Kemiripan": p["similarity_percentage"],
                            "Klasifikasi": p["coordination_level"],
                            "Teks unggahan A": p["text_a"],
                            "Teks unggahan B": p["text_b"],
                        }
                        for p in suspicious_pairs
                    ])
                    st.dataframe(
                        pairs_df,
                        column_config={
                            "Pasangan": st.column_config.TextColumn("Pasangan", pinned=True),
                            "Kemiripan": st.column_config.ProgressColumn(
                                "Tingkat kemiripan",
                                format="%.1f%%",
                                min_value=0,
                                max_value=100,
                            ),
                        },
                        hide_index=True,
                        alt="Tabel pasangan unggahan dengan kemiripan di atas ambang batas",
                    )
                else:
                    st.caption(
                        f"Tidak ditemukan pasangan unggahan yang melampaui ambang batas kemiripan {int(sim_threshold * 100)}%."
                    )


# ==============================================================================
# TAB 3: LEMBAR RINGKASAN INTELIJEN & PROTOKOL MITIGASI
# ==============================================================================
with tab3:
    batch = st.session_state.get("last_batch_result")
    single = st.session_state.get("last_single_result")

    if not batch and not single:
        st.info(
            "Jalankan analisis teks pada tab **Inspeksi risiko kognitif** atau muat dataset pada tab **Deteksi jaringan astroturfing** untuk menyusun lembar ringkasan intelijen.",
            title="Belum ada data analisis aktif",
            icon=":material/info:",
        )
    else:
        is_high_risk = (batch and batch["metrics"]["astroturfing_detected"]) or (
            single and single["analysis"]["overall_risk_score"] >= 65
        )

        if batch:
            m = batch["metrics"]
            thresh = int(batch["threshold"] * 100)
            threat_status = (
                ":red-badge[:material/gpp_maybe: KRITIS — Operasi Astroturfing Terkoordinasi]"
                if m["astroturfing_detected"]
                else ":green-badge[:material/verified_user: NOMINAL — Sebaran Narasi Organik]"
            )
            exec_summary = (
                m.get("detection_reason")
                or (
                    f"Teridentifikasi amplifikasi narasi terkoordinasi pada **{m['involved_posts_count']} dari {m['total_posts']} unggahan** "
                    f"(**{m['amplification_ratio']}%**) yang melampaui ambang kemiripan **{thresh}%**, dengan **{m['high_similarity_pairs_count']} pasang** duplikasi template."
                )
            )
        else:
            a = single["analysis"]
            cat = a["risk_category"]
            score = a["overall_risk_score"]
            badge_prefix = ":red-badge" if cat == "Bahaya" else (":orange-badge" if cat == "Waspada" else ":green-badge")
            threat_status = f"{badge_prefix}[Status: {cat.upper()} — Indeks Risiko Kognitif {score}%]"
            exec_summary = a["summary"]

        # Header + Tombol Unduh
        with st.container(horizontal=True, horizontal_alignment="distribute", vertical_alignment="center"):
            st.subheader("Lembar ringkasan intelijen & protokol mitigasi")
            report_txt = format_plain_dossier(single, batch)
            st.download_button(
                label="Unduh laporan (.txt)",
                data=report_txt,
                file_name="CogniShield_Laporan_Intelijen.txt",
                mime="text/plain",
                type="primary",
                icon=":material/download:",
            )

        # Bagian 1: Ringkasan Eksekutif (menggunakan native st.table key-value sesuai SKILL.md)
        with st.container(border=True):
            st.markdown("#### 1. Ringkasan eksekutif")
            summary_kv = {
                "Status ancaman": threat_status,
                "Protokol aktif": (
                    ":primary-badge[:material/gpp_bad: Protokol Merah — Intervensi Aktif]"
                    if is_high_risk
                    else ":gray-badge[:material/visibility: Protokol Standar — Pemantauan Pasif]"
                ),
                "Evaluasi diagnostik": exec_summary,
            }
            if single and single["analysis"]["detected_flags"]:
                flags_str = " ".join([
                    f"`{f['keyword']}` ({f['dimensi']})" for f in single["analysis"]["detected_flags"]
                ])
                summary_kv["Indikator leksikal"] = flags_str
            if batch and batch["top_terms"]:
                terms_str = ", ".join([f"`{t[0]}` ({t[1]})" for t in batch["top_terms"][:5]])
                summary_kv["Slogan direplikasi"] = terms_str

            st.table(summary_kv, border="horizontal", alt="Ringkasan eksekutif penilaian ancaman")

        # Bagian 2 & 3 berdampingan dengan tinggi seragam
        col_vec, col_proto = st.columns([1, 1.25], gap="medium")

        with col_vec:
            with st.container(border=True, height="stretch"):
                st.markdown("#### 2. Vektor risiko kognitif")
                if single:
                    dims = single["analysis"]["dimensions"]
                    vec_df = pd.DataFrame([
                        {
                            "Dimensi risiko": k,
                            "Skor": v,
                            "Tingkat": "Tinggi" if v >= 65 else ("Sedang" if v >= 30 else "Rendah"),
                        }
                        for k, v in dims.items()
                    ])
                    st.dataframe(
                        vec_df,
                        column_config={
                            "Skor": st.column_config.ProgressColumn(
                                "Skor (0–100%)",
                                format="%.1f%%",
                                min_value=0,
                                max_value=100,
                            ),
                        },
                        hide_index=True,
                        alt="Tabel skor empat dimensi risiko kognitif",
                    )
                elif batch:
                    m = batch["metrics"]
                    st.table(
                        {
                            "Total unggahan dianalisis": f"**{m['total_posts']}** unggahan",
                            "Unggahan bermuatan pemicu buzzer": f"**{m.get('hostile_posts_count', m['involved_posts_count'])}** unggahan (**{m.get('hostile_ratio', m['amplification_ratio'])}%**)",
                            "Vektor kampanye dominan": f"**{m.get('dominant_campaign_vector', 'Campuran')}**",
                            "Pasangan terkoordinasi (kloning / konteks)": f"**{m['high_similarity_pairs_count']}** pasang (puncak **{round(m['max_pairwise_similarity']*100, 1)}%**)",
                        },
                        border="horizontal",
                        alt="Metrik jaringan kampanye astroturfing",
                    )

        with col_proto:
            with st.container(border=True, height="stretch"):
                st.markdown("#### 3. Protokol tindakan taktis")
                if is_high_risk:
                    st.table(
                        {
                            "01 · Audit akun": "Tandai akun dalam klaster kemiripan ≥85% untuk pemeriksaan aktivitas bot.",
                            "02 · Pembatasan laju": "Terapkan pembatasan distribusi pada slogan atau tagar yang direplikasi secara mekanik.",
                            "03 · Kontra-narasi": "Rilis klarifikasi berbasis data resmi (*prebunking*) sebelum narasi mendominasi.",
                            "04 · Forensik jaringan": "Simpan jejak waktu dan relasi antar-unggah untuk pemetaan aktor kampanye.",
                        },
                        border="horizontal",
                        alt="Daftar protokol mitigasi aktif",
                    )
                else:
                    st.table(
                        {
                            "01 · Telemetri berkala": "Lanjutkan pemantauan sentimen dan fluktuasi volume selama 6–12 jam ke depan.",
                            "02 · Radar kata kunci": "Masukkan kata kunci dominan ke dalam daftar pantau deteksi dini.",
                            "03 · Komunikasi publik": "Pertahankan saluran informasi resmi secara transparan dan terjadwal.",
                        },
                        border="horizontal",
                        alt="Daftar protokol pemantauan standar",
                    )
