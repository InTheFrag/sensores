-- Tabla principal de lecturas de temperatura
CREATE TABLE IF NOT EXISTS lecturas (
    id          SERIAL PRIMARY KEY,
    ciudad      VARCHAR(50)   NOT NULL,
    temperatura FLOAT         NOT NULL,
    unidad      VARCHAR(5)    DEFAULT 'C',
    latitud     FLOAT,
    longitud    FLOAT,
    instancia   VARCHAR(20)   NOT NULL,
    fecha_hora  TIMESTAMP     DEFAULT CURRENT_TIMESTAMP
);

-- Indice para consultas por ciudad y fecha
CREATE INDEX IF NOT EXISTS idx_ciudad      ON lecturas(ciudad);
CREATE INDEX IF NOT EXISTS idx_fecha_hora  ON lecturas(fecha_hora);
