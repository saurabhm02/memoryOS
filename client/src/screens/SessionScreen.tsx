import { Sparkles } from "lucide-react";
import { useEffect, useState } from "react";
import { toast } from "sonner";

import { RememberingIndicator } from "@/components/RememberingIndicator";
import { RootCauseCallout } from "@/components/RootCauseCallout";
import { EmptyState, ErrorState } from "@/components/states";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { CompetencyGraph } from "@/features/graph";
import { AssessmentCard } from "@/features/session/AssessmentCard";
import { PracticePanel } from "@/features/session/PracticePanel";
import { SESSION_ORDER, getQuestion } from "@/features/session/questionBank";
import { useDiagnosis, useGraph, useProvision, useScoreAnswer } from "@/lib/api/hooks";
import type { AnswerAssessment } from "@/lib/api/schemas";
import { isStarted, markStarted, useScope } from "@/lib/scope";

function ScreenHeader({ pending }: { pending: boolean }) {
  return (
    <header className="flex items-center justify-between gap-4 border-b border-border px-5 py-4 sm:px-6">
      <div>
        <h1 className="text-lg font-semibold tracking-tight text-ink">Session</h1>
        <p className="text-[13px] text-ink-muted">
          Practice, and watch your competency graph remember.
        </p>
      </div>
      {pending && <RememberingIndicator />}
    </header>
  );
}

export function SessionScreen() {
  const scope = useScope();
  const graph = useGraph(scope);
  const diagnosis = useDiagnosis(scope);
  const provision = useProvision(scope);
  const scoreAnswer = useScoreAnswer(scope);

  const [started, setStarted] = useState(() => isStarted(scope.userId));
  const [index, setIndex] = useState(0);
  const [assessment, setAssessment] = useState<AnswerAssessment | null>(null);

  // The authenticated user id may resolve after first paint; pick up a prior provision.
  useEffect(() => {
    if (scope.userId && isStarted(scope.userId)) setStarted(true);
  }, [scope.userId]);

  const rootCause = graph.data?.root_cause ?? null;
  // Once a root cause emerges, drill it; otherwise walk the curated order.
  const focusConcept = rootCause?.concept ?? SESSION_ORDER[index % SESSION_ORDER.length];

  const handleBegin = () =>
    provision.mutate(undefined, {
      onSuccess: () => {
        markStarted(scope.userId);
        setStarted(true);
        toast.success("Memory ready", {
          description: "Answer questions to start building your competency graph.",
        });
      },
      onError: () =>
        toast.error("Couldn't reach the memory engine", {
          description: "Check that the API is running, then try again.",
        }),
    });

  const handleSubmit = (answer: string) =>
    scoreAnswer.mutate(
      { concept: focusConcept, question: getQuestion(focusConcept), answer },
      {
        onSuccess: (result) => {
          setAssessment(result);
          setIndex((current) => current + 1);
          toast.success("Graded", {
            description: `${result.concept} · ${result.score}/5`,
          });
        },
        onError: () =>
          toast.error("Couldn't grade your answer", {
            description: "The grader was unavailable. Try again.",
          }),
      },
    );

  if (!started) {
    return (
      <div className="flex h-full flex-col">
        <ScreenHeader pending={provision.isPending} />
        <div className="grid flex-1 place-items-center p-5 sm:p-6">
          <EmptyState
            icon={Sparkles}
            title="Build your competency graph"
            description="Answer practice questions and RecallOS grades each one, remembers what it reveals, then shows you the single concept to fix first. Your memory persists across every session."
            action={
              <Button onClick={handleBegin} disabled={provision.isPending}>
                {provision.isPending ? "Preparing…" : "Begin a session"}
              </Button>
            }
          />
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col">
      <ScreenHeader pending={scoreAnswer.isPending} />

      <div className="flex min-h-0 flex-1 flex-col gap-5 overflow-auto p-5 sm:p-6">
        {graph.isLoading ? (
          <Skeleton className="h-28 w-full" />
        ) : rootCause ? (
          <RootCauseCallout
            rootCause={rootCause.concept}
            resolves={rootCause.resolves}
            narration={diagnosis.data?.narration}
          />
        ) : null}

        <div className="grid min-h-0 flex-1 grid-cols-1 gap-5 lg:grid-cols-[minmax(320px,38%)_1fr]">
          <div className="flex min-h-0 flex-col gap-5">
            <PracticePanel
              key={`${focusConcept}-${index}`}
              concept={focusConcept}
              question={getQuestion(focusConcept)}
              isPending={scoreAnswer.isPending}
              onSubmit={handleSubmit}
            />
            {assessment && <AssessmentCard assessment={assessment} />}
          </div>

          <div className="min-h-[440px] overflow-hidden rounded-lg border border-border bg-surface">
            {graph.isLoading ? (
              <Skeleton className="h-full w-full" />
            ) : graph.isError ? (
              <ErrorState onRetry={() => void graph.refetch()} />
            ) : graph.data ? (
              <CompetencyGraph data={graph.data} />
            ) : null}
          </div>
        </div>
      </div>
    </div>
  );
}
