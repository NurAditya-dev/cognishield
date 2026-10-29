"""
Modul Pra-Pemrosesan Teks (Preprocessing)
CogniShield: Cognitive Risk & Disinformation Detection Engine
"""

import re
import unicodedata
from typing import Dict, List, Optional

# Kamus normalisasi kata slang, singkatan, dan ejaan umum di media sosial Indonesia
SLANG_DICTIONARY: Dict[str, str] = {
    "yg": "yang",
    "dgn": "dengan",
    "bgt": "banget",
    "bkn": "bukan",
    "gak": "tidak",
    "ga": "tidak",
    "gk": "tidak",
    "tdk": "tidak",
    "nggak": "tidak",
    "ngga": "tidak",
    "udah": "sudah",
    "udh": "sudah",
    "sdh": "sudah",
    "blm": "belum",
    "blom": "belum",
    "kalo": "kalau",
    "klo": "kalau",
    "kl": "kalau",
    "tp": "tapi",
    "krn": "karena",
    "bisa": "bisa",
    "bs": "bisa",
    "aja": "saja",
    "aj": "saja",
    "lg": "lagi",
    "lgi": "lagi",
    "sy": "saya",
    "gw": "saya",
    "gue": "saya",
    "lo": "kamu",
    "lu": "kamu",
    "dr": "dari",
    "utk": "untuk",
    "sm": "sama",
    "org": "orang",
    "jgn": "jangan",
    "bener": "benar",
    "bnr": "benar",
    "emg": "memang",
    "emang": "memang",
    "tau": "tahu",
    "gmn": "bagaimana",
    "gimana": "bagaimana",
    "knp": "kenapa",
    "dmn": "dimana",
    "bgtu": "begitu",
    "bgst": "bangsat",
    "buzzer": "pendengung",
    "framing": "pembingkaian",
    "hoax": "hoaks",
    "info": "informasi",
    "pls": "tolong",
    "plis": "tolong",
    "viralkan": "viralkan",
    "sebarkan": "sebarkan"
}


def remove_urls(text: str) -> str:
    """Menghapus URL tautan web (http, https, ftp, www)."""
    if not isinstance(text, str):
        return ""
    # Menghapus pola http://, https://, dan www.
    url_pattern = re.compile(r'https?://\S+|www\.\S+')
    return url_pattern.sub('', text)


def remove_mentions_and_handles(text: str) -> str:
    """Menghapus mention pengguna (@username)."""
    if not isinstance(text, str):
        return ""
    return re.sub(r'@\w+', '', text)


def clean_hashtags(text: str, keep_text: bool = True) -> str:
    """
    Membersihkan tagar (#). Jika keep_text True, karakter '#' dihilangkan
    tetapi kata di belakangnya dipertahankan.
    """
    if not isinstance(text, str):
        return ""
    if keep_text:
        return re.sub(r'#(\w+)', r'\1', text)
    return re.sub(r'#\w+', '', text)


def remove_emojis(text: str) -> str:
    """Menghapus karakter emoji dan varian simbol unicode grafis."""
    if not isinstance(text, str):
        return ""
    # Menghilangkan emoji menggunakan range unicode standar emoji & pictorial
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # Emoticons
        "\U0001F300-\U0001F5FF"  # Symbols & pictographs
        "\U0001F680-\U0001F6FF"  # Transport & map
        "\U0001F1E0-\U0001F1FF"  # Flags (iOS)
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "\U0001F900-\U0001F9FF"  # Supplemental symbols & pictographs
        "\U0001FA70-\U0001FAFF"  # Symbols and pictographs extended-A
        "]+",
        flags=re.UNICODE
    )
    # Hapus juga non-BMP simbol lainnya
    cleaned = emoji_pattern.sub('', text)
    # Normalisasi unicode (NFKD)
    cleaned = unicodedata.normalize('NFKD', cleaned)
    return cleaned


def case_folding(text: str) -> str:
    """Mengubah teks menjadi huruf kecil (lowercase)."""
    if not isinstance(text, str):
        return ""
    return text.lower().strip()


def remove_special_characters(text: str, allow_alphanumeric_only: bool = True) -> str:
    """
    Menghapus tanda baca, angka (opsional), dan karakter khusus.
    """
    if not isinstance(text, str):
        return ""
    if allow_alphanumeric_only:
        # Hanya pertahankan huruf a-z dan spasi
        cleaned = re.sub(r'[^a-zA-Z\s]', ' ', text)
    else:
        # Pertahankan huruf dan angka
        cleaned = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
    
    # Hapus spasi berlebih
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned


def normalize_slang(text: str, custom_dict: Optional[Dict[str, str]] = None) -> str:
    """
    Mengganti kata slang/singkatan informal menjadi bentuk baku bahasa Indonesia.
    """
    if not isinstance(text, str):
        return ""
    
    dictionary = SLANG_DICTIONARY.copy()
    if custom_dict:
        dictionary.update(custom_dict)

    words = text.split()
    normalized_words = [dictionary.get(word, word) for word in words]
    return " ".join(normalized_words)


def preprocess_text(
    text: str,
    remove_url: bool = True,
    remove_mentions: bool = True,
    remove_emoji: bool = True,
    to_lower: bool = True,
    remove_specials: bool = True,
    normalize_slang_words: bool = True,
    custom_slang: Optional[Dict[str, str]] = None
) -> str:
    """
    Pipeline pembersihan teks lengkap untuk analisis kognitif & astroturfing.
    """
    if not text or not isinstance(text, str):
        return ""

    result = text

    if remove_url:
        result = remove_urls(result)

    if remove_mentions:
        result = remove_mentions_and_handles(result)

    result = clean_hashtags(result, keep_text=True)

    if remove_emoji:
        result = remove_emojis(result)

    if to_lower:
        result = case_folding(result)

    if remove_specials:
        result = remove_special_characters(result, allow_alphanumeric_only=True)

    if normalize_slang_words:
        result = normalize_slang(result, custom_slang)

    # Pastikan kerapian spasi akhir
    result = re.sub(r'\s+', ' ', result).strip()
    return result


def tokenize(text: str) -> List[str]:
    """Tokenisasi sederhana berbasis spasi setelah preprocessing."""
    cleaned = preprocess_text(text)
    if not cleaned:
        return []
    return cleaned.split()
