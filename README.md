# Circular Linked List Visualizer

**DES Pune University — School of Science and Mathematics**  
**Department of Computer Science | CE3 Mini Project**  
**Course: Data Structures and Algorithms**

---

## Group Members

| Roll No. | Name |
|---|---|
| 3542511029 | Pranjal Rajesh Kale |
| 3542511031 | Sakshi Mandar Kapre |
| 3542511032 | Nikhil Shantkumar Patil |

**Group:** 8 | **Topic:** Circular Linked List

---

## What This Project Does

An interactive desktop application that **visualizes a Circular Linked List** with animations.  
Nodes are displayed in a ring layout. Every operation animates step-by-step so you can see exactly how pointers change.

### Features

| Feature | Description |
|---|---|
| Insert at Beginning | Adds a node before HEAD, updates circular pointer |
| Insert at End | Appends a node, last → HEAD pointer maintained |
| Insert at Position | Inserts at any index |
| Delete by Value | Finds and removes a node, re-links the ring |
| Delete by Position | Removes node at a given index |
| Search / Find | Animates traversal, highlights the found node |
| Traverse | Visits every node with a moving highlight |
| Reverse | Reverses the list with animated pointer updates |
| Undo | Restores the list to the previous state |
| Step-by-step mode | Pause at each step — press Next Step to continue |
| Speed control | Slow / Medium / Fast animation speed |
| Export | Saves the canvas as a PostScript (.ps) file |

---

## Tech Stack

- **Language:** Python 3.x
- **GUI:** tkinter (built-in)
- **Animation:** tkinter Canvas with `after()` scheduling
- **Export:** Python `postscript()` (+ Pillow optional)
- **No web server, no database, no external frameworks**

---

## How to Run

### 1. Install the only dependency
```bash
pip install pillow
```

### 2. Run the app
```bash
python main.py
```

That's it. The app window opens with a demo list pre-loaded.

---

## File Structure

```
circular_linked_list/
├── main.py          ← Entry point — run this
├── cll.py           ← Pure CLL logic (Node class, all operations)
├── visualizer.py    ← Canvas drawing & animation engine
├── app.py           ← Main window, control panel, button wiring
├── README.md        ← This file
└── requirements.txt ← pillow
```

---

## How Operations Work (for Viva)

**Circular Linked List:** The last node's `next` pointer points back to the HEAD instead of `None`. This makes traversal loop forever unless you track where you started.

**Insert at Beginning:**
1. Create new node
2. Find last node (traverse until `node.next == head`)
3. `new_node.next = head`
4. `last.next = new_node`
5. `head = new_node`

**Delete by Value:**
1. If deleting head: `last.next = head.next`, `head = head.next`
2. Otherwise: find node where `current.next.data == target`, set `current.next = current.next.next`

**Reverse:**
1. Iterate through all nodes
2. Flip each `next` pointer to point backward
3. Fix head and circular link



## Requirements

```
pillow
```