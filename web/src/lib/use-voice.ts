"use client";

import { useCallback, useEffect, useRef, useState } from "react";

import { api } from "@/lib/api";
import type { Language } from "@/lib/i18n";

export type VoiceState = "unavailable" | "off" | "on";

type Line = { key: string; url: string };
type Player = { queue: Line[]; audio: HTMLAudioElement | null; playing: boolean };

/** Plays the queue to the end, one line after another. */
function playNext(player: Player) {
  const next = player.queue.shift();
  if (!next) {
    player.playing = false;
    return;
  }
  player.playing = true;
  const audio = new Audio(next.url);
  player.audio = audio;
  audio.onended = audio.onerror = () => {
    URL.revokeObjectURL(next.url);
    playNext(player);
  };
  void audio.play().catch(() => playNext(player));
}

/**
 * Reads lines aloud, one after another, in the channel's language. Lines are fetched
 * from the API's Speech route as they arrive and queued, so a burst of cuts never
 * talks over itself. If the API has no Speech key the switch disappears.
 */
export function useVoice(lang: Language): {
  voice: VoiceState;
  toggle: () => void;
  say: (text: string, key: string) => void;
} {
  const [voice, setVoice] = useState<VoiceState>("off");
  const player = useRef<Player>({ queue: [], audio: null, playing: false });
  const spoken = useRef(new Set<string>());

  useEffect(() => {
    api
      .health()
      .then((h) => {
        if (!h.speech) setVoice("unavailable");
      })
      .catch(() => setVoice("unavailable"));
  }, []);

  // Stable, so callers can schedule it without the schedule resetting on every render.
  const say = useCallback(
    (text: string, key: string) => {
      if (voice !== "on" || spoken.current.has(key) || !text.trim()) return;
      spoken.current.add(key);
      api
        .speak(text, lang)
        .then((url) => {
          player.current.queue.push({ key, url });
          if (!player.current.playing) playNext(player.current);
        })
        .catch(() => undefined);
    },
    [voice, lang]
  );

  const toggle = useCallback(() => {
    setVoice((v) => {
      if (v === "unavailable") return v;
      if (v === "on") {
        player.current.audio?.pause();
        player.current.queue = [];
        player.current.playing = false;
        return "off";
      }
      return "on";
    });
  }, []);

  return { voice, toggle, say };
}
