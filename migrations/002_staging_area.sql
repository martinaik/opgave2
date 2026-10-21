
CREATE TABLE staging_batch (
    batch_id SERIAL PRIMARY KEY,
    source_id INTEGER NOT NULL REFERENCES source(source_id),
    fetched_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    raw_data JSONB NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    error_message TEXT,
    processed_at TIMESTAMPTZ,

    CONSTRAINT staging_batch_status_check
        CHECK (
            status IN (
                'pending',
                'processing',
                'failed',
                'completed'
            )
        )
);

CREATE INDEX idx_staging_batch_status
    ON staging_batch(status);
