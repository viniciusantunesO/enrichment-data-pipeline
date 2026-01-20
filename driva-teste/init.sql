-- BRONZE (dados crus)
CREATE TABLE IF NOT EXISTS bronze_enrichments (
    id_enriquecimento UUID PRIMARY KEY,
    payload JSONB NOT NULL,
    dw_ingested_at TIMESTAMP NOT NULL,
    dw_updated_at TIMESTAMP NOT NULL
);

-- GOLD (dados tratados)
CREATE TABLE IF NOT EXISTS gold_enrichments (
    id_enriquecimento UUID PRIMARY KEY,
    id_workspace UUID,
    nome_workspace TEXT,

    total_contatos INTEGER,
    tipo_contato TEXT,
    status_processamento TEXT,

    data_criacao TIMESTAMP,
    data_atualizacao TIMESTAMP,

    duracao_processamento_minutos FLOAT,
    tempo_por_contato_minutos FLOAT,

    processamento_sucesso BOOLEAN,
    necessita_reprocessamento BOOLEAN,

    categoria_tamanho_job TEXT,
    data_atualizacao_dw TIMESTAMP NOT NULL
);


CREATE INDEX IF NOT EXISTS idx_gold_status ON gold_enrichments(status_processamento);
CREATE INDEX IF NOT EXISTS idx_gold_workspace ON gold_enrichments(id_workspace);
