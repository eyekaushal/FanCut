import { describe, expect, it } from "vitest";

import { site } from "./site";

describe("site", () => {
  it("names the product and keeps the tagline to one short line", () => {
    expect(site.name).toBe("FanCut");
    expect(site.tagline.length).toBeLessThanOrEqual(90);
  });
});
