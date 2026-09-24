import csv
import tkinter as tk
from collections import Counter
from datetime import datetime
from pathlib import Path
from tkinter import messagebox, scrolledtext, ttk

APP_TITLE = "Thoughts Journal"
DATA_FILE = Path(__file__).resolve().with_name("thoughts_data.csv")
CSV_FIELDS = [
    "timestamp",
    "topic",
    "thought",
    "emotion",
    "labels",
    "intensity",
    "like_it",
    "keep_it",
]

EMOTIONS = [
    "Happy",
    "Calm",
    "Hopeful",
    "Inspired",
    "Neutral",
    "Confused",
    "Anxious",
    "Sad",
    "Angry",
    "Overwhelmed",
]


def ensure_data_file():
    if not DATA_FILE.exists():
        with DATA_FILE.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=CSV_FIELDS)
            writer.writeheader()


def load_entries():
    ensure_data_file()
    entries = []
    with DATA_FILE.open("r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if not row.get("thought"):
                continue
            entries.append(row)
    return sorted(entries, key=lambda item: item.get("timestamp", ""), reverse=True)


def save_entry(topic, thought, emotion, labels, intensity, like_it, keep_it):
    if not thought.strip():
        raise ValueError("Thought cannot be empty.")

    entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "topic": topic.strip() or "General",
        "thought": thought.strip(),
        "emotion": emotion,
        "labels": labels.strip(),
        "intensity": str(intensity),
        "like_it": str(bool(like_it)),
        "keep_it": str(bool(keep_it)),
    }

    with DATA_FILE.open("a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_FIELDS)
        writer.writerow(entry)


def parse_labels(raw_labels):
    return [label.strip().lower() for label in raw_labels.split(",") if label.strip()]


def summarize_entries(entries):
    if not entries:
        return {
            "total": 0,
            "top_emotion": "No entries yet",
            "top_labels": "No labels yet",
            "liked": 0,
            "kept": 0,
            "pattern": "Start capturing thoughts to spot recurring themes.",
        }

    emotion_counts = Counter(entry.get("emotion", "Unknown") for entry in entries)
    label_counts = Counter()
    liked = 0
    kept = 0

    for entry in entries:
        liked += 1 if entry.get("like_it") == "True" else 0
        kept += 1 if entry.get("keep_it") == "True" else 0
        for label in parse_labels(entry.get("labels", "")):
            label_counts[label] += 1

    top_emotion = emotion_counts.most_common(1)[0][0]
    top_labels = ", ".join(
        f"{label} ({count})" for label, count in label_counts.most_common(4)
    ) if label_counts else "No recurring labels yet"

    pattern = (
        f"Your journal shows a pattern around {top_emotion.lower()} emotions "
        f"and recurring themes like {top_labels}."
        if top_labels != "No recurring labels yet"
        else f"You seem to revisit {top_emotion.lower()} feelings most often."
    )

    return {
        "total": len(entries),
        "top_emotion": top_emotion,
        "top_labels": top_labels,
        "liked": liked,
        "kept": kept,
        "pattern": pattern,
    }


def build_app():
    root = tk.Tk()
    root.title(APP_TITLE)
    root.geometry("1180x760")
    root.minsize(1000, 640)

    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    style.configure("Header.TLabel", font=("Segoe UI", 18, "bold"))
    style.configure("Card.TFrame", background="#f4f4f8")

    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    main = ttk.Frame(root, padding=16)
    main.grid(row=0, column=0, sticky="nsew")
    main.grid_columnconfigure(0, weight=1)
    main.grid_columnconfigure(1, weight=1)
    main.grid_rowconfigure(0, weight=1)

    form_frame = ttk.LabelFrame(main, text="New thought", padding=12)
    form_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
    form_frame.grid_columnconfigure(0, weight=1)

    ttk.Label(form_frame, text="Topic").grid(row=0, column=0, sticky="w", pady=(0, 4))
    topic_entry = ttk.Entry(form_frame)
    topic_entry.grid(row=1, column=0, sticky="ew")

    ttk.Label(form_frame, text="What are you thinking about?").grid(row=2, column=0, sticky="w", pady=(12, 4))
    thought_box = scrolledtext.ScrolledText(form_frame, height=9, wrap=tk.WORD)
    thought_box.grid(row=3, column=0, sticky="ew")

    row_1 = ttk.Frame(form_frame)
    row_1.grid(row=4, column=0, sticky="ew", pady=(12, 0))
    row_1.grid_columnconfigure(1, weight=1)

    ttk.Label(row_1, text="Emotion").grid(row=0, column=0, sticky="w", padx=(0, 12))
    emotion_var = tk.StringVar(value="Neutral")
    emotion_combo = ttk.Combobox(row_1, textvariable=emotion_var, values=EMOTIONS, state="readonly", width=18)
    emotion_combo.grid(row=0, column=1, sticky="w")

    ttk.Label(row_1, text="Intensity").grid(row=0, column=2, sticky="w", padx=(18, 6))
    intensity_var = tk.IntVar(value=5)
    intensity_scale = ttk.Scale(row_1, from_=1, to=10, variable=intensity_var, orient="horizontal")
    intensity_scale.grid(row=0, column=3, sticky="ew")

    ttk.Label(form_frame, text="Labels (comma separated)").grid(row=5, column=0, sticky="w", pady=(12, 4))
    labels_entry = ttk.Entry(form_frame)
    labels_entry.grid(row=6, column=0, sticky="ew")

    options_frame = ttk.Frame(form_frame)
    options_frame.grid(row=7, column=0, sticky="w", pady=(12, 0))
    like_var = tk.BooleanVar(value=True)
    keep_var = tk.BooleanVar(value=True)

    ttk.Checkbutton(options_frame, text="I like this thought", variable=like_var).grid(row=0, column=0, padx=(0, 14))
    ttk.Checkbutton(options_frame, text="I want to keep it", variable=keep_var).grid(row=0, column=1)

    actions = ttk.Frame(form_frame)
    actions.grid(row=8, column=0, sticky="ew", pady=(18, 0))
    actions.grid_columnconfigure(0, weight=1)

    def clear_form():
        topic_entry.delete(0, tk.END)
        thought_box.delete("1.0", tk.END)
        emotion_var.set("Neutral")
        labels_entry.delete(0, tk.END)
        intensity_var.set(5)
        like_var.set(True)
        keep_var.set(True)

    def save_current_entry():
        topic = topic_entry.get()
        thought = thought_box.get("1.0", tk.END).strip()
        emotion = emotion_var.get()
        labels = labels_entry.get()
        intensity = intensity_var.get()
        like_it = like_var.get()
        keep_it = keep_var.get()

        try:
            save_entry(topic, thought, emotion, labels, intensity, like_it, keep_it)
            clear_form()
            refresh_entries()
        except ValueError as error:
            messagebox.showwarning("Missing content", str(error))

    save_button = ttk.Button(actions, text="Save thought", command=save_current_entry)
    save_button.grid(row=0, column=0, sticky="e")

    history_frame = ttk.LabelFrame(main, text="Thought history", padding=12)
    history_frame.grid(row=0, column=1, sticky="nsew")
    history_frame.grid_columnconfigure(0, weight=1)
    history_frame.grid_rowconfigure(1, weight=1)

    search_row = ttk.Frame(history_frame)
    search_row.grid(row=0, column=0, sticky="ew")
    search_row.grid_columnconfigure(1, weight=1)

    ttk.Label(search_row, text="Search").grid(row=0, column=0, sticky="w", padx=(0, 8))
    search_var = tk.StringVar()
    search_box = ttk.Entry(search_row, textvariable=search_var)
    search_box.grid(row=0, column=1, sticky="ew")

    tree = ttk.Treeview(
        history_frame,
        columns=("timestamp", "topic", "emotion", "keep"),
        show="headings",
        height=14,
    )
    tree.heading("timestamp", text="Time")
    tree.heading("topic", text="Topic")
    tree.heading("emotion", text="Emotion")
    tree.heading("keep", text="Keep")
    tree.column("timestamp", width=150, anchor="center")
    tree.column("topic", width=200, anchor="w")
    tree.column("emotion", width=120, anchor="center")
    tree.column("keep", width=80, anchor="center")
    tree.grid(row=1, column=0, sticky="nsew", pady=(8, 0))

    action_row = ttk.Frame(history_frame)
    action_row.grid(row=2, column=0, sticky="e", pady=(8, 0))

    def delete_selected():
        selection = tree.selection()
        if not selection:
            return

        entry_to_delete = entry_lookup.get(selection[0])
        if not entry_to_delete:
            return

        confirm = messagebox.askyesno("Delete thought", "Delete this thought from your journal?")
        if not confirm:
            return

        entries = load_entries()
        remaining = [
            entry
            for entry in entries
            if entry.get("timestamp") != entry_to_delete.get("timestamp") or entry.get("thought") != entry_to_delete.get("thought")
        ]

        with DATA_FILE.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=CSV_FIELDS)
            writer.writeheader()
            writer.writerows(remaining)

        refresh_entries()

    delete_button = ttk.Button(action_row, text="Delete selected", command=delete_selected)
    delete_button.grid(row=0, column=0)

    detail_frame = ttk.LabelFrame(main, text="Entry details", padding=10)
    detail_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 12), pady=(12, 0))
    detail_frame.grid_columnconfigure(0, weight=1)
    detail_text = scrolledtext.ScrolledText(detail_frame, height=12, wrap=tk.WORD)
    detail_text.grid(row=0, column=0, sticky="nsew")

    insight_frame = ttk.LabelFrame(main, text="Patterns & insight", padding=10)
    insight_frame.grid(row=1, column=1, sticky="nsew", pady=(12, 0))
    insight_frame.grid_columnconfigure(0, weight=1)
    insight_text = scrolledtext.ScrolledText(insight_frame, height=12, wrap=tk.WORD)
    insight_text.grid(row=0, column=0, sticky="nsew")

    entry_lookup = {}

    def refresh_entries():
        nonlocal entry_lookup
        entries = load_entries()
        query = search_var.get().strip().lower()

        if query:
            filtered = [
                entry
                for entry in entries
                if query in entry.get("topic", "").lower()
                or query in entry.get("thought", "").lower()
                or query in entry.get("emotion", "").lower()
                or query in entry.get("labels", "").lower()
            ]
        else:
            filtered = entries

        tree.delete(*tree.get_children())
        entry_lookup = {}
        for entry in filtered:
            row_id = tree.insert(
                "",
                "end",
                values=(
                    entry.get("timestamp", "")[:16],
                    entry.get("topic", "General"),
                    entry.get("emotion", "Neutral"),
                    "Yes" if entry.get("keep_it") == "True" else "No",
                ),
            )
            entry_lookup[row_id] = entry

        summary = summarize_entries(filtered if filtered else entries)
        insight_text.delete("1.0", tk.END)
        insight_text.insert(
            "1.0",
            f"Total thoughts: {summary['total']}\n"
            f"Top emotion: {summary['top_emotion']}\n"
            f"Top labels: {summary['top_labels']}\n"
            f"Liked: {summary['liked']}\n"
            f"Marked to keep: {summary['kept']}\n\n"
            f"Pattern note: {summary['pattern']}"
        )

        selection = tree.selection()
        if selection:
            selected_entry = entry_lookup.get(selection[0])
            if selected_entry:
                detail_text.delete("1.0", tk.END)
                detail_text.insert(
                    "1.0",
                    f"Time: {selected_entry.get('timestamp', '')}\n"
                    f"Topic: {selected_entry.get('topic', 'General')}\n"
                    f"Emotion: {selected_entry.get('emotion', 'Neutral')}\n"
                    f"Intensity: {selected_entry.get('intensity', '5')} / 10\n"
                    f"Labels: {selected_entry.get('labels', '') or 'None'}\n"
                    f"Liked: {'Yes' if selected_entry.get('like_it') == 'True' else 'No'}\n"
                    f"Keep: {'Yes' if selected_entry.get('keep_it') == 'True' else 'No'}\n\n"
                    f"Thought:\n{selected_entry.get('thought', '')}"
                )
        else:
            detail_text.delete("1.0", tk.END)
            detail_text.insert("1.0", "Select an entry from the history list to view details.")

    def show_selected_item(event=None):
        selection = tree.selection()
        if not selection:
            return
        selected_entry = entry_lookup.get(selection[0])
        if not selected_entry:
            return

        detail_text.delete("1.0", tk.END)
        detail_text.insert(
            "1.0",
            f"Time: {selected_entry.get('timestamp', '')}\n"
            f"Topic: {selected_entry.get('topic', 'General')}\n"
            f"Emotion: {selected_entry.get('emotion', 'Neutral')}\n"
            f"Intensity: {selected_entry.get('intensity', '5')} / 10\n"
            f"Labels: {selected_entry.get('labels', '') or 'None'}\n"
            f"Liked: {'Yes' if selected_entry.get('like_it') == 'True' else 'No'}\n"
            f"Keep: {'Yes' if selected_entry.get('keep_it') == 'True' else 'No'}\n\n"
            f"Thought:\n{selected_entry.get('thought', '')}"
        )

    tree.bind("<<TreeviewSelect>>", show_selected_item)
    search_var.trace_add("write", lambda *_: refresh_entries())

    refresh_entries()
    root.mainloop()


if __name__ == "__main__":
    ensure_data_file()
    build_app()
