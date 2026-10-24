"use client";

import { useEffect, useState } from "react";

/** Frames per second over the last second, so "60 fps" is measured, not claimed. */
export function FpsMeter() {
  const [fps, setFps] = useState<number | null>(null);

  useEffect(() => {
    let frames = 0;
    let last = performance.now();
    let handle = 0;
    const tick = (now: number) => {
      frames += 1;
      if (now - last >= 1000) {
        setFps(Math.round((frames * 1000) / (now - last)));
        frames = 0;
        last = now;
      }
      handle = requestAnimationFrame(tick);
    };
    handle = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(handle);
  }, []);

  return (
    <output
      className="t-caption tabular fixed right-4 bottom-4 z-50 rounded-chip border border-hairline bg-bg-elevated px-3 py-1.5 text-fg-muted shadow-sm"
      aria-label="frames per second"
    >
      {fps === null ? "— fps" : `${fps} fps`}
    </output>
  );
}
