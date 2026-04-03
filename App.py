

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from Cll import CircularLinkedList
from Visualizer import Visualizer
import copy


# ── Theme Constants 

BG_DARK     = "#181825"
BG_PANEL    = "#1e1e2e"
BG_CARD     = "#2d2d44"
ACCENT      = "#5865f2"
ACCENT_HOVER= "#7289da"
SUCCESS     = "#57f287"
DANGER      = "#ed4245"
WARNING     = "#fee75c"
TEXT_MAIN   = "#cdd6f4"
TEXT_MUTED  = "#7c7caa"
BORDER      = "#313145"
FONT_MAIN   = ("Consolas", 11)
FONT_BOLD   = ("Consolas", 11, "bold")
FONT_SMALL  = ("Consolas", 9)
FONT_HEAD   = ("Consolas", 13, "bold")


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        # Window setup
        self.title("Circular Linked List Visualizer — DES Pune University")
        self.geometry("1100x680")
        self.minsize(900, 580)
        self.configure(bg=BG_DARK)

        # Data
        self.cll = CircularLinkedList()
        self._undo_stack = []              # Stack of list snapshots for undo

        # Control variables
        self.step_var = tk.BooleanVar(value=False)
        self.speed_var = tk.StringVar(value="Medium")

        # Build UI
        self._build_layout()
        self._seed_demo_data()             # Pre-populate with a few nodes

    # ── Layout 

    def _build_layout(self):
        """Split the window into left panel and right canvas."""
        # Left panel (fixed width)
        self.panel = tk.Frame(self, bg=BG_PANEL, width=220)
        self.panel.pack(side=tk.LEFT, fill=tk.Y, padx=(10, 0), pady=10)
        self.panel.pack_propagate(False)

        # Right canvas area
        canvas_frame = tk.Frame(self, bg=BG_DARK)
        canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Canvas title
        tk.Label(
            canvas_frame,
            text="Circular Linked List",
            bg=BG_DARK, fg=TEXT_MAIN,
            font=FONT_HEAD
        ).pack(anchor="w", padx=8, pady=(0, 6))

        # Visualizer canvas
        self.viz = Visualizer(
            canvas_frame,
            cll_ref=self.cll,
            log_callback=self._log,
            step_var=self.step_var,
            speed_var=self.speed_var,
        )
        self.viz.pack(fill=tk.BOTH, expand=True)

        self._build_panel()

    def _build_panel(self):
        p = self.panel

        # ── Title ──
        tk.Label(p, text="Operations", bg=BG_PANEL, fg=TEXT_MAIN,
                 font=FONT_HEAD).pack(pady=(16, 10))

        self._divider(p)

        # ── Insert section ──
        tk.Label(p, text="INSERT", bg=BG_PANEL, fg=TEXT_MUTED,
                 font=FONT_SMALL).pack(anchor="w", padx=14, pady=(8, 2))

        self._btn(p, "➕  Insert at Beginning", self._insert_beginning, color=ACCENT)
        self._btn(p, "➕  Insert at End",       self._insert_end,       color=ACCENT)
        self._btn(p, "➕  Insert at Position",  self._insert_position,  color=ACCENT)

        self._divider(p)

        # ── Delete section ──
        tk.Label(p, text="DELETE", bg=BG_PANEL, fg=TEXT_MUTED,
                 font=FONT_SMALL).pack(anchor="w", padx=14, pady=(8, 2))

        self._btn(p, "✖  Delete by Value",    self._delete_value,    color=DANGER)
        self._btn(p, "✖  Delete at Position", self._delete_position, color=DANGER)

        self._divider(p)

        # ── Explore section ──
        tk.Label(p, text="EXPLORE", bg=BG_PANEL, fg=TEXT_MUTED,
                 font=FONT_SMALL).pack(anchor="w", padx=14, pady=(8, 2))

        self._btn(p, "⌕  Search",            self._search)
        self._btn(p, "⟳  Traverse",          self._traverse)
        self._btn(p, "⇄  Reverse",           self._reverse, color=WARNING, text_color="#1e1e2e")

        self._divider(p)

        # ── Utilities ──
        tk.Label(p, text="UTILITIES", bg=BG_PANEL, fg=TEXT_MUTED,
                 font=FONT_SMALL).pack(anchor="w", padx=14, pady=(8, 2))

        self._btn(p, "↩  Undo",              self._undo)
        self._btn(p, "⬜  Clear All",         self._clear, color="#555577")
        self._btn(p, "📷  Export Image",      self._export, color=SUCCESS, text_color="#1e1e2e")

        self._divider(p)

        # ── Speed control ──
        tk.Label(p, text="SPEED", bg=BG_PANEL, fg=TEXT_MUTED,
                 font=FONT_SMALL).pack(anchor="w", padx=14, pady=(8, 2))

        speed_frame = tk.Frame(p, bg=BG_PANEL)
        speed_frame.pack(fill=tk.X, padx=14, pady=(0, 6))
        for speed in ["Slow", "Medium", "Fast"]:
            tk.Radiobutton(
                speed_frame,
                text=speed,
                variable=self.speed_var,
                value=speed,
                bg=BG_PANEL, fg=TEXT_MAIN,
                selectcolor=BG_CARD,
                activebackground=BG_PANEL,
                font=FONT_SMALL
            ).pack(side=tk.LEFT)

        # ── Step-by-step toggle ──
        step_frame = tk.Frame(p, bg=BG_PANEL)
        step_frame.pack(fill=tk.X, padx=14, pady=(4, 4))
        tk.Checkbutton(
            step_frame,
            text="Step-by-step mode",
            variable=self.step_var,
            bg=BG_PANEL, fg=TEXT_MAIN,
            selectcolor=BG_CARD,
            activebackground=BG_PANEL,
            font=FONT_SMALL
        ).pack(side=tk.LEFT)

        # ── Next Step button (shown in step mode) ──
        self.next_step_btn = self._btn(
            p, "▶  Next Step", self._next_step, color="#ff9f43", text_color="#1e1e2e"
        )

        self._divider(p)

        # ── Log panel ──
        tk.Label(p, text="LOG", bg=BG_PANEL, fg=TEXT_MUTED,
                 font=FONT_SMALL).pack(anchor="w", padx=14, pady=(8, 2))

        log_frame = tk.Frame(p, bg=BG_CARD, bd=0)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        self.log_box = tk.Text(
            log_frame,
            bg=BG_CARD, fg=TEXT_MAIN,
            font=FONT_SMALL,
            state=tk.DISABLED,
            wrap=tk.WORD,
            relief=tk.FLAT,
            padx=6, pady=6
        )
        self.log_box.pack(fill=tk.BOTH, expand=True)

        # ── Size counter at bottom of panel ──
        self.size_label = tk.Label(
            p, text="Nodes: 0",
            bg=BG_PANEL, fg=TEXT_MUTED,
            font=FONT_SMALL
        )
        self.size_label.pack(pady=(0, 8))

    # ── Button Factory 

    def _btn(self, parent, text, command, color=BG_CARD, text_color=TEXT_MAIN):
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            bg=color,
            fg=text_color,
            font=FONT_MAIN,
            relief=tk.FLAT,
            activebackground=ACCENT_HOVER,
            activeforeground="#ffffff",
            cursor="hand2",
            pady=6
        )
        btn.pack(fill=tk.X, padx=10, pady=3)

        # Hover effects
        original_bg = color
        btn.bind("<Enter>", lambda e: btn.config(bg=ACCENT_HOVER, fg="#ffffff"))
        btn.bind("<Leave>", lambda e: btn.config(bg=original_bg, fg=text_color))

        return btn

    def _divider(self, parent):
        tk.Frame(parent, bg=BORDER, height=1).pack(fill=tk.X, padx=10, pady=4)

    # ── Insert Operations 

    def _get_int_input(self, prompt, title="Input"):
        val = simpledialog.askstring(title, prompt, parent=self)
        if val is None:
            return None
        try:
            return int(val.strip())
        except ValueError:
            messagebox.showerror("Invalid input", "Please enter a whole number.")
            return None

    def _push_undo(self):
        """Save current list state before any mutation."""
        self._undo_stack.append(self.cll.to_list())
        if len(self._undo_stack) > 20:
            self._undo_stack.pop(0)            # Cap stack at 20 snapshots

    def _insert_beginning(self):
        val = self._get_int_input("Enter value to insert at beginning:")
        if val is None:
            return
        self._push_undo()
        node = self.cll.insert_at_beginning(val)
        self._update_size()
        self.viz.animate_insert(node, "beginning")

    def _insert_end(self):
        val = self._get_int_input("Enter value to insert at end:")
        if val is None:
            return
        self._push_undo()
        node = self.cll.insert_at_end(val)
        self._update_size()
        self.viz.animate_insert(node, "end")

    def _insert_position(self):
        val = self._get_int_input("Enter value to insert:")
        if val is None:
            return
        pos = self._get_int_input(f"Enter position (0 = beginning, max = {self.cll.size()}):", "Position")
        if pos is None:
            return
        self._push_undo()
        node = self.cll.insert_at_position(val, pos)
        self._update_size()
        self.viz.animate_insert(node, f"position {pos}")

    # ── Delete Operations 

    def _delete_value(self):
        if self.cll.is_empty():
            messagebox.showinfo("Empty", "The list is already empty.")
            return
        val = self._get_int_input("Enter value to delete:")
        if val is None:
            return
        self._push_undo()
        # Highlight the node before deleting
        nodes = self.cll.get_nodes()
        target = next((n for n in nodes if n.data == val), None)
        if target:
            self.viz.redraw({target: "node_delete"})
            self.viz.after(700, lambda: self._do_delete_value(val))
        else:
            self._do_delete_value(val)

    def _do_delete_value(self, val):
        deleted = self.cll.delete_by_value(val)
        self._update_size()
        self.viz.animate_delete(val, deleted is not None)

    def _delete_position(self):
        if self.cll.is_empty():
            messagebox.showinfo("Empty", "The list is already empty.")
            return
        pos = self._get_int_input(f"Enter position to delete (0–{self.cll.size()-1}):", "Position")
        if pos is None:
            return
        if pos < 0 or pos >= self.cll.size():
            messagebox.showerror("Out of range", f"Position must be between 0 and {self.cll.size()-1}.")
            return
        self._push_undo()
        nodes = self.cll.get_nodes()
        target = nodes[pos]
        self.viz.redraw({target: "node_delete"})
        self.viz.after(700, lambda: self._do_delete_position(pos, target.data))

    def _do_delete_position(self, pos, val):
        self.cll.delete_at_position(pos)
        self._update_size()
        self.viz.animate_delete(val, True)

    # ── Explore Operations 

    def _search(self):
        if self.cll.is_empty():
            messagebox.showinfo("Empty", "The list is empty.")
            return
        val = self._get_int_input("Enter value to search:")
        if val is None:
            return
        found, pos, steps = self.cll.search(val)
        self.viz.animate_search(val, steps, found, pos)

    def _traverse(self):
        if self.cll.is_empty():
            messagebox.showinfo("Empty", "The list is empty.")
            return
        values = self.cll.to_list()
        self.viz.animate_traverse(values)

    def _reverse(self):
        if self.cll.size() < 2:
            messagebox.showinfo("Nothing to reverse", "Need at least 2 nodes to reverse.")
            return
        self._push_undo()
        steps = self.cll.reverse()
        self.viz.animate_reverse(steps)

    # ── Utilities 

    def _undo(self):
        if not self._undo_stack:
            messagebox.showinfo("Nothing to undo", "No operations to undo.")
            return
        previous = self._undo_stack.pop()
        self.cll = CircularLinkedList()
        for val in previous:
            self.cll.insert_at_end(val)
        # Update visualizer's reference
        self.viz.cll = self.cll
        self._update_size()
        self.viz.redraw()
        self._log("↩ Undo — restored previous state")

    def _clear(self):
        if self.cll.is_empty():
            return
        if messagebox.askyesno("Clear All", "Delete all nodes?"):
            self._push_undo()
            self.cll = CircularLinkedList()
            self.viz.cll = self.cll
            self._update_size()
            self.viz.redraw()
            self._log("⬜ List cleared")

    def _export(self):
        """Save the canvas as a PostScript file, then convert to PNG if Pillow available."""
        try:
            from PIL import Image
            import io, os

            # Save postscript
            ps_data = self.viz.postscript(colormode="color")

            # Convert to PNG using Pillow + Ghostscript if available
            # Fallback: save as .ps (always works)
            save_path = "cll_export.ps"
            with open(save_path, "w") as f:
                f.write(ps_data)

            self._log(f"📷 Exported to {save_path}")
            messagebox.showinfo(
                "Exported",
                f"Canvas saved as '{save_path}'.\nOpen with any PostScript viewer or convert to PDF."
            )
        except Exception as e:
            messagebox.showerror("Export failed", str(e))

    def _next_step(self):
        """Called when user presses 'Next Step' in step mode."""
        self.viz.resume_step()

    # ── Helpers 

    def _log(self, message):
        self.log_box.config(state=tk.NORMAL)
        self.log_box.insert(tk.END, message + "\n")
        self.log_box.see(tk.END)
        self.log_box.config(state=tk.DISABLED)

    def _update_size(self):
        self.size_label.config(text=f"Nodes: {self.cll.size()}")

    def _seed_demo_data(self):
        """Pre-populate with demo nodes so the app opens looking good."""
        for val in [10, 25, 42, 67, 89]:
            self.cll.insert_at_end(val)
        self._update_size()
        self.viz.after(200, self.viz.redraw)   # Small delay to let canvas size settle
        self._log("▶ Demo list loaded: 10 → 25 → 42 → 67 → 89 → ↻")
        self._log("  Try Insert, Traverse, or Search!")