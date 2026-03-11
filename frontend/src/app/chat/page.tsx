"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Sidebar from "@/components/layout/Sidebar";
import ChatWindow from "@/components/chat/ChatWindow";
import ChatInput from "@/components/chat/ChatInput";
import { useChat } from "@/hooks/useChat";

export default function ChatPage() {
  const [userId, setUserId] = useState<number | null>(null);
  const router = useRouter();
  const { messages, isLoading, sendMessage } = useChat(userId);

  useEffect(() => {
    const id = localStorage.getItem("neuronav_user_id");
    if (!id) {
      router.push("/");
      return;
    }
    setUserId(parseInt(id));
  }, [router]);

  return (
    <div className="flex h-screen">
      <Sidebar />
      <main className="flex-1 flex flex-col bg-gray-50">
        <div className="border-b border-gray-200 bg-white px-6 py-4">
          <h1 className="text-lg font-semibold text-gray-900">Chat</h1>
          <p className="text-sm text-gray-500">
            Ask me about medications, symptoms, appointments, or anything else
          </p>
        </div>
        <ChatWindow messages={messages} isLoading={isLoading} />
        <ChatInput onSend={sendMessage} disabled={isLoading} />
      </main>
    </div>
  );
}
