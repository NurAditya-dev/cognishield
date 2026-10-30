"""
Modul Deteksi Astroturfing & Koordinasi Kampanye (Astroturfing Detection)
CogniShield: Menggabungkan Kemiripan Leksikal (TF-IDF + Karakter N-Gram)
dengan Kesamaan Konteks Vektor Kognitif & Deteksi Sinyal Buzzer.
"""

from typing import Dict, List, Tuple, Any, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .preprocessing import preprocess_text
from .risk_scoring import CognitiveRiskScorer


# Stopwords Bahasa Indonesia esensial untuk pembersihan TF-IDF
INDONESIAN_STOPWORDS = [
    "yang", "di", "dan", "itu", "dengan", "untuk", "ini", "dari", "dalam", "akan",
    "pada", "juga", "saya", "ke", "karena", "tersebut", "bisa", "ada", "mereka",
    "kita", "kami", "oleh", "saat", "setelah", "sudah", "para", "atau", "hanya",
    "seperti", "lebih", "secara", "sebagai", "dapat", "ia", "namun", "sampai",
    "buat", "sama", "kalau", "tidak", "lagi", "saja", "udah", "banget", "cuma"
]


class AstroturfingDetector:
    """
    Mesin pendeteksi astroturfing dan narasi terkoordinasi (Coordinated Inauthentic Behavior / CIB).
    Mendeteksi baik:
    1. Kloning / Copy-Paste Bot (kemiripan leksikal TF-IDF kata & karakter)
    2. Kerumunan Buzzer Terkoordinasi (kesamaan konteks vektor risiko kognitif & kepadatan narasi manipulatif)
    """

    def __init__(
        self,
        ngram_range: Tuple[int, int] = (1, 2),
        min_df: int = 1,
        stop_words: Optional[List[str]] = None
    ):
        self.ngram_range = ngram_range
        self.min_df = min_df
        self.stop_words = stop_words or INDONESIAN_STOPWORDS
        self.word_vectorizer = TfidfVectorizer(
            ngram_range=self.ngram_range,
            min_df=self.min_df,
            stop_words=self.stop_words,
            sublinear_tf=True
        )
        self.char_vectorizer = TfidfVectorizer(
            analyzer="char_wb",
            ngram_range=(3, 5),
            min_df=self.min_df,
            sublinear_tf=True
        )
        self.risk_scorer = CognitiveRiskScorer()
        self._last_post_profiles: List[Dict[str, Any]] = []

    def _compute_contextual_similarity(self, raw_texts: List[str]) -> Tuple[np.ndarray, List[Dict[str, Any]]]:
        """
        Membangun profil vektor risiko 4-dimensi tiap unggahan dan menghitung kemiripan
        konteks antar-unggahan yang sama-sama membawa muatan manipulatif/buzzer.
        """
        n = len(raw_texts)
        profiles = [self.risk_scorer.analyze_text(t) for t in raw_texts]
        self._last_post_profiles = profiles

        # Matriks vektor 4 dimensi (N x 4)
        dim_keys = [
            "Sensasionalitas & Urgensi",
            "Provokasi & Polarisasi",
            "Manipulasi & Konspirasi",
            "Toksisitas Emosional"
        ]
        vec_matrix = np.zeros((n, 4), dtype=float)
        risk_scores = np.zeros(n, dtype=float)
        flag_sets = []

        for idx, prof in enumerate(profiles):
            dims = prof["dimensions"]
            vec_matrix[idx] = [dims[k] for k in dim_keys]
            risk_scores[idx] = prof["overall_risk_score"]
            flag_sets.append(set(f["keyword"].lower() for f in prof["detected_flags"]))

        # Cosine similarity antar vektor dimensi kognitif (N x N)
        norms = np.linalg.norm(vec_matrix, axis=1, keepdims=True)
        safe_norms = np.where(norms == 0, 1.0, norms)
        normalized_vecs = vec_matrix / safe_norms
        dim_cos = np.dot(normalized_vecs, normalized_vecs.T)

        # Bobot intensitas risiko gabungan (agar teks netral/0% tidak dianggap mirip secara kontekstual)
        intensity = np.clip(risk_scores / 45.0, 0.0, 1.0)
        joint_intensity = np.outer(intensity, intensity)

        # Bonus kesamaan kata kunci leksikon / dimensi dominan
        context_sim = dim_cos * joint_intensity

        for i in range(n):
            for j in range(i + 1, n):
                shared_flags = flag_sets[i].intersection(flag_sets[j])
                if shared_flags:
                    bonus = min(0.30, len(shared_flags) * 0.15)
                    context_sim[i, j] = min(1.0, context_sim[i, j] + bonus)
                    context_sim[j, i] = context_sim[i, j]

        np.fill_diagonal(context_sim, 1.0)
        return np.clip(context_sim, 0.0, 1.0), profiles

    def fit_transform_similarity(
        self,
        texts: List[str],
        preprocess: bool = True
    ) -> Tuple[np.ndarray, List[str]]:
        """
        Melakukan vectorization hibrida (TF-IDF Kata + Karakter N-gram + Konteks Kognitif)
        dan menghitung matriks kemiripan gabungan N x N.
        """
        if not texts or len(texts) == 0:
            self._last_post_profiles = []
            return np.array([[]]), []

        if preprocess:
            processed_texts = [preprocess_text(t) for t in texts]
        else:
            processed_texts = [t.strip() for t in texts]

        non_empty = [t for t in processed_texts if len(t) > 0]
        n = len(texts)
        if not non_empty:
            self._last_post_profiles = []
            return np.zeros((n, n)), processed_texts

        # 1. Kemiripan leksikal kata (TF-IDF word n-grams)
        tfidf_word = self.word_vectorizer.fit_transform(processed_texts)
        word_sim = cosine_similarity(tfidf_word, tfidf_word)

        # 2. Kemiripan morfologi/karakter (menangkap variasi kata/slang/imbuhan)
        tfidf_char = self.char_vectorizer.fit_transform(processed_texts)
        char_sim = cosine_similarity(tfidf_char, tfidf_char)

        lexical_sim = (0.70 * word_sim) + (0.30 * char_sim)

        # 3. Kemiripan konteks vektor kognitif (menangkap narasi buzzer sejenis yang diparafrase)
        context_sim, _ = self._compute_contextual_similarity(texts)

        # Kombinasi adaptif: ambil nilai terkuat antara kemiripan copy-paste vs koordinasi konteks
        hybrid_sim = np.maximum(
            lexical_sim,
            (0.42 * lexical_sim) + (0.58 * context_sim)
        )

        np.fill_diagonal(hybrid_sim, 1.0)
        return np.clip(hybrid_sim, 0.0, 1.0), processed_texts

    def find_suspicious_pairs(
        self,
        similarity_matrix: np.ndarray,
        raw_texts: List[str],
        threshold: float = 0.55
    ) -> List[Dict[str, Any]]:
        """
        Mendeteksi pasangan unggahan yang memiliki kemiripan di atas ambang batas (threshold),
        baik karena kloning teks maupun kesamaan pola framing buzzer.
        """
        n = similarity_matrix.shape[0]
        suspicious_pairs = []
        profiles = self._last_post_profiles if len(self._last_post_profiles) == n else [
            self.risk_scorer.analyze_text(t) for t in raw_texts
        ]

        for i in range(n):
            for j in range(i + 1, n):
                score = float(similarity_matrix[i, j])
                if score >= threshold:
                    dom_i = max(profiles[i]["dimensions"], key=profiles[i]["dimensions"].get)
                    dom_j = max(profiles[j]["dimensions"], key=profiles[j]["dimensions"].get)

                    if score >= 0.88:
                        level = "Identik / Kloning Bot"
                    elif score >= 0.72:
                        level = "Sangat Mirip / Template Buzzer"
                    elif dom_i == dom_j and profiles[i]["overall_risk_score"] >= 25:
                        level = f"Koordinasi Konteks ({dom_i})"
                    else:
                        level = "Kemiripan Narasi Signifikan"

                    suspicious_pairs.append({
                        "post_a_id": i + 1,
                        "post_b_id": j + 1,
                        "similarity_score": round(score, 4),
                        "similarity_percentage": round(score * 100, 1),
                        "coordination_level": level,
                        "text_a": raw_texts[i],
                        "text_b": raw_texts[j]
                    })

        suspicious_pairs.sort(key=lambda x: x["similarity_score"], reverse=True)
        return suspicious_pairs

    def calculate_coordination_metrics(
        self,
        similarity_matrix: np.ndarray,
        threshold: float = 0.55
    ) -> Dict[str, Any]:
        """
        Menghitung metrik agregat kampanye astroturfing secara holistik:
        mengukur baik duplikasi pasangan maupun kepadatan serangan buzzer (cognitive hostility).
        """
        n = similarity_matrix.shape[0]
        if n <= 1:
            return {
                "total_posts": n,
                "high_similarity_pairs_count": 0,
                "involved_posts_count": 0,
                "amplification_ratio": 0.0,
                "hostile_posts_count": 0,
                "hostile_ratio": 0.0,
                "dominant_campaign_vector": "Tidak ada",
                "mean_pairwise_similarity": 0.0,
                "max_pairwise_similarity": 0.0,
                "campaign_risk_score": 0.0,
                "astroturfing_detected": False,
                "detection_reason": "Data kurang dari 2 unggahan."
            }

        triu_indices = np.triu_indices(n, k=1)
        pairwise_scores = similarity_matrix[triu_indices]

        mean_sim = float(np.mean(pairwise_scores)) if len(pairwise_scores) > 0 else 0.0
        max_sim = float(np.max(pairwise_scores)) if len(pairwise_scores) > 0 else 0.0

        involved_indices = set()
        suspicious_pairs_count = 0
        for i, j in zip(*triu_indices):
            if similarity_matrix[i, j] >= threshold:
                involved_indices.add(i)
                involved_indices.add(j)
                suspicious_pairs_count += 1

        # Evaluasi kepadatan sinyal buzzer per unggahan dari profil risiko kognitif
        profiles = self._last_post_profiles
        hostile_indices = set()
        vector_counts: Dict[str, int] = {}

        if profiles and len(profiles) == n:
            for idx, prof in enumerate(profiles):
                if prof["overall_risk_score"] >= 22.0 or len(prof["detected_flags"]) >= 1:
                    hostile_indices.add(idx)
                    dom_vec = max(prof["dimensions"], key=prof["dimensions"].get)
                    if prof["dimensions"][dom_vec] > 0:
                        vector_counts[dom_vec] = vector_counts.get(dom_vec, 0) + 1

        hostile_count = len(hostile_indices)
        hostile_ratio = round((hostile_count / n) * 100, 1)
        dominant_vector = max(vector_counts, key=vector_counts.get) if vector_counts else "Campuran / Umum"

        # Unggahan yang terindikasi bagian dari operasi adalah gabungan klaster kemiripan & sinyal agresif
        combined_involved = involved_indices.union(hostile_indices) if suspicious_pairs_count >= 2 else involved_indices
        involved_count = len(combined_involved) if len(combined_involved) > 0 else len(involved_indices)
        cluster_ratio = round((len(involved_indices) / n) * 100, 1)
        amplification_ratio = round(max(cluster_ratio, hostile_ratio * 0.85 if suspicious_pairs_count >= 1 else cluster_ratio), 1)

        # Skor risiko kampanye gabungan (0 - 100)
        risk_score = min(
            100.0,
            (cluster_ratio * 0.40) + (hostile_ratio * 0.45) + (mean_sim * 100 * 0.15)
        )

        astroturfing_detected = (
            cluster_ratio >= 20.0
            or suspicious_pairs_count >= 3
            or hostile_ratio >= 35.0
        )

        if cluster_ratio >= 25.0 and hostile_ratio >= 35.0:
            reason = (
                f"Terdeteksi kombinasi kloning/kesamaan pola ({suspicious_pairs_count} pasang) "
                f"dan konsentrasi narasi manipulatif tinggi ({hostile_ratio}% unggahan bermuatan {dominant_vector})."
            )
        elif hostile_ratio >= 35.0:
            reason = (
                f"Terdeteksi operasi kerumunan buzzer (swarming): {hostile_count} dari {n} unggahan ({hostile_ratio}%) "
                f"mengandung indikator leksikon manipulatif terkoordinasi (dominan: {dominant_vector})."
            )
        elif astroturfing_detected:
            reason = (
                f"Terdeteksi replikasi template narasi pada {len(involved_indices)} unggahan "
                f"({suspicious_pairs_count} pasang melampaui ambang kemiripan)."
            )
        else:
            reason = "Sebaran narasi cenderung organik dan tidak menunjukkan konsentrasi pemicu manipulatif."

        return {
            "total_posts": n,
            "high_similarity_pairs_count": suspicious_pairs_count,
            "involved_posts_count": max(len(involved_indices), hostile_count if astroturfing_detected else len(involved_indices)),
            "amplification_ratio": amplification_ratio,
            "hostile_posts_count": hostile_count,
            "hostile_ratio": hostile_ratio,
            "dominant_campaign_vector": dominant_vector,
            "mean_pairwise_similarity": round(mean_sim, 4),
            "max_pairwise_similarity": round(max_sim, 4),
            "campaign_risk_score": round(risk_score, 1),
            "astroturfing_detected": astroturfing_detected,
            "detection_reason": reason
        }

    def get_top_repetitive_keywords(
        self,
        texts: List[str],
        top_n: int = 10
    ) -> List[Tuple[str, float]]:
        """
        Mengekstrak kata kunci atau frase dominan yang sering direplikasi.
        """
        if not texts:
            return []

        processed = [preprocess_text(t) for t in texts]
        non_empty = [t for t in processed if t.strip()]
        if not non_empty:
            return []

        try:
            tfidf = TfidfVectorizer(
                ngram_range=(1, 2),
                stop_words=self.stop_words,
                max_features=60
            )
            matrix = tfidf.fit_transform(non_empty)
            scores = np.asarray(matrix.mean(axis=0)).ravel()
            features = tfidf.get_feature_names_out()

            ranked = sorted(zip(features, scores), key=lambda x: x[1], reverse=True)
            return [(term, round(float(score), 4)) for term, score in ranked[:top_n]]
        except Exception:
            return []
