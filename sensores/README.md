# Sistema de Sensores Climáticos con Load Balancer

Proyecto de Big Data para capturar temperaturas de Tegucigalpa y San Pedro Sula usando Flask, Nginx, PostgreSQL y un simulador de sensores.

## Requisitos previos

Antes de ejecutar el proyecto, asegúrate de tener instalado lo siguiente:

- Docker Desktop y Docker Compose funcionando
  - https://www.docker.com/products/docker-desktop/
- Python 3.10+ (solo si vas a ejecutar el notebook desde tu PC)
- Internet para consultar la API de Open-Meteo

> En Windows, usa PowerShell o CMD desde la carpeta del proyecto.

---

## Estructura del proyecto

```text
sensores/
├── docker-compose.yml
├── nginx/
│   └── nginx.conf
├── api/
│   ├── app.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── init.sql
├── sensor/
│   ├── sensor.py
│   └── Dockerfile
└── notebook/
    └── analisis_clima.ipynb
```

---

## Inicio rápido

### 1) Levantar toda la pila

Desde la raíz del proyecto ejecuta:

```bash
docker compose up --build
```

Si tu versión de Docker usa el comando antiguo, también funciona:

```bash
docker-compose up --build
```

Esto levantará:

- PostgreSQL en el puerto 5432
- 3 instancias de la API Flask
- Nginx como balanceador en el puerto 8080
- El simulador de sensores que envía lecturas cada 30 segundos

### 2) Esperar a que el sistema quede listo

Cuando todo esté activo, deberías ver mensajes como estos en el contenedor `sensor_clima`:

```text
sensor_clima  | [08:15:30] #0001 | API-1 | Tegucigalpa     | 28.3°C
sensor_clima  | [08:15:31] #0002 | API-2 | San Pedro Sula  | 30.1°C
sensor_clima  | [08:16:00] #0003 | API-3 | Tegucigalpa     | 28.3°C
```

Si no aparecen mensajes, espera 20–30 segundos y revisa con:

```bash
docker compose ps
```

---

## Verificar que todo funcione

### Endpoint principal

Abre estas URLs en el navegador:

```text
http://localhost:8080/temperatura?ciudad=tegucigalpa
http://localhost:8080/temperatura?ciudad=san_pedro_sula
```

Debes recibir una respuesta JSON con la temperatura, instancia y hora.

### Historial guardado en PostgreSQL

```text
http://localhost:8080/historial
http://localhost:8080/historial?ciudad=tegucigalpa&limite=20
```

### Estado de una instancia de API

```text
http://localhost:8080/estado
```

---

## Ejecutar el notebook de análisis

### Opción recomendada (desde tu computadora)

1. Instala las dependencias necesarias:

```bash
pip install jupyter pandas matplotlib psycopg2-binary
```

2. Abre el notebook desde la raíz del proyecto:

```bash
jupyter notebook notebook/analisis_clima.ipynb
```

3. En la primera celda del notebook, asegúrate de que la conexión use:

```python
host="localhost"
port=5432
```

4. Ejecuta todas las celdas con:
   - Kernel → Restart & Run All

### Importante

Si el notebook muestra error de conexión a PostgreSQL, normalmente es porque:

- Docker aún no está completamente levantado
- La base de datos no está expuesta en el puerto 5432
- El servicio `postgres` aún está iniciando

En ese caso, espera unos segundos y vuelve a correr el notebook.

---

## Tiempo recomendado para recopilar datos

Para que los gráficos sean representativos, deja el sistema corriendo al menos 30 minutos.

El simulador genera 2 lecturas cada 30 segundos (una por ciudad).

---

## Evidencia del balanceo de carga

El notebook genera gráficos de barras y pastel mostrando cuántas peticiones atendió cada instancia:

- API-1
- API-2
- API-3

Si el balanceo funciona correctamente, la distribución debería ser aproximadamente equitativa entre las tres instancias.

---

## Detener el sistema

```bash
docker compose down
```

Si también quieres borrar los datos persistidos de PostgreSQL:

```bash
docker compose down -v
```

---

## Endpoints disponibles

| Endpoint                                  | Método | Descripción                               |
| ----------------------------------------- | ------ | ----------------------------------------- |
| `/temperatura?ciudad=tegucigalpa`         | GET    | Consulta la temperatura de Tegucigalpa    |
| `/temperatura?ciudad=san_pedro_sula`      | GET    | Consulta la temperatura de San Pedro Sula |
| `/historial`                              | GET    | Muestra todas las lecturas guardadas      |
| `/historial?ciudad=tegucigalpa&limite=20` | GET    | Historial filtrado por ciudad             |
| `/estado`                                 | GET    | Estado de la instancia de API             |

---

## Solución de problemas frecuentes

### Error: "Connection refused" en el notebook

Verifica que la base de datos esté levantada:

```bash
docker compose ps
```

Si `postgres` no está `Up`, ejecuta:

```bash
docker compose up -d postgres
```

### Error: no aparecen temperaturas

Asegúrate de que el servicio `sensor` esté corriendo y de que el sistema haya estado activo por unos minutos.

### Error: el navegador no responde en localhost:8080

Revisa que Nginx esté levantado con:

```bash
docker compose ps
```

Si hace falta, reinicia toda la pila:

```bash
docker compose up --build
```
