"use client";

import { useEffect, useReducer, useState } from "react";

import { API_URL } from "@/lib/api";
import { applyOverlay, initialState, type ChannelState } from "@/lib/channel-state";
import type { Overlay } from "@/lib/overlay";

export type Connection = "connecting" | "live" | "ended" | "lost";

const EVENT_TYPES: Overlay["type"][] = ["cut", "narration", "action", "scoreboard", "table", "fantasy", "end"];

/**
 * Subscribes to one channel's SSE stream and folds every overlay into state. The
 * browser reconnects on its own if the connection drops; duplicate events are dropped
 * by the reducer, and a stream that has ended is closed rather than reopened.
 */
export function useChannel(channelId: string | null): { state: ChannelState; connection: Connection } {
  const [state, dispatch] = useReducer(applyOverlay, initialState);
  const [connection, setConnection] = useState<Connection>("connecting");

  useEffect(() => {
    if (!channelId) return;
    const source = new EventSource(`${API_URL}/channels/${channelId}/stream`);
    const listeners = EVENT_TYPES.map((type) => {
      const listener = (event: MessageEvent<string>) => {
        const message = JSON.parse(event.data) as Overlay;
        dispatch(message);
        if (type === "end") {
          setConnection("ended");
          source.close();
        }
      };
      source.addEventListener(type, listener);
      return [type, listener] as const;
    });
    source.onopen = () => setConnection("live");
    source.onerror = () => setConnection((c) => (c === "ended" ? c : "lost"));
    return () => {
      for (const [type, listener] of listeners) source.removeEventListener(type, listener);
      source.close();
    };
  }, [channelId]);

  return { state, connection };
}
