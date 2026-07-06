"""Generate the HLD architecture diagram and the ER (database schema) diagram.

Run with the backend venv (matplotlib installed there):
    ../../backend/.venv/Scripts/python.exe generate_diagrams.py
Outputs: hld_architecture.png, er_diagram.png
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

BRAND = "#6c5ce7"
BRAND_DK = "#4c38b4"
INK = "#1f2937"
GRAY = "#6b7280"
LIGHT = "#eef1ff"
CARD = "#f8f9ff"
GREEN = "#0e9f6e"
AMBER = "#f59e0b"


def box(ax, x, y, w, h, text, fc=CARD, ec=BRAND, tc=INK, fs=10, bold=False, round=0.02):
    ax.add_patch(
        FancyBboxPatch(
            (x, y), w, h,
            boxstyle=f"round,pad=0.3,rounding_size={round*100}",
            linewidth=1.4, edgecolor=ec, facecolor=fc, mutation_aspect=1,
        )
    )
    ax.text(
        x + w / 2, y + h / 2, text, ha="center", va="center",
        fontsize=fs, color=tc, fontweight="bold" if bold else "normal", wrap=True,
    )


def arrow(ax, x1, y1, x2, y2, text="", color=GRAY, ls="-"):
    ax.add_patch(
        FancyArrowPatch(
            (x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=16,
            linewidth=1.6, color=color, linestyle=ls, shrinkA=2, shrinkB=2,
        )
    )
    if text:
        ax.text((x1 + x2) / 2, (y1 + y2) / 2, text, ha="center", va="center",
                fontsize=8, color=color, backgroundcolor="white")


# ---------------------------------------------------------------- HLD diagram
def hld():
    fig, ax = plt.subplots(figsize=(12, 9))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")
    ax.text(50, 97, "Fireflies.ai Clone — High-Level Design (HLD)",
            ha="center", fontsize=16, fontweight="bold", color=INK)
    ax.text(50, 93.5, "Next.js (TypeScript) frontend  ·  FastAPI (Python) backend  ·  SQLite",
            ha="center", fontsize=10, color=GRAY)

    # User
    box(ax, 38, 85, 24, 6, "User  (Web Browser)", fc=BRAND, ec=BRAND_DK, tc="white", fs=12, bold=True)

    # Frontend container
    box(ax, 6, 55, 88, 26, "", fc="#fbfbff", ec=BRAND, round=0.015)
    ax.text(10, 78.5, "FRONTEND  —  Next.js App Router  (frontend/)", fontsize=11,
            fontweight="bold", color=BRAND_DK)
    box(ax, 9, 63, 24, 11, "Pages (app/)\nDashboard · Meeting\nDetail · Search · Settings", fs=9)
    box(ax, 37, 63, 24, 11, "Components (components/)\nCards · Player · Transcript\nTabs · Modals · Toasts", fs=9)
    box(ax, 65, 68, 26, 6, "Context: Theme + Toast", fs=9)
    box(ax, 65, 62.5, 26, 4.5, "lib/api.ts — typed client", fs=9, ec=GREEN, tc=GREEN, bold=True)

    # Arrows user <-> frontend
    arrow(ax, 50, 85, 50, 81, color=GRAY)

    # HTTP boundary
    arrow(ax, 78, 62.5, 78, 47, "HTTP / JSON\n(REST, /api)", color=BRAND)
    arrow(ax, 22, 47, 22, 55, color=BRAND, ls="--")

    # Backend container
    box(ax, 6, 12, 88, 34, "", fc="#fffdfa", ec=AMBER, round=0.015)
    ax.text(10, 43, "BACKEND  —  FastAPI  (backend/app/)", fontsize=11,
            fontweight="bold", color="#b45309")

    box(ax, 9, 33, 82, 6.5,
        "Routers (routers/):  meetings · action_items · highlights · search   —  thin HTTP layer",
        fs=9, ec=AMBER)
    arrow(ax, 50, 33, 50, 30, color=GRAY)
    box(ax, 9, 23.5, 40, 6.5, "CRUD (crud.py)\nall DB operations — the only ORM layer",
        fs=9, ec=BRAND, bold=True)
    box(ax, 52, 22, 39, 8.5,
        "Services (services/)\nparser · generator · ask\n(transcript → segments → AI notes)",
        fs=9, ec=GREEN)
    arrow(ax, 49, 26.7, 52, 26.7, color=GREEN)

    arrow(ax, 29, 23.5, 29, 20, color=GRAY)
    box(ax, 9, 14, 40, 6, "Models (models.py) — SQLAlchemy ORM", fs=9, ec=BRAND)
    arrow(ax, 60, 14, 60, 8, color=GRAY)

    # DB
    box(ax, 40, 2, 30, 6, "SQLite Database  (fireflies.db)", fc=INK, ec=INK, tc="white", fs=11, bold=True)
    arrow(ax, 29, 14, 40, 6.5, color=GRAY)

    # Seed note
    box(ax, 72, 14, 19, 6, "seed.py\nauto-seeds on\nempty DB", fs=8, ec=GRAY, tc=GRAY)
    arrow(ax, 72, 17, 70, 5.5, color=GRAY, ls="--")

    plt.tight_layout()
    fig.savefig("hld_architecture.png", dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("wrote hld_architecture.png")


# ---------------------------------------------------------------- ER diagram
def er():
    fig, ax = plt.subplots(figsize=(13, 9))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")
    ax.text(50, 97, "Fireflies.ai Clone — Database Schema (ER Diagram)",
            ha="center", fontsize=16, fontweight="bold", color=INK)

    def table(x, y, title, cols, w=22, ec=BRAND):
        h = 4.2 + len(cols) * 3.0
        ax.add_patch(FancyBboxPatch((x, y - h), w, h, boxstyle="round,pad=0.2,rounding_size=1",
                                    linewidth=1.6, edgecolor=ec, facecolor="white"))
        ax.add_patch(FancyBboxPatch((x, y - 4.2), w, 4.2, boxstyle="square,pad=0",
                                    linewidth=0, facecolor=ec))
        ax.text(x + w / 2, y - 2.1, title, ha="center", va="center", color="white",
                fontsize=10, fontweight="bold")
        for i, c in enumerate(cols):
            ax.text(x + 1.5, y - 4.2 - 1.6 - i * 3.0, c, ha="left", va="center",
                    fontsize=8, color=INK)
        return (x, y, w, h)

    # Central: meetings
    m = table(39, 82, "meetings", [
        "id  (PK)", "title", "description", "date",
        "duration_seconds", "audio_url", "created_at", "updated_at",
    ])

    # Children
    table(6, 88, "participants", ["id (PK)", "meeting_id (FK)", "name", "email", "role"], ec=GREEN)
    table(6, 58, "transcript_segments",
          ["id (PK)", "meeting_id (FK)", "speaker", "start_ms", "end_ms", "text", "order_index"], ec=GREEN)
    table(6, 26, "summaries  (1:1)", ["id (PK)", "meeting_id (FK,uniq)", "overview", "generated_by"], ec=BRAND_DK)
    table(72, 88, "key_topics", ["id (PK)", "meeting_id (FK)", "title", "start_ms", "order_index"], ec=GREEN)
    table(72, 62, "action_items",
          ["id (PK)", "meeting_id (FK)", "text", "assignee", "due_date", "completed", "order_index"], ec=GREEN)
    table(72, 30, "highlights",
          ["id (PK)", "meeting_id (FK)", "segment_id (FK)", "quote", "note", "start_ms"], ec=AMBER)
    table(39, 36, "tags", ["id (PK)", "name (uniq)"], w=20, ec=BRAND_DK)
    table(39, 21, "meeting_tags  (M:N)", ["meeting_id (FK)", "tag_id (FK)"], w=20, ec=GRAY)

    def rel(x1, y1, x2, y2, label):
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-", linewidth=1.3,
                                     color=GRAY, shrinkA=1, shrinkB=1))
        ax.text((x1 + x2) / 2, (y1 + y2) / 2, label, ha="center", va="center",
                fontsize=8, color=BRAND_DK, backgroundcolor="white", fontweight="bold")

    rel(28, 80, 39, 78, "1:N")     # participants
    rel(28, 50, 39, 74, "1:N")     # segments
    rel(28, 20, 40, 70, "1:1")     # summaries
    rel(72, 80, 61, 78, "1:N")     # key_topics
    rel(72, 55, 61, 74, "1:N")     # action_items
    rel(72, 26, 61, 70, "1:N")     # highlights
    rel(49, 54, 49, 36, "M:N")     # meetings -> tags
    rel(49, 25, 49, 21, "")        # tags -> meeting_tags

    ax.text(50, 4, "All child rows CASCADE-DELETE when their meeting is deleted.",
            ha="center", fontsize=9, color=GRAY, style="italic")

    plt.tight_layout()
    fig.savefig("er_diagram.png", dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("wrote er_diagram.png")


if __name__ == "__main__":
    hld()
    er()
