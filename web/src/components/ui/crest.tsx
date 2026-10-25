import Image from "next/image";

/**
 * A club's crest, by its three-letter code (the one key every overlay carries). The
 * crests are original, flat SVGs in `public/crests/`. Decorative: the club's name is
 * always written beside it, so screen readers skip the image.
 */
export function Crest({ short, size, className = "" }: { short: string; size: number; className?: string }) {
  return (
    <Image
      src={`/crests/${short.toLowerCase()}.svg`}
      alt=""
      width={size}
      height={size}
      draggable={false}
      className={`block shrink-0 select-none ${className}`}
    />
  );
}
