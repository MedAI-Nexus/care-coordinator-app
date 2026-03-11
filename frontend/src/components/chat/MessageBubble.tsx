"use client";

import ReactMarkdown from "react-markdown";
import { Brain, User } from "lucide-react";

interface MessageBubbleProps {
  role: "user" | "assistant";
  content: string;
}

export default function MessageBubble({ role, content }: MessageBubbleProps) {
  const isAssistant = role === "assistant";

  return (
    <div
      className={`flex gap-3 ${isAssistant ? "" : "flex-row-reverse"}`}
    >
      <div
        className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
          isAssistant ? "bg-indigo-100" : "bg-gray-200"
        }`}
      >
        {isAssistant ? (
          <Brain className="w-4 h-4 text-indigo-600" />
        ) : (
          <User className="w-4 h-4 text-gray-600" />
        )}
      </div>
      <div
        className={`max-w-[75%] rounded-2xl px-4 py-3 ${
          isAssistant
            ? "bg-white border border-gray-200 text-gray-800"
            : "bg-indigo-600 text-white"
        }`}
      >
        {isAssistant ? (
          <div className="prose prose-sm max-w-none prose-p:my-1 prose-li:my-0.5 prose-headings:my-2">
            <ReactMarkdown>{content || "..."}</ReactMarkdown>
          </div>
        ) : (
          <p className="text-sm whitespace-pre-wrap">{content}</p>
        )}
      </div>
    </div>
  );
}
