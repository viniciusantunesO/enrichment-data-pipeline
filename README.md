# enrichment-data-pipeline
# Desafio Técnico – Pipeline de Dados

Este projeto implementa um pipeline de dados completo conforme especificado no enunciado do desafio técnico da Driva, integrando uma API REST, orquestração com n8n e um Data Warehouse com modelagem em camadas Bronze e Gold.  
O objetivo do projeto é demonstrar boas práticas de engenharia de dados, organização de workflows, clareza arquitetural e funcionamento ponta a ponta.

---

## Funcionamento do Pipeline

A solução funciona de forma automatizada a partir de uma API que expõe dados de enriquecimentos com autenticação e paginação.

O n8n consome essa API em execuções recorrentes configuradas para rodar a cada **cinco minutos**.  
Os dados coletados são armazenados inicialmente na camada **Bronze** do Data Warehouse sem qualquer transformação.  

Em seguida, o próprio n8n executa o processo de transformação e consolidação dos dados, gravando o resultado final na camada **Gold**, que é utilizada para análises e consumo posterior.

---

## Modelagem de Dados

A modelagem do Data Warehouse segue o padrão solicitado no enunciado:

- **Bronze**
  - Armazena os dados brutos exatamente como recebidos da API
  - Preserva o payload original em formato JSON
  - Permite reprocessamentos futuros
  - Contém campos técnicos de Data Warehouse (`dw_ingested_at`, `dw_updated_at`)

- **Gold**
  - Contém dados tratados, consolidados e prontos para consumo analítico
  - Aplica regras de negócio simples
  - Garante idempotência por meio de chave primária
  - Possui métricas derivadas para análise (status, categorias, flags de sucesso)

---

## API

A API foi desenvolvida seguindo boas práticas REST:

- Autenticação via **Bearer Token**
- Paginação através dos parâmetros `page` e `limit`
- Retorno estruturado em `meta` + `data`
- Simulação de erro **429 (Too Many Requests)** para validação de retry e backoff
- Endpoint de **health check** para verificação do status do serviço

## Workflows no n8n

Os workflows foram construídos de forma organizada e modular:

- Execução automática a cada **5 minutos**
- Paginação completa da API
- Tratamento de erro 429 com retry
- Separação clara entre:
  - Ingestão para camada Bronze
  - Transformação e carga na camada Gold
- Uso do node PostgreSQL para persistência
- Logs visuais de execução para validação

Toda a lógica de orquestração e ETL está concentrada no **n8n**, mantendo a API simples e desacoplada.

---

## Boas Práticas e Decisões Técnicas

- Todos os timestamps são tratados em **UTC**
- Idempotência garantida na camada Gold
- Separação clara de responsabilidades:
  - API: exposição dos dados
  - n8n: orquestração e transformação
  - Banco de dados: persistência e análise
- Pipeline resiliente a falhas temporárias
- Possibilidade de reprocessamento completo a partir da Bronze

---

Execução do projeto em ambiente local

O projeto foi desenvolvido e testado em ambiente local, com os serviços executados separadamente. O banco de dados PostgreSQL deve estar em execução com as tabelas Bronze e Gold criadas conforme o modelo do projeto. A API é executada localmente e fica disponível na porta 3000. O n8n é executado separadamente e os workflows devem estar ativos para que o pipeline funcione corretamente.

Como rodar o projeto

Para executar o projeto em ambiente local, é necessário ter Docker e Docker Compose instalados. Após clonar o repositório, acesse a pasta raiz do projeto pelo terminal e execute o comando docker compose up -d para subir todos os serviços necessários. Esse comando iniciará automaticamente o banco de dados PostgreSQL, a API e o serviço do n8n. O banco de dados será criado com as tabelas das camadas Bronze e Gold a partir dos scripts de inicialização configurados no projeto. A API ficará disponível em http://localhost:3000 e pode ser iniciada manualmente, caso necessário, utilizando o comando uvicorn main:app --host 0.0.0.0 --port 3000. O n8n ficará disponível em http://localhost:5678 e deve ser acessado pelo navegador para importar e ativar os workflows fornecidos. Após importar os workflows, é necessário ativar o workflow orquestrador, que está configurado para executar automaticamente a cada cinco minutos. Esse workflow realiza a coleta dos dados da API, grava os dados brutos na camada Bronze e executa a transformação para a camada Gold. Para testar a API, pode-se utilizar o comando curl.exe -H "Authorization: Bearer driva_test_key_abc123xyz789" "http://localhost:3000/people/v1/enrichments?page=1&limit=50" diretamente no terminal. Para fins de validação dos dados ingeridos, o banco PostgreSQL pode ser acessado via terminal utilizando o comando psql -h localhost -p 5432 -U postgres -d driva_db ou docker exec -it driva_postgres psql -U driva -d driva_db. A consulta direta ao banco foi utilizada apenas para conferência dos dados nas camadas Bronze e Gold, não sendo necessária para a execução normal do sistema.
