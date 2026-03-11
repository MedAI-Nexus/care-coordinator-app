"use client";

import { useRef, useEffect } from "react";
import { Message } from "@/hooks/useChat";
import MessageBubble from "./MessageBubble";
import { Loader2 } from "lucide-react";

interface ChatWindowProps {
  messages: Message[];
  isLoading: boolean;
}

export default function ChatWindow({ messages, isLoading }: ChatWindowProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="flex-1 overflow-y-auto p-6">
      <div className="max-w-3xl mx-auto space-y-6">
        {messages.length === 0 && (
          <div className="text-center py-20">
            <div className="w-16 h-16 bg-indigo-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl">🧠</span>
            </div>
            <h2 className="text-xl font-semibold text-gray-900 mb-2">
              Welcome to NeuroNav
            </h2>
            <p className="text-gray-500 max-w-md mx-auto">
              I&apos;m your care companion for navigating brain tumour treatment.
              Tell me a bit about yourself to get started.
            </p>
          </div>
        )}

        {messages.map((msg) => (
          <MessageBubble key={msg.id} role={msg.role} content={msg.content} />
        ))}

        {isLoading &&
          messages.length > 0 &&
          messages[messages.length - 1].content === "" && (
            <div className="flex items-center gap-2 text-gray-400 text-sm">
              <Loader2 className="w-4 h-4 animate-spin" />
              Thinking...
            </div>
          )}

        <div ref={bottomRef} />
      </div>
    </div>
  );
}
