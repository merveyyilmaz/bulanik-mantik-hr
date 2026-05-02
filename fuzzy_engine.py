"""
Bulanık Mantık Motoru
T-norm ve S-norm operatörleri ile personel değerlendirme
"""

import math


# ─────────────────────────────────────────────
#  1. ÜYELİK FONKSİYONLARI  (Fuzzification)
# ─────────────────────────────────────────────

def triangular_mf(x, a, b, c):
    """Üçgen üyelik fonksiyonu"""
    if x <= a or x >= c:
        return 0.0
    elif x <= b:
        return (x - a) / (b - a)
    else:
        return (c - x) / (c - b)

def trapezoid_mf(x, a, b, c, d):
    """Trapezoid üyelik fonksiyonu"""
    if x <= a or x >= d:
        return 0.0
    elif x <= b:
        return (x - a) / (b - a)
    elif x <= c:
        return 1.0
    else:
        return (d - x) / (d - c)

def gaussian_mf(x, mean, sigma):
    """Gaussian üyelik fonksiyonu"""
    return math.exp(-((x - mean) ** 2) / (2 * sigma ** 2))


def fuzzify(value, max_val=5.0):
    """
    1-5 arası ham değeri 0-1 arasında bulanık skora çevir.
    Trapezoid üyelik fonksiyonları ile dilsel etiketler:
    Düşük / Orta-Düşük / Orta / Orta-Yüksek / Yüksek
    """
    x = value  # 1-5 skalasında

    # Beş dilsel etiket için üyelik fonksiyonları
    very_low  = trapezoid_mf(x, 1.0, 1.0, 1.5, 2.5)   # 1.0-2.5
    low_med   = triangular_mf(x, 1.5, 2.0, 3.0)         # 2.0
    medium    = triangular_mf(x, 2.0, 3.0, 4.0)          # 3.0
    med_high  = triangular_mf(x, 3.0, 4.0, 5.0)          # 4.0
    high      = trapezoid_mf(x, 4.0, 4.5, 5.0, 5.0)     # 4.5-5.0

    # Skor: 0.0, 0.25, 0.5, 0.75, 1.0
    fuzzy_score = (0.00 * very_low +
                   0.25 * low_med +
                   0.50 * medium +
                   0.75 * med_high +
                   1.00 * high)

    total = very_low + low_med + medium + med_high + high
    if total > 0:
        normalized = fuzzy_score / total
    else:
        # Lineer fallback
        normalized = (value - 1.0) / (max_val - 1.0)

    return min(max(normalized, 0.0), 1.0)


# ─────────────────────────────────────────────
#  2. T-NORM OPERATÖRLER  (VE Mantığı)
# ─────────────────────────────────────────────

def t_min(a, b):
    """Zadeh Minimum - En zayıf kriteri al"""
    return min(a, b)

def t_product(a, b):
    """Çarpım - Dengeli değerlendirme"""
    return a * b

def t_lukasiewicz(a, b):
    """Łukasiewicz - En katı filtre"""
    return max(0.0, a + b - 1.0)

def t_schweizer_sklar(a, b, p=2.0):
    """Schweizer-Sklar parametrik ailesi"""
    if p == 0:
        return t_product(a, b)
    if a == 0 or b == 0:
        return 0.0
    val = a**(-p) + b**(-p) - 1
    if val <= 0:
        return 0.0
    return val ** (-1.0 / p)

def t_frank(a, b, s=2.0):
    """Frank parametrik ailesi"""
    if s == 1:
        return t_product(a, b)
    if s == float('inf'):
        return t_min(a, b)
    numerator = math.log(1 + (s**a - 1) * (s**b - 1) / (s - 1))
    return numerator / math.log(s)

def apply_tnorm(values, method="product"):
    """Çoklu değere T-norm uygula"""
    result = values[0]
    for v in values[1:]:
        if method == "min":
            result = t_min(result, v)
        elif method == "product":
            result = t_product(result, v)
        elif method == "lukasiewicz":
            result = t_lukasiewicz(result, v)
        elif method == "schweizer_sklar":
            result = t_schweizer_sklar(result, v, p=2.0)
        elif method == "frank":
            result = t_frank(result, v, s=2.0)
    return result


# ─────────────────────────────────────────────
#  3. S-NORM OPERATÖRLER  (VEYA Mantığı)
# ─────────────────────────────────────────────

def s_max(a, b):
    """Zadeh Maksimum - En iyi kriteri al"""
    return max(a, b)

def s_probabilistic(a, b):
    """Olasılıksal toplam - Dengeli birleştirme"""
    return a + b - a * b

