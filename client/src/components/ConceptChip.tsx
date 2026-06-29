import { Check, type LucideIcon, Minus, Star, X } from "lucide-react";

import type { CompetencyState } from "@/lib/api/schemas";
import { cn } from "@/lib/utils";

export type ChipTone = CompetencyState | "root-cause";

const TONE: Record<ChipTone, { cssVar: string; Icon: LucideIcon }> = {
  unvisited: { cssVar: "--unvisited", Icon: Minus },
  weak: { cssVar: "--weak", Icon: X },
  medium: { cssVar: "--medium", Icon: Minus },
  mastered: { cssVar: "--mastered", Icon: Check },
  "root-cause": { cssVar: "--root-cause", Icon: Star },
};

interface ConceptChipProps {
  concept: string;
  tone?: ChipTone;
  className?: string;
}

/** A concept pill carrying state via icon + color + label (never color alone). */
export function ConceptChip({
  concept,
  tone = "unvisited",
  className,
}: ConceptChipProps) {
  const { cssVar, Icon } = TONE[tone];
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 font-mono text-[12px] text-ink",
        className,
      )}
      style={{
        borderColor: `color-mix(in oklch, var(${cssVar}) 40%, var(--border))`,
        backgroundColor: `color-mix(in oklch, var(${cssVar}) 10%, transparent)`,
      }}
    >
      <Icon className="h-3 w-3" style={{ color: `var(${cssVar})` }} aria-hidden />
      {concept}
    </span>
  );
}
