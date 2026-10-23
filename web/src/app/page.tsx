import { site } from "@/lib/site";

export default function Home() {
  return (
    <main className="flex flex-1 flex-col items-center justify-center gap-3 px-6 text-center">
      <h1 className="text-4xl font-medium tracking-tight">{site.name}</h1>
      <p className="max-w-md text-moon-50/70">{site.tagline}</p>
    </main>
  );
}
