import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Loader2, CheckCircle2, Circle } from "lucide-react"

export type AgentStatus = "idle" | "running" | "done"

export interface AgentCardProps {
  name: string
  description: string
  status: AgentStatus
}

const statusConfig = {
  idle: {
    badge: <Badge variant="outline">Waiting</Badge>,
    icon: <Circle className="h-5 w-5 text-slate-300" />,
    ring: "border-slate-200",
  },
  running: {
    badge: <Badge variant="warning">Running</Badge>,
    icon: <Loader2 className="h-5 w-5 text-amber-500 animate-spin" />,
    ring: "border-amber-300 shadow-amber-100 shadow-md",
  },
  done: {
    badge: <Badge variant="success">Done</Badge>,
    icon: <CheckCircle2 className="h-5 w-5 text-emerald-500" />,
    ring: "border-emerald-300",
  },
}

export function AgentProgressCard({ name, description, status }: AgentCardProps) {
  const cfg = statusConfig[status]

  return (
    <Card className={`transition-all duration-300 ${cfg.ring}`}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            {cfg.icon}
            <CardTitle className="text-base">{name}</CardTitle>
          </div>
          {cfg.badge}
        </div>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-slate-500">{description}</p>
      </CardContent>
    </Card>
  )
}
