import { Suspense } from "react";

import { Split } from "./split";

export default function SplitPage() {
  return (
    <Suspense>
      <Split />
    </Suspense>
  );
}
