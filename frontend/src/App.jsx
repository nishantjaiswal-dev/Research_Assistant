import { useCallback, useEffect, useRef, useState } from "react";
import Sidebar from "./components/Sidebar.jsx";
import ChatPanel from "./components/ChatPanel.jsx";
import SearchPanel from "./components/SearchPanel.jsx";
import ProjectsApp from "./components/projects/ProjectsApp.jsx";
import { listDocuments, detectDemoMode } from "./services/api.js";

const ACTIVE_STATUSES = new Set(["uploaded", "extracting", "chunking", "embedding"]);

export default function App() {
  const [mode, setMode] = useState("single"); // "single" | "projects"
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedId, setSelectedId] = useState(null);
  const [searchOpen, setSearchOpen] = useState(false);
  // "connecting" while we wait for the backend, "ready" once health check passes
  const [startupState, setStartupState] = useState("connecting");
  const pollRef = useRef(null);

  // ── Auto-connect to local .dat demo on startup ─────────────────────────────
  useEffect(() => {
    let cancelled = false;
    (async () => {
      const isDemo = await detectDemoMode();
      if (cancelled) return;
      if (isDemo) {
        // Automatically land on Research Projects for the richest demo experience
        setMode("projects");
      }
      setStartupState("ready");
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const refresh = useCallback(async () => {
    try {
      const docs = await listDocuments();
      setDocuments(docs);
      return docs;
    } catch {
      return [];
    }
  }, []);

  useEffect(() => {
    if (startupState !== "ready") return; // wait until backend is confirmed up
    (async () => {
      const docs = await refresh();
      setLoading(false);
      if (docs.length > 0) setSelectedId(docs[0].id);
    })();
  }, [refresh, startupState]);

  // Poll while any document is still processing, so the status track
  // updates live without the user refreshing the page.
  useEffect(() => {
    const hasActive = documents.some((d) => ACTIVE_STATUSES.has(d.status));
    if (hasActive && !pollRef.current) {
      pollRef.current = setInterval(refresh, 1800);
    }
    if (!hasActive && pollRef.current) {
      clearInterval(pollRef.current);
      pollRef.current = null;
    }
    return () => {
      if (pollRef.current) {
        clearInterval(pollRef.current);
        pollRef.current = null;
      }
    };
  }, [documents, refresh]);

  async function handleUploaded(uploadResult) {
    await refresh();
    setSelectedId(uploadResult.id);
  }

  const selectedDocument = documents.find((d) => d.id === selectedId) ?? null;

  // ── Startup connection splash ──────────────────────────────────────────────
  if (startupState === "connecting") {
    return (
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          height: "100vh",
          gap: 24,
          background: "var(--color-paper, #fafaf9)",
        }}
      >
        <div style={{ textAlign: "center" }}>
          <div style={{ fontSize: 48, marginBottom: 16 }}>🔬</div>
          <p
            style={{
              fontFamily: "var(--font-display, serif)",
              fontSize: "1.25rem",
              fontWeight: 600,
              color: "var(--color-ink, #1c1917)",
              marginBottom: 8,
            }}
          >
            Research Nexus
          </p>
          <p
            style={{
              fontFamily: "monospace",
              fontSize: "0.7rem",
              letterSpacing: "0.15em",
              textTransform: "uppercase",
              color: "#15803d",
            }}
          >
            Connecting to local .dat demo…
          </p>
          <div style={{ width: 240, margin: "20px auto 0" }}>
            <div
              style={{
                height: 3,
                borderRadius: 9999,
                background:
                  "linear-gradient(90deg, #15803d 0%, #22c55e 50%, #15803d 100%)",
                backgroundSize: "200% 100%",
                animation: "rn-slide 1.4s linear infinite",
              }}
            />
          </div>
          <style>{`
            @keyframes rn-slide {
              0%   { background-position: 0%   50%; }
              100% { background-position: 200% 50%; }
            }
          `}</style>
        </div>
        <p
          style={{
            maxWidth: 300,
            textAlign: "center",
            fontFamily: "var(--font-body, sans-serif)",
            fontSize: "0.875rem",
            color: "var(--color-muted, #78716c)",
          }}
        >
          Waiting for the mock API server to start. This only takes a few seconds
          on the first run.
        </p>
      </div>
    );
  }

  return (
    <div className="flex h-screen flex-col bg-paper">
      <div className="flex shrink-0 items-center gap-1 border-b border-line bg-paper px-4 py-2">
        <ModeTab active={mode === "single"} onClick={() => setMode("single")}>
          Single Document
        </ModeTab>
        <ModeTab active={mode === "projects"} onClick={() => setMode("projects")}>
          Research Projects
        </ModeTab>
      </div>

      <div className="min-h-0 flex-1">
        {mode === "projects" ? (
          <ProjectsApp />
        ) : (
          <div className="flex h-full">
            <Sidebar
              documents={documents}
              selectedId={selectedId}
              onSelect={setSelectedId}
              onUploaded={handleUploaded}
              loading={loading}
            />

            <main className="flex min-w-0 flex-1 flex-col">
              <header className="flex items-center justify-between border-b border-line px-8 py-4">
                <div>
                  <p className="font-display text-lg text-ink">
                    {selectedDocument
                      ? selectedDocument.title || selectedDocument.filename
                      : "No paper selected"}
                  </p>
                  {selectedDocument && (
                    <p className="font-mono text-[11px] uppercase tracking-wide text-muted">
                      {selectedDocument.status}
                    </p>
                  )}
                </div>
                <button
                  onClick={() => setSearchOpen(true)}
                  className="rounded-md border border-line px-3 py-1.5 font-mono text-xs uppercase tracking-wide text-pine-700 hover:border-pine-400"
                >
                  Semantic search
                </button>
              </header>

              <ChatPanel selectedDocument={selectedDocument} />
            </main>

            {searchOpen && (
              <SearchPanel
                selectedDocument={selectedDocument}
                documents={documents}
                onClose={() => setSearchOpen(false)}
              />
            )}
          </div>
        )}
      </div>
    </div>
  );
}

function ModeTab({ active, onClick, children }) {
  return (
    <button
      onClick={onClick}
      className={`rounded-md px-3 py-1.5 font-mono text-xs uppercase tracking-wide transition-colors ${
        active ? "bg-pine-600 text-paper" : "text-muted hover:bg-pine-50 hover:text-pine-700"
      }`}
    >
      {children}
    </button>
  );
}
