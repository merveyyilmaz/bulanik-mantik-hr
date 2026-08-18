# Bulanık Mantık Tabanlı Personel Değerlendirme Sistemi

---

## Kurulum

### 1. PostgreSQL Kurulumu
```bash
sudo apt-get install postgresql postgresql-client
sudo service postgresql start
sudo -u postgres psql -c "CREATE USER fuzzy_user WITH PASSWORD 'fuzzy123';"
sudo -u postgres psql -c "CREATE DATABASE fuzzy_hr OWNER fuzzy_user;"
```

### 2. Python Bağımlılıkları
```bash
pip install flask psycopg2-binary
```

### 3. Veritabanını Oluştur (50 aday yükle)
```bash
python3 setup_db.py
```

### 4. Sunucuyu Başlat
```bash
python3 app.py
```

### 5. Tarayıcıda Aç
```
http://localhost:5050
```

---

## Veritabanı Şeması

```sql
CREATE TABLE adaylar (
    id SERIAL PRIMARY KEY,
    ad VARCHAR(50),
    soyad VARCHAR(50),
    tecrube INTEGER,         -- 1=0-1yıl, 2=1-3yıl, 3=3-5yıl, 4=5-8yıl, 5=8+yıl
    yabanci_dil INTEGER,     -- 1=Başlangıç ... 5=Uzman C2
    egitim_derecesi INTEGER, -- 1=Lise, 2=Önlisans, 3=Lisans, 4=YL, 5=Doktora
    problem_cozme INTEGER    -- 1=Çok Zayıf ... 5=Mükemmel
);
```

---

## Bulanık Mantık Algoritmaları

### Fuzzification (Bulanıklaştırma)
Ham 1-5 değerleri, 5 dilsel etiket ile 0-1 arasına dönüştürülür:
- Trapezoid + Üçgen üyelik fonksiyonları
- Ağırlıklı ortalama ile tek skor

### T-norm Operatörleri (VE Mantığı)
| Operatör | Formül | Kullanım |
|----------|--------|----------|
| Minimum (Zadeh) | min(a, b) | Katı politika |
| Çarpım | a × b | Dengeli politika |
| Łukasiewicz | max(0, a+b-1) | Çok katı |
| Schweizer-Sklar | parametrik | Ayarlanabilir |
| Frank | parametrik | Ayarlanabilir |

### S-norm Operatörleri (VEYA Mantığı)
| Operatör | Formül | Kullanım |
|----------|--------|----------|
| Maksimum (Zadeh) | max(a, b) | Esnek - uzman yeter |
| Prob. Toplam | a+b-a×b | Dengeli birleştirme |
| Łukasiewicz | min(1, a+b) | Çok cömert |

### Şirket Politikaları
- **Katı (Finans/Savunma):** Łukasiewicz T-norm + Max S-norm
- **Dengeli (Teknoloji):** Çarpım T-norm + Prob. S-norm
- **Esnek (Startup):** Min T-norm + Łukasiewicz S-norm

### Karar Eşikleri
- Skor ≥ 65 → **İşe Al**
- 40 ≤ Skor < 65 → **Gözden Geçir**  
- Skor < 40 → **Red**

---

## API Endpointleri

| Endpoint | Açıklama |
|----------|----------|
| `GET /` | Ana sayfa (web arayüzü) |
| `GET /api/candidates?policy=dengeli` | Tüm adaylar sıralı |
| `GET /api/candidate/:id` | Tek aday detayı (3 politika karşılaştırması) |
| `GET /api/stats?policy=dengeli` | İstatistikler |
| `POST /api/add_candidate` | Yeni aday ekle |

---

## Dosya Yapısı
```
fuzzy_hr/
├── setup_db.py      # Veritabanı kurulum + 50 aday seed
├── fuzzy_engine.py  # T-norm, S-norm, üyelik fonksiyonları
├── app.py           # Flask REST API
├── index.html       # Web arayüzü
└── README.md
```

> "Bulanık mantık, insan yargısını silmez — onu sistematik ve tekrarlanabilir kılar."
