"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Chip } from "@/components/ui/chip";
import { Panel } from "@/components/ui/panel";
import { api, type CompiledProfile } from "@/lib/api";
import { fontClass } from "@/lib/i18n";

const EXAMPLES = [
  "I support Kingsmere City. My fantasy captain is Rohan Mehta. Hinglish please.",
  "मैं Oakbridge Town का फ़ैन हूँ, हिंदी में बताना।",
  "Neutral, analyst. Show me where the game is tactically alive, in English.",
];

/**
 * Onboarding: the fan describes themselves in their own words; the Profile Compiler
 * reads back what it understood, in their language, and asks about anything it could
 * not resolve. Nothing is guessed on their behalf.
 */
export default function Start() {
  const router = useRouter();
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<{ profile_id: string; compiled: CompiledProfile } | null>(null);

  const compile = async () => {
    setBusy(true);
    setError(null);
    try {
      setResult(await api.compileProfile(message.trim()));
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  };

  const profile = result?.compiled.profile;

  return (
    <main className="mx-auto w-full max-w-[720px] px-(--gutter) py-10 sm:px-(--gutter-wide) sm:py-16">
      <p className="t-caption text-fg-muted">FanCut</p>
      <h1 className="t-display mt-2">Tell me about yourself.</h1>
      <p className="t-body mt-4 max-w-[52ch] text-fg-muted">
        Your club, players you follow, your fantasy squad, the language you want. In your own words, in English, हिंदी or
        Hinglish.
      </p>

      <form
        className="mt-8"
        onSubmit={(e) => {
          e.preventDefault();
          if (message.trim().length >= 3) void compile();
        }}
      >
        <textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          rows={4}
          maxLength={500}
          placeholder={EXAMPLES[0]}
          aria-label="About you"
          className="t-body w-full resize-none rounded-panel border border-hairline bg-bg-elevated p-4 placeholder:text-fg-faint"
        />
        <ul className="mt-3 flex flex-wrap gap-2">
          {EXAMPLES.map((example) => (
            <li key={example}>
              <button
                type="button"
                onClick={() => setMessage(example)}
                className="pressable t-caption rounded-chip bg-fg/8 px-3 py-1.5 text-fg-muted hover:text-fg"
              >
                {example}
              </button>
            </li>
          ))}
        </ul>
        <div className="mt-6 flex flex-wrap items-center gap-3">
          <Button type="submit" variant="primary" disabled={busy || message.trim().length < 3}>
            {busy ? "Reading…" : "Read it back to me"}
          </Button>
          <Button variant="quiet" onClick={() => router.push("/channel?profile=arjun")}>
            Skip: watch as Arjun
          </Button>
          <Button variant="quiet" onClick={() => router.push("/channel?profile=maya")}>
            Watch as Maya
          </Button>
        </div>
      </form>

      {error && (
        <Panel className="mt-6">
          <p className="t-body">That didn&rsquo;t go through.</p>
          <p className="t-caption mt-1 text-fg-muted">{error}</p>
        </Panel>
      )}

      {result && profile && (
        <Panel className="mt-6" title="What I understood">
          <p lang={profile.language === "hi" ? "hi" : undefined} className={`t-body ${fontClass(profile.language)}`}>
            {result.compiled.readback}
          </p>
          <ul className="mt-4 flex flex-wrap gap-2">
            {profile.club_id && <Chip tone="page">Club · {profile.club_id}</Chip>}
            {profile.player_ids.map((id) => (
              <Chip key={id} tone="page">
                Follows · {id}
              </Chip>
            ))}
            {profile.fantasy_squad.length > 0 && <Chip tone="page">Fantasy · {profile.fantasy_squad.length}</Chip>}
            {profile.captain_id && <Chip tone="page">Captain · {profile.captain_id}</Chip>}
            <Chip tone="page">{profile.language}</Chip>
            <Chip tone="page">{profile.depth}</Chip>
          </ul>
          {result.compiled.questions.length > 0 && (
            <ul className="t-callout mt-4 space-y-1 text-fg-muted">
              {result.compiled.questions.map((q) => (
                <li key={q}>· {q}</li>
              ))}
            </ul>
          )}
          <div className="mt-6 flex gap-3">
            <Button variant="primary" onClick={() => router.push(`/channel?profile=${result.profile_id}`)}>
              Start my channel
            </Button>
            <Button variant="quiet" onClick={() => setResult(null)}>
              Change something
            </Button>
          </div>
        </Panel>
      )}
    </main>
  );
}
