import psycopg2
from psycopg2.extras import RealDictCursor

DB_CONFIG = {
    "host": "localhost",
    "database": "fuzzy_hr",
    "user": "postgres",
    "password": "*****"
}

def get_conn():
    return psycopg2.connect(**DB_CONFIG)

def setup():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS adaylar (
            id SERIAL PRIMARY KEY,
            ad VARCHAR(50) NOT NULL,
            soyad VARCHAR(50) NOT NULL,
            tecrube INTEGER NOT NULL CHECK (tecrube BETWEEN 1 AND 5),
            yabanci_dil INTEGER NOT NULL CHECK (yabanci_dil BETWEEN 1 AND 5),
            egitim_derecesi INTEGER NOT NULL CHECK (egitim_derecesi BETWEEN 1 AND 5),
            problem_cozme INTEGER NOT NULL CHECK (problem_cozme BETWEEN 1 AND 5),
            created_at TIMESTAMP DEFAULT NOW()
        );
    """)

    cur.execute("SELECT COUNT(*) FROM adaylar;")
    count = cur.fetchone()[0]

    if count == 0:
        adaylar = [
            ("Ahmet", "Yılmaz", 5, 4, 4, 5),
            ("Mehmet", "Kaya", 4, 3, 3, 4),
            ("Ayşe", "Demir", 3, 5, 5, 4),
            ("Fatma", "Çelik", 2, 2, 3, 3),
            ("Ali", "Şahin", 5, 5, 5, 5),
            ("Zeynep", "Arslan", 1, 3, 2, 2),
            ("Mustafa", "Doğan", 4, 4, 4, 4),
            ("Elif", "Kılıç", 3, 2, 3, 3),
            ("Hasan", "Yıldız", 5, 3, 4, 5),
            ("Hülya", "Güneş", 2, 4, 2, 3),
            ("İbrahim", "Aydın", 4, 5, 5, 4),
            ("Seda", "Erdoğan", 3, 3, 3, 4),
            ("Emre", "Türk", 1, 2, 2, 2),
            ("Derya", "Koç", 5, 4, 5, 5),
            ("Burak", "Özkan", 2, 3, 3, 3),
            ("Cansu", "Çetin", 4, 4, 4, 4),
            ("Serkan", "Yıldırım", 3, 5, 3, 4),
            ("Pınar", "Kurt", 1, 1, 2, 2),
            ("Cem", "Öztürk", 5, 4, 5, 5),
            ("Gül", "Avcı", 2, 3, 2, 3),
            ("Tarık", "Polat", 4, 3, 4, 4),
            ("Neslihan", "Aktaş", 3, 4, 3, 3),
            ("Uğur", "Bulut", 5, 5, 5, 5),
            ("Dilek", "Tekin", 2, 2, 3, 2),
            ("Mert", "Özdemir", 4, 4, 4, 4),
            ("Selin", "Kaplan", 1, 3, 2, 3),
            ("Oğuz", "Çakır", 3, 2, 3, 4),
            ("Berna", "Acar", 5, 4, 5, 4),
            ("Volkan", "Güler", 2, 3, 2, 2),
            ("Esra", "Kara", 4, 5, 4, 5),
            ("Tolga", "Şimşek", 3, 3, 3, 3),
            ("Merve", "Toprak", 1, 2, 1, 2),
            ("Arda", "Çelik", 5, 4, 5, 5),
            ("Gülsüm", "Uçar", 2, 3, 3, 3),
            ("Kerem", "Aslan", 4, 4, 4, 4),
            ("Tuğba", "Duman", 3, 5, 3, 4),
            ("Barış", "Korkmaz", 1, 1, 2, 1),
            ("Arzu", "Solmaz", 5, 3, 5, 4),
            ("Onur", "Ateş", 2, 4, 2, 3),
            ("Sibel", "Karaca", 4, 3, 4, 4),
            ("Berk", "Özgür", 3, 4, 3, 3),
            ("Hande", "Yüksel", 5, 5, 5, 5),
            ("Serhat", "Bircan", 2, 2, 2, 2),
            ("Filiz", "Güven", 4, 4, 5, 4),
            ("Murat", "Demirci", 3, 3, 3, 3),
            ("Sema", "Özcan", 1, 3, 2, 2),
            ("Engin", "Bayrak", 5, 4, 4, 5),
            ("Tuğçe", "İlhan", 2, 3, 3, 3),
            ("Kaan", "Yener", 4, 5, 4, 4),
            ("Büşra", "Arslan", 3, 2, 3, 3),
        ]

        cur.executemany("""
            INSERT INTO adaylar (ad, soyad, tecrube, yabanci_dil, egitim_derecesi, problem_cozme)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, adaylar)
        print(f"{len(adaylar)} aday eklendi.")

    conn.commit()
    cur.close()
    conn.close()
    print("Veritabanı hazır.")

if __name__ == "__main__":
    setup()
