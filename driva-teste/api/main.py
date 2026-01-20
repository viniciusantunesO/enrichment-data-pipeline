from fastapi import FastAPI
from fastapi import Query
from fastapi import Header, HTTPException
import math
import uuid
import random
from datetime import timedelta, datetime
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends
from fastapi.staticfiles import StaticFiles
from db import get_connection




app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

def generate_enrichments(total=5000):
    data = []

    for _ in range(total):
        created = datetime.now() - timedelta(minutes=random.randint(5, 120))
        updated = created + timedelta(minutes=random.randint(1, 10))

        data.append({
            "id": str(uuid.uuid4()),
            "id_workspace": str(uuid.uuid4()),
            "workspace_name": random.choice([
                "Tech Solutions Corp",
                "Data Masters",
                "Sales Boost",
                "Growth Labs"
            ]),
            "total_contacts": random.randint(10, 2000),
            "contact_type": random.choice(["PERSON", "COMPANY"]),
            "status": random.choice([
                "PROCESSING",
                "COMPLETED",
                "FAILED",
                "CANCELED"
            ]),
            "created_at": created.isoformat(),
            "updated_at": updated.isoformat()
        })

    return data

ENRICHMENTS=generate_enrichments()
KEY="driva_test_key_abc123xyz789"
security = HTTPBearer()


@app.get("/people/v1/enrichments")
def get_enrichments(
    page: int | None = Query(None),
    limit: int | None = Query(None),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):

    if page is None or page < 1:
        page = 1

    if limit is None or limit < 1 or limit > 100:
        limit = 50


    if credentials.credentials != KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    if random.random() < 0.1:
        raise HTTPException(status_code=429, detail="Too Many Requests")

    total_items = len(ENRICHMENTS)
    total_pages = math.ceil(total_items / limit)

    start = (page - 1) * limit
    end = start + limit
    batch=ENRICHMENTS[start:end]

    return {
        "meta": {
            "current_page": page,
            "items_per_page": limit,
            "total_items": total_items,
            "total_pages": total_pages
        },
        "data": batch
    }

@app.get("/analytics/overview")
def analytics_overview(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != KEY:
        raise HTTPException(status_code=401)

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            COUNT(*) AS total_jobs,
            AVG(duracao_processamento_minutos) AS tempo_medio,
            SUM(CASE WHEN processamento_sucesso THEN 1 ELSE 0 END)::float / COUNT(*) AS taxa_sucesso
        FROM gold_enrichments
    """)

    total, tempo_medio, taxa = cur.fetchone()

    cur.close()
    conn.close()

    return {
        "total_jobs": total,
        "tempo_medio_minutos": round(tempo_medio or 0, 2),
        "taxa_sucesso": round((taxa or 0) * 100, 2)
    }

@app.get("/analytics/enrichments")
def list_enrichments(
    page: int = 1,
    limit: int = 20,
    status: str | None = None,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    if credentials.credentials != KEY:
        raise HTTPException(status_code=401)

    offset = (page - 1) * limit
    filters = []
    params = []

    if status:
        filters.append("status_processamento = %s")
        params.append(status)

    where = f"WHERE {' AND '.join(filters)}" if filters else ""

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(f"""
        SELECT
            id_enriquecimento,
            nome_workspace,
            total_contatos,
            tipo_contato,
            status_processamento,
            categoria_tamanho_job,
            duracao_processamento_minutos,
            processamento_sucesso,
            data_atualizacao_dw
        FROM gold_enrichments
        {where}
        ORDER BY data_atualizacao_dw DESC
        LIMIT %s OFFSET %s
    """, params + [limit, offset])

    columns = [desc[0] for desc in cur.description]
    rows = cur.fetchall()

    data = [dict(zip(columns, row)) for row in rows]

    cur.close()
    conn.close()

    return {
        "page": page,
        "limit": limit,
        "data": data
    }

