import argparse
import csv
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

import requests


BASE_URL = "http://cheapest-alb-1599766835.us-east-1.elb.amazonaws.com"

TIENDA_ID = "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"
MONEDA_ID = "cccccccc-cccc-4ccc-8ccc-cccccccccccc"

PRODUCTOS = [
    "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
    "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaab",
    "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaac",
    "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaad",
]


def crear_body_post():
    items = []

    for producto_id in PRODUCTOS:
        items.append({
            "productoId": producto_id,
            "cantidad": 1,
            "precioUnitario": 25.5,
            "descuento": 0,
            "monedaId": MONEDA_ID
        })

    return {
        "identificador": f"pedido-python-{uuid.uuid4()}",
        "tiendaId": TIENDA_ID,
        "fechaHoraCreacion": datetime.now(timezone.utc).isoformat(),
        "montoTotal": round(len(items) * 25.5, 2),
        "monedaId": MONEDA_ID,
        "items": items
    }


def guardar_resultado(archivo, resultado, lock):
    with lock:
        with open(archivo, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                resultado["timestamp_iso"],
                resultado["status_code"],
                resultado["latency_ms"],
                resultado["error"]
            ])


def hacer_request(method, url, archivo, lock):
    inicio = time.perf_counter()
    timestamp = datetime.now(timezone.utc).isoformat()

    status_code = 0
    error = ""

    try:
        if method == "GET":
            response = requests.get(url, timeout=30)
        else:
            response = requests.post(
                url,
                json=crear_body_post(),
                headers={"Content-Type": "application/json"},
                timeout=30
            )

        status_code = response.status_code

        if not response.ok:
            error = f"HTTP {status_code}"
            

    except Exception as e:
        error = str(e)

    latency_ms = round(
        (time.perf_counter() - inicio) * 1000,
        2
    )

    resultado = {
        "timestamp_iso": timestamp,
        "status_code": status_code,
        "latency_ms": latency_ms,
        "error": error
    }

    guardar_resultado(archivo, resultado, lock)

    return resultado


def percentile(values, p):
    if not values:
        return 0

    index = int(len(values) * p / 100)
    index = min(index, len(values) - 1)

    return values[index]


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("--method", choices=["GET", "POST"], required=True)
    parser.add_argument("--users", type=int, required=True)
    parser.add_argument("--ramp-up", type=int, required=True)
    parser.add_argument("--duration", type=int, required=True)
    parser.add_argument("--rate", type=float, required=True)

    args = parser.parse_args()

    if args.method == "GET":
        url = (
            f"{BASE_URL}/logistics/tenderos/"
            f"productos-disponibles"
            f"?tiendaId={TIENDA_ID}&zona=Zona%20Norte"
        )
        archivo = "results_get.csv"

    else:
        url = f"{BASE_URL}/logistics/pedidos"
        archivo = "results_post.csv"

    # Reiniciar CSV
    with open(archivo, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "timestamp_iso",
            "status_code",
            "latency_ms",
            "error"
        ])

    print("\n" + "=" * 60)
    print("CHEAPEST API - PRUEBA DE CARGA")
    print("=" * 60)
    print(f"Endpoint:     {args.method}")
    print(f"Usuarios:     {args.users}")
    print(f"Ramp-up:      {args.ramp_up} segundos")
    print(f"Duracion:     {args.duration} segundos")
    print(f"Tasa objetivo:{args.rate} req/s")
    print(f"Archivo:      {archivo}")
    print("=" * 60)

    resultados = []
    resultados_lock = threading.Lock()
    csv_lock = threading.Lock()

    # Pool de usuarios concurrentes
    executor = ThreadPoolExecutor(
        max_workers=args.users
    )

    # Creamos progresivamente los usuarios durante el ramp-up.
    # Cada usuario queda disponible para recibir una solicitud.
    usuarios_disponibles = 0

    inicio_ramp = time.perf_counter()

    for i in range(args.users):

        usuarios_disponibles += 1

        if args.ramp_up > 0:
            espera = args.ramp_up / args.users
            time.sleep(espera)

    print("\nRamp-up completado.")
    print("Iniciando carga durante", args.duration, "segundos...\n")

    inicio_carga = time.perf_counter()
    siguiente_request = inicio_carga

    futures = []

    while time.perf_counter() - inicio_carga < args.duration:

        ahora = time.perf_counter()

        if ahora >= siguiente_request:

            future = executor.submit(
                hacer_request,
                args.method,
                url,
                archivo,
                csv_lock
            )

            futures.append(future)

            siguiente_request += 1 / args.rate

        else:
            time.sleep(0.001)

    # Esperar solicitudes pendientes
    for future in futures:
        resultado = future.result()

        with resultados_lock:
            resultados.append(resultado)

    executor.shutdown()

    total = len(resultados)

    exitosas = [
        r for r in resultados
        if 200 <= r["status_code"] < 400
        and not r["error"]
    ]

    errores = total - len(exitosas)

    latencias = sorted(
        r["latency_ms"]
        for r in resultados
        if not r["error"]
    )

    promedio = (
        sum(latencias) / len(latencias)
        if latencias
        else 0
    )

    p95 = percentile(latencias, 95)
    p99 = percentile(latencias, 99)

    error_percent = (
        errores / total * 100
        if total
        else 0
    )

    tiempo_real = time.perf_counter() - inicio_carga

    throughput = (
        total / tiempo_real
        if tiempo_real > 0
        else 0
    )

    print("\n" + "=" * 60)
    print("RESULTADOS")
    print("=" * 60)
    print(f"Solicitudes:       {total}")
    print(f"Exitosas:          {len(exitosas)}")
    print(f"Errores:           {errores}")
    print(f"Error %:           {error_percent:.2f}%")
    print(f"Throughput real:   {throughput:.2f} req/s")
    print(f"Latencia promedio: {promedio:.2f} ms")
    print(f"P95:               {p95:.2f} ms")
    print(f"P99:               {p99:.2f} ms")
    print("=" * 60)
    print(f"\nResultados guardados en: {archivo}")


if __name__ == "__main__":
    main()
