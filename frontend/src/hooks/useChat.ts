"use client";

import { useState, useCallback, useEffect } from "react";
import { sendChatMessage, fetchApi } from "@/lib/api";

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
}

interface ConversationMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  created_at: string | null;
}

export function useChat(userId: number | null) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [historyLoaded, setHistoryLoaded] = useState(false);

  // Load conversation history on mount
  useEffect(() => {
    if (!userId || historyLoaded) return;

    fetchApi<ConversationMessage[]>(`/api/conversations/${userId}`)
      .then((history) => {
        if (history.length > 0) {
          setMessages(
            history.map((m) => ({
              id: m.id,
              role: m.role,
              content: m.content,
            }))
          );
        }
        setHistoryLoaded(true);
      })
      .catch(() => {
        setHistoryLoaded(true);
      });
  }, [userId, historyLoaded]);

  const sendMessage = useCallback(
    async (content: string) => {
      if (!userId || !content.trim()) return;

      const userMsg: Message = {
        id: Date.now().toString(),
        role: "user",
        content: content.trim(),
      };
      setMessages((prev) => [...prev, userMsg]);
      setIsLoading(true);

      const assistantId = (Date.now() + 1).toString();
      setMessages((prev) => [
        ...prev,
        { id: assistantId, role: "assistant", content: "" },
      ]);

      try {
        await sendChatMessage(userId, content.trim(), (chunk) => {
          setMessages((prev) =>
            prev.map((m) =>
              m.id === assistantId ? { ...m, content: chunk } : m
            )
          );
        });
      } catch (error) {
        setMessages((prev) =>
          prev.map((m) =>
            m.id === assistantId
              ? {
                  ...m,
                  content:
                    "Sorry, I encountered an error. Please try again.",
                }
              : m
          )
        );
      } finally {
        setIsLoading(false);
      }
    },
    [userId]
  );

  return { messages, isLoading, sendMessage };
}
