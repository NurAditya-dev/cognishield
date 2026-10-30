"""
Modul Multi-Dimensional Cognitive Risk Index (risk_scoring.py)
CogniShield: Mengukur Indeks Risiko Kognitif (0 - 100%) dengan 4 Dimensi Analisis:
1. Sensasionalitas & Urgensi Semu (Sensationalism & Fake Urgency)
2. Provokasi & Polarisasi Sosial (Provocation & Divisiveness)
3. Pembingkaian Manipulasi & Konspirasi (Conspiracy & Narrative Framing)
4. Toksisitas Emosional & Agresi (Emotional Toxicity & Aggression)
"""

import re
from typing import Dict, List, Any, Tuple
from .preprocessing import preprocess_text


# Leksikon Indikator Kognitif Bahasa Indonesia (Unik & Ternormalisasi)
LEXICON_SENSATIONALISM = list(dict.fromkeys([
    "viralkan", "sebarkan", "sebar luaskan", "wajib tahu", "jangan kaget",
    "bongkar habis", "terbongkar", "gawat darurat", "parah banget", "gempar",
    "menghebohkan", "bikin syok", "jangan diam", "awas tertipu", "darurat",
    "buka mata", "semua harus tahu", "terkuak fakta", "viral", "hancur lebur",
    "heboh", "luar biasa parah", "detik detik", "terbaru menggemparkan",
    "akhirnya terkuak", "borok", "aib", "skandal besar", "fakta mengejutkan",
    "kuliti habis", "dikuliti habis", "terciduk", "bukti nyata", "bikin geger",
    "pecah", "detik-detik", "mendadak", "auto", "ngeri banget", "blunder fatal",
    "ketar-ketir", "ketar ketir", "panik", "skakmat", "tamparan keras",
    "rata dengan tanah", "krisis besar"
]))

LEXICON_PROVOCATION = list(dict.fromkeys([
    "antek", "khianat", "pengkhianat", "rezim", "musuh bersama", "hancurkan",
    "laknat", "biadab", "sesat", "goblok", "tolol", "dungu", "fitnah",
    "bajingan", "bangsat", "kadrun", "cebong", "penjilat", "komunis",
    "antek asing", "antek aseng", "musnahkan", "usir", "tenggelamkan",
    "haram jadah", "iblis", "murtad", "penipu", "pemberontak", "boikot",
    "serbu", "geruduk", "jangan kasih panggung", "viralkan biar kapok",
    "tandai mukanya", "bubarkan", "turunkan", "lawan", "kawal sampai tuntas",
    "dikawal sampai", "buka mata kalian", "jangan mau dibodohi",
    "sampai kapan kita diam", "darah mendidih", "menginjak-injak",
    "menginjak injak", "pelecehan terhadap", "merusak moral", "perusak moral",
    "adu domba", "pecah belah", "pengkhianat bangsa", "musuh rakyat",
    "ancaman nyata"
]))

LEXICON_CONSPIRACY_FRAMING = list(dict.fromkeys([
    "media bungkam", "media bayaran", "disembunyikan", "fakta sebenarnya",
    "agenda tersembunyi", "rekayasa", "skenario jahat", "agenda global",
    "konspirasi", "cuci otak", "fakta ditutupi", "pembodohan massal",
    "disetir", "didalangi", "ada konspirasi", "jangan mau dibodohi",
    "dalang utama", "fakta yang ditutup tutupi", "ditutup-tutupi",
    "ditutup tutupi", "kambing hitam", "sandiwara", "fufufafa",
    "saya menerima laporan", "saya dapat laporan", "pengalihan isu",
    "settingan", "skenario besar", "dikondisikan", "operasi senyap",
    "agenda terselubung", "ada udang di balik batu", "framing jahat",
    "pembingkaian jahat", "propaganda", "dalang", "aktor intelektual",
    "aktor intelektualnya", "oligarki", "boneka", "cukong", "bekingan",
    "pesanan sponsor", "mafia", "kartel", "tangan tak terlihat",
    "ditunggangi", "permainan elit", "dibungkam", "kriminalisasi",
    "tebang pilih", "pesanan pusat", "menggiring opini"
]))

