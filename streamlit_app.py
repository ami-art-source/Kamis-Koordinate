import math
import random
import streamlit as st

# -----------------------------
# Dynamisches Farbschema
# -----------------------------
THEMES = [
    {"bg": "#f3e8ff", "accent": "#9d4edd", "text": "#2b0b3f"},
    {"bg": "#e0f7fa", "accent": "#00838f", "text": "#00363a"},
    {"bg": "#fff3e0", "accent": "#fb8c00", "text": "#4a2c00"},
    {"bg": "#fce4ec", "accent": "#d81b60", "text": "#4a001f"},
    {"bg": "#e8f5e9", "accent": "#43a047", "text": "#0b3014"},
]
theme = random.choice(THEMES)

st.set_page_config(page_title="Magisches System", layout="wide")

st.markdown(
    f"""
    <style>
    body {{
        background-color: {theme["bg"]};
        color: {theme["text"]};
    }}
    .stApp {{
        background-color: {theme["bg"]};
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# Gemeinsame Hilfsfunktionen
# -----------------------------

def x_from_units(k):
    return round(k * math.sqrt(3), 10)

def format_x_as_k_sqrt3(k):
    if k == 0:
        return "0"
    if k == 1:
        return "√3"
    if k == -1:
        return "-√3"
    return f"{k}·√3"

def weight_function(x, y):
    r = math.sqrt(x*x + y*y)
    alpha = 0.32
    base = math.exp(alpha * r)
    max_r = math.sqrt(20*20 + 20*20)
    edge_boost = 1 + 200000 * (r / max_r)**4
    return base * edge_boost

# -----------------------------
# Generator-Funktionen
# -----------------------------

def generate_single_coordinate():
    if random.random() < 1/2000000:
        return (0, 0, 0)
    if random.random() < 0.8:
        return None

    possible_k = list(range(-10, 11))
    x_candidates = [x_from_units(k) for k in possible_k]
    valid_kx = [(k, x) for k, x in zip(possible_k, x_candidates) if -20 <= x <= 20]
    possible_y = list(range(-20, 21))

    weighted_coords = []
    for k, x in valid_kx:
        for y in possible_y:
            sqrt3_units = abs(k)
            y_units = abs(y)
            sqrt3_is_odd = (sqrt3_units % 2 != 0)
            y_is_odd = (y_units % 2 != 0)
            if sqrt3_is_odd and not y_is_odd:
                continue
            if not sqrt3_is_odd and y_is_odd:
                continue
            if abs(y) > 20 - abs(k):
                continue
            w = weight_function(x, y)
            weighted_coords.append((k, x, y, w))

    total_weight = sum(w for (_, _, _, w) in weighted_coords)
    r = random.uniform(0, total_weight)
    cumulative = 0
    for k, x, y, w in weighted_coords:
        cumulative += w
        if cumulative >= r:
            return (k, x, y)

def generate_multiple_coordinates(n):
    return [generate_single_coordinate() for _ in range(n)]

def compute_full_probability_table():
    possible_k = list(range(-10, 11))
    possible_y = list(range(-20, 21))
    coords = []
    for k in possible_k:
        x = x_from_units(k)
        if not (-20 <= x <= 20):
            continue
        for y in possible_y:
            sqrt3_units = abs(k)
            y_units = abs(y)
            sqrt3_is_odd = (sqrt3_units % 2 != 0)
            y_is_odd = (y_units % 2 != 0)
            if sqrt3_is_odd and not y_is_odd:
                continue
            if not sqrt3_is_odd and y_is_odd:
                continue
            if abs(y) > 20 - abs(k):
                continue
            r = math.sqrt(x*x + y*y)
            coords.append((k, x, y, r))

    groups = {}
    for k, x, y, r in coords:
        r_key = round(r, 10)
        groups.setdefault(r_key, []).append((k, x, y))

    group_weights = {}
    for r_key, group in groups.items():
        w = sum(weight_function(x, y) for (k, x, y) in group)
        group_weights[r_key] = w

    total_weight = sum(group_weights.values())
    result = []
    for r_key, group in groups.items():
        p_group = (group_weights[r_key] / total_weight) * 100
        p_each = p_group / len(group)
        for (k, x, y) in group:
            result.append((k, y, p_each, p_group, len(group)))

    result.sort(key=lambda t: t[2])
    return result

# -----------------------------
# Konverter-Funktionen
# -----------------------------

def parse_points(text):
    cleaned = text.replace("(", " ").replace(")", " ")
    cleaned = cleaned.replace(",", " ")
    tokens = cleaned.split()
    if len(tokens) % 2 != 0:
        return None
    points = []
    for i in range(0, len(tokens), 2):
        try:
            k = int(tokens[i])
            y = int(tokens[i+1])
            points.append((k, y))
        except:
            return None
    return points

def convert_coordinate(k, y):
    if k == 0 and y == 0:
        return {
            "farbe": "Selenit",
            "farbhex": "#FFFFFF",
            "typ": "Zentrum",
            "reinheit": 100,
            "sonderfall": "Zentrum",
            "winkel": 0,
            "radius": 0
        }

    x = k * math.sqrt(3)
    r = math.sqrt(x*x + y*y)
    r_rounded = int(round(r / 2) * 2)
    r_rounded = max(0, min(20, r_rounded))

    color_map = {
        0:  ("Selenit",   "#FFFFFF"),
        2:  ("Rhodolith", "#b00b69"),
        4:  ("Amethyst",  "#7209b7"),
        6:  ("Saphir",    "#496ddb"),
        8:  ("Aquamarin", "#45aaed"),
        10: ("Smaragd",   "#00cc66"),
        12: ("Peridot",   "#a1ff0a"),
        14: ("Citrin",    "#ffff00"),
        16: ("Bernstein", "#fcc00b"),
        18: ("Carnelian", "#f98016"),
        20: ("Rubin",     "#f2002b")
    }

    farbname, farbhex = color_map[r_rounded]

    theta = math.degrees(math.atan2(y, x))
    if theta < 0:
        theta += 360

    directions = {
        90:  "Puppetry",
        30:  "Tempering",
        330: "Alchemy",
        270: "Necromancy",
        210: "Sorcery",
        150: "Forging"
    }

    def angle_diff(a, b):
        d = abs(a - b)
        return min(d, 360 - d)

    diffs = [(angle_diff(theta, d), d) for d in directions.keys()]
    diffs.sort()
    smallest_diff, best_dir = diffs[0]

    if abs(smallest_diff - 30) < 1e-9:
        second_dir = diffs[1][1]
        typ = f"{directions[best_dir]} + {directions[second_dir]}"
        reinheit = 50
        sonderfall = "Doppelte Richtung"
    else:
        typ = directions[best_dir]
        reinheit = 100 - (smallest_diff / 30) * 50
        reinheit = max(50, min(100, reinheit))
        sonderfall = None

    reinheit = round(reinheit / 10) * 10

    return {
        "farbe": farbname,
        "farbhex": farbhex,
        "typ": typ,
        "reinheit": reinheit,
        "sonderfall": sonderfall,
        "winkel": theta,
        "radius": r
    }

def build_hexagon_svg(results, points, width=700, height=750):
    cx, cy = 350, 350
    size = 300
    scale = 15

    def svg_circle(x, y, r, fill, stroke="none", sw=1):
        return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'

    def svg_line(x1, y1, x2, y2, stroke, sw=2):
        return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="{sw}"/>'

    # SVG Header
    svg = [
        f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">',
        f'<rect width="100%" height="100%" fill="{theme["bg"]}"/>'
    ]

    # Hexagon
    hex_points = []
    for angle in [90, 30, 330, 270, 210, 150]:
        rad = math.radians(angle)
        x = cx + size * math.cos(rad)
        y = cy - size * math.sin(rad)
        hex_points.append((x, y))
    hex_points_str = " ".join(f"{x},{y}" for x, y in hex_points)
    svg.append(f'<polygon points="{hex_points_str}" fill="none" stroke="#4b0082" stroke-width="3"/>')

    # Pfeile (ohne Pfeilspitzen, einfache Linien)
    arrow_specs = [
        (210, 30, "red"),
        (330, 150, "green"),
        (90, 270, "blue")
    ]
    for start_ang, end_ang, col in arrow_specs:
        r1 = size * 1.15
        r2 = size * 1.15
        sx = cx + r1 * math.cos(math.radians(start_ang))
        sy = cy - r1 * math.sin(math.radians(start_ang))
        ex = cx + r2 * math.cos(math.radians(end_ang))
        ey = cy - r2 * math.sin(math.radians(end_ang))
        svg.append(svg_line(sx, sy, ex, ey, col, 5))

    # Hintergrundpunkte
    dark_gray = "#444444"
    for kk in range(-10, 11):
        xx = kk * math.sqrt(3)
        for yy in range(-20, 21):
            sqrt3_units = abs(kk)
            y_units = abs(yy)
            sqrt3_is_odd = (sqrt3_units % 2 != 0)
            y_is_odd = (y_units % 2 != 0)
            if sqrt3_is_odd and not y_is_odd:
                continue
            if not sqrt3_is_odd and y_is_odd:
                continue
            if abs(yy) > 20 - abs(kk):
                continue
            px = cx + xx * scale
            py = cy - yy * scale
            svg.append(svg_circle(px, py, 3, dark_gray))

    # Eingabepunkte + Labels
    for index, ((k, y), res) in enumerate(zip(points, results), start=1):
        x = k * math.sqrt(3)
        px = cx + x * scale
        py = cy - y * scale
        svg.append(svg_circle(px, py, 10, res["farbhex"], stroke="#000000", sw=2))
        svg.append(
            f'<text x="{px}" y="{py - 18}" fill="{res["farbhex"]}" '
            f'font-size="10" text-anchor="middle" font-family="Arial" font-weight="bold">'
            f'{index}: ({k},{y})</text>'
        )

    # Farbverlauf-Balken
    color_map = {
        0:  "#FFFFFF",
        2:  "#b00b69",
        4:  "#7209b7",
        6:  "#496ddb",
        8:  "#45aaed",
        10: "#00cc66",
        12: "#a1ff0a",
        14: "#ffff00",
        16: "#fcc00b",
        18: "#f98016",
        20: "#f2002b"
    }
    bar_x0, bar_y0 = 50, 700
    bar_x1, bar_y1 = 650, 730
    svg.append(f'<rect x="{bar_x0}" y="{bar_y0}" width="{bar_x1-bar_x0}" height="{bar_y1-bar_y0}" fill="#eeeeee"/>')
    step_width = (bar_x1 - bar_x0) / 11
    radii = [0,2,4,6,8,10,12,14,16,18,20]
    for i, rr in enumerate(radii):
        x0 = bar_x0 + i * step_width
        svg.append(
            f'<rect x="{x0}" y="{bar_y0}" width="{step_width}" height="{bar_y1-bar_y0}" '
            f'fill="{color_map[rr]}" stroke="none"/>'
        )

    svg.append("</svg>")
    return "\n".join(svg)

# -----------------------------
# Formel-Rechner
# -----------------------------

COLOR_VALUES = {
    "Rubin": 1,
    "Carnelian": 2,
    "Bernstein": 3,
    "Citrin": 5,
    "Peridot": 6,
    "Smaragd": 7,
    "Aquamarin": 8,
    "Saphir": 9,
    "Amethyst": 10,
    "Rhodolith": 11,
    "Selenit": 13
}

def calculate_formula(c_name, p, t, l, multiplier):
    c = COLOR_VALUES[c_name]
    part1 = (math.sqrt(p) * (c ** 2)) / 10
    part2 = (t * 5 + l + 1) ** 2
    result = part1 * part2
    if multiplier:
        result *= 2
    return result

# -----------------------------
# Streamlit Layout
# -----------------------------

st.title("Magisches System – Generator, Konverter & Formel-Rechner")

tab_gen, tab_conv, tab_form = st.tabs(["Generator", "Konverter", "Formel-Rechner"])

# --- Generator-Tab ---
with tab_gen:
    st.header("Koordinaten-Generator")
    n = st.number_input("Anzahl Koordinaten", min_value=1, max_value=200, value=5, step=1)
    if st.button("Koordinaten generieren"):
        coords = generate_multiple_coordinates(n)

        st.subheader("Tabelle")
        rows = []
        for i, c in enumerate(coords, start=1):
            if c is None:
                rows.append({"Nr": i, "X": "—", "Y": "—"})
            else:
                k, x, y = c
                rows.append({"Nr": i, "X": format_x_as_k_sqrt3(k), "Y": y})
        st.table(rows)

        st.subheader("Farbliche Blöcke")
        for i, c in enumerate(coords, start=1):
            if c is None:
                st.write(f"[{i}] — keine —")
            else:
                k, x, y = c
                st.write(f"[{i}] ({format_x_as_k_sqrt3(k)}, {y})")

        st.subheader("Gewichte (sortiert)")
        weighted_list = []
        for c in coords:
            if c is not None:
                k, x, y = c
                w = weight_function(x, y)
                weighted_list.append((k, y, w))
        weighted_list.sort(key=lambda t: t[2])
        for k, y, w in weighted_list:
            st.write(f"({format_x_as_k_sqrt3(k)}, {y})   Gewicht: {w:.5f}")

    st.subheader("Vollständige Wahrscheinlichkeitstabelle")
    if st.button("Alle Wahrscheinlichkeiten berechnen"):
        table = compute_full_probability_table()
        grouped = {}
        for k, y, p_each, p_group, count in table:
            key = round(p_each, 12)
            grouped.setdefault(key, []).append((k, y, p_group, count))
        sorted_probs = sorted(grouped.keys())
        for p_each in sorted_probs:
            coords = grouped[p_each]
            p_group = coords[0][2]
            count = coords[0][3]
            st.markdown(f"**{p_each:.12f}% pro Koordinate | {p_group:.12f}% pro Ring | {count} Koordinaten**")
            line = ", ".join(f"({format_x_as_k_sqrt3(k)}, {y})" for (k, y, _, _) in coords)
            st.write(line)
            st.write("")

# --- Konverter-Tab ---
with tab_conv:
    st.header("Hexagon-Konverter")
    text = st.text_area("Mehrere Punkte eingeben (z.B. (0,0), 3 5, -4 6):", "(0,0)")
    if st.button("Konvertieren"):
        points = parse_points(text)
        if not points:
            st.error("Ungültige Eingabe.")
        else:
            results = [convert_coordinate(k, y) for k, y in points]
            st.subheader("Ergebnisse")
            for (k, y), res in zip(points, results):
                st.write(f"({k}, {y}) → {res['farbe']} | {res['typ']} | Reinheit {res['reinheit']}")
            st.subheader("Hexagon-Visualisierung")
            svg = build_hexagon_svg(results, points)
            st.markdown(svg, unsafe_allow_html=True)

# --- Formel-Rechner-Tab ---
with tab_form:
    st.header("Magischer Formel-Rechner")
    c_name = st.selectbox("Farbe (c)", list(COLOR_VALUES.keys()))
    p = st.selectbox("Reinheit (p)", [50, 60, 70, 80, 90, 100])
    t = st.selectbox("t-Wert", list(range(1, 14)))
    l = st.selectbox("l-Wert", list(range(0, 6)))
    multiplier = st.checkbox("×2 Multiplikator aktivieren")
    if st.button("Berechnen"):
        result = calculate_formula(c_name, p, t, l, multiplier)
        st.subheader(f"Ergebnis: {round(result, 3)}")
