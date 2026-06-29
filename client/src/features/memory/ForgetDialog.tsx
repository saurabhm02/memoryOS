import { ConceptChip } from "@/components/ConceptChip";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogTrigger } from "@/components/ui/dialog";
import type { CompetencyGraph } from "@/lib/api/schemas";

interface ForgetDialogProps {
  graph: CompetencyGraph | null;
  onForget: (concept: string) => void;
  pendingConcept: string | null;
}

/** Retire a concept the learner has demonstrated, so it leaves the active plan. History
 * is kept — forgetting means "stop spending attention here," not "erase." */
export function ForgetDialog({ graph, onForget, pendingConcept }: ForgetDialogProps) {
  const forgettable = (graph?.nodes ?? [])
    .filter((node) => node.state === "mastered" || node.state === "medium")
    .map((node) => node.concept);

  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button variant="secondary">Forget mastered…</Button>
      </DialogTrigger>
      <DialogContent
        title="Forget a mastered concept"
        description="Stop drilling a concept you've mastered. Its history stays; it just leaves your active plan."
      >
        {forgettable.length === 0 ? (
          <p className="text-sm text-ink-muted">
            Nothing to forget yet — demonstrate a concept first and it will appear here.
          </p>
        ) : (
          <ul className="flex max-h-72 flex-col gap-1.5 overflow-y-auto">
            {forgettable.map((concept) => (
              <li
                key={concept}
                className="flex items-center justify-between gap-3 rounded-md border border-border bg-surface-2 px-3 py-2"
              >
                <ConceptChip concept={concept} tone="mastered" />
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => onForget(concept)}
                  disabled={pendingConcept === concept}
                >
                  {pendingConcept === concept ? "Forgetting…" : "Forget"}
                </Button>
              </li>
            ))}
          </ul>
        )}
      </DialogContent>
    </Dialog>
  );
}
