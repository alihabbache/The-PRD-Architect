import ReactMarkdown from "react-markdown"
import { Button } from "@/components/ui/button"
import { Download, Copy, CheckCheck } from "lucide-react"
import { useState } from "react"

interface PRDViewerProps {
  markdown: string
  jsonData: object
}

export function PRDViewer({ markdown, jsonData }: PRDViewerProps) {
  const [copied, setCopied] = useState(false)

  function downloadMd() {
    const blob = new Blob([markdown], { type: "text/markdown" })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = "prd.md"
    a.click()
    URL.revokeObjectURL(url)
  }

  function downloadJson() {
    const blob = new Blob([JSON.stringify(jsonData, null, 2)], { type: "application/json" })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = "prd.json"
    a.click()
    URL.revokeObjectURL(url)
  }

  function copyMarkdown() {
    navigator.clipboard.writeText(markdown)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-slate-900">Generated PRD</h2>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={copyMarkdown}>
            {copied ? <CheckCheck className="h-3.5 w-3.5 text-emerald-600" /> : <Copy className="h-3.5 w-3.5" />}
            {copied ? "Copied!" : "Copy"}
          </Button>
          <Button variant="outline" size="sm" onClick={downloadMd}>
            <Download className="h-3.5 w-3.5" />
            .md
          </Button>
          <Button variant="outline" size="sm" onClick={downloadJson}>
            <Download className="h-3.5 w-3.5" />
            .json
          </Button>
        </div>
      </div>

      <div className="rounded-xl border border-slate-200 bg-white p-8 prose prose-slate max-w-none
        prose-headings:font-semibold prose-h1:text-2xl prose-h2:text-xl prose-h2:mt-8 prose-h2:border-b prose-h2:border-slate-100 prose-h2:pb-2
        prose-h3:text-base prose-h3:text-indigo-700 prose-li:text-slate-700 prose-p:text-slate-700
        overflow-auto max-h-[640px]">
        <ReactMarkdown>{markdown}</ReactMarkdown>
      </div>
    </div>
  )
}
