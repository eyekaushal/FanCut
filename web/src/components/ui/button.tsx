import type { ButtonHTMLAttributes } from "react";

type Variant = "primary" | "secondary" | "quiet";
type Size = "regular" | "small";

const VARIANT: Record<Variant, string> = {
  primary: "bg-fg text-bg hover:opacity-90",
  secondary: "bg-fg/8 text-fg hover:bg-fg/12",
  quiet: "text-fg-muted hover:text-fg hover:bg-fg/6",
};

// 44 px tall by default: the comfortable touch target. Small is for dense rows.
const SIZE: Record<Size, string> = {
  regular: "h-11 px-5 t-headline",
  small: "h-9 px-4 t-caption font-semibold",
};

/** Feedback on press, not on release; one primary per screen. */
export function Button({
  variant = "secondary",
  size = "regular",
  className = "",
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: Variant; size?: Size }) {
  return (
    <button
      className={`pressable inline-flex items-center justify-center gap-2 rounded-control whitespace-nowrap transition-colors duration-(--t-fast) disabled:pointer-events-none disabled:opacity-40 ${VARIANT[variant]} ${SIZE[size]} ${className}`}
      {...props}
    />
  );
}
