import { describe, expect, it } from "vitest";

import { project, rubberband } from "./motion";

describe("project", () => {
  it("throws further with more velocity, in the direction of the flick", () => {
    expect(project(0)).toBe(0);
    expect(project(1000)).toBeCloseTo(499, 0);
    expect(project(-1000)).toBeCloseTo(-499, 0);
    expect(project(2000)).toBeGreaterThan(project(1000));
  });

  it("lands sooner with a snappier deceleration rate", () => {
    expect(project(1000, 0.99)).toBeLessThan(project(1000, 0.998));
  });
});

describe("rubberband", () => {
  it("follows the finger at first and resists more the further past the edge it goes", () => {
    expect(rubberband(0, 300)).toBe(0);
    const near = rubberband(10, 300);
    const far = rubberband(200, 300);
    expect(near).toBeGreaterThan(0);
    expect(near).toBeLessThan(10);
    expect(far / 200).toBeLessThan(near / 10);
  });

  it("never exceeds the dimension", () => {
    expect(rubberband(100000, 300)).toBeLessThan(300);
  });
});
