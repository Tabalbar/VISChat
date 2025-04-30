"use client";
import React from "react";

export const dynamic = "force-static"; // force static rendering (optional)

export default function Home() {
  const handleClick = async () => {
    const res = await fetch(
      "https://my-python-server-latest.onrender.com/chat",
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: "Hello World" }),
      }
    );

    const data = await res.json();
    console.log(data);
  };

  return (
    <main style={{ padding: 40 }}>
      <h1>Hello from App Router 🎉</h1>
      <p>This is Teyanni Esaki's Page!</p>
      <button onClick={handleClick}>Click Me</button>
    </main>
  );
}
