import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Loader2, Zap } from "lucide-react"

interface ConceptFormProps {
  onSubmit: (concept: string) => void
  isLoading: boolean
}

export function ConceptForm({ onSubmit, isLoading }: ConceptFormProps) {
  const [concept, setConcept] = useState("")

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (concept.trim()) onSubmit(concept.trim())
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <Textarea
        placeholder="Describe your product idea… e.g. 'A mobile app that helps remote teams run async standups without scheduling meetings'"
        value={concept}
        onChange={(e) => setConcept(e.target.value)}
        className="min-h-[120px] text-sm resize-none"
        disabled={isLoading}
      />
      <Button
        type="submit"
        disabled={isLoading || !concept.trim()}
        size="lg"
        className="w-full"
      >
        {isLoading ? (
          <>
            <Loader2 className="h-4 w-4 animate-spin" />
            Generating PRD…
          </>
        ) : (
          <>
            <Zap className="h-4 w-4" />
            Generate PRD
          </>
        )}
      </Button>
    </form>
  )
}
