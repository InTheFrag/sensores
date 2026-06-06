import os
import time
import requests
from datetime import datetime

LB_URL    = os.getenv("LB_URL",              "http://localhost:8080/temperatura")
INTERVALO = int(os.getenv("INTERVALO_SEGUNDOS", "30"))
CIUDADES  = ["tegucigalpa", "san_pedro_sula"]

print("=" * 55)
print("  Simulador de Sensores Climaticos")
print(f"  URL Load Balancer : {LB_URL}")
print(f"  Intervalo         : {INTERVALO} segundos")
print(f"  Ciudades          : {', '.join(CIUDADES)}")
print("=" * 55)

# Espera inicial para que Nginx y las APIs esten listas
print("\nEsperando 10 segundos para que el sistema inicie...")
time.sleep(10)

contador = 0

while True:
    for ciudad in CIUDADES:
        try:
            url  = f"{LB_URL}?ciudad={ciudad}"
            resp = requests.get(url, timeout=15)

            if resp.status_code == 200:
                datos = resp.json()
                contador += 1
                print(
                    f"[{datetime.now().strftime('%H:%M:%S')}] "
                    f"#{contador:04d} | {datos['instancia']} | "
                    f"{datos['ciudad']:<16} | "
                    f"{datos['temperatura']}°C"
                )
            else:
                print(f"[ERROR] {ciudad} -> HTTP {resp.status_code}: {resp.text}")

        except Exception as e:
            print(f"[ERROR] No se pudo conectar al Load Balancer: {e}")

    print(f"  -- Esperando {INTERVALO}s antes de la proxima lectura --")
    time.sleep(INTERVALO)
