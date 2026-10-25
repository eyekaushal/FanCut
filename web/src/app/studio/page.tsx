import { Suspense } from "react";

import { Studio } from "./studio";

export default function StudioPage() {
  return (
    <Suspense>
      <Studio />
    </Suspense>
  );
}
