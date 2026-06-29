import { Suspense, lazy } from "react";

import { Skeleton } from "@/components/ui/skeleton";
import type { CompetencyGraph as CompetencyGraphData } from "@/lib/api/schemas";

/** Code-split the graph: React Flow + dagre are heavy and only needed once data
 * arrives, so they load in their own chunk behind a skeleton. */
const Inner = lazy(() =>
  import("./CompetencyGraph").then((module) => ({ default: module.CompetencyGraph })),
);

export function CompetencyGraph({
  data,
  className,
}: {
  data: CompetencyGraphData;
  className?: string;
}) {
  return (
    <Suspense fallback={<Skeleton className="h-full w-full" />}>
      <Inner data={data} className={className} />
    </Suspense>
  );
}
