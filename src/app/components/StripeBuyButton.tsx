"use client";

import Script from "next/script";
import React, { useId } from "react";

interface StripeBuyButtonProps {
  buyButtonId: string;
  publishableKey?: string;
}

const DEFAULT_KEY = "pk_live_51TUfbVGrDuTtAB3mJWGlkkSBwFlWW1w8ljNuwzfk53knlVaPHEB7fa0CGtvzyQqeEgl6QhmrHZbHJnniSkyGFlP900lIIYME9o";

export default function StripeBuyButton({
  buyButtonId,
  publishableKey = DEFAULT_KEY,
}: StripeBuyButtonProps) {
  const id = useId();
  return (
    <div className="w-full">
      <Script
        src="https://js.stripe.com/v3/buy-button.js"
        strategy="lazyOnload"
      />
      {/* eslint-disable-next-line @typescript-eslint/no-explicit-any */}
      {(React as any).createElement("stripe-buy-button", {
        "buy-button-id": buyButtonId,
        "publishable-key": publishableKey,
        key: id,
      })}
    </div>
  );
}
