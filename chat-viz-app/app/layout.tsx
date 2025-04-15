import "./globals.css";

export const metadata = {
  title: "It Works",
  description: "Basic layout test",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body style={{ background: "lightyellow" }}>
        <div>🌟 Layout is rendering...</div>
        {children}
      </body>
    </html>
  );
}
