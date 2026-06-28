"use client";

import { createContext, useCallback, useContext, useRef, useState } from "react";

type ToastKind = "success" | "error" | "info";

interface Toast {
  id: number;
  message: string;
  kind: ToastKind;
}

interface ToastCtx {
  notify: (message: string, kind?: ToastKind) => void;
}

const Ctx = createContext<ToastCtx>({ notify: () => {} });

const KIND_STYLES: Record<ToastKind, string> = {
  success: "bg-green-600",
  error: "bg-red-600",
  info: "bg-brand-600",
};

const ICONS: Record<ToastKind, string> = {
  success: "✓",
  error: "✕",
  info: "i",
};

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);
  const nextId = useRef(1);

  const notify = useCallback((message: string, kind: ToastKind = "success") => {
    const id = nextId.current++;
    setToasts((prev) => [...prev, { id, message, kind }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 3500);
  }, []);

  return (
    <Ctx.Provider value={{ notify }}>
      {children}
      <div className="fixed bottom-5 right-5 z-50 flex flex-col gap-2">
        {toasts.map((t) => (
          <div
            key={t.id}
            className={`${KIND_STYLES[t.kind]} flex items-center gap-3 rounded-lg px-4 py-3 text-sm text-white shadow-lg animate-[slidein_0.2s_ease-out]`}
          >
            <span className="flex h-5 w-5 items-center justify-center rounded-full bg-white/25 text-xs font-bold">
              {ICONS[t.kind]}
            </span>
            <span>{t.message}</span>
          </div>
        ))}
      </div>
    </Ctx.Provider>
  );
}

export const useToast = () => useContext(Ctx);
