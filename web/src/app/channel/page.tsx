import { Suspense } from "react";

import { Channel } from "./channel";

export default function ChannelPage() {
  return (
    <Suspense>
      <Channel />
    </Suspense>
  );
}
