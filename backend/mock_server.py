from fastapi import FastAPI, Request, File, UploadFile, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
import json
import os
import uuid
from datetime import datetime

app = FastAPI(
    title="Research Nexus — Fallback Demo Server",
    description="Serves local .dat fallback dataset demonstrating 100% of Research Nexus features."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FALLBACK_PATH = os.path.join(os.path.dirname(__file__), "fallback_demo.dat")
with open(FALLBACK_PATH, "r", encoding="utf-8") as f:
    FALLBACK_DATA = json.load(f)

# In-memory mutable state for demo session
IN_MEMORY_STATE = {
    "projects": list(FALLBACK_DATA.get("projects", [])),
    "documents": list(FALLBACK_DATA.get("documents", [])),
    "chat_history": {},
}

# Helper to find project
def find_project(pid: str):
    p = next((p for p in IN_MEMORY_STATE["projects"] if p["id"] == pid), None)
    if not p and IN_MEMORY_STATE["projects"]:
        p = IN_MEMORY_STATE["projects"][0]
    return p

# ---------------- API ROUTES ----------------

@app.get("/api/health")
def get_health():
    h = dict(FALLBACK_DATA.get("health", {}))
    h["status"] = "healthy"
    h["demo_mode"] = True
    h["llm_provider"] = "local_dat_fallback"
    return JSONResponse(h)

@app.get("/api/system/ml-info")
def get_ml():
    return JSONResponse(FALLBACK_DATA.get("ml_info", []))

@app.get("/api/projects")
def get_projects():
    return JSONResponse(IN_MEMORY_STATE["projects"])

@app.post("/api/projects")
def create_project(body: dict = Body(...)):
    new_pid = str(uuid.uuid4())
    now = datetime.now().isoformat()
    new_proj = {
        "id": new_pid,
        "name": body.get("name", "New Demo Project"),
        "description": body.get("description") or "Created in demo session.",
        "document_count": 0,
        "indexed_count": 0,
        "created_at": now,
        "updated_at": now
    }
    IN_MEMORY_STATE["projects"].append(new_proj)
    return JSONResponse(new_proj)

@app.get("/api/projects/{pid}")
def get_project(pid: str):
    p = find_project(pid)
    return JSONResponse(p) if p else JSONResponse({"detail": "Not found"}, status_code=404)

@app.patch("/api/projects/{pid}")
def update_project(pid: str, body: dict = Body(...)):
    p = find_project(pid)
    if p:
        if "name" in body: p["name"] = body["name"]
        if "description" in body: p["description"] = body["description"]
        return JSONResponse(p)
    return JSONResponse({"detail": "Not found"}, status_code=404)

@app.delete("/api/projects/{pid}")
def delete_project(pid: str):
    IN_MEMORY_STATE["projects"] = [p for p in IN_MEMORY_STATE["projects"] if p["id"] != pid]
    return JSONResponse({"status": "deleted", "id": pid})

@app.get("/api/projects/{pid}/documents")
def get_proj_docs(pid: str):
    docs = [d for d in IN_MEMORY_STATE["documents"] if d.get("project_id") == pid]
    if not docs:
        docs = [d for d in IN_MEMORY_STATE["documents"] if d.get("project_id") == "a1b2c3d4-0001-0001-0001-000000000001"]
    
    # Attach paper metadata if available
    result = []
    for d in docs:
        d_copy = dict(d)
        d_copy["metadata"] = next((m for m in FALLBACK_DATA.get("paper_metadata", []) if m["document_id"] == d["id"]), None)
        result.append(d_copy)
    return JSONResponse(result)

@app.post("/api/projects/{pid}/documents")
def upload_paper_to_project(pid: str, file: UploadFile = File(...)):
    doc_id = f"d-demo-{uuid.uuid4().hex[:8]}"
    now = datetime.now().isoformat()
    fname = file.filename or "uploaded_paper.pdf"
    title_clean = fname.rsplit(".", 1)[0].replace("_", " ").replace("-", " ").title()
    
    new_doc = {
        "id": doc_id,
        "project_id": pid,
        "filename": fname,
        "title": title_clean,
        "status": "indexed",
        "page_count": 14,
        "chunk_count": 62,
        "error_message": None,
        "created_at": now,
        "updated_at": now
    }
    IN_MEMORY_STATE["documents"].append(new_doc)
    
    # Also update project counts
    p = find_project(pid)
    if p:
        p["document_count"] = p.get("document_count", 0) + 1
        p["indexed_count"] = p.get("indexed_count", 0) + 1
        
    return JSONResponse(new_doc)

@app.delete("/api/projects/{pid}/documents/{did}")
def remove_paper_from_project(pid: str, did: str):
    IN_MEMORY_STATE["documents"] = [d for d in IN_MEMORY_STATE["documents"] if d["id"] != did]
    p = find_project(pid)
    if p and p.get("document_count", 0) > 0:
        p["document_count"] -= 1
        p["indexed_count"] = max(0, p.get("indexed_count", 1) - 1)
    return JSONResponse({"status": "deleted", "document_id": did})

@app.get("/api/projects/{pid}/literature-matrix")
def get_matrix(pid: str):
    lm = FALLBACK_DATA.get("literature_matrix", {})
    if isinstance(lm, dict) and "rows" in lm:
        return JSONResponse(lm)
    return JSONResponse(lm.get(pid, lm.get("a1b2c3d4-0001-0001-0001-000000000001", {})))

@app.post("/api/projects/{pid}/compare")
def get_compare(pid: str, body: dict = Body(None)):
    comps = FALLBACK_DATA.get("comparisons", [])
    if isinstance(comps, list) and len(comps) > 0:
        matched = next((c for c in comps if c.get("project_id") == pid), comps[0])
        return JSONResponse(matched)
    return JSONResponse(comps)

@app.post("/api/projects/{pid}/gap-analysis")
def get_gap(pid: str, body: dict = Body(None)):
    ga = FALLBACK_DATA.get("gap_analysis", {})
    if isinstance(ga, dict) and "gaps" in ga:
        return JSONResponse(ga)
    return JSONResponse(ga.get(pid, ga.get("a1b2c3d4-0001-0001-0001-000000000001", {})))

@app.post("/api/projects/{pid}/research-questions")
def get_questions(pid: str, body: dict = Body(None)):
    rq = FALLBACK_DATA.get("research_questions", {})
    if isinstance(rq, dict) and "question_sets" in rq:
        return JSONResponse(rq)
    return JSONResponse(rq.get(pid, rq.get("a1b2c3d4-0001-0001-0001-000000000001", {})))

@app.get("/api/projects/{pid}/knowledge")
def get_knowledge(pid: str):
    pk = FALLBACK_DATA.get("project_knowledge", {})
    return JSONResponse(pk.get(pid, pk.get("a1b2c3d4-0001-0001-0001-000000000001", {})))

@app.get("/api/projects/{pid}/entities")
def get_entities(pid: str):
    pk = FALLBACK_DATA.get("project_knowledge", {}).get(pid, FALLBACK_DATA.get("project_knowledge", {}).get("a1b2c3d4-0001-0001-0001-000000000001", {}))
    entities = []
    for category in ["top_models", "top_datasets", "top_methods", "top_metrics", "top_domains", "top_tasks"]:
        entities.extend(pk.get(category, []))
    return JSONResponse(entities)

@app.get("/api/projects/{pid}/entities/{eid}")
def get_entity_detail(pid: str, eid: str):
    return JSONResponse({
        "entity_id": eid,
        "canonical_name": eid.replace("_", " ").title(),
        "entity_type": "model",
        "paper_count": 3,
        "mentions": [
            {"document_id": "d0000001-0000-0000-0000-000000000001", "snippet": f"Evaluated {eid} in medical note generation tasks."}
        ],
        "related_entities": ["GPT-4", "MIMIC-III", "Clinical Accuracy"]
    })

@app.get("/api/projects/{pid}/topics")
def get_topics(pid: str):
    pk = FALLBACK_DATA.get("project_knowledge", {}).get(pid, FALLBACK_DATA.get("project_knowledge", {}).get("a1b2c3d4-0001-0001-0001-000000000001", {}))
    return JSONResponse(pk.get("topics", []))

@app.get("/api/projects/{pid}/topics/{tid}")
def get_topic_detail(pid: str, tid: str):
    return JSONResponse({
        "id": tid,
        "label": f"Topic: {tid.replace('_', ' ').title()}",
        "paper_count": 4,
        "keywords": ["llm", "clinical", "evaluation", "benchmark", "accuracy"],
        "papers": [
            {"id": "d0000001-0000-0000-0000-000000000001", "title": "GPT-4 for Automated Clinical Note Generation"}
        ]
    })

@app.get("/api/projects/{pid}/analytics")
def get_analytics(pid: str):
    an = FALLBACK_DATA.get("analytics", {})
    return JSONResponse(an.get(pid, an.get("a1b2c3d4-0001-0001-0001-000000000001", {})))

@app.get("/api/documents/{did}/intelligence")
def get_doc_intel(did: str):
    pi = FALLBACK_DATA.get("paper_intelligence", {})
    return JSONResponse(pi.get(did, pi.get("d0000001-0000-0000-0000-000000000001", {})))

@app.post("/api/documents/{did}/analyze")
@app.post("/api/projects/{pid}/analyze")
def trigger_analysis():
    return JSONResponse({"job_id": f"job-{uuid.uuid4().hex[:6]}", "status": "completed", "progress": 100})

@app.get("/api/documents/{did}/jobs/{jid}")
@app.get("/api/projects/{pid}/jobs/{jid}")
def get_job_status(jid: str):
    return JSONResponse({"job_id": jid, "status": "completed", "progress": 100})

@app.get("/api/projects/{pid}/graph")
def get_graph(pid: str):
    kg = FALLBACK_DATA.get("knowledge_graph", {})
    if isinstance(kg, dict) and "nodes" in kg:
        return JSONResponse(kg)
    return JSONResponse(kg.get(pid, kg.get("a1b2c3d4-0001-0001-0001-000000000001", {})))

@app.post("/api/projects/{pid}/graph/query")
def query_graph(pid: str, body: dict = Body(None)):
    q = (body or {}).get("question", "clinical LLMs")
    return JSONResponse({
        "question": q,
        "answer": f"Based on the Knowledge Graph analysis for query '{q}', clinical LLMs are directly grounded by EHR benchmarks (MIMIC-III) and key evaluation metrics.",
        "focused_node_ids": ["n-model-1", "n-ds-1", "n-gap-1"],
        "reasoning_path": ["GPT-4 Clinical -> MIMIC-III Dataset -> Hallucination & Domain Adaptation Gap"]
    })

@app.get("/api/projects/{pid}/authoring/{stype}")
def get_auth(pid: str, stype: str):
    auth_sec = FALLBACK_DATA.get("authoring_sections", {}).get(pid, FALLBACK_DATA.get("authoring_sections", {}).get("a1b2c3d4-0001-0001-0001-000000000001", {}))
    sec = auth_sec.get(stype, {})
    if not sec:
        sec = {
            "project_id": pid,
            "section_type": stype,
            "title": stype.replace("_", " ").title(),
            "content": f"## {stype.replace('_', ' ').title()}\n\nThis synthesized section integrates grounded evidence from the project paper corpus...",
            "citations": [
                {"citation_id": "c1", "text": "Smith et al. (2024)", "document_id": "d0000001-0000-0000-0000-000000000001"}
            ],
            "updated_at": datetime.now().isoformat()
        }
    return JSONResponse(sec)

@app.post("/api/projects/{pid}/authoring/generate")
def gen_auth(pid: str, body: dict = Body(None)):
    stype = (body or {}).get("section_type", "abstract")
    instructions = (body or {}).get("custom_instructions", "")
    return JSONResponse({
        "project_id": pid,
        "section_type": stype,
        "title": stype.replace("_", " ").title(),
        "content": f"## {stype.replace('_', ' ').title()}\n\n[Synthesized with custom instructions: '{instructions if instructions else 'Standard scholarly synthesis'}']\n\nRecent empirical evaluations across clinical NLP benchmarks demonstrate that specialized domain adaptation yields significant improvements over generic models. Grounded analysis across our document corpus confirms key trade-offs between model scale and privacy compliance.",
        "citations": [
            {"citation_id": "c1", "text": "Smith et al. (2024)", "document_id": "d0000001-0000-0000-0000-000000000001"},
            {"citation_id": "c2", "text": "Singhal et al. (2023)", "document_id": "d0000002-0000-0000-0000-000000000002"}
        ],
        "updated_at": datetime.now().isoformat()
    })

@app.get("/api/projects/{pid}/chat/history")
def get_chat_hist(pid: str):
    hist = IN_MEMORY_STATE["chat_history"].get(pid)
    if hist is None:
        hist = list(FALLBACK_DATA.get("chat_history", {}).get(f"project_{pid}", FALLBACK_DATA.get("chat_history", {}).get("project_a1b2c3d4-0001-0001-0001-000000000001", [])))
        IN_MEMORY_STATE["chat_history"][pid] = hist
    return JSONResponse(hist)

@app.post("/api/projects/{pid}/chat")
def ask_chat(pid: str, body: dict = Body(...)):
    question = body.get("question", "Summarize findings.")
    now = datetime.now().isoformat()
    user_msg = {"role": "user", "message": question, "timestamp": now}
    
    assistant_msg = {
        "role": "assistant",
        "message": f"Based on the grounded analysis of your project documents regarding **\"{question}\"**:\n\n1. **Core Evidence**: GPT-4 and Med-PaLM 2 demonstrate high zero-shot clinical reasoning, with Med-PaLM 2 reaching clinician-level accuracy on 9 benchmarks.\n2. **Identified Constraints**: Hallucination rates in un-grounded note synthesis remain a key safety bottleneck (occurring in ~8.4% of generated summaries).\n3. **Practical Recommendations**: Implementing RAG with dense vector retrieval reduces clinical hallucination by up to 64%.",
        "citations": [
            {
                "document_id": "d0000001-0000-0000-0000-000000000001",
                "filename": "gpt4_clinical_notes_2024.pdf",
                "page": 4,
                "snippet": "GPT-4 models fine-tuned on clinical notes show a 14% improvement in diagnostic reasoning accuracy."
            },
            {
                "document_id": "d0000004-0000-0000-0000-000000000004",
                "filename": "llm_hallucination_clinical_2024.pdf",
                "page": 11,
                "snippet": "Dense RAG retrieval grounding reduced clinical hallucination occurrences from 8.4% to 3.0%."
            }
        ],
        "timestamp": now
    }
    
    if pid not in IN_MEMORY_STATE["chat_history"]:
        IN_MEMORY_STATE["chat_history"][pid] = []
    IN_MEMORY_STATE["chat_history"][pid].append(user_msg)
    IN_MEMORY_STATE["chat_history"][pid].append(assistant_msg)
    
    return JSONResponse(assistant_msg)

@app.delete("/api/projects/{pid}/chat/history")
def clear_chat_history(pid: str):
    IN_MEMORY_STATE["chat_history"][pid] = []
    return JSONResponse({"status": "cleared"})

@app.get("/api/discovery/search")
def search_discovery(request: Request):
    q = request.query_params.get("query", "machine learning").strip()
    return JSONResponse({
        "query": q,
        "results": [
            {
                "paper_id": "arxiv:2403.09911",
                "title": f"Next-Generation {q.title()}: State-of-the-Art Architecture & Benchmarks",
                "authors": ["Dr. Elena Rostova", "Prof. Marcus Thorne"],
                "publication_year": 2025,
                "venue": "arXiv preprint / CS.CL",
                "abstract": f"This survey examines breakthrough methodology, empirical performance, and key open challenges in {q} applications across healthcare and scientific discovery.",
                "url": "https://arxiv.org/abs/2403.09911",
                "pdf_url": "https://arxiv.org/pdf/2403.09911.pdf",
                "citation_count": 58,
                "source": "arXiv"
            },
            {
                "paper_id": "s2:2024.88721",
                "title": f"Empirical Evaluation of {q.title()} Models on Real-World Datasets",
                "authors": ["Chen Wei", "Sarah Al-Mansoor", "David Kim"],
                "publication_year": 2024,
                "venue": "NeurIPS 2024",
                "abstract": f"We conduct extensive empirical evaluations evaluating computational efficiency, memory bounds, and accuracy for {q} techniques.",
                "url": "https://semanticscholar.org/paper/2024.88721",
                "pdf_url": None,
                "citation_count": 142,
                "source": "Semantic Scholar"
            }
        ]
    })

@app.post("/api/projects/{pid}/discovery/import")
@app.post("/api/documents/discovery/import")
def import_discovery_paper(pid: str = "a1b2c3d4-0001-0001-0001-000000000001", body: dict = Body(...)):
    doc_id = f"d-disc-{uuid.uuid4().hex[:8]}"
    now = datetime.now().isoformat()
    paper_title = body.get("title", "Discovered Scientific Paper")
    
    new_doc = {
        "id": doc_id,
        "project_id": pid,
        "filename": f"{paper_title.lower().replace(' ', '_')[:30]}.pdf",
        "title": paper_title,
        "status": "indexed",
        "page_count": 16,
        "chunk_count": 78,
        "error_message": None,
        "created_at": now,
        "updated_at": now
    }
    IN_MEMORY_STATE["documents"].append(new_doc)
    p = find_project(pid)
    if p:
        p["document_count"] = p.get("document_count", 0) + 1
        p["indexed_count"] = p.get("indexed_count", 0) + 1
        
    return JSONResponse(new_doc)

@app.get("/api/documents/{did}/citation")
def get_citation(did: str):
    doc = next((d for d in IN_MEMORY_STATE["documents"] if d["id"] == did), None)
    title = doc["title"] if doc else "Clinical LLM Survey"
    return JSONResponse({
        "document_id": did,
        "bibtex": f"@article{{demo2025,\n  title={{{title}}},\n  author={{Smith, John and Johnson, Alice}},\n  journal={{Journal of AI in Medicine}},\n  year={{2024}}\n}}",
        "apa": f"Smith, J., & Johnson, A. (2024). {title}. Journal of AI in Medicine."
    })

@app.get("/api/projects/{pid}/export/bibtex")
def export_bibtex(pid: str):
    docs = [d for d in IN_MEMORY_STATE["documents"] if d.get("project_id") == pid]
    if not docs:
        docs = IN_MEMORY_STATE["documents"][:3]
    entries = []
    for d in docs:
        entries.append(
            f"@article{{{d['id'][:8]},\n"
            f"  title={{{d['title']}}},\n"
            f"  author={{Research Nexus Authors}},\n"
            f"  year={{2024}},\n"
            f"  journal={{Scientific Research Archive}}\n"
            f"}}\n"
        )
    return PlainTextResponse("\n".join(entries), media_type="text/plain")

@app.get("/api/projects/{pid}/export/ris")
def export_ris(pid: str):
    docs = [d for d in IN_MEMORY_STATE["documents"] if d.get("project_id") == pid]
    if not docs:
        docs = IN_MEMORY_STATE["documents"][:3]
    entries = []
    for d in docs:
        entries.append(
            f"TY  - JOUR\n"
            f"TI  - {d['title']}\n"
            f"AU  - Research Nexus Authors\n"
            f"PY  - 2024\n"
            f"ER  -\n"
        )
    return PlainTextResponse("\n".join(entries), media_type="text/plain")

# Single Document Fallback Endpoints
@app.post("/api/documents/upload")
def upload_doc(file: UploadFile = File(...)):
    return upload_paper_to_project("a1b2c3d4-0001-0001-0001-000000000001", file)

@app.get("/api/documents")
def list_docs():
    return JSONResponse(IN_MEMORY_STATE["documents"])

@app.get("/api/documents/{did}")
def get_doc(did: str):
    d = next((doc for doc in IN_MEMORY_STATE["documents"] if doc["id"] == did), None)
    if not d and IN_MEMORY_STATE["documents"]:
        d = IN_MEMORY_STATE["documents"][0]
    return JSONResponse(d) if d else JSONResponse({"detail": "Not found"}, status_code=404)

@app.post("/api/documents/{did}/process")
def reprocess_doc(did: str):
    d = get_doc(did)
    return d

@app.post("/api/search")
def search_docs(body: dict = Body(...)):
    q = body.get("query", "")
    return JSONResponse({
        "query": q,
        "results": [
            {
                "document_id": "d0000001-0000-0000-0000-000000000001",
                "filename": "gpt4_clinical_notes_2024.pdf",
                "title": "GPT-4 for Automated Clinical Note Generation",
                "score": 0.94,
                "snippet": "Controlled trial evaluating GPT-4 generated notes against physician benchmarks...",
                "page": 3
            },
            {
                "document_id": "d0000002-0000-0000-0000-000000000002",
                "filename": "medpalm2_diagnosis_eval_2023.pdf",
                "title": "Med-PaLM 2: Towards Clinician-Level QA",
                "score": 0.88,
                "snippet": "Med-PaLM 2 achieved 86.5% accuracy on MedQA benchmarks...",
                "page": 7
            }
        ]
    })

@app.post("/api/chat")
def single_doc_chat(body: dict = Body(...)):
    q = body.get("question", "")
    return JSONResponse({
        "answer": f"Based on document context for '{q}', the paper demonstrates significant performance gains when fine-tuning on specialized domain corpora.",
        "citations": [
            {
                "document_id": "d0000001-0000-0000-0000-000000000001",
                "filename": "gpt4_clinical_notes_2024.pdf",
                "page": 5,
                "snippet": "Documentation efficiency improved by 32% with physician-in-the-loop workflows."
            }
        ]
    })

# Catch-all fallback
@app.api_route("/{path_name:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
def catch_all(path_name: str):
    return JSONResponse(status_code=200, content={"mocked": True, "message": f"Fallback route served for /{path_name}."})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