def s_lukasiewicz(a, b):
    """Łukasiewicz S-norm - En cömert"""
    return min(1.0, a + b)

def apply_snorm(values, method="probabilistic"):
    """Çoklu değere S-norm uygula"""
    result = values[0]
    for v in values[1:]:
        if method == "max":
            result = s_max(result, v)
        elif method == "probabilistic":
            result = s_probabilistic(result, v)
        elif method == "lukasiewicz":
            result = s_lukasiewicz(result, v)
    return result


# ─────────────────────────────────────────────
#  4. PERSONEL DEĞERLENDİRME
# ─────────────────────────────────────────────

WEIGHTS = {
    "tecrube":          0.30,
    "yabanci_dil":      0.20,
    "egitim_derecesi":  0.25,
    "problem_cozme":    0.25,
}

POLICIES = {
    "kati": {
        "label": "Katı Politika",
        "description": "Finans / Savunma — Tüm kriterler yüksek olmalı",
        "tnorm": "lukasiewicz",
        "snorm": "max",
        "color": "#ef4444",
    },
    "dengeli": {
        "label": "Dengeli Politika",
        "description": "Teknoloji Şirketi — Güçlü yönler zayıfları telafi eder",
        "tnorm": "product",
        "snorm": "probabilistic",
        "color": "#3b82f6",
    },
    "esnek": {
        "label": "Esnek Politika",
        "description": "Startup — Bir alanda parlayan aday yeterli",
        "tnorm": "min",
        "snorm": "lukasiewicz",
        "color": "#22c55e",
    },
}


def evaluate_candidate(row, policy_key="dengeli"):
    """
    Bir adayı bulanık mantık ile değerlendir.
    Döndürür: skor (0-100) + detaylar
    """
    policy = POLICIES[policy_key]

    # Fuzzification
    fuzzy = {
        "tecrube":         fuzzify(row["tecrube"]),
        "yabanci_dil":     fuzzify(row["yabanci_dil"]),
        "egitim_derecesi": fuzzify(row["egitim_derecesi"]),
        "problem_cozme":   fuzzify(row["problem_cozme"]),
    }

    # Ağırlıklı bulanık değerler
    weighted = {k: fuzzy[k] * WEIGHTS[k] for k in fuzzy}

    # Zorunlu kriterler (VE mantığı) — T-norm
    mandatory = [fuzzy["tecrube"], fuzzy["egitim_derecesi"]]
    t_score = apply_tnorm(mandatory, method=policy["tnorm"])

    # Tamamlayıcı kriterler (VEYA mantığı) — S-norm
    optional = [fuzzy["yabanci_dil"], fuzzy["problem_cozme"]]
    s_score = apply_snorm(optional, method=policy["snorm"])

    # Karma birleştirme — ağırlıklı ortalama
    final_score = (
        WEIGHTS["tecrube"] * fuzzy["tecrube"] +
        WEIGHTS["egitim_derecesi"] * fuzzy["egitim_derecesi"] +
        WEIGHTS["yabanci_dil"] * fuzzy["yabanci_dil"] +
        WEIGHTS["problem_cozme"] * fuzzy["problem_cozme"]
    )

    # T ve S skorlarını karıştır (0.6 T-norm, 0.4 S-norm)
    combined = 0.6 * t_score + 0.4 * s_score

    # Final: ağırlıklı ortalama ile karma değeri birleştir
    final = 0.7 * final_score + 0.3 * combined
    final_pct = round(final * 100, 2)

    # Karar
    if final_pct >= 65:
        decision = "İşe Al"
        decision_color = "#22c55e"
    elif final_pct >= 40:
        decision = "Gözden Geçir"
        decision_color = "#f59e0b"
    else:
        decision = "Red"
        decision_color = "#ef4444"

    return {
        "id": row["id"],
        "ad": row["ad"],
        "soyad": row["soyad"],
        "ham": {
            "tecrube": row["tecrube"],
            "yabanci_dil": row["yabanci_dil"],
            "egitim_derecesi": row["egitim_derecesi"],
            "problem_cozme": row["problem_cozme"],
        },
        "fuzzy": {k: round(v, 3) for k, v in fuzzy.items()},
        "t_score": round(t_score, 3),
        "s_score": round(s_score, 3),
        "final_score": final_pct,
        "decision": decision,
        "decision_color": decision_color,
        "policy": policy_key,
        "policy_label": policy["label"],
    }


def rank_candidates(rows, policy_key="dengeli"):
    results = [evaluate_candidate(r, policy_key) for r in rows]
    results.sort(key=lambda x: x["final_score"], reverse=True)
    for i, r in enumerate(results):
        r["rank"] = i + 1
    return results
