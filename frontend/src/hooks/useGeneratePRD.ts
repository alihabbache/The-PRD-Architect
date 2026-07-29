import { useState, useCallback } from "react"
import type { AgentStatus } from "@/components/AgentProgressCard"

export interface AgentState {
  market_researcher: AgentStatus
  ux_specifier: AgentStatus
  technical_translator: AgentStatus
}

const AGENT_NAME_MAP: Record<string, keyof AgentState> = {
  "Market Researcher": "market_researcher",
  "UX Specifier": "ux_specifier",
  "Technical Translator": "technical_translator",
}

// The agent that fires next in the sequence
const NEXT_AGENT: Partial<Record<keyof AgentState, keyof AgentState>> = {
  market_researcher: "ux_specifier",
  ux_specifier: "technical_translator",
}

interface GenerateResult {
  markdown: string
  json: object
}

export function useGeneratePRD() {
  const [agents, setAgents] = useState<AgentState>({
    market_researcher: "idle",
    ux_specifier: "idle",
    technical_translator: "idle",
  })
  const [isLoading, setIsLoading] = useState(false)
  const [result, setResult] = useState<GenerateResult | null>(null)
  const [error, setError] = useState<string | null>(null)

  const generate = useCallback(async (concept: string) => {
    setIsLoading(true)
    setError(null)
    setResult(null)
    setAgents({ market_researcher: "running", ux_specifier: "idle", technical_translator: "idle" })

    try {
      const response = await fetch("/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ concept }),
      })

      if (!response.ok) throw new Error(`Server error: ${response.status}`)
      if (!response.body) throw new Error("No response body")

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ""

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split("\n")
        buffer = lines.pop() ?? ""

        for (const line of lines) {
          if (!line.startsWith("data: ")) continue
          const payload = JSON.parse(line.slice(6))

          if (payload.status === "complete") {
            setAgents((prev) => ({ ...prev, technical_translator: "done" }))
            setResult({ markdown: payload.markdown, json: payload.json })
          } else if (payload.status === "done") {
            const agentKey = AGENT_NAME_MAP[payload.agent]
            if (agentKey) {
              const nextKey = NEXT_AGENT[agentKey]
              setAgents((prev) => ({
                ...prev,
                [agentKey]: "done",
                ...(nextKey ? { [nextKey]: "running" } : {}),
              }))
            }
          }
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error")
    } finally {
      setIsLoading(false)
    }
  }, [])

  const reset = useCallback(() => {
    setAgents({ market_researcher: "idle", ux_specifier: "idle", technical_translator: "idle" })
    setResult(null)
    setError(null)
    setIsLoading(false)
  }, [])

  return { agents, isLoading, result, error, generate, reset }
}
