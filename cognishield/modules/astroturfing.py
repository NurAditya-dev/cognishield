"""
Modul Deteksi Astroturfing & Koordinasi Kampanye (Astroturfing Detection)
CogniShield: Menggunakan TF-IDF Vectorizer dan Cosine Similarity (Scikit-Learn)
"""

from typing import Dict, List, Tuple, Any, Optional
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .preprocessing import preprocess_text


# Stopwords Bahasa Indonesia esensial untuk pembersihan TF-IDF
INDONESIAN_STOPWORDS = [
    "yang", "di", "dan", "itu", "dengan", "untuk", "ini", "dari", "dalam", "akan",
    "pada", "juga", "saya", "ke", "karena", "tersebut", "bisa", "ada", "mereka",
    "kita", "kami", "oleh", "saat", "setelah", "sudah", "para", "atau", "hanya",
    "seperti", "lebih", "secara", "sebagai", "dapat", "ia", "namun", "sampai"
]


class AstroturfingDetector:
    """
    Mesin pendeteksi astroturfing dan narasi terkoordinasi (coordinated inauthentic behavior).
    Mengukur kesamaan semantik dan leksikal antar teks menggunakan TF-IDF dan Cosine Similarity.
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
        self.vectorizer = TfidfVectorizer(
            ngram_range=self.ngram_range,
            min_df=self.min_df,
            stop_words=self.stop_words,
            sublinear_tf=True
        )

    def fit_transform_similarity(
        self,
        texts: List[str],
        preprocess: bool = True
    ) -> Tuple[np.ndarray, List[str]]:
        """
        Melakukan vectorization dan menghitung matriks cosine similarity N x N.
        
        Returns:
            similarity_matrix: matriks numpy float (N x N)
            processed_texts: teks yang telah dibersihkan
        """
        if not texts or len(texts) == 0:
            return np.array([[]]), []

        if preprocess:
            processed_texts = [preprocess_text(t) for t in texts]
        else:
            processed_texts = [t.strip() for t in texts]

        # Validasi jika semua teks kosong setelah pra-pemrosesan
        non_empty = [t for t in processed_texts if len(t) > 0]
        if not non_empty:
            n = len(texts)
            return np.zeros((n, n)), processed_texts

        # Bangun TF-IDF matrix
        tfidf_matrix = self.vectorizer.fit_transform(processed_texts)
        sim_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)

        # Pastikan diagonal bernilai 1.0
        np.fill_diagonal(sim_matrix, 1.0)
        return np.clip(sim_matrix, 0.0, 1.0), processed_texts

    def find_suspicious_pairs(
        self,
        similarity_matrix: np.ndarray,
        raw_texts: List[str],
        threshold: float = 0.65
    ) -> List[Dict[str, Any]]:
        """
        Mendeteksi pasangan unggahan yang memiliki kemiripan di atas ambang batas (threshold),
        yang mengindikasikan copy-paste narasi, bot buzzer, atau pola terkoordinasi.
        """
        n = similarity_matrix.shape[0]
        suspicious_pairs = []

        for i in range(n):
            for j in range(i + 1, n):
                score = float(similarity_matrix[i, j])
                if score >= threshold:
                    # Klasifikasi tingkat kesamaan
                    if score >= 0.90:
                        level = "Identik / Kloning Bot"
                    elif score >= 0.75:
                        level = "Sangat Mirip / Template Buzzer"
                    else:
                        level = "Kemiripan Signifikan"

                    suspicious_pairs.append({
                        "post_a_id": i + 1,
                        "post_b_id": j + 1,
                        "similarity_score": round(score, 4),
                        "similarity_percentage": round(score * 100, 2),
                        "coordination_level": level,
                        "text_a": raw_texts[i],
                        "text_b": raw_texts[j]
                    })

        # Urutkan berdasarkan kemiripan tertinggi
        suspicious_pairs.sort(key=lambda x: x["similarity_score"], reverse=True)
        return suspicious_pairs

    def calculate_coordination_metrics(
        self,
        similarity_matrix: np.ndarray,
        threshold: float = 0.65
    ) -> Dict[str, Any]:
        """
        Menghitung metrik agregat kampanye astroturfing.
        """
        n = similarity_matrix.shape[0]
        if n <= 1:
            return {
                "total_posts": n,
                "high_similarity_pairs_count": 0,
                "involved_posts_count": 0,
                "amplification_ratio": 0.0,
                "mean_pairwise_similarity": 0.0,
                "max_pairwise_similarity": 0.0,
                "campaign_risk_score": 0.0,
                "astroturfing_detected": False
            }

        # Dapatkan nilai off-diagonal (pasangan antar dokumen berbeda)
        triu_indices = np.triu_indices(n, k=1)
        pairwise_scores = similarity_matrix[triu_indices]

        mean_sim = float(np.mean(pairwise_scores)) if len(pairwise_scores) > 0 else 0.0
        max_sim = float(np.max(pairwise_scores)) if len(pairwise_scores) > 0 else 0.0

        # Hitung postingan yang terlibat dalam kemiripan di atas threshold
        involved_indices = set()
        suspicious_pairs_count = 0
        for i, j in zip(*triu_indices):
            if similarity_matrix[i, j] >= threshold:
                involved_indices.add(i)
                involved_indices.add(j)
                suspicious_pairs_count += 1

        involved_count = len(involved_indices)
        amplification_ratio = round((involved_count / n) * 100, 2)

        # Skor risiko kampanye astroturfing (0 - 100)
        # Berdasarkan proporsi unggahan terlibat dan rata-rata kemiripan pasangan mencurigakan
        risk_score = min(100.0, (amplification_ratio * 0.6) + (mean_sim * 100 * 0.4))
        astroturfing_detected = amplification_ratio >= 25.0 or suspicious_pairs_count >= 3

        return {
            "total_posts": n,
            "high_similarity_pairs_count": suspicious_pairs_count,
            "involved_posts_count": involved_count,
            "amplification_ratio": amplification_ratio,
            "mean_pairwise_similarity": round(mean_sim, 4),
            "max_pairwise_similarity": round(max_sim, 4),
            "campaign_risk_score": round(risk_score, 1),
            "astroturfing_detected": astroturfing_detected
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
                max_features=50
            )
            matrix = tfidf.fit_transform(non_empty)
            scores = np.asarray(matrix.mean(axis=0)).ravel()
            features = tfidf.get_feature_names_out()

            ranked = sorted(zip(features, scores), key=lambda x: x[1], reverse=True)
            return [(term, round(float(score), 4)) for term, score in ranked[:top_n]]
        except Exception:
            return []
