"use client";

import { useState } from "react";
import type { ActionItem } from "@/lib/types";
import { api } from "@/lib/api";
import { useToast } from "@/context/ToastContext";

export default function ActionItems({
  meetingId,
  items,
  onChange,
}: {
  meetingId: number;
  items: ActionItem[];
  onChange: (items: ActionItem[]) => void;
}) {
  const { notify } = useToast();
  const [newText, setNewText] = useState("");
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editText, setEditText] = useState("");

  const toggle = async (item: ActionItem) => {
    const updated = await api.updateActionItem(item.id, { completed: !item.completed });
    onChange(items.map((i) => (i.id === item.id ? updated : i)));
  };

  const add = async () => {
    if (!newText.trim()) return;
    const item = await api.addActionItem(meetingId, newText.trim());
    onChange([...items, item]);
    setNewText("");
    notify("Action item added");
  };

  const saveEdit = async (item: ActionItem) => {
    const updated = await api.updateActionItem(item.id, { text: editText.trim() });
    onChange(items.map((i) => (i.id === item.id ? updated : i)));
    setEditingId(null);
    notify("Action item updated");
  };

  const remove = async (item: ActionItem) => {
    await api.deleteActionItem(item.id);
    onChange(items.filter((i) => i.id !== item.id));
    notify("Action item deleted");
  };

  const done = items.filter((i) => i.completed).length;

  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-center justify-between text-sm text-gray-500">
        <span>
          {done}/{items.length} completed
        </span>
        <div className="h-1.5 w-32 overflow-hidden rounded-full bg-gray-200 dark:bg-gray-700">
          <div
            className="h-full bg-brand-500 transition-all"
            style={{ width: `${items.length ? (done / items.length) * 100 : 0}%` }}
          />
        </div>
      </div>

      <ul className="flex flex-col gap-2">
        {items.map((item) => (
          <li
            key={item.id}
            className="group flex items-start gap-3 rounded-lg border border-gray-200 p-3 dark:border-gray-800"
          >
            <input
              type="checkbox"
              checked={item.completed}
              onChange={() => toggle(item)}
              className="mt-0.5 h-4 w-4 shrink-0 cursor-pointer accent-brand-500"
            />
            <div className="min-w-0 flex-1">
              {editingId === item.id ? (
                <div className="flex gap-2">
                  <input
                    autoFocus
                    value={editText}
                    onChange={(e) => setEditText(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && saveEdit(item)}
                    className="flex-1 rounded border border-gray-200 px-2 py-1 text-sm dark:border-gray-700 dark:bg-gray-800"
                  />
                  <button onClick={() => saveEdit(item)} className="text-xs font-medium text-brand-600">
                    Save
                  </button>
                </div>
              ) : (
                <p
                  className={`text-sm ${
                    item.completed ? "text-gray-400 line-through" : "text-gray-800 dark:text-gray-200"
                  }`}
                >
                  {item.text}
                </p>
              )}
              <div className="mt-1 flex flex-wrap items-center gap-2 text-xs text-gray-500">
                <span className="rounded bg-gray-100 px-1.5 py-0.5 dark:bg-gray-800">
                  👤 {item.assignee}
                </span>
                {item.due_date && (
                  <span className="rounded bg-amber-50 px-1.5 py-0.5 text-amber-700 dark:bg-amber-500/10 dark:text-amber-300">
                    📅 {item.due_date}
                  </span>
                )}
              </div>
            </div>
            <div className="flex shrink-0 gap-1 opacity-0 transition group-hover:opacity-100">
              <button
                onClick={() => {
                  setEditingId(item.id);
                  setEditText(item.text);
                }}
                className="rounded px-1 text-xs text-gray-400 hover:text-brand-600"
              >
                ✏️
              </button>
              <button
                onClick={() => remove(item)}
                className="rounded px-1 text-xs text-gray-400 hover:text-red-600"
              >
                🗑
              </button>
            </div>
          </li>
        ))}
        {items.length === 0 && (
          <li className="rounded-lg border border-dashed border-gray-300 p-4 text-center text-sm text-gray-500 dark:border-gray-700">
            No action items yet.
          </li>
        )}
      </ul>

      <div className="flex gap-2">
        <input
          value={newText}
          onChange={(e) => setNewText(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && add()}
          placeholder="Add an action item…"
          className="flex-1 rounded-lg border border-gray-200 px-3 py-2 text-sm outline-none focus:border-brand-400 dark:border-gray-700 dark:bg-gray-800"
        />
        <button
          onClick={add}
          className="rounded-lg bg-brand-500 px-3 py-2 text-sm font-semibold text-white hover:bg-brand-600"
        >
          Add
        </button>
      </div>
    </div>
  );
}
