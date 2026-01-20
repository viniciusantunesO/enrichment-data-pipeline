# enrichment-data-pipeline

Data Pipeline – API + n8n + Data Warehouse

Este projeto implementa um pipeline de dados ponta-a-ponta, simulando a ingestão de dados de uma API externa, orquestração com n8n, armazenamento em Data Warehouse e exposição de dados analíticos via API.
O foco está em boas práticas de engenharia de dados, separação de responsabilidades e resiliência do pipeline.

🏗️ Arquitetura Geral

Fluxo do pipeline:

API (FastAPI)

Expõe dados paginados de enriquecimentos

Possui autenticação Bearer

Simula falhas (429 Too Many Requests)

n8n (Orquestração)

Consome a API

Controla paginação

Implementa retry/backoff

Realiza ingestão na camada Bronze

Transforma dados e grava na camada Gold

Data Warehouse (PostgreSQL)

Camada Bronze: dados brutos

Camada Gold: dados tratados e prontos para consumo analítico

API Analítica (FastAPI)

Expõe métricas e dados consolidados da camada Gold
