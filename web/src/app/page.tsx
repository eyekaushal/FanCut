import { site } from "@/lib/site";

export default function Home() {
  return (
    <main className="flex flex-1 flex-col items-center justify-center gap-3 px-6 text-center">
      <h1 className="title text-4xl font-semibold">{site.name}</h1>
      <p className="max-w-md text-fg-muted">{site.tagline}</p>
    </main>
  );
}
