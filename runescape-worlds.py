import requests
import tkinter as tk
from bs4 import BeautifulSoup

URL = "http://oldschool.runescape.com/slu?order=WmpLA"

CELL_W = 90
CELL_H = 55
COLS = 25

previous = {}
cells = {}
world_order = []


# --- UI CONFIG STATE ---
def get_refresh():
    return int(refresh_var.get())

def get_pos_limit():
    return int(pos_var.get())

def get_neg_limit():
    return int(neg_var.get())


def fetch_worlds():
    res = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(res.text, "html.parser")

    result = []
    rows = soup.select(".server-list__body .server-list__row")

    for row in rows:
        world_el = row.select_one(".server-list__world-link")
        if not world_el:
            continue

        digits = "".join(filter(str.isdigit, world_el.text))
        if not digits:
            continue

        world = int(digits) + 300

        cols = row.select(".server-list__row-cell")
        if len(cols) < 2:
            continue

        players_text = cols[1].text.strip()
        digits = "".join(filter(str.isdigit, players_text))
        players = int(digits) if digits else 0

        result.append((world, players))

    return result


def get_color(delta):
    if delta >= get_pos_limit():
        return "#003300"
    elif delta <= get_neg_limit():
        return "#330000"
    return "#1a1a1a"


def create_grid(canvas, worlds):
    for i, world in enumerate(worlds):
        row = i // COLS
        col = i % COLS

        x1 = col * CELL_W
        y1 = row * CELL_H
        x2 = x1 + CELL_W
        y2 = y1 + CELL_H

        rect = canvas.create_rectangle(x1, y1, x2, y2, fill="#1a1a1a", outline="#333")

        text_world = canvas.create_text(
            x1 + CELL_W // 2, y1 + 12,
            text=str(world),
            fill="white",
            font=("Arial", 9, "bold")
        )

        text_players = canvas.create_text(
            x1 + CELL_W // 2, y1 + 28,
            text="0",
            fill="white",
            font=("Arial", 9)
        )

        text_delta = canvas.create_text(
            x1 + CELL_W // 2, y1 + 44,
            text="0",
            fill="gray",
            font=("Arial", 8)
        )

        cells[world] = {
            "rect": rect,
            "players": text_players,
            "delta": text_delta
        }


def update():
    try:
        data = fetch_worlds()
        world_map = dict(data)

        global world_order

        if not world_order:
            world_order = sorted(world_map.keys())
            create_grid(canvas, world_order)

            rows = (len(world_order) // COLS) + 1
            canvas.config(width=COLS * CELL_W, height=rows * CELL_H)

        for world in world_order:
            players = world_map.get(world, 0)

            prev = previous.get(world)
            delta = players - prev if prev is not None else 0

            color = get_color(delta)

            cell = cells[world]

            canvas.itemconfig(cell["rect"], fill=color)
            canvas.itemconfig(cell["players"], text=str(players))
            canvas.itemconfig(cell["delta"], text=f"{delta:+}")

            previous[world] = players

    except Exception as e:
        print("Error:", e)

    root.after(get_refresh(), update)


# --- UI ---
root = tk.Tk()
root.title("OSRS World Grid (Fast)")
root.configure(bg="#111")


# CONTROL BAR
controls = tk.Frame(root, bg="#111")
controls.pack(fill="x", pady=5)

# Refresh dropdown
tk.Label(controls, text="Refresh (ms):", fg="white", bg="#111").pack(side="left")

refresh_var = tk.StringVar(value="10000")
refresh_menu = tk.OptionMenu(
    controls,
    refresh_var,
    "1000", "2000", "5000", "10000", "20000", "30000"
)
refresh_menu.pack(side="left", padx=5)

# + limit
tk.Label(controls, text="+ Limit:", fg="white", bg="#111").pack(side="left", padx=(10, 0))

pos_var = tk.StringVar(value="5")
tk.Spinbox(controls, from_=0, to=100, textvariable=pos_var, width=5).pack(side="left", padx=5)

# - limit
tk.Label(controls, text="- Limit:", fg="white", bg="#111").pack(side="left", padx=(10, 0))

neg_var = tk.StringVar(value="-5")
tk.Spinbox(controls, from_=-100, to=0, textvariable=neg_var, width=5).pack(side="left", padx=5)


# CANVAS
canvas = tk.Canvas(root, bg="#111", highlightthickness=0)
canvas.pack()

update()
root.mainloop()