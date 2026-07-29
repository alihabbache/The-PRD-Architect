import { useGeneratePRD } from "@/hooks/useGeneratePRD"
import { ConceptForm } from "@/components/ConceptForm"
import { AgentProgressCard } from "@/components/AgentProgressCard"
import { PRDViewer } from "@/components/PRDViewer"
import { Button } from "@/components/ui/button"
import { RotateCcw } from "lucide-react"

const AGENTS = [
  {
    key: "market_researcher" as const,
    name: "Market Researcher",
    description: "Analyses the target market, maps competitors, and builds user personas.",
  },
  {
    key: "ux_specifier" as const,
    name: "UX Specifier",
    description: "Translates personas into detailed user journeys and interaction flows.",
  },
  {
    key: "technical_translator" as const,
    name: "Technical Translator",
    description: "Converts user journeys into Gherkin acceptance criteria ready for dev.",
  },
]

export default function App() {
  const { agents, isLoading, result, error, generate, reset } = useGeneratePRD()

  const hasStarted = Object.values(agents).some((s) => s !== "idle")

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-white">
      <div className="mx-auto max-w-3xl px-4 py-12 space-y-10">

        {/* Header */}
        <header className="text-center space-y-3">
          <div className="inline-flex items-center gap-2 rounded-full border border-indigo-200 bg-indigo-50 px-4 py-1.5 text-xs font-medium text-indigo-700">
            Multi-Agent · LangGraph · Groq / Ollama
          </div>
          <h1 className="text-4xl font-bold tracking-tight text-slate-900">
            PRD Architect
          </h1>
          <p className="text-slate-500 max-w-lg mx-auto">
            Describe your product concept. Three specialised AI agents will research the market,
            define user journeys, and write acceptance criteria — producing a full PRD in seconds.
          </p>
        </header>

        {/* Input form — hide while running or done */}
        {!hasStarted && (
          <section>
            <ConceptForm onSubmit={generate} isLoading={isLoading} />
          </section>
        )}

        {/* Agent progress cards */}
        {hasStarted && (
          <section className="space-y-3">
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-medium text-slate-500 uppercase tracking-wider">
                Agent Pipeline
              </h2>
              {!isLoading && (
                <Button variant="ghost" size="sm" onClick={reset}>
                  <RotateCcw className="h-3.5 w-3.5" />
                  New concept
                </Button>
              )}
            </div>
            <div className="space-y-3">
              {AGENTS.map((a) => (
                <AgentProgressCard
                  key={a.key}
                  name={a.name}
                  description={a.description}
                  status={agents[a.key]}
                />
              ))}
            </div>
          </section>
        )}

        {/* Error */}
        {error && (
          <div className="rounded-xl border border-red-200 bg-red-50 px-6 py-4 text-sm text-red-700">
            <strong>Error:</strong> {error}
          </div>
        )}

        {/* PRD Output */}
        {result && (
          <section>
            <PRDViewer markdown={result.markdown} jsonData={result.json} />
          </section>
        )}

        {/* Footer */}
        <footer className="text-center text-xs text-slate-400">
          Powered by LangGraph · Built for the article
        </footer>
      </div>
    </div>
  )
}
