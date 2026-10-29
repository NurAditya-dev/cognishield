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


# Leksikon Indikator Kognitif Bahasa Indonesia
LEXICON_SENSATIONALISM = [
    "viralkan", "sebarkan", "sebar luaskan", "wajib tahu", "jangan kaget",
    "bongkar habis", "terbongkar", "gawat darurat", "parah banget", "gempar",
    "menghebohkan", "bikin syok", "jangan diam", "awas tertipu", "darurat",
    "buka mata", "semua harus tahu", "terkuak fakta", "viral", "hancur lebur",
    "heboh", "luar biasa parah", "detik detik", "terbaru menggemparkan"
]

LEXICON_PROVOCATION = [
    "antek", "khianat", "pengkhianat", "rezim", "musuh bersama", "hancurkan",
    "laknat", "biadab", "sesat", "goblok", "tolol", "dungu", "fitnah",
    "bajingan", "bangsat", "kadrun", "cebong", "penjilat", "komunis",
    "antek asing", "antek aseng", "musnahkan", "usir", "tenggelamkan",
    "haram jadah", "iblis", "murtad", "penipu", "pemberontak"
]

LEXICON_CONSPIRACY_FRAMING = [
    "media bungkam", "media bayaran", "disembunyikan", "fakta sebenarnya",
    "agenda tersembunyi", "rekayasa", "skenario jahat", "agenda global",
    "konspirasi", "cuci otak", "fakta ditutupi", "pembodohan massal",
    "disetir", "didalangi", "ada konspirasi", "jangan mau dibodohi",
    "dalang utama", "fakta yang ditutup tutupi", "kambing hitam", "sandiwara"
]

LEXICON_TOXICITY = [
    "benci", "jijik", "hina", "najis", "muntah", "muak", "sampah", "mati kau",
    "pengecut", "biadab", "hancur", "perusak", "busuk", "laknat", "celaka",
    "bodoh sekali", "gak guna", "sampah masyarakat", "kutuk", "terkutuk"
]


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
        text_lower: str,
        lexicon: List[str],
        base_factor: float = 25.0
    ) -> Tuple[float, List[str]]:
        """
        Menghitung skor dimensi berdasarkan deteksi kecocokan leksikon kata kunci dan intensitas.
        """
        detected = []
        raw_count = 0

        for keyword in lexicon:
            # Gunakan regex boundary atau substring frase
            pattern = r'\b' + re.escape(keyword) + r'\b' if ' ' not in keyword else re.escape(keyword)
            matches = len(re.findall(pattern, text_lower))
            if matches > 0:
                detected.append(keyword)
                raw_count += matches

        # Penilaian asimtotik skor (0 - 100)
        # 1 match ~ 28-35, 2 match ~ 55-65, 3+ match ~ 80-100
        score = min(100.0, raw_count * base_factor)
        return round(score, 1), detected

    def _assess_stylistic_urgency(self, raw_text: str) -> float:
        """
        Menilai gaya tipografi manipulatif: HURUF BESAR BERLEBIH dan tanda seru ganda.
        """
        if not raw_text:
            return 0.0

        # Rasio huruf kapital
        alpha_chars = [c for c in raw_text if c.isalpha()]
        if len(alpha_chars) >= 10:
            upper_ratio = sum(1 for c in alpha_chars if c.isupper()) / len(alpha_chars)
        else:
            upper_ratio = 0.0

        caps_penalty = 30.0 if upper_ratio > 0.40 else (15.0 if upper_ratio > 0.25 else 0.0)

        # Tanda seru ganda (misal: !!, !!!)
        exclamation_count = len(re.findall(r'!{2,}', raw_text))
        exclamation_penalty = min(30.0, exclamation_count * 15.0)

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

        # Pra-pemrosesan teks untuk pencocokan leksikon
        cleaned_text = preprocess_text(raw_text, remove_url=True, remove_emoji=True, to_lower=True)

        # 1. Sensasionalitas & Urgensi
        sens_score, sens_flags = self._calculate_dimension_score(cleaned_text, LEXICON_SENSATIONALISM, base_factor=25.0)
        style_urgency = self._assess_stylistic_urgency(raw_text)
        sens_score = min(100.0, sens_score + (style_urgency * 0.4))

        # 2. Provokasi & Polarisasi
        prov_score, prov_flags = self._calculate_dimension_score(cleaned_text, LEXICON_PROVOCATION, base_factor=30.0)

        # 3. Manipulasi & Narasi Konspirasi
        consp_score, consp_flags = self._calculate_dimension_score(cleaned_text, LEXICON_CONSPIRACY_FRAMING, base_factor=32.0)

        # 4. Toksisitas Emosional
        tox_score, tox_flags = self._calculate_dimension_score(cleaned_text, LEXICON_TOXICITY, base_factor=28.0)

        # Hitung skor agregat tertimbang dan perhatikan lonjakan dimensi kritis
        weighted_score = (
            sens_score * self.weights["sensationalism"] +
            prov_score * self.weights["provocation"] +
            consp_score * self.weights["conspiracy"] +
            tox_score * self.weights["toxicity"]
        )
        max_dim_score = max(sens_score, prov_score, consp_score, tox_score)
        
        # Kombinasi tertimbang dengan pembobotan dimensi kritis
        combined_score = (0.65 * weighted_score) + (0.35 * max_dim_score)
        overall_score = round(min(100.0, max(0.0, combined_score)), 1)

        # Penentuan Kategori Risiko Kognitif (Aman, Waspada, Bahaya)
        if overall_score < 30.0 and max_dim_score < 60.0:
            category = "Aman"
            color = "#28a745"  # Hijau
            summary_desc = "Narasi berada pada kategori risiko rendah. Tidak ditemukan pola provokasi agresif, amplifikasi kebencian, atau urgensi artifisial."
        elif overall_score < 65.0 and max_dim_score < 85.0:
            category = "Waspada"
            color = "#fd7e14"  # Oranye / Kuning Waspada
            summary_desc = "Narasi menunjukkan indikasi pembingkaian emosional atau retorika yang berpotensi memicu polarisasi opini publik."
        else:
            category = "Bahaya"
            color = "#dc3545"  # Merah
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
