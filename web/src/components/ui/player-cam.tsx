"use client";

import { t, type Language } from "@/lib/i18n";
import type { PlayerStats } from "@/lib/overlay";

const kmh = (mps: number) => (mps > 0 ? `${(mps * 3.6).toFixed(1)} km/h` : "—"); // 0 means never timed
const pct = (v: number | null) => (v === null ? "—" : `${Math.round(v * 100)}%`);

/**
 * Follow one player through the match: pick a name and the pitch keeps only their
 * plays bright while these numbers track them. All of it is computed in code from
 * the event stream; nothing is estimated here.
 */
export function PlayerCam({
  players,
  selected,
  onSelect,
  lang,
}: {
  players: PlayerStats[];
  selected: string | null;
  onSelect: (name: string | null) => void;
  lang: Language;
}) {
  const ranked = [...players].sort((a, b) => b.distance_carried_m + b.passes - (a.distance_carried_m + a.passes));
  const player = players.find((p) => p.name === selected) ?? null;
  const accuracy = player && player.passes ? player.passes_completed / player.passes : null;

  return (
    <div>
      <div className="flex items-center gap-3">
        <label className="t-micro uppercase text-fg-faint" htmlFor="player-cam">
          {t(lang, "playerCam")}
        </label>
        <select
          id="player-cam"
          value={selected ?? ""}
          onChange={(e) => onSelect(e.target.value || null)}
          className="t-caption h-9 rounded-control border border-hairline bg-bg-elevated px-3 text-fg"
        >
          <option value="">{t(lang, "everyone")}</option>
          {ranked.map((p) => (
            <option key={p.player_id} value={p.name}>
              {p.name}
            </option>
          ))}
        </select>
      </div>

      {player && (
        <dl className="tabular mt-4 grid grid-cols-2 gap-x-6 gap-y-4 sm:grid-cols-4">
          <Stat label={t(lang, "distance")} value={`${Math.round(player.distance_carried_m)} m`} note={`${player.carries} carries`} />
          <Stat label={t(lang, "topSpeed")} value={kmh(player.top_speed_mps)} note={`${player.bursts} ${t(lang, "bursts").toLowerCase()}`} />
          <Stat label={t(lang, "passes")} value={`${player.passes_completed}/${player.passes}`} note={pct(accuracy)} />
          <Stat label={t(lang, "passDifficulty")} value={player.pass_difficulty.toFixed(2)} note={`${Math.round(player.longest_pass_m)} m longest`} />
          <Stat label={t(lang, "fastestPass")} value={kmh(player.fastest_pass_mps)} />
          <Stat label={t(lang, "shots")} value={`${player.shots} · ${player.xg.toFixed(2)}`} note={player.goals ? `${player.goals} goal${player.goals > 1 ? "s" : ""}` : undefined} />
          <Stat label={t(lang, "fastestShot")} value={kmh(player.fastest_shot_mps)} />
          <Stat label="Tackles · Int." value={`${player.tackles} · ${player.interceptions}`} />
        </dl>
      )}
    </div>
  );
}

function Stat({ label, value, note }: { label: string; value: string; note?: string }) {
  return (
    <div className="min-w-0">
      <dt className="t-micro truncate uppercase text-fg-faint">{label}</dt>
      <dd className="t-title2 mt-0.5">{value}</dd>
      {note && <dd className="t-caption text-fg-muted">{note}</dd>}
    </div>
  );
}
