"use client";

import { useEffect, useReducer, useState } from "react";

import { API_URL } from "@/lib/api";
import { applyOverlay, initialState, type ChannelState } from "@/lib/channel-state";
import type { Overlay } from "@/lib/overlay";
import { ReplayHold } from "@/lib/replay-hold";

export type Connection = "connecting" | "live" | "ended" | "lost";

const EVENT_TYPES: Overlay["type"][] = [
  "cut",
  "narration",
  "action",
  "scoreboard",
  "table",
  "fantasy",
  "focus",
  "players",
  "end",
];

/**
 * Subscribes to one channel's SSE stream and folds every overlay into state, pausing
 * on each replay so it can be seen. The browser reconnects on its own if the connection
 * drops; duplicate events are dropped by the reducer, and a stream that has ended is
 * closed rather than reopened.
 */
export function useChannel(channelId: string | null): { state: ChannelState; connection: Connection } {
  const [state, dispatch] = useReducer(applyOverlay, initialState);
  const [connection, setConnection] = useState<Connection>("connecting");

  useEffect(() => {
    if (!channelId) return;
    const source = new EventSource(`${API_URL}/channels/${channelId}/stream`);
    const hold = new ReplayHold((overlay) => {
      dispatch(overlay);
      if (overlay.type === "end") setConnection("ended");
    });
    const listeners = EVENT_TYPES.map((type) => {
      const listener = (event: MessageEvent<string>) => {
        hold.push(JSON.parse(event.data) as Overlay);
        if (type === "end") source.close(); // the held tail still flushes
      };
      source.addEventListener(type, listener);
      return [type, listener] as const;
    });
    source.onopen = () => setConnection("live");
    source.onerror = () => setConnection((c) => (c === "ended" ? c : "lost"));
    return () => {
      for (const [type, listener] of listeners) source.removeEventListener(type, listener);
      source.close();
      hold.dispose();
    };
  }, [channelId]);

  return { state, connection };
}
