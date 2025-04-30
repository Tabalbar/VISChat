"use client";
import React, { useState } from "react";
import { SYSTEM_PROMPT } from "./context";

export const dynamic = "force-static"; // optional

export default function ChatPage() {
  /**
   * [
    {"role": "developer", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello!"}
  ]
   */
  const [messages, setMessages] = useState<{ role: string; content: string }[]>(
    [{ role: "system", content: SYSTEM_PROMPT }]
  );
  const [input, setInput] = useState("");

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = { role: "user", content: input };
    const tmpMessages = [...messages, userMessage];
    try {
      const res = await fetch(
        // "http://localhost:8500/chat",
        "https://my-python-server-latest.onrender.com/chat",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ messages: tmpMessages }),
        }
      );

      const data = await res.json();
      console.log(data);
      const botMessage = {
        role: "assistant",
        content: data.reply || "No response",
      };

      tmpMessages.push(botMessage);
      setMessages(tmpMessages);
    } catch (err) {
      console.error(err);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Error connecting to server." },
      ]);
    }

    setInput("");
  };

  return (
    <main
      style={{
        minHeight: "100vh",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        backgroundColor: "#f7f7f7",
      }}
    >
      <div
        style={{
          width: "100%",
          maxWidth: "90vw",
          backgroundColor: "white",
          padding: 20,
          borderRadius: 10,
          boxShadow: "0 0 10px rgba(0,0,0,0.1)",
          display: "flex",
          flexDirection: "column",
        }}
      >
        <h2 style={{ textAlign: "center", marginBottom: 20 }}>
          Hawaii Climate Data Portal
        </h2>
        <div
          style={{
            flexGrow: 1,
            minHeight: "70vh",
            maxHeight: 500,
            overflowY: "auto",
            marginBottom: 10,
            border: "1px solid #ddd",
            padding: 10,
            borderRadius: 6,
          }}
        >
          {messages.map((msg, index) => (
            <div key={index} style={{ margin: "5px 0" }}>
              <strong>{msg.role}: </strong>
              <span>{msg.content}</span>
            </div>
          ))}
        </div>
        <div style={{ display: "flex", gap: 10 }}>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
            placeholder="Type your message..."
            style={{
              flexGrow: 1,
              padding: 10,
              borderRadius: 6,
              border: "1px solid #ccc",
            }}
          />
          <button
            onClick={handleSend}
            style={{
              padding: "10px 16px",
              borderRadius: 6,
              backgroundColor: "#0070f3",
              color: "white",
              border: "none",
              cursor: "pointer",
            }}
          >
            Send
          </button>
        </div>
      </div>
    </main>
  );
}