LEXICON_TOXICITY = list(dict.fromkeys([
    "benci", "jijik", "hina", "najis", "muntah", "muak", "sampah", "mati kau",
    "pengecut", "biadab", "hancur", "perusak", "busuk", "laknat", "celaka",
    "bodoh sekali", "gak guna", "tidak guna", "sampah masyarakat", "kutuk",
    "terkutuk", "boti", "bangsat", "iblis", "setan", "maling", "pengkhianat",
    "penipu", "pembohong", "buzzerRp", "buzzerrp", "pendengung", "cebong",
    "kadrun", "kampret", "bayaran", "pasukan nasi bungkus", "penjilat",
    "antek", "kacung", "ternak", "SDM rendah", "sdm rendah", "IQ jongkok",
    "iq jongkok", "otak udang", "gagal paham", "kurang literasi", "dungu",
    "dongo", "tolol", "halu", "buta hati", "mental pengemis", "munafik",
    "playing victim", "pencitraan", "badut politik", "beban negara",
    "bermuka dua", "tidak tahu malu"
]))


class CognitiveRiskScorer:
    """
    Mesin Penilai Indeks Risiko Kognitif Multi-Dimensi (CogniShield Risk Index).
    Menghasilkan skor komprehensif 0 - 100% dan kategori 'Aman', 'Waspada', 'Bahaya'.
    """

    def __init__(
        self,
        weight_sensationalism: float = 0.25,
        weight_provocation: float = 0.30,
        weight_conspiracy: float = 0.25,
        weight_toxicity: float = 0.20
    ):
        self.weights = {
            "sensationalism": weight_sensationalism,
            "provocation": weight_provocation,
            "conspiracy": weight_conspiracy,
            "toxicity": weight_toxicity
        }

    def _calculate_dimension_score(
        self,
        text_cleaned: str,
        raw_lower: str,
        lexicon: List[str],
        base_factor: float = 28.0
    ) -> Tuple[float, List[str]]:
        """
        Menghitung skor dimensi berdasarkan deteksi kecocokan leksikon kata kunci dan intensitas.
        Mencocokkan secara case-insensitive baik pada teks yang telah dinormalisasi maupun teks asli.
        """
        detected = []
        raw_count = 0

        for keyword in lexicon:
            kw_lower = keyword.lower().strip()
            kw_norm = kw_lower.replace("-", " ")

            pattern_raw = r'\b' + re.escape(kw_lower) + r'\b' if ' ' not in kw_lower else re.escape(kw_lower)
            pattern_norm = r'\b' + re.escape(kw_norm) + r'\b' if ' ' not in kw_norm else re.escape(kw_norm)

            matches_norm = len(re.findall(pattern_norm, text_cleaned, flags=re.IGNORECASE))
            matches_raw = len(re.findall(pattern_raw, raw_lower, flags=re.IGNORECASE))
            matches = max(matches_norm, matches_raw)

            if matches > 0:
                if kw_lower not in [d.lower() for d in detected]:
                    detected.append(keyword)
                raw_count += matches

        score = min(100.0, raw_count * base_factor)
        return round(score, 1), detected

    def _assess_stylistic_urgency(self, raw_text: str) -> float:
        """
        Menilai gaya tipografi manipulatif: HURUF BESAR BERLEBIH dan tanda seru.
        """
        if not raw_text:
            return 0.0

        alpha_chars = [c for c in raw_text if c.isalpha()]
        if len(alpha_chars) >= 10:
            upper_ratio = sum(1 for c in alpha_chars if c.isupper()) / len(alpha_chars)
        else:
            upper_ratio = 0.0

        caps_penalty = 30.0 if upper_ratio > 0.40 else (15.0 if upper_ratio > 0.25 else 0.0)

        double_excl = len(re.findall(r'!{2,}', raw_text))
        single_excl = 1 if '!' in raw_text and double_excl == 0 else 0
        exclamation_penalty = min(30.0, (double_excl * 15.0) + (single_excl * 6.0))

        return min(50.0, caps_penalty + exclamation_penalty)

    def analyze_text(self, raw_text: str) -> Dict[str, Any]:
        """
        Menganalisis teks masukan dan menghasilkan laporan risiko kognitif lengkap.
        """
        if not raw_text or not raw_text.strip():
            return {
                "overall_risk_score": 0.0,
                "risk_category": "Aman",
                "risk_color": "#28a745",
                "dimensions": {
                    "Sensasionalitas & Urgensi": 0.0,
                    "Provokasi & Polarisasi": 0.0,
                    "Manipulasi & Konspirasi": 0.0,
                    "Toksisitas Emosional": 0.0
                },
                "detected_flags": [],
                "stylistic_cues": {"caps_ratio": 0.0, "excess_exclamation": 0},
                "summary": "Teks kosong atau tidak mengandung narasi yang dapat dinilai."
            }

        cleaned_text = preprocess_text(raw_text, remove_url=True, remove_emoji=True, to_lower=True)
        raw_lower = raw_text.lower()

        # 1. Sensasionalitas & Urgensi
        sens_score, sens_flags = self._calculate_dimension_score(cleaned_text, raw_lower, LEXICON_SENSATIONALISM, base_factor=26.0)
        style_urgency = self._assess_stylistic_urgency(raw_text)
        sens_score = min(100.0, sens_score + (style_urgency * 0.4))

        # 2. Provokasi & Polarisasi
        prov_score, prov_flags = self._calculate_dimension_score(cleaned_text, raw_lower, LEXICON_PROVOCATION, base_factor=30.0)

        # 3. Manipulasi & Narasi Konspirasi
        consp_score, consp_flags = self._calculate_dimension_score(cleaned_text, raw_lower, LEXICON_CONSPIRACY_FRAMING, base_factor=32.0)

        # 4. Toksisitas Emosional
        tox_score, tox_flags = self._calculate_dimension_score(cleaned_text, raw_lower, LEXICON_TOXICITY, base_factor=28.0)

        weighted_score = (
            sens_score * self.weights["sensationalism"] +
            prov_score * self.weights["provocation"] +
            consp_score * self.weights["conspiracy"] +
            tox_score * self.weights["toxicity"]
        )
        max_dim_score = max(sens_score, prov_score, consp_score, tox_score)

        combined_score = (0.55 * weighted_score) + (0.45 * max_dim_score)
        overall_score = round(min(100.0, max(0.0, combined_score)), 1)

        if overall_score < 25.0 and max_dim_score < 50.0:
            category = "Aman"
            color = "#28a745"
            summary_desc = "Narasi berada pada kategori risiko rendah. Tidak ditemukan pola provokasi agresif, amplifikasi kebencian, atau urgensi artifisial."
        elif overall_score < 60.0 and max_dim_score < 85.0:
            category = "Waspada"
            color = "#fd7e14"
            summary_desc = "Narasi menunjukkan indikasi pembingkaian emosional, konspirasi, atau retorika yang berpotensi memicu polarisasi opini publik."
        else:
            category = "Bahaya"
            color = "#dc3545"
            summary_desc = "Tingkat risiko kognitif tinggi! Terdeteksi muatan provokasi tajam, pembingkaian manipulatif, toksisitas, atau ajakan amplifikasi agresif."

        all_flags = []
        for f in sens_flags:
            all_flags.append({"keyword": f, "dimensi": "Sensasionalitas/Urgensi"})
        for f in prov_flags:
            all_flags.append({"keyword": f, "dimensi": "Provokasi/Polarisasi"})
        for f in consp_flags:
            all_flags.append({"keyword": f, "dimensi": "Manipulasi/Konspirasi"})
        for f in tox_flags:
            all_flags.append({"keyword": f, "dimensi": "Toksisitas Emosional"})

        return {
            "overall_risk_score": overall_score,
            "risk_category": category,
            "risk_color": color,
            "dimensions": {
                "Sensasionalitas & Urgensi": round(sens_score, 1),
                "Provokasi & Polarisasi": round(prov_score, 1),
                "Manipulasi & Konspirasi": round(consp_score, 1),
                "Toksisitas Emosional": round(tox_score, 1)
            },
            "detected_flags": all_flags,
            "raw_text_length": len(raw_text),
            "summary": summary_desc
        }
