import { describe, expect, it } from "vitest";

import { cut, scoreboard } from "@/lib/demo-data";
import type { Overlay } from "@/lib/overlay";
import { emptyStore, reduceStore, type Store } from "./use-channel";

const at = (seq: number, type: Overlay["type"], data: unknown, t = seq): Overlay => ({ seq, t, type, data }) as Overlay;

function play(store: Store, channelId: string, overlays: Overlay[]): Store {
  return overlays.reduce((s, overlay) => reduceStore(s, { type: "overlay", channelId, overlay }), store);
}

describe("reduceStore", () => {
  it("folds a channel's events and marks the end", () => {
    let store = reduceStore(emptyStore, { type: "connection", channelId: "a", connection: "live" });
    store = play(store, "a", [at(1, "scoreboard", { matches: scoreboard }), at(2, "cut", cut("en"))]);
    expect(store.connection).toBe("live");
    expect(store.state.cut?.match_id).toBe("md34-09");
    expect(store.log).toHaveLength(2);
    store = play(store, "a", [at(3, "end", {})]);
    expect(store.connection).toBe("ended");
    // The socket's error after the end does not reopen anything.
    expect(reduceStore(store, { type: "connection", channelId: "a", connection: "lost" }).connection).toBe("ended");
  });

  it("starts over for a new channel, so low sequence numbers are not dropped as duplicates", () => {
    const old = play(emptyStore, "a", [at(40, "scoreboard", { matches: scoreboard }), at(41, "cut", cut("en")), at(42, "end", {})]);
    expect(old.state.ended).toBe(true);
    const fresh = play(old, "b", [at(1, "scoreboard", { matches: scoreboard }), at(2, "cut", cut("hi"))]);
    expect(fresh.channelId).toBe("b");
    expect(fresh.state.ended).toBe(false);
    expect(fresh.state.seq).toBe(2);
    expect(fresh.state.cut?.language).toBe("hi");
    expect(fresh.log).toHaveLength(2);
    expect(fresh.connection).toBe("connecting");
  });
});
