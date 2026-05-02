from flask import Flask, jsonify, request, render_template_string, send_from_directory
import psycopg2
from psycopg2.extras import RealDictCursor
from fuzzy_engine import rank_candidates, evaluate_candidate, POLICIES, fuzzify
import os

app = Flask(__name__)

DB_CONFIG = {
    "host": "localhost",
    "database": "fuzzy_hr",
    "user": "postgres",
    "password": "*****"
}

def get_rows():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM adaylar ORDER BY id;")
    rows = [dict(r) for r in cur.fetchall()]
    cur.close()
    conn.close()
    return rows

@app.route("/")
def index():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.route("/api/candidates")
def api_candidates():
    policy = request.args.get("policy", "dengeli")
    rows = get_rows()
    ranked = rank_candidates(rows, policy)
    return jsonify({"candidates": ranked, "policies": POLICIES, "total": len(ranked)})

@app.route("/api/candidate/<int:cid>")
def api_candidate(cid):
    policy = request.args.get("policy", "dengeli")
    rows = get_rows()
    row = next((r for r in rows if r["id"] == cid), None)
    if not row:
        return jsonify({"error": "Aday bulunamadı"}), 404
    results = {}
    for p in POLICIES:
        results[p] = evaluate_candidate(row, p)
    return jsonify({"candidate": row, "evaluations": results})

@app.route("/api/add_candidate", methods=["POST"])
def add_candidate():
    data = request.json
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
        INSERT INTO adaylar (ad, soyad, tecrube, yabanci_dil, egitim_derecesi, problem_cozme)
        VALUES (%s, %s, %s, %s, %s, %s) RETURNING *
    """, (data["ad"], data["soyad"], data["tecrube"], data["yabanci_dil"],
          data["egitim_derecesi"], data["problem_cozme"]))
    new_row = dict(cur.fetchone())
    conn.commit()
    cur.close()
    conn.close()
    policy = data.get("policy", "dengeli")
    result = evaluate_candidate(new_row, policy)
    return jsonify({"success": True, "candidate": result})

@app.route("/api/stats")
def api_stats():
    policy = request.args.get("policy", "dengeli")
    rows = get_rows()
    ranked = rank_candidates(rows, policy)
    ise_al = sum(1 for r in ranked if r["decision"] == "İşe Al")
    gozden = sum(1 for r in ranked if r["decision"] == "Gözden Geçir")
    red = sum(1 for r in ranked if r["decision"] == "Red")
    avg = sum(r["final_score"] for r in ranked) / len(ranked) if ranked else 0
    return jsonify({
        "total": len(ranked),
        "ise_al": ise_al,
        "gozden_gecir": gozden,
        "red": red,
        "avg_score": round(avg, 2),
        "top3": ranked[:3]
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=False)
