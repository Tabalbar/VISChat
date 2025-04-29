"use client";
import React from "react";

export const dynamic = "force-static"; // force static rendering (optional)

export default function Home() {
  const handleClick = async () => {
    const res = await fetch("http://localhost:8500/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: "Hello World" }),
    });

    const data = await res.json();
    console.log(data);
  };

  return (
    <main style={{ padding: 40 }}>
      <h1>Hello from App Router 🎉</h1>
      <p>If you see this, the homepage is rendering correctly.</p>
      <button onClick={handleClick}>Click Me</button>
    </main>
  );
}
