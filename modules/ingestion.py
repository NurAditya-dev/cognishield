"""
Modul Pengolahan Input Data (ingestion.py)
CogniShield: Membaca teks langsung, berkas CSV, dan JSON serta validasi skema data.
"""

import io
import json
from typing import List, Dict, Any, Tuple, Optional
import pandas as pd


# Kandidat nama kolom teks umum dalam dataset media sosial Indonesia
CANDIDATE_TEXT_COLUMNS = [
    "text", "teks", "comment_text", "comment", "content", "konten", "post",
    "tweet", "komentar", "caption", "narasi", "pesan", "message", "body", "kalimat"
]


def load_dataframe_from_file(file_obj: Any) -> pd.DataFrame:
    """
    Membaca berkas masukan (BytesIO / file buffer dari st.file_uploader)
    baik berupa format CSV maupun JSON ke dalam pandas DataFrame.
    """
    filename = getattr(file_obj, "name", "").lower()

    if filename.endswith(".json"):
        try:
            content = file_obj.read()
            if isinstance(content, bytes):
                content = content.decode("utf-8", errors="replace")
            data = json.loads(content)
            if isinstance(data, list):
                return pd.DataFrame(data)
            elif isinstance(data, dict):
                for val in data.values():
                    if isinstance(val, list):
                        return pd.DataFrame(val)
                return pd.DataFrame([data])
        except Exception as e:
            raise ValueError(f"Gagal memproses berkas JSON: {str(e)}")
    else:
        try:
            if hasattr(file_obj, "seek"):
                file_obj.seek(0)
            df = pd.read_csv(file_obj)
            return df
        except Exception:
            try:
                if hasattr(file_obj, "seek"):
                    file_obj.seek(0)
                df = pd.read_csv(file_obj, sep=None, engine="python", encoding="utf-8-sig")
                return df
            except Exception as e:
                raise ValueError(f"Gagal membaca format CSV: {str(e)}")


def detect_text_column(df: pd.DataFrame) -> Optional[str]:
    """
    Mendeteksi secara otomatis kolom yang paling tepat menyimpan narasi/teks.
    """
    if df.empty:
        return None

    lower_cols = {col.lower().strip(): col for col in df.columns}
    for cand in CANDIDATE_TEXT_COLUMNS:
        if cand in lower_cols:
            return lower_cols[cand]

    text_candidates = []
    for col in df.columns:
        if df[col].dtype == object or pd.api.types.is_string_dtype(df[col]):
            non_nulls = df[col].dropna().astype(str)
            if len(non_nulls) > 0:
                avg_len = non_nulls.str.len().mean()
                text_candidates.append((col, avg_len))

    if text_candidates:
        text_candidates.sort(key=lambda x: x[1], reverse=True)
        return text_candidates[0][0]

    return None


def extract_clean_posts(df: pd.DataFrame, text_col: str) -> List[str]:
    """
    Mengekstrak daftar teks mentah non-kosong dari kolom terpilih.
    """
    if text_col not in df.columns:
        return []

    texts = df[text_col].dropna().astype(str).tolist()
    cleaned_posts = [t.strip() for t in texts if len(t.strip()) > 0]
    return cleaned_posts
