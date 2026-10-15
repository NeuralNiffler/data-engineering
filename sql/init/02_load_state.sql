-- Aktueller Ladestand (Wasserzeichen) pro Quelle + Tabelle
CREATE TABLE IF NOT EXISTS etl.load_state (
    source       TEXT        NOT NULL,
    table_name   TEXT        NOT NULL,
    last_cursor  BIGINT      NOT NULL DEFAULT 0,
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (source, table_name)
);

-- Protokoll jedes Ladelaufs
CREATE TABLE IF NOT EXISTS etl.load_runs (
    run_id       BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source       TEXT        NOT NULL,
    table_name   TEXT        NOT NULL,
    cursor_from  BIGINT      NOT NULL,
    cursor_to    BIGINT,
    rows_loaded  INTEGER,
    status       TEXT        NOT NULL DEFAULT 'running'
                 CHECK (status IN ('running', 'success', 'failed')),
    started_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    finished_at  TIMESTAMPTZ,
    error_msg    TEXT,
    FOREIGN KEY (source, table_name) REFERENCES etl.load_state (source, table_name)
);

-- Startwert für Energy
INSERT INTO etl.load_state (source, table_name)
VALUES ('energy', 'readings')
ON CONFLICT DO NOTHING;
