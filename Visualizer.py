

import tkinter as tk
import math
import time


# ── Color Palette 

COLORS = {
    "bg":           "#1e1e2e",    # Canvas background (dark)
    "ring_guide":   "#313145",    # Faint dashed circle
    "node_default": "#2d2d44",    # Normal node fill
    "node_border":  "#7c7caa",    # Normal node border
    "node_head":    "#5865f2",    # HEAD node fill (blue)
    "node_head_border": "#7289da",
    "node_new":     "#57f287",    # Newly inserted node (green)
    "node_new_border": "#3ba55c",
    "node_found":   "#fee75c",    # Search result (yellow)
    "node_found_border": "#fcc419",
    "node_visiting":"#eb459e",    # Node being visited during traverse (pink)
    "node_visiting_border": "#c13584",
    "node_delete":  "#ed4245",    # Node being deleted (red)
    "node_delete_border": "#c03537",
    "node_reverse": "#ff9f43",    # Reverse highlight (orange)
    "node_reverse_border": "#f39c12",
    "node_text":    "#ffffff",    # Node data text
    "node_label":   "#a0a0c0",    # HEAD label text
    "arrow":        "#7c7caa",    # Normal arrow color
    "arrow_active": "#5865f2",    # Active arrow color
    "arrow_new":    "#57f287",    # New connection arrow
    "circular_arrow":"#fee75c",   # The special circular back-arrow
    "step_text":    "#c0c0e0",    # Step description text
    "panel_bg":     "#181825",    # Left panel bg (unused here, for reference)
}

ANIMATION_SPEEDS = {
    "Slow": 0.08,
    "Medium": 0.035,
    "Fast": 0.012,
}


