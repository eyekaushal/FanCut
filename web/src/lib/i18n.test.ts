import { describe, expect, it } from "vitest";

import { LANGUAGES, ordinal, stakesLabel, t } from "./i18n";

describe("t", () => {
  it("returns the string for each language", () => {
    expect(t("en", "yourClub")).toBe("Your club");
    expect(t("hi", "yourClub")).toBe("आपका क्लब");
    expect(t("hinglish", "yourClub")).toBe("Aapka club");
  });

  it("fills slots, every occurrence", () => {
    expect(t("en", "minute", { n: 24 })).toBe("24′");
    expect(t("hi", "position", { n: "2रा" })).toBe("तालिका में 2रा");
    expect(t("en", "measuring", { n: 6, done: 3 })).toBe("Measuring the Director on 6 matchdays… 3/6");
  });

  it("has every language for every stakes label", () => {
    for (const { id } of LANGUAGES) {
      expect(stakesLabel(id, "title_race")).not.toBe("");
    }
  });
});

describe("ordinal", () => {
  it("handles the English teens", () => {
    expect(ordinal("en", 1)).toBe("1st");
    expect(ordinal("en", 2)).toBe("2nd");
    expect(ordinal("en", 11)).toBe("11th");
    expect(ordinal("en", 12)).toBe("12th");
    expect(ordinal("en", 13)).toBe("13th");
    expect(ordinal("en", 22)).toBe("22nd");
  });

  it("uses Hindi suffixes", () => {
    expect(ordinal("hi", 1)).toBe("1ला");
    expect(ordinal("hi", 2)).toBe("2रा");
    expect(ordinal("hi", 4)).toBe("4वाँ");
  });
});
