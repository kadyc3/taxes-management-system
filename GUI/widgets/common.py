"""Reusable GUI widgets."""
import tkinter as tk
from tkinter import ttk, messagebox


# ─────────────────────────────────────────────────────────── SearchBar
class SearchBar(tk.Frame):
    """A search entry with a clear button."""

    def __init__(self, parent, placeholder: str = "Search…", command=None, **kw):
        super().__init__(parent, **kw)
        self._command = command
        self._var = tk.StringVar()

        self._entry = ttk.Entry(self, textvariable=self._var, width=30)
        self._entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self._entry.bind("<KeyRelease>", self._on_key)

        self._btn_clear = ttk.Button(self, text="✕", width=3, command=self.clear)
        self._btn_clear.pack(side=tk.LEFT, padx=(2, 0))

        self._placeholder = placeholder
        self._set_placeholder()

        self._entry.bind("<FocusIn>", self._clear_placeholder)
        self._entry.bind("<FocusOut>", self._restore_placeholder)

    def _set_placeholder(self):
        self._entry.insert(0, self._placeholder)
        self._entry.config(foreground="grey")

    def _clear_placeholder(self, _=None):
        if self._entry.get() == self._placeholder:
            self._entry.delete(0, tk.END)
            self._entry.config(foreground="")

    def _restore_placeholder(self, _=None):
        if not self._entry.get():
            self._set_placeholder()

    def _on_key(self, _=None):
        if self._command:
            val = self.get()
            self._command(val)

    def get(self) -> str:
        val = self._var.get()
        return "" if val == self._placeholder else val

    def clear(self):
        self._var.set("")
        self._set_placeholder()
        if self._command:
            self._command("")


# ─────────────────────────────────────────────────────────── StatusBadge
STATUS_COLORS = {
    # Taxpayer statuses
    "active":        ("#d1fae5", "#065f46"),
    "suspended":     ("#fef3c7", "#92400e"),
    "deregistered":  ("#fee2e2", "#991b1b"),
    # Declaration statuses
    "draft":         ("#e0e7ff", "#3730a3"),
    "submitted":     ("#dbeafe", "#1e40af"),
    "validated":     ("#d1fae5", "#065f46"),
    "rejected":      ("#fee2e2", "#991b1b"),
}


class StatusBadge(tk.Label):
    def __init__(self, parent, status: str = "", **kw):
        bg, fg = STATUS_COLORS.get(status.lower(), ("#f3f4f6", "#374151"))
        super().__init__(
            parent,
            text=status.capitalize(),
            background=bg,
            foreground=fg,
            padx=6,
            pady=2,
            relief=tk.FLAT,
            **kw,
        )

    def set_status(self, status: str):
        bg, fg = STATUS_COLORS.get(status.lower(), ("#f3f4f6", "#374151"))
        self.config(text=status.capitalize(), background=bg, foreground=fg)


# ─────────────────────────────────────────────────────────── ConfirmDialog
def confirm_delete(parent, name: str) -> bool:
    return messagebox.askyesno(
        "Confirm Delete",
        f"Are you sure you want to delete '{name}'?\nThis action cannot be undone.",
        parent=parent,
        icon="warning",
    )


# ─────────────────────────────────────────────────────────── Themed Treeview
def make_treeview(parent, columns: list, show="headings", height=14) -> ttk.Treeview:
    style = ttk.Style()
    style.configure("Treeview", rowheight=26, font=("Segoe UI", 10))
    style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
    style.map("Treeview", background=[("selected", "#2563eb")], foreground=[("selected", "white")])

    tree = ttk.Treeview(parent, columns=columns, show=show, height=height)
    # alternating row colors
    tree.tag_configure("odd", background="#f9fafb")
    tree.tag_configure("even", background="white")
    return tree