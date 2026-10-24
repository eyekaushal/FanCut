"use client";

import { useEffect, useRef, useState } from "react";

import { matchSurface } from "@/lib/color";
import { silkRenderer } from "@/lib/silk";

/**
 * The lit, folded surface two clubs share on a card. The server renders a CSS
 * approximation so the card has colour at first paint; once mounted, the WebGL silk is
 * drawn at the card's exact size and fades in over it.
 */
export function MatchSurface({
  home,
  away,
  size = "large",
  seed = 0,
}: {
  home: string;
  away: string;
  size?: "large" | "small";
  seed?: number;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const [image, setImage] = useState<string | null>(null);

  useEffect(() => {
    const el = ref.current;
    const renderer = silkRenderer();
    if (!el || !renderer) return;

    let url: string | null = null;
    let cancelled = false;
    const draw = async (width: number, height: number) => {
      const next = await renderer.render({
        home,
        away,
        width,
        height,
        seed,
        detail: size === "large" ? 0.75 : 0.5,
      });
      if (cancelled) return URL.revokeObjectURL(next);
      if (url) URL.revokeObjectURL(url);
      url = next;
      setImage(next);
    };

    const observer = new ResizeObserver(([entry]) => {
      const { width, height } = entry.contentRect;
      if (width && height) void draw(width, height);
    });
    observer.observe(el);
    return () => {
      cancelled = true;
      observer.disconnect();
      if (url) URL.revokeObjectURL(url);
    };
  }, [home, away, size, seed]);

  return (
    <div ref={ref} aria-hidden className="silk" style={{ background: matchSurface(home, away) }}>
      {image && (
        <div
          className="silk-image"
          style={{ backgroundImage: `url(${image})` }}
        />
      )}
    </div>
  );
}
