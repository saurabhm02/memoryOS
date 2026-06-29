/** True when the user has requested reduced motion. Guard every non-essential
 * animation with this and provide an instant/crossfade fallback. */
export function prefersReducedMotion(): boolean {
  return (
    typeof window !== "undefined" &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches
  );
}
