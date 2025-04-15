import "./globals.css";

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <header style={{ backgroundColor: "#f0f0f0", padding: 16 }}>
          Layout loaded ✅
        </header>
        {children}
      </body>
    </html>
  );
}
