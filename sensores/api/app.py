import os
import requests
import psycopg2
from flask import Flask, jsonify, request
from datetime import datetime

app = Flask(__name__)

# ── Variables de entorno ──────────────────────────────────────
INSTANCIA   = os.getenv("API_INSTANCE", "API-?")
DB_HOST     = os.getenv("DB_HOST",     "localhost")
DB_NAME     = os.getenv("DB_NAME",     "clima_db")
DB_USER     = os.getenv("DB_USER",     "clima_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "clima_pass")

# ── Ciudades disponibles con coordenadas ─────────────────────
CIUDADES = {
    "tegucigalpa":   {"lat": 14.0818, "lon": -87.2068, "nombre": "Tegucigalpa"},
    "san_pedro_sula":{"lat": 15.5000, "lon": -88.0333, "nombre": "San Pedro Sula"},
}

# ── Conexion a base de datos ─────────────────────────────────
def get_conn():
    return psycopg2.connect(
        host=DB_HOST, dbname=DB_NAME,
        user=DB_USER, password=DB_PASSWORD
    )

# ── Ruta principal: obtener temperatura ─────────────────────
@app.route("/temperatura", methods=["GET"])
def obtener_temperatura():
    ciudad_param = request.args.get("ciudad", "tegucigalpa").lower()

    if ciudad_param not in CIUDADES:
        return jsonify({
            "error": "Ciudad no valida. Usa: tegucigalpa o san_pedro_sula"
        }), 400

    ciudad  = CIUDADES[ciudad_param]
    lat     = ciudad["lat"]
    lon     = ciudad["lon"]
    nombre  = ciudad["nombre"]

    # ── Consultar Open-Meteo ──────────────────────────────────
    try:
        url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lon}"
            f"&current=temperature_2m"
            f"&timezone=America%2FTegucigalpa"
        )
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        temperatura = data["current"]["temperature_2m"]
    except Exception as e:
        return jsonify({"error": f"Error consultando Open-Meteo: {str(e)}"}), 500

    # ── Guardar en base de datos ──────────────────────────────
    try:
        conn = get_conn()
        cur  = conn.cursor()
        cur.execute(
            """
            INSERT INTO lecturas (ciudad, temperatura, unidad, latitud, longitud, instancia, fecha_hora)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (nombre, temperatura, "C", lat, lon, INSTANCIA, datetime.now())
        )
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        return jsonify({"error": f"Error guardando en BD: {str(e)}"}), 500

    return jsonify({
        "ciudad":      nombre,
        "temperatura": temperatura,
        "unidad":      "C",
        "latitud":     lat,
        "longitud":    lon,
        "instancia":   INSTANCIA,
        "fecha_hora":  datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

# ── Historial de lecturas por ciudad ─────────────────────────
@app.route("/historial", methods=["GET"])
def historial():
    ciudad_param = request.args.get("ciudad", "").lower()
    limite       = int(request.args.get("limite", 50))

    try:
        conn = get_conn()
        cur  = conn.cursor()

        if ciudad_param in CIUDADES:
            nombre = CIUDADES[ciudad_param]["nombre"]
            cur.execute(
                "SELECT ciudad, temperatura, unidad, instancia, fecha_hora "
                "FROM lecturas WHERE ciudad=%s ORDER BY fecha_hora DESC LIMIT %s",
                (nombre, limite)
            )
        else:
            cur.execute(
                "SELECT ciudad, temperatura, unidad, instancia, fecha_hora "
                "FROM lecturas ORDER BY fecha_hora DESC LIMIT %s",
                (limite,)
            )

        rows = cur.fetchall()
        cur.close()
        conn.close()

        resultado = [
            {
                "ciudad":      r[0], "temperatura": r[1],
                "unidad":      r[2], "instancia":   r[3],
                "fecha_hora":  str(r[4])
            }
            for r in rows
        ]
        return jsonify({"total": len(resultado), "lecturas": resultado})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ── Estado de la instancia ───────────────────────────────────
@app.route("/estado", methods=["GET"])
def estado():
    return jsonify({
        "instancia": INSTANCIA,
        "estado":    "activa",
        "hora":      datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
