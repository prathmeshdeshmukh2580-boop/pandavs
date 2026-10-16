import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Verified Course Material Studio",
  description: "Zero-trust course material generation and verification studio",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="bg-slate-950 text-slate-100 min-h-screen antialiased">
        {children}
      </body>
    </html>
  );
}
