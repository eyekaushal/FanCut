"use client";

import { useEffect, useReducer } from "react";

import { API_URL } from "@/lib/api";
import { applyOverlay, initialState, type ChannelState } from "@/lib/channel-state";
import type { Overlay } from "@/lib/overlay";
import { appendLog } from "@/lib/overlay-log";
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

/** Everything one subscription knows, tagged with the channel it belongs to. */
export type Store = { channelId: string | null; state: ChannelState; connection: Connection; log: Overlay[] };

export type StoreAction =
  | { type: "overlay"; channelId: string; overlay: Overlay }
  | { type: "connection"; channelId: string; connection: Connection };

export const emptyStore: Store = { channelId: null, state: initialState, connection: "connecting", log: [] };

/**
 * Folds stream events into the store. An action for a different channel than the one
 * stored starts from scratch first, so switching channel (a new language, a new fan)
 * never keeps the old picture or drops the new stream's early events as duplicates.
 */
export function reduceStore(store: Store, action: StoreAction): Store {
  const base = store.channelId === action.channelId ? store : { ...emptyStore, channelId: action.channelId };
  switch (action.type) {
    case "overlay": {
      const state = applyOverlay(base.state, action.overlay);
      const connection = action.overlay.type === "end" ? "ended" : base.connection;
      return { ...base, state, connection, log: appendLog(base.log, action.overlay) };
    }
    case "connection":
      // A stream that has ended stays ended, whatever the socket reports afterwards.
      if (base.connection === "ended") return base;
      return { ...base, connection: action.connection };
  }
}

/**
 * Subscribes to one channel's SSE stream and folds every overlay into state, pausing
 * on each replay so it can be seen. The browser reconnects on its own if the connection
 * drops; duplicate events are dropped by the reducer, and a stream that has ended is
 * closed rather than reopened. `log` is the raw stream as it arrived, for the inspector.
 */
export function useChannel(channelId: string | null): { state: ChannelState; connection: Connection; log: Overlay[] } {
  const [store, dispatch] = useReducer(reduceStore, emptyStore);

  useEffect(() => {
    if (!channelId) return;
    const source = new EventSource(`${API_URL}/channels/${channelId}/stream`);
    const hold = new ReplayHold((overlay) => dispatch({ type: "overlay", channelId, overlay }));
    const listeners = EVENT_TYPES.map((type) => {
      const listener = (event: MessageEvent<string>) => {
        hold.push(JSON.parse(event.data) as Overlay);
        if (type === "end") source.close(); // the held tail still flushes
      };
      source.addEventListener(type, listener);
      return [type, listener] as const;
    });
    source.onopen = () => dispatch({ type: "connection", channelId, connection: "live" });
    source.onerror = () => dispatch({ type: "connection", channelId, connection: "lost" });
    return () => {
      for (const [type, listener] of listeners) source.removeEventListener(type, listener);
      source.close();
      hold.dispose();
    };
  }, [channelId]);

  // Until the new channel's first event lands, show nothing of the old one.
  if (store.channelId !== channelId) return { state: initialState, connection: "connecting", log: [] };
  return { state: store.state, connection: store.connection, log: store.log };
}
