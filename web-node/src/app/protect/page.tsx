"use client";

import { useEffect, useState, useRef } from "react";
import { useSearchParams } from "next/navigation";
import { Shield, TriangleAlert, Loader2, Chrome } from "lucide-react";

export default function ProtectPage() {
  const searchParams = useSearchParams();
  const [status, setStatus] = useState<"checking" | "ready" | "verifying" | "error">("checking");
  const [errorMsg, setErrorMsg] = useState("");
  const [timer, setTimer] = useState(10);
  const [canContinue, setCanContinue] = useState(false);
  const broadcastChannel = useRef<BroadcastChannel | null>(null);

  const data = searchParams.get("data");

  useEffect(() => {
    // 1. CHROME ONLY CHECK
    const isChrome = () => {
      const ua = window.navigator.userAgent;
      const isChromium = (window as any).chrome;
      const vendorName = window.navigator.vendor;
      const isOpera = typeof (window as any).opr !== "undefined";
      const isEdge = ua.indexOf("Edg") > -1;
      const isBrave = !!(window.navigator as any).brave;

      return (
        isChromium !== null &&
        typeof isChromium !== "undefined" &&
        vendorName === "Google Inc." &&
        isOpera === false &&
        isEdge === false &&
        isBrave === false
      );
    };

    if (!isChrome()) {
      setStatus("error");
      setErrorMsg("Please open this protected link in Google Chrome.");
      return;
    }

    // 2. SAME TAB CHECK (BroadcastChannel)
    const channelId = `tab_lock_${data}`;
    broadcastChannel.current = new BroadcastChannel(channelId);

    broadcastChannel.current.onmessage = (event) => {
      if (event.data === "ping") {
        broadcastChannel.current?.postMessage("pong");
      }
      if (event.data === "pong" || event.data === "already_open") {
        setStatus("error");
        setErrorMsg("Multiple tabs detected. This link can only be opened in one tab.");
      }
    };

    // Broadcast our presence
    broadcastChannel.current.postMessage("ping");

    // 3. STORAGE LOCK
    const storageKey = `active_session_${data}`;
    const existingSession = localStorage.getItem(storageKey);
    const sessionExpiry = localStorage.getItem(`${storageKey}_expiry`);

    if (existingSession && sessionExpiry && parseInt(sessionExpiry) > Date.now()) {
        // Double check with broadcast if it's really another tab or just a refresh
    }

    localStorage.setItem(storageKey, "active");
    localStorage.setItem(`${storageKey}_expiry`, (Date.now() + 30000).toString());

    setStatus("ready");

    return () => {
      broadcastChannel.current?.close();
      localStorage.removeItem(storageKey);
      localStorage.removeItem(`${storageKey}_expiry`);
    };
  }, [data]);

  useEffect(() => {
    if (status === "ready" && timer > 0) {
      const interval = setInterval(() => {
        setTimer((prev) => prev - 1);
      }, 1000);
      return () => clearInterval(interval);
    } else if (timer === 0) {
      setCanContinue(true);
    }
  }, [status, timer]);

  const handleVerify = async () => {
    if (!canContinue) return;
    setStatus("verifying");

    try {
      const res = await fetch("/api/verify", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          token: data,
          browser: "chrome",
          tabId: sessionStorage.getItem("tabId") || (Math.random().toString(36).substring(7))
        }),
      });

      const result = await res.json();
      if (result.success) {
        window.location.replace(result.redirect);
      } else {
        setStatus("error");
        setErrorMsg(result.message || "Verification failed. Session expired or invalid.");
      }
    } catch (err) {
      setStatus("error");
      setErrorMsg("Network error. Please try again.");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="glass-container p-8 sm:p-10 rounded-[2.5rem] w-full max-width-[450px] text-center relative overflow-hidden z-10">
        <div className="absolute top-0 left-0 right-0 h-[120px] bg-gradient-to-b from-sky-400/20 to-transparent z-0"></div>

        <div className="relative z-10 space-y-8">
          <div className="flex justify-center">
            <div className="p-5 bg-sky-500/10 rounded-3xl border border-sky-500/20 shadow-inner">
              <Shield className="w-12 h-12 text-sky-400" />
            </div>
          </div>

          <div className="space-y-2">
            <h1 className="text-3xl sm:text-4xl font-black tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-sky-400 to-indigo-400">
              ˹ ᴀɴɪᴢᴏɴᴇꜰʟɪx ˼
            </h1>
            <p className="text-slate-400 text-xs font-bold tracking-[0.25em] uppercase animate-pulse">sᴇᴄᴜʀᴇ ʟɪɴᴋ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ</p>
          </div>

          <div className="min-h-[220px] flex flex-col items-center justify-center space-y-6">
            {status === "checking" && (
                <div className="space-y-4">
                    <Loader2 className="w-12 h-12 text-sky-400 animate-spin mx-auto" />
                    <p className="text-sky-400 font-black text-sm tracking-widest uppercase">Initializing Security Check...</p>
                </div>
            )}

            {status === "ready" && (
              <div className="w-full space-y-4">
                <button
                  disabled={!canContinue}
                  onClick={handleVerify}
                  className={`w-full py-5 rounded-2xl text-white font-black text-lg uppercase tracking-widest flex items-center justify-center space-x-3 transition-all duration-300 ${
                    canContinue
                      ? "bg-gradient-to-r from-sky-400 to-indigo-400 shadow-lg shadow-sky-400/40 hover:scale-[1.02] active:scale-[0.98]"
                      : "bg-slate-800 text-slate-500 cursor-not-allowed"
                  }`}
                >
                  {canContinue ? (
                    <span>⚡️ ᴠᴇʀɪꜰʏ ɴᴏᴡ ⚡️</span>
                  ) : (
                    <span>ᴡᴀɪᴛ {timer}s...</span>
                  )}
                </button>
                <p className="text-slate-500 text-[10px] font-bold uppercase tracking-tighter">
                  {canContinue ? "ᴄʟɪᴄᴋ ᴛᴏ ᴜɴʟᴏᴄᴋ ʏᴏᴜʀ ᴅᴇsᴛɪɴᴀᴛɪᴏɴ" : "sᴇᴄᴜʀɪɴɢ ʏᴏᴜʀ ᴄᴏɴɴᴇᴄᴛɪᴏɴ..."}
                </p>
              </div>
            )}

            {status === "verifying" && (
                <div className="space-y-4">
                    <Loader2 className="w-12 h-12 text-sky-400 animate-spin mx-auto" />
                    <p className="text-sky-400 font-black text-sm tracking-widest uppercase">˹ ꜰɪɴᴀʟɪᴢɪɴɢ ᴄʜᴇᴄᴋ ˼</p>
                </div>
            )}

            {status === "error" && (
              <div className="p-6 bg-red-500/10 border border-red-500/20 rounded-3xl space-y-4 w-full">
                <TriangleAlert className="w-10 h-10 text-red-500 mx-auto" />
                <p className="text-red-400 text-sm font-black uppercase leading-relaxed">{errorMsg}</p>
                <button
                  onClick={() => window.location.reload()}
                  className="text-xs font-black text-white bg-slate-800 px-6 py-2 rounded-xl uppercase hover:bg-slate-700 transition-colors"
                >
                  ᴛʀʏ ᴀɢᴀɪɴ
                </button>
              </div>
            )}
          </div>

          <div className="pt-6 border-t border-slate-800">
            <div className="flex items-center justify-center space-x-3 text-slate-500">
              <Chrome className="w-5 h-5" />
              <span className="text-[9px] font-black uppercase tracking-widest">ᴘᴏᴡᴇʀᴇᴅ ʙʏ ᴄʜʀᴏᴍᴇ sᴇᴄᴜʀɪᴛʏ</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
