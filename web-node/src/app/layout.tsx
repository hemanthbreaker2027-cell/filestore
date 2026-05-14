import type { Metadata } from "next";
import { Outfit } from "next/font/google";
import "./globals.css";

const outfit = Outfit({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "˹ ᴀɴɪᴢᴏɴᴇꜰʟɪx sᴇᴄᴜʀᴇ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ ˼",
  description: "Secure Link Protection System",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head>
         <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet" />
      </head>
      <body className={outfit.className}>{children}</body>
    </html>
  );
}
