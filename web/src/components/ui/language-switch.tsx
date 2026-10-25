"use client";

import { Segmented } from "@/components/ui/segmented";
import { LANGUAGES, t, type Language } from "@/lib/i18n";

/** The three languages as a segmented control; Hindi in its own font. */
export function LanguageSwitch({ value, onChange }: { value: Language; onChange: (lang: Language) => void }) {
  return (
    <Segmented
      value={value}
      onChange={onChange}
      label={t(value, "language")}
      options={LANGUAGES.map(({ id, label }) => ({ id, label, className: id === "hi" ? "font-devanagari" : "" }))}
    />
  );
}
