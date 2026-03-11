"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    const userId = localStorage.getItem("neuronav_user_id");
    if (userId) {
      router.push("/chat");
    } else {
      router.push("/onboarding");
    }
  }, [router]);

  return null;
}
