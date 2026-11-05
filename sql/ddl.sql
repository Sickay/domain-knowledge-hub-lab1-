-- Створення зіркової схеми для DuckDB

-- Вимір таксономії (з IRI)
CREATE TABLE IF NOT EXISTS dim_taxonomy (
    taxonomy_id VARCHAR PRIMARY KEY,
    class_uri VARCHAR NOT NULL,
    class_name VARCHAR NOT NULL,
    subclass_name VARCHAR,
    category VARCHAR
);

-- Вимір обладнання (SCD Type 2)
CREATE TABLE IF NOT EXISTS dim_equipment (
    equipment_key INTEGER PRIMARY KEY,
    equipment_id VARCHAR NOT NULL,
    model VARCHAR,
    location VARCHAR,
    valid_from DATE,
    valid_to DATE,
    is_current BOOLEAN
);

-- Вимір часу
CREATE TABLE IF NOT EXISTS dim_time (
    time_key INTEGER PRIMARY KEY,
    date DATE,
    hour INTEGER,
    shift VARCHAR,
    day_of_week VARCHAR
);

-- Вимір контролерів/сенсорів
CREATE TABLE IF NOT EXISTS dim_controller (
    controller_key INTEGER PRIMARY KEY,
    controller_id VARCHAR,
    sensor_type VARCHAR,
    sensitivity VARCHAR
);

-- Таблиця фактів телеметрії та подій
CREATE TABLE IF NOT EXISTS fact_telemetry (
    fact_id INTEGER PRIMARY KEY,
    equipment_key INTEGER REFERENCES dim_equipment(equipment_key),
    taxonomy_id VARCHAR REFERENCES dim_taxonomy(taxonomy_id),
    time_key INTEGER REFERENCES dim_time(time_key),
    controller_key INTEGER REFERENCES dim_controller(controller_key),
    duration_sec INTEGER,
    energy_kwh DOUBLE,
    error_count INTEGER,
    avg_temperature DOUBLE,
    avg_vibration DOUBLE,
    efficiency_ratio DOUBLE
);
