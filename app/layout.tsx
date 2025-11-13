import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "大台北租屋網 - 最新物件彙整",
  description: "從 Facebook 租屋社團抓取最新物件資訊，清晰易讀的租屋資訊平台",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-TW">
      <body>{children}</body>
    </html>
  );
}
