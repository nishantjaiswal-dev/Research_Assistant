# 🔬 Research Nexus — Research Intelligence Core & Manuscript Authoring Platform

> A full-stack AI-powered research assistant that turns a collection of academic PDFs into an interactive knowledge engine — with literature matrices, multi-paper comparison, gap analysis, visual knowledge graphs, and AI-authored manuscript sections.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Feature Highlights](#feature-highlights)
- [Demo Mode (No Setup Required)](#demo-mode-no-setup-required)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Feature Deep-Dive](#feature-deep-dive)
  - [1. Research Projects](#1-research-projects)
  - [2. Paper Management](#2-paper-management)
  - [3. Overview Dashboard](#3-overview-dashboard)
  - [4. Literature Matrix](#4-literature-matrix)
  - [5. Multi-Paper Comparison](#5-multi-paper-comparison)
  - [6. Gap Analysis & Research Questions](#6-gap-analysis--research-questions)
  - [7. Paper Intelligence](#7-paper-intelligence)
  - [8. Project Knowledge Explorer](#8-project-knowledge-explorer)
  - [9. Visual Knowledge Graph](#9-visual-knowledge-graph)
  - [10. AI Manuscript Authoring](#10-ai-manuscript-authoring)
  - [11. Multi-Turn Project Chat](#11-multi-turn-project-chat)
  - [12. Literature Discovery](#12-literature-discovery)
  - [13. Single-Document Mode](#13-single-document-mode)
- [API Reference](#api-reference)
- [ML & AI Subsystems](#ml--ai-subsystems)
- [Production Setup](#production-setup)
- [Environment Variables](#environment-variables)
- [Running Tests](#running-tests)
- [Changelog](#changelog)

---

## Overview

**Research Nexus** is a full-stack research intelligence platform built for academic researchers, scientists, and knowledge workers. Upload a collection of scholarly PDFs and get:

- Automatic extraction of entities, claims, limitations, methodologies, and findings
- Side-by-side structured comparison across any combination of papers
- AI-identified research gaps with evidence quotes
- An interactive, physics-based visual knowledge graph
- AI-authored manuscript sections (abstract, introduction, related work, etc.) grounded in your actual papers
- A multi-turn chat assistant with inline source citations

The platform runs in two modes:
| Mode | Backend | Database | LLM | Use case |
|------|---------|----------|-----|----------|
| **Demo** | Mock FastAPI (local `.dat`) | None | None | Try all features offline, zero setup |
| **Production** | FastAPI + asyncpg | Supabase (pgvector) | Claude / OpenAI | Real research workloads |

---

## Feature Highlights

| # | Feature | Description |
|---|---------|-------------|
| 1 | **Research Projects** | Group papers around a research topic; manage multiple projects |
| 2 | **PDF Ingestion** | Upload PDFs; auto-extract text, chunk, embed, and index |
| 3 | **Overview Dashboard** | Live metrics: paper count, indexed count, topic distribution |
| 4 | **Literature Matrix** | 8-dimension structured comparison table with grounding sources |
| 5 | **Multi-Paper Comparison** | N-way deep comparison with evidence drawer and citation tracing |
| 6 | **Gap Analysis** | 6-category gap detection with verbatim evidence quotes |
| 7 | **Research Questions** | Auto-generated targeted research questions from gaps |
| 8 | **Paper Intelligence** | Per-paper: sections, entities, keyphrases, claims, limitations, topics |
| 9 | **Knowledge Explorer** | Project-level entity and topic aggregation with detail panels |
| 10 | **Visual Knowledge Graph** | Interactive ReactFlow graph: 14 node types, 13 edge types, physics controls |
| 11 | **AI Manuscript Authoring** | 6 section types generated with grounded citations from your corpus |
| 12 | **Project Chat** | Multi-turn RAG assistant with source highlights |
| 13 | **Literature Discovery** | Search arXiv and Semantic Scholar; import results into projects |
| 14 | **Citation Export** | BibTeX and RIS export for your entire project |
| 15 | **Single-Doc Mode** | Upload, chat, and semantic-search a single document |
| 16 | **Demo Mode** | One-command offline demo from local `.dat` — no API keys needed |

---

## Demo Mode (No Setup Required)

Run the full application offline with pre-loaded demo data. **No database, no API keys, no cloud.**

### Quick start

```bash
# Windows
python run_demo.py

# or double-click
launch_demo.bat

# macOS / Linux
bash launch_demo.sh
```

The launcher will:
1. Generate `backend/fallback_demo.dat` if it doesn't exist
2. Start the mock API server on **http://localhost:8000**
3. Start the Vite frontend on **http://localhost:5173**
4. Open the browser automatically
5. Auto-detect demo mode and switch straight to the **Research Projects** view with data pre-loaded

Stop with `Ctrl+C`.

### What demo data includes

The `fallback_demo.dat` dataset covers **100% of all platform features**:

- **2 research projects** — *LLMs in Healthcare* (5 papers) and *Federated Learning* (3 papers)
- **8 papers** with full scholarly metadata, page counts, chunk counts
- **Literature matrix** with 8 dimensions and grounding sources
- **3-way and 2-way paper comparisons** with evidence citations
- **6 research gaps** across 6 categories with verbatim evidence quotes
- **Auto-generated research questions**
- **Deep paper intelligence** for each document (sections, entities, keyphrases, claims, limitations, topics)
- **Project knowledge aggregation** with entity and topic detail pages
- **Visual knowledge graph** — 25+ nodes, 30+ typed edges
- **6 manuscript sections** with grounded citations (abstract, introduction, related work, methodology comparison, research gaps, conclusion)
- **Multi-turn chat history** with grounded answers and source snippets
- **Literature discovery results** from arXiv and Semantic Scholar
- **System health** and ML model registry data

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Browser / Frontend                    │
│  React 18 + Vite + @xyflow/react + TailwindCSS          │
│                                                         │
│  App.jsx ──► ProjectsApp ──► ProjectWorkspace           │
│                              └── 12 feature tabs        │
│                                                         │
│  api.js  ──► /api/* (proxied by Vite dev server)        │
└────────────────────────────┬────────────────────────────┘
                             │ HTTP/JSON (REST)
          ┌──────────────────▼──────────────────┐
          │          FastAPI Backend             │
          │   uvicorn · asyncpg · Python 3.12   │
          │                                     │
          │  ┌─────────┐  ┌──────────────────┐  │
          │  │  API    │  │    Services       │  │
          │  │ Routes  │  │                  │  │
          │  │ projects│  │ PDF processor    │  │
          │  │ docs    │  │ Chunker          │  │
          │  │ intel.  │  │ Embeddings       │  │
          │  │ research│  │ RAG / Retrieval  │  │
          │  │ chat    │  │ LLM Provider     │  │
          │  │ discovery  │ Scientific ML    │  │
          │  │ health  │  │  ├ Entity extractor│ │
          │  └─────────┘  │  ├ Keyphrase      │ │
          │               │  ├ Section class. │ │
          │               │  ├ Claim extract. │ │
          │               │  ├ Topic model    │ │
          │               │  └ Model registry │ │
          │               └──────────────────┘  │
          └──────────────────┬──────────────────┘
                             │
              ┌──────────────▼──────────────┐
              │   Supabase (PostgreSQL)      │
              │   + pgvector extension       │
              │   Vector similarity search   │
              └─────────────────────────────┘

  ─ ─ ─ Demo Mode ─ ─ ─
  FastAPI backend is replaced by mock_server.py
  which loads all data from fallback_demo.dat
  No database or LLM keys required.
```

---

## Tech Stack

### Backend
| Component | Technology |
|-----------|-----------|
| Web framework | **FastAPI 0.115** + Uvicorn |
| Database | **PostgreSQL** via **asyncpg 0.30** (Supabase hosted) |
| Vector search | **pgvector** (stored as `embedding vector(384)`) |
| PDF parsing | **PyMuPDF 1.25** |
| Embeddings | **sentence-transformers 3.3** (`all-MiniLM-L6-v2` default) |
| LLM | **Anthropic Claude** / **OpenAI** (provider-agnostic abstraction) |
| Keyphrase extraction | **KeyBERT 0.8** |
| Topic modelling | **BERTopic 0.16** |
| NER | **spaCy 3.8** (`en_core_web_sm`) + domain gazetteer |
| Fuzzy matching | **rapidfuzz 3.11** |
| Config | **pydantic-settings 2.7** |

### Frontend
| Component | Technology |
|-----------|-----------|
| UI framework | **React 18** |
| Build tool | **Vite 6** |
| Graph visualization | **@xyflow/react 12** (ReactFlow) |
| Styling | **TailwindCSS 3** |
| API layer | Custom `fetch`-based `api.js` |

### Demo / Offline
| Component | Technology |
|-----------|-----------|
| Mock server | **FastAPI** loading `fallback_demo.dat` |
| Demo data | `generate_fallback.py` → `fallback_demo.dat` (JSON) |
| Launcher | `run_demo.py` (Python), `launch_demo.bat` (Windows), `launch_demo.sh` (Unix) |

---

## Project Structure

```
Research_Assistant/
├── run_demo.py               # One-command demo launcher
├── launch_demo.bat           # Windows double-click launcher
├── launch_demo.sh            # macOS/Linux launcher
├── package.json              # Root npm scripts (demo, mock-server, etc.)
│
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI app entry point + lifespan
│   │   ├── api/              # Route handlers
│   │   │   ├── projects.py
│   │   │   ├── documents.py
│   │   │   ├── intelligence.py
│   │   │   ├── research.py
│   │   │   ├── chat.py
│   │   │   ├── discovery.py
│   │   │   ├── search.py
│   │   │   └── health.py
│   │   ├── core/
│   │   │   ├── config.py     # Pydantic-settings config
│   │   │   ├── database.py   # asyncpg connection pool
│   │   │   └── exceptions.py
│   │   ├── models/
│   │   │   └── schemas.py    # Pydantic request/response models
│   │   └── services/         # Business logic
│   │       ├── pdf_processor.py
│   │       ├── chunker.py
│   │       ├── embeddings.py
│   │       ├── retrieval.py
│   │       ├── rag.py
│   │       ├── llm_provider.py
│   │       ├── knowledge_graph.py
│   │       ├── literature_matrix.py
│   │       ├── comparison.py
│   │       ├── gap_analysis.py
│   │       ├── research_questions.py
│   │       ├── scientific_extraction.py
│   │       ├── authoring.py
│   │       ├── project_chat.py
│   │       ├── discovery.py
│   │       ├── citations.py
│   │       ├── analytics.py
│   │       └── ml/           # Local ML models
│   │           ├── entity_extraction.py
│   │           ├── claim_extraction.py
│   │           ├── keyphrase.py
│   │           ├── section_classifier.py
│   │           ├── topic_model.py
│   │           ├── gazetteer.py
│   │           └── model_registry.py
│   ├── mock_server.py        # Offline demo FastAPI server (loads .dat)
│   ├── generate_fallback.py  # Generates fallback_demo.dat
│   ├── fallback_demo.dat     # Pre-built demo dataset (JSON)
│   ├── tests/                # pytest test suite (41 tests)
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx           # Root component + demo auto-connect
│   │   ├── services/
│   │   │   └── api.js        # All API calls + demo-mode helpers
│   │   └── components/
│   │       ├── Sidebar.jsx
│   │       ├── ChatPanel.jsx
│   │       ├── SearchPanel.jsx
│   │       ├── UploadArea.jsx
│   │       ├── StatusTrack.jsx
│   │       └── projects/
│   │           ├── ProjectsApp.jsx
│   │           ├── ProjectWorkspace.jsx
│   │           └── tabs/
│   │               ├── OverviewTab.jsx
│   │               ├── PapersTab.jsx
│   │               ├── MatrixTab.jsx
│   │               ├── CompareTab.jsx
│   │               ├── GapsTab.jsx
│   │               ├── IntelligenceTab.jsx
│   │               ├── KnowledgeTab.jsx
│   │               ├── VisualKnowledgeGraph.jsx
│   │               ├── AuthoringTab.jsx
│   │               ├── AssistantTab.jsx
│   │               ├── DiscoveryTab.jsx
│   │               └── InsightsTab.jsx
│   ├── vite.config.js        # Vite + /api proxy to :8000
│   └── package.json
│
└── supabase/
    └── migrations/           # pgvector schema migrations
```

---

## Feature Deep-Dive

### 1. Research Projects

Create named research projects to group related papers. Each project tracks:
- Total paper count and indexed count
- Creation and last-updated timestamps
- Project description

**API:** `GET/POST /api/projects`, `GET/PATCH/DELETE /api/projects/{id}`

---

### 2. Paper Management

Upload PDFs directly into a project. The pipeline runs automatically:

1. **PDF Parsing** — PyMuPDF extracts text page-by-page
2. **Chunking** — Sliding window at 400 tokens, 80-token overlap
3. **Embedding** — sentence-transformers encodes each chunk to a 384-dim vector
4. **Indexing** — Vectors stored in Supabase with pgvector
5. **Metadata Extraction** — Title, authors, publication year, venue, abstract, DOI extracted via LLM

**API:** `POST /api/projects/{id}/documents` (multipart), `GET /api/projects/{id}/documents`

---

### 3. Overview Dashboard

Live project summary card showing:
- Paper and chunk counts
- Indexed vs. total breakdown
- Topic distribution pie chart
- Recent activity timeline
- Quick-action buttons (Analyze, Export)

---

### 4. Literature Matrix

An 8-dimension structured comparison table across all papers in the project:

| Dimension | Description |
|-----------|-------------|
| **Methodology** | Research approach and experimental design |
| **Dataset** | Training/evaluation datasets used |
| **Model / Algorithm** | Core technical contribution |
| **Metric** | Evaluation metrics reported |
| **Performance** | Quantitative results |
| **Limitations** | Stated constraints and caveats |
| **Application Domain** | Target use case / domain |
| **Future Work** | Directions identified by authors |

Each cell includes grounding source references back to the original paper.

**API:** `GET /api/projects/{id}/literature-matrix`

---

### 5. Multi-Paper Comparison

Select 2–N papers for deep structured side-by-side comparison. Features:
- **Evidence drawer** — expand any comparison point to see the verbatim passage it came from
- **Citation tracing** — each evidence item links to the source document and page
- **Highlighted differences** — visual emphasis on where papers diverge
- **3-way comparison** supported out of the box

**API:** `POST /api/projects/{id}/compare` with `{ document_ids: [...] }`

---

### 6. Gap Analysis & Research Questions

Automatically identifies what **hasn't been solved yet** across your paper collection:

**6 gap categories:**
- 📊 **Methodological** — gaps in approaches and techniques
- 📈 **Empirical** — missing experiments or evaluation scenarios
- 🌐 **Domain** — underexplored application domains
- ⚡ **Scalability** — performance and efficiency gaps
- 🔒 **Ethical / Safety** — bias, fairness, privacy concerns
- 🔀 **Integration** — gaps in combining techniques

Each gap includes:
- A descriptive title and explanation
- Verbatim evidence quotes from the papers
- A confidence score
- Source document and page references

**Research Questions** are auto-generated from identified gaps — each question is targeted, specific, and grounded.

**API:** `POST /api/projects/{id}/gap-analysis`, `POST /api/projects/{id}/research-questions`

---

### 7. Paper Intelligence

Per-paper deep analysis panel. Select any paper in your project to see:

| Component | Details |
|-----------|---------|
| **Section Breakdown** | Abstract, Introduction, Methods, Results, Discussion, Conclusion detected via heading patterns + embedding fallback |
| **Named Entities** | Models, datasets, methods, metrics, domains, tasks extracted via domain gazetteer + spaCy |
| **Keyphrases** | Top 10 keyphrases via KeyBERT (reuses the same embedding model) |
| **Claims** | Key factual assertions extracted and normalized via LLM |
| **Limitations** | Author-stated and inferred limitations |
| **Topics** | BERTopic cluster labels for this paper |
| **Relationships** | Cross-paper entity relationships |

**API:** `GET /api/documents/{id}/intelligence`, `POST /api/documents/{id}/analyze`

---

### 8. Project Knowledge Explorer

Aggregates intelligence across all papers in a project:

- **Entity browser** — filter by type (model, dataset, method, metric, domain, task, concept); click any entity for a detail panel showing which papers mention it and in what context
- **Topic explorer** — BERTopic clusters across the whole corpus; click a topic to see constituent papers and key terms
- **Relationship graph** — mini force-directed graph of entity co-occurrences

**API:** `GET /api/projects/{id}/knowledge`, `GET /api/projects/{id}/entities`, `GET /api/projects/{id}/topics`

---

### 9. Visual Knowledge Graph

A fully interactive, physics-based research knowledge graph powered by **@xyflow/react (ReactFlow)**.

#### Node Types (14)
| Type | Icon | Color | Description |
|------|------|-------|-------------|
| Paper | 📄 | Green | Research papers |
| Author | 👤 | Blue | Paper authors |
| Topic | 🔬 | Purple | Research topics |
| Model | 🤖 | Rose | ML models (GPT-4, BERT, etc.) |
| Algorithm | 🧮 | Teal | Core algorithms |
| Dataset | 📊 | Amber | Training/eval datasets |
| Method | ⚙️ | Emerald | Research methodologies |
| Metric | 📏 | Indigo | Evaluation metrics |
| Domain | 🌐 | Yellow | Application domains |
| Task | ✅ | Green | Research tasks |
| Concept | 💡 | Slate | Abstract concepts |
| Gap | ⚠️ | Orange | Identified research gaps |
| Finding | 🔍 | Sky | Key findings |
| Question | ❓ | Violet | Research questions |

#### Edge Types (13)
`flows_to` · `compares_with` · `written_by` · `studies` · `discusses` · `uses` · `proposes` · `evaluates_on` · `reports` · `has_limitation` · `addresses` · `related_to` · `extends`

#### View Modes
| Mode | Description |
|------|-------------|
| **Literature Flow** | Papers arranged as a sequential pipeline with methodology flow |
| **Full Network** | All node types in a physics-simulated force-directed graph |

#### Interactive Controls
- **Filter panel** — show/hide any combination of node types
- **Search** — fuzzy-search nodes by label; matching nodes highlighted
- **Node inspector** — click any node to see full metadata panel
- **Edge inspector** — click any edge to see relationship details
- **Physics panel** — adjust repulsion force, link strength, collision radius live
- **AI query** — ask a natural language question about the graph (e.g. *"Which models are evaluated on MIMIC-III?"*)
- **Export** — download graph as PNG or JSON
- **Fit / Reset** — one-click layout reset
- **MiniMap** — bird's-eye navigation panel

**API:** `GET /api/projects/{id}/graph`, `POST /api/projects/{id}/graph/query`

---

### 10. AI Manuscript Authoring

Generate full manuscript sections grounded entirely in your project's papers.

**6 section types:**

| Section | Purpose |
|---------|---------|
| **Abstract** | Concise summary of the collective research |
| **Introduction** | Background, motivation, and scope |
| **Related Work** | Systematic review with in-text citations |
| **Methodology Comparison** | Structured comparison of approaches |
| **Research Gaps** | Synthesis of open problems |
| **Conclusion** | Summary, contributions, future directions |

Each section is:
- Grounded in evidence from your actual paper corpus (not hallucinated)
- Accompanied by inline citation markers linked to source documents
- Editable with custom instructions (e.g. *"write for a clinical audience"*)
- Cached and re-generatable on demand

**API:** `GET /api/projects/{id}/authoring/{section_type}`, `POST /api/projects/{id}/authoring/generate`

---

### 11. Multi-Turn Project Chat

A full RAG-powered conversational assistant over your entire project corpus:

- **Multi-turn memory** — conversation history maintained per project
- **Dense retrieval** — top-k chunk retrieval via pgvector similarity search
- **Grounded answers** — every response includes citations with document name, page, and verbatim snippet
- **Source highlighting** — click any citation to open the source passage
- **History management** — clear history or review full conversation timeline

**API:** `POST /api/projects/{id}/chat`, `GET /api/projects/{id}/chat/history`

---

### 12. Literature Discovery

Search external academic databases without leaving the app:

- **arXiv** integration — search the open-access preprint server
- **Semantic Scholar** integration — 200M+ papers with citation counts
- **Unified results** — combined view with title, authors, year, venue, abstract, and links
- **One-click import** — add any discovered paper directly into your project
- **PDF auto-import** — papers with open-access PDFs are downloaded and indexed automatically

**API:** `GET /api/discovery/search?query=...&source=arxiv|s2|all`, `POST /api/projects/{id}/discovery/import`

---

### 13. Single-Document Mode

Lightweight mode for working with a single PDF:

- **Upload** — drag-and-drop or click-to-browse
- **Processing status** — live status track: uploading → extracting → chunking → embedding → indexed
- **Semantic search** — vector similarity search over the document's chunks
- **Document chat** — ask questions grounded in that single document
- **Citation export** — APA, BibTeX formats

**API:** `POST /api/documents/upload`, `POST /api/search`, `POST /api/chat`

---

## API Reference

### Health
| Method | Endpoint | Description |
|--------|---------|-------------|
| GET | `/api/health` | System health + demo_mode flag |
| GET | `/api/system/ml-info` | Loaded ML model registry |

### Projects
| Method | Endpoint | Description |
|--------|---------|-------------|
| GET | `/api/projects` | List all projects |
| POST | `/api/projects` | Create project |
| GET | `/api/projects/{id}` | Get project |
| PATCH | `/api/projects/{id}` | Update project |
| DELETE | `/api/projects/{id}` | Delete project |
| GET | `/api/projects/{id}/analytics` | Project analytics |

### Documents
| Method | Endpoint | Description |
|--------|---------|-------------|
| POST | `/api/projects/{id}/documents` | Upload PDF to project |
| GET | `/api/projects/{id}/documents` | List project documents |
| DELETE | `/api/projects/{id}/documents/{did}` | Remove paper |
| GET | `/api/documents/{id}/intelligence` | Paper deep analysis |
| POST | `/api/documents/{id}/analyze` | Trigger analysis job |
| GET | `/api/documents/{id}/citation` | Get citation formats |

### Research Intelligence
| Method | Endpoint | Description |
|--------|---------|-------------|
| GET | `/api/projects/{id}/literature-matrix` | Literature matrix |
| POST | `/api/projects/{id}/compare` | Multi-paper comparison |
| POST | `/api/projects/{id}/gap-analysis` | Gap analysis |
| POST | `/api/projects/{id}/research-questions` | Research questions |
| GET | `/api/projects/{id}/knowledge` | Project knowledge |
| GET | `/api/projects/{id}/entities` | Entity list |
| GET | `/api/projects/{id}/entities/{eid}` | Entity detail |
| GET | `/api/projects/{id}/topics` | Topic list |
| GET | `/api/projects/{id}/topics/{tid}` | Topic detail |

### Knowledge Graph
| Method | Endpoint | Description |
|--------|---------|-------------|
| GET | `/api/projects/{id}/graph` | Full graph data (nodes + edges) |
| POST | `/api/projects/{id}/graph/query` | AI graph query |

### Authoring & Chat
| Method | Endpoint | Description |
|--------|---------|-------------|
| GET | `/api/projects/{id}/authoring/{section}` | Get section |
| POST | `/api/projects/{id}/authoring/generate` | Generate section |
| POST | `/api/projects/{id}/chat` | Ask question |
| GET | `/api/projects/{id}/chat/history` | Get history |
| DELETE | `/api/projects/{id}/chat/history` | Clear history |

### Discovery & Export
| Method | Endpoint | Description |
|--------|---------|-------------|
| GET | `/api/discovery/search` | Search arXiv / S2 |
| POST | `/api/projects/{id}/discovery/import` | Import paper |
| GET | `/api/projects/{id}/export/bibtex` | Download BibTeX |
| GET | `/api/projects/{id}/export/ris` | Download RIS |

---

## ML & AI Subsystems

### Embedding Model
Default: `sentence-transformers/all-MiniLM-L6-v2` (384 dimensions)  
Compatible with any sentence-transformers model — just update `EMBEDDING_MODEL_NAME` and `EMBEDDING_DIMENSION` in `.env`.

Supported alternatives:
- `BAAI/bge-small-en-v1.5` — higher quality, same dimension
- `allenai/specter2` — domain-tuned for scientific papers (768-dim)
- `malteos/scincl` — citation-informed scientific embeddings

### LLM Provider
Provider-agnostic abstraction in `llm_provider.py`. Switch between:
- **Anthropic Claude** (`claude-sonnet-4-6` default)
- **OpenAI** (`gpt-4o`, `gpt-4-turbo`, etc.)
- **Mock** (offline, clearly labeled — used in tests)

### Scientific ML Models
| Model | Library | Purpose |
|-------|---------|---------|
| KeyBERT | keybert | Keyphrase extraction (reuses embedding model) |
| BERTopic | bertopic | Topic clustering across corpus |
| spaCy `en_core_web_sm` | spacy | NER candidate generation |
| Domain Gazetteer | rapidfuzz | Exact + fuzzy match for ML/AI entities |
| Section Classifier | custom | Heading-pattern + embedding-similarity section detection |
| Claim Extractor | LLM | Normalized factual claim extraction |

---

## Production Setup

### Prerequisites

- Python 3.12+
- Node.js 20+
- A Supabase project (free tier works)
- An LLM API key (Anthropic or OpenAI)

### 1. Clone and install

```bash
git clone https://github.com/nishantjaiswal-dev/Research_Assistant
cd Research_Assistant

# Backend
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate    # macOS/Linux
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# Frontend
cd ../frontend
npm install
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env with your values (see Environment Variables section below)
```

### 3. Run database migrations

Apply the Supabase migration to enable pgvector and create all tables:

```bash
# Via Supabase dashboard: SQL Editor → paste content of supabase/migrations/*.sql
# Or via Supabase CLI:
supabase db push
```

### 4. Start the application

```bash
# Terminal 1 — Backend
cd backend
uvicorn app.main:app --reload --port 8000

# Terminal 2 — Frontend
cd frontend
npm run dev
```

Open **http://localhost:5173**

---

## Environment Variables

Create `backend/.env` (copy from `.env.example`):

```env
# ── Database ──────────────────────────────────────────────
DATABASE_URL=postgresql://postgres.YOURREF:PASSWORD@aws-0-REGION.pooler.supabase.com:5432/postgres
SUPABASE_URL=https://YOURREF.supabase.co
SUPABASE_KEY=your-supabase-anon-key

# ── LLM Provider ──────────────────────────────────────────
LLM_PROVIDER=anthropic          # anthropic | openai
LLM_API_KEY=sk-ant-...
LLM_MODEL=claude-sonnet-4-6    # or gpt-4o, gpt-4-turbo

# ── Embeddings ────────────────────────────────────────────
EMBEDDING_MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_DIMENSION=384

# ── App ───────────────────────────────────────────────────
CORS_ORIGINS=http://localhost:5173
ENVIRONMENT=development

# ── ML / Phase 3 ──────────────────────────────────────────
ML_DEVICE=cpu                   # cpu | cuda
ENABLE_SPACY_CANDIDATES=true
```

> **Demo mode** requires none of the above — just run `python run_demo.py`.

---

## Running Tests

```bash
cd backend
pytest tests/ -v
```

41 tests across all service layers:
- `test_knowledge_graph.py` — graph construction, subgraph filtering, hub detection
- `test_literature_matrix.py` — matrix generation, dimension coverage
- `test_comparison_validation.py` — comparison result validation
- `test_gap_analysis.py` — gap categorization, evidence linking
- `test_claim_extraction.py` — claim and limitation extraction
- `test_entity_extraction.py` — gazetteer matching, spaCy NER
- `test_scientific_extraction.py` — full pipeline integration
- `test_section_classifier.py` — heading detection, embedding fallback
- `test_project_knowledge.py` — knowledge aggregation
- `test_project_chat.py` — RAG pipeline, citation tracing
- `test_projects_api.py` — project CRUD API
- `test_discovery.py` — external search integration
- `test_authoring.py` — manuscript section generation
- `test_citations.py` — citation format generation

---

## Changelog

See [CHANGELOG.md](./CHANGELOG.md) for a full phase-by-phase history.

### Recent additions
- **v2.0.0** — Enhanced Visual Knowledge Graph (14 node types, AI query, physics controls, export), standalone demo launcher with auto-connect, `waitForBackend()` / `detectDemoMode()` helpers for zero-click startup
- **v1.3.0** — Knowledge Graph tab with @xyflow/react
- **v1.2.0** — AI Manuscript Authoring (6 sections), Citation export (BibTeX/RIS)
- **v1.1.0** — Paper Intelligence, Project Knowledge Explorer, Literature Discovery
- **v1.0.0** — Research Projects, Literature Matrix, Comparison, Gap Analysis, Project Chat

---

## License

MIT — see [LICENSE](./LICENSE) for details.

---

*Built with ❤️ for researchers who have too many papers and too little time.*
