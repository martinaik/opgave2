CREATE TABLE IF NOT EXISTS herodot_measurement (
    measurement_id SERIAL PRIMARY KEY,
    node_id UUID NOT NULL,
    instrument_id VARCHAR(100),
    instrument_model VARCHAR(50),
    source_id INTEGER NOT NULL REFERENCES source(source_id),
    observed TIMESTAMPTZ NOT NULL,
    temperature DOUBLE PRECISION,
    co2_concentration DOUBLE PRECISION,
    humidity DOUBLE PRECISION,
    pressure DOUBLE PRECISION,

    UNIQUE (node_id, instrument_id, source_id, observed)
);