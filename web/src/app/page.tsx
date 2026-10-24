import Link from "next/link";

import { MatchSurface } from "@/components/match-surface";
import { site } from "@/lib/site";

const DEMO_FANS = [
  { id: "arjun", name: "Arjun", note: "Kingsmere City · fantasy · हिंदी", colors: ["#2E5EAA", "#2A9D8F"] },
  { id: "maya", name: "Maya", note: "Neutral · analyst · English", colors: ["#7A1F2B", "#457B9D"] },
];

export default function Home() {
  return (
    <main className="mx-auto flex w-full max-w-(--page) flex-1 flex-col px-(--gutter) py-10 sm:px-(--gutter-wide) sm:py-16">
      <p className="t-caption text-fg-muted">{site.name}</p>
      <h1 className="t-display mt-2 max-w-[14ch]">Ten matches. One channel. Yours.</h1>
      <p className="t-body mt-5 max-w-[52ch] text-fg-muted">
        On a big matchday ten games kick off at once. FanCut watches all of them, cuts to the one that matters to you,
        and says why. In English, हिंदी or Hinglish.
      </p>

      <div className="mt-10 flex flex-wrap gap-3">
        <Link
          href="/start"
          className="pressable t-headline inline-flex h-11 items-center rounded-control bg-fg px-5 text-bg"
        >
          Start my channel
        </Link>
        <Link
          href="/split"
          className="pressable t-headline inline-flex h-11 items-center rounded-control bg-fg/8 px-5 text-fg"
        >
          Two fans, side by side
        </Link>
      </div>

      <section aria-label="Demo fans" className="mt-14 grid gap-4 sm:grid-cols-2">
        {DEMO_FANS.map((fan, i) => (
          <Link
            key={fan.id}
            href={`/channel?profile=${fan.id}`}
            className="grain pressable block rounded-card p-6 text-on-card"
          >
            <MatchSurface home={fan.colors[0]} away={fan.colors[1]} seed={i + 5} />
            <p className="t-micro uppercase text-on-card-muted">Watch as</p>
            <p className="t-title1 mt-1">{fan.name}</p>
            <p className="t-caption mt-1 text-on-card-muted">{fan.note}</p>
          </Link>
        ))}
      </section>
    </main>
  );
}