class Visualizer(tk.Canvas):
    """
    The main canvas widget. Draws the CLL ring and animates operations.
    Inherits from tk.Canvas so it can be placed directly in a frame.
    """

    def __init__(self, parent, cll_ref, log_callback, step_var, speed_var, **kwargs):
        super().__init__(parent, bg=COLORS["bg"], highlightthickness=0, **kwargs)

        self.cll = cll_ref              # Reference to the CircularLinkedList object
        self.log = log_callback         # Function to write to the log panel
        self.step_var = step_var        # BooleanVar — step-by-step mode toggle
        self.speed_var = speed_var      # StringVar — "Slow" / "Medium" / "Fast"

        # Internal state
        self._node_positions = {}       # {node_data_id: (x, y)} — canvas coords
        self._step_pause = False        # Pause flag for step mode
        self._animating = False         # Lock to prevent overlapping animations
        self._highlight_states = {}     # {node_obj: color_key}
        self._step_text_id = None       # Canvas text item for step descriptions

        # Bind resize so the ring redraws when window is resized
        self.bind("<Configure>", lambda e: self.redraw())

    # ── Public API (called by app.py) 

    def redraw(self, highlights=None):
        """Full redraw of the canvas. highlights = {node_obj: color_key}."""
        self.delete("all")
        if self.cll.is_empty():
            self._draw_empty_message()
            return
        cx, cy, radius = self._ring_params()
        self._draw_ring_guide(cx, cy, radius)
        nodes = self.cll.get_nodes()
        positions = self._compute_positions(nodes, cx, cy, radius)
        self._node_positions = {id(n): positions[i] for i, n in enumerate(nodes)}
        self._draw_arrows(nodes, positions, highlights or {})
        self._draw_circular_back_arrow(nodes, positions)
        self._draw_nodes(nodes, positions, highlights or {})

    def animate_insert(self, node_obj, position_label="end"):
        """Flash the new node green, then normalize."""
        highlights = {node_obj: "node_new"}
        self.redraw(highlights)
        self.log(f"✦ Inserted {node_obj.data} at {position_label}")
        self._step_desc(f"Node {node_obj.data} inserted — next pointer updated ↻")
        self._schedule(1200, lambda: self.redraw())

    def animate_delete(self, value, success):
        """Briefly highlight the node red before removing it from CLL."""
        if not success:
            self.log(f"✗ Value {value} not found")
            self._step_desc(f"Value {value} not found in list")
            return
        self.log(f"✦ Deleted node {value}")
        self._step_desc(f"Node {value} removed — pointers re-linked ↻")
        self._schedule(900, lambda: self.redraw())

    def animate_traverse(self, values_in_order):
        """
        Highlight each node one at a time to simulate traversal.
        values_in_order = list of node data values to highlight sequentially.
        """
        if self._animating:
            return
        self._animating = True
        self.log("⟳ Traversing ring...")
        self._traverse_step(values_in_order, 0)

    def animate_search(self, target, steps, found, position):
        """
        Animate the search: visit each node in steps, highlight found in yellow.
        """
        if self._animating:
            return
        self._animating = True
        self.log(f"⌕ Searching for {target}...")
        self._search_step(target, steps, 0, found, position)

    def animate_reverse(self, reverse_steps):
        """
        Animate the reversal: highlight nodes orange one by one.
        """
        if self._animating:
            return
        self._animating = True
        self.log("⇄ Reversing list...")
        nodes_before = self.cll.get_nodes()
        self._reverse_step(nodes_before, 0, len(nodes_before))

    def stop_animation(self):
        """Force-stop any running animation."""
        self._animating = False
        self.redraw()

    # ── Drawing Helpers 

    def _ring_params(self):
        """Compute center and radius based on current canvas size."""
        w = self.winfo_width() or 600
        h = self.winfo_height() or 500
        cx = w // 2
        cy = h // 2
        # Radius: leave at least 70px margin for nodes (r=28)
        radius = min(w, h) // 2 - 90
        radius = max(radius, 80)
        return cx, cy, radius

    def _compute_positions(self, nodes, cx, cy, radius):
        """
        Compute (x, y) for each node evenly spaced on a circle.
        Start angle = -90° so first node is at top.
        """
        n = len(nodes)
        positions = []
        for i in range(n):
            angle = math.radians(-90 + (360 / n) * i)
            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)
            positions.append((x, y))
        return positions

    def _node_color(self, node, highlights):
        """Return fill and border color for a node."""
        key = highlights.get(node)
        if key:
            return COLORS[key], COLORS.get(key + "_border", COLORS["node_border"])
        return COLORS["node_default"], COLORS["node_border"]

    def _draw_empty_message(self):
        w = self.winfo_width() or 600
        h = self.winfo_height() or 500
        self.create_text(
            w // 2, h // 2,
            text="List is empty\nUse 'Insert' to add nodes",
            fill=COLORS["node_label"],
            font=("Consolas", 14),
            justify="center"
        )

    def _draw_ring_guide(self, cx, cy, radius):
        """Draw the faint dashed circle that guides node placement."""
        self.create_oval(
            cx - radius, cy - radius,
            cx + radius, cy + radius,
            outline=COLORS["ring_guide"],
            width=1,
            dash=(6, 6)
        )

    def _draw_arrows(self, nodes, positions, highlights):
        """Draw straight arrows between consecutive nodes."""
        n = len(nodes)
        for i in range(n - 1):             # Last arrow is the circular one
            x1, y1 = positions[i]
            x2, y2 = positions[i + 1]
            color = COLORS["arrow_active"] if highlights.get(nodes[i]) else COLORS["arrow"]
            self._draw_arrow_between(x1, y1, x2, y2, color, node_r=28)

    def _draw_circular_back_arrow(self, nodes, positions):
        """
        Draw the special circular arrow from last node back to head.
        Uses a curved arc path to make it visually distinct.
        """
        if len(nodes) < 2:
            return
        x1, y1 = positions[-1]             # Last node
        x2, y2 = positions[0]              # Head node

        cx = (x1 + x2) / 2
        cy_ctrl = (y1 + y2) / 2
        # Offset the control point outward for a nice curve
        mx, my = self._ring_params()[:2]
        dx = cx - mx
        dy = cy_ctrl - my
        dist = math.hypot(dx, dy) or 1
        curve_factor = 0.6
        ctrl_x = cx + dx / dist * dist * curve_factor
        ctrl_y = cy_ctrl + dy / dist * dist * curve_factor

        # Draw dashed curved arrow
        self.create_line(
            x1, y1, ctrl_x, ctrl_y, x2, y2,
            fill=COLORS["circular_arrow"],
            width=2,
            dash=(5, 4),
            smooth=True,
            arrow=tk.LAST,
            arrowshape=(10, 12, 4)
        )
        # Label
        label_x = ctrl_x + (ctrl_x - mx) / dist * 18
        label_y = ctrl_y + (ctrl_y - my) / dist * 18
        self.create_text(
            label_x, label_y,
            text="↻ circular",
            fill=COLORS["circular_arrow"],
            font=("Consolas", 9)
        )

    def _draw_arrow_between(self, x1, y1, x2, y2, color, node_r=28):
        """Draw an arrow from edge of node1 to edge of node2."""
        dx = x2 - x1
        dy = y2 - y1
        dist = math.hypot(dx, dy) or 1
        # Shorten line so it starts/ends at node edge
        sx = x1 + dx / dist * node_r
        sy = y1 + dy / dist * node_r
        ex = x2 - dx / dist * node_r
        ey = y2 - dy / dist * node_r
        self.create_line(
            sx, sy, ex, ey,
            fill=color,
            width=2,
            arrow=tk.LAST,
            arrowshape=(10, 12, 4)
        )

    def _draw_nodes(self, nodes, positions, highlights):
        """Draw each node circle with its value and optional label."""
        node_r = 28
        for i, (node, (x, y)) in enumerate(zip(nodes, positions)):
            fill, border = self._node_color(node, highlights)

            # Circle
            self.create_oval(
                x - node_r, y - node_r,
                x + node_r, y + node_r,
                fill=fill, outline=border, width=2
            )

            # Value text
            self.create_text(
                x, y,
                text=str(node.data),
                fill=COLORS["node_text"],
                font=("Consolas", 13, "bold")
            )

            # HEAD label below the top node
            if i == 0:
                self.create_text(
                    x, y + node_r + 14,
                    text="HEAD",
                    fill=COLORS["node_label"],
                    font=("Consolas", 9, "bold")
                )

    def _draw_step_text(self, text):
        """Draw step description at the bottom of the canvas."""
        if self._step_text_id:
            self.delete(self._step_text_id)
        w = self.winfo_width() or 600
        h = self.winfo_height() or 500
        self._step_text_id = self.create_text(
            w // 2, h - 20,
            text=text,
            fill=COLORS["step_text"],
            font=("Consolas", 10),
            anchor="s"
        )

    def _step_desc(self, text):
        self._draw_step_text(text)

    # ── Animation Step Loops 

    def _traverse_step(self, values, index):
        """Recursive step function for traversal animation."""
        if not self._animating or index >= len(values):
            self._animating = False
            self.redraw()
            self.log("✓ Traversal complete")
            return

        nodes = self.cll.get_nodes()
        target_node = next((n for n in nodes if n.data == values[index]), None)

        highlights = {target_node: "node_visiting"} if target_node else {}
        self.redraw(highlights)
        self._step_desc(f"Visiting node [{values[index]}]  —  step {index + 1} of {len(values)}")

        delay = self._get_delay()

        if self.step_var.get():
            # Step mode: wait for user to press Next
            self._step_pause = True
            self._wait_for_step(lambda: self._traverse_step(values, index + 1))
        else:
            self._schedule(delay, lambda: self._traverse_step(values, index + 1))

    def _search_step(self, target, steps, index, found, found_pos):
        """Recursive step function for search animation."""
        if not self._animating or index >= len(steps):
            self._animating = False
            if found:
                self.log(f"✓ Found {target} at position {found_pos}")
            else:
                self.log(f"✗ {target} not found in list")
            self.redraw()
            return

        nodes = self.cll.get_nodes()
        current_val = steps[index]
        current_node = next((n for n in nodes if n.data == current_val), None)

        if current_node:
            if current_val == target:
                highlights = {current_node: "node_found"}
                self._step_desc(f"✓ Found {target} at position {found_pos}!")
            else:
                highlights = {current_node: "node_visiting"}
                self._step_desc(f"Checking node [{current_val}] — not {target}, moving on...")
            self.redraw(highlights)

        delay = self._get_delay()
        if self.step_var.get():
            self._wait_for_step(lambda: self._search_step(target, steps, index + 1, found, found_pos))
        else:
            self._schedule(delay, lambda: self._search_step(target, steps, index + 1, found, found_pos))

    def _reverse_step(self, nodes_snapshot, index, total):
        """Highlight nodes one by one during reversal."""
        if not self._animating or index >= total:
            self._animating = False
            self.redraw()
            self.log("✓ Reverse complete")
            self._step_desc("List reversed — head is now the old tail ↻")
            return

        current_nodes = self.cll.get_nodes()
        # Highlight the node at current index from the new order
        target = current_nodes[index] if index < len(current_nodes) else None
        highlights = {target: "node_reverse"} if target else {}
        self.redraw(highlights)
        self._step_desc(f"Reversing pointer at node [{target.data if target else '?'}]")

        delay = self._get_delay()
        if self.step_var.get():
            self._wait_for_step(lambda: self._reverse_step(nodes_snapshot, index + 1, total))
        else:
            self._schedule(delay, lambda: self._reverse_step(nodes_snapshot, index + 1, total))

    # ── Utilities 

    def _get_delay(self):
        """Return animation delay in milliseconds based on speed setting."""
        speed_str = self.speed_var.get()
        sec = ANIMATION_SPEEDS.get(speed_str, 0.035)
        return int(sec * 1000)

    def _schedule(self, ms, fn):
        """Schedule a callback using tkinter's after() (non-blocking)."""
        self.after(ms, fn)

    def _wait_for_step(self, callback):
        """
        In step mode, store the callback and wait for the user to press
        the 'Next Step' button (which calls resume_step).
        """
        self._pending_step = callback

    def resume_step(self):
        """Called by the Next Step button in step mode."""
        if hasattr(self, "_pending_step") and self._pending_step:
            fn = self._pending_step
            self._pending_step = None
            fn()