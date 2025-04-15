// app/layout.tsx

import "./globals.css";
import { ReactNode } from "react";

export const metadata = {
  title: "Chat Viz App",
  description: "Chat with AI to generate charts",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
