import type { Overlay } from "@/lib/overlay";

/** A replay and its follow-up cut arrive together; the replay is held on screen this long. */
export const REPLAY_HOLD_MS = 2500;

/**
 * Holds the picture on a replay. The API sends a replay and the cut that follows it
 * in the same instant; a broadcast pauses the live feed while the replay plays, so
 * every event after a replay waits in order until the hold ends, then flushes.
 */
export class ReplayHold {
  private until = 0;
  private queue: Overlay[] = [];
  private timer: ReturnType<typeof setTimeout> | null = null;

  constructor(
    private readonly deliver: (overlay: Overlay) => void,
    private readonly holdMs = REPLAY_HOLD_MS,
    private readonly now: () => number = () => Date.now()
  ) {}

  push(overlay: Overlay): void {
    if (this.now() < this.until) {
      this.queue.push(overlay);
      this.schedule();
      return;
    }
    this.send(overlay);
  }

  dispose(): void {
    if (this.timer) clearTimeout(this.timer);
    this.timer = null;
    this.queue = [];
  }

  private send(overlay: Overlay): void {
    this.deliver(overlay);
    if (overlay.type === "cut" && overlay.data.kind === "replay") this.until = this.now() + this.holdMs;
  }

  private schedule(): void {
    if (this.timer) return;
    this.timer = setTimeout(
      () => {
        this.timer = null;
        this.flush();
      },
      Math.max(0, this.until - this.now())
    );
  }

  private flush(): void {
    while (this.queue.length && this.now() >= this.until) this.send(this.queue.shift()!);
    if (this.queue.length) this.schedule(); // a second replay in the queue starts a new hold
  }
}
