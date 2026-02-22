
import streamlit as st
import random
import math

# ---------------------------------------------------------
# Hilfsfunktionen
# ---------------------------------------------------------

def count_sqrt3_units(x):
    if x == 0:
        return 0
    return round(x / math.sqrt(3))

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

# ---------------------------------------------------------
# Gewichtungsfunktion
# ---------------------------------------------------------

def weight_function(x, y):
    r = math.sqrt(x*x + y*y)

    # (0,0) extrem selten machen: ~1 von 100000
    if x == 0 and y == 0:
        return 0.1

    alpha = 0.32
    base = math.exp(alpha * r)

    max_r = math.sqrt(20*20 + 20*20)
    edge_boost = 1 + 200000 * (r / max_r)**4

    return base * edge_boost

# ---------------------------------------------------------
# Koordinaten-Generator
# ---------------------------------------------------------


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

            # Point-top Hexagon Regel
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

# ---------------------------------------------------------
# Streamlit UI (Dark Mode)
# ---------------------------------------------------------

st.set_page_config(
    page_title="Koordinaten-Generator",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark Theme Styling
st.markdown("""
<style>
body {
    background-color: #1a1a1a;
    color: #e0d7ff;
}
.block-container {
    background-color: #1a1a1a;
}
</style>
""", unsafe_allow_html=True)

st.title("🔮 Kamis-Koordinate Generator")

# Eingabe
n = st.number_input("Anzahl der Koordinaten", min_value=1, max_value=10000, value=5)

if st.button("Koordinaten generieren"):
    coords = generate_multiple_coordinates(n)

    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 Kompakte Liste",
        "📑 Tabelle",
        "📦 Gruppiert",
        "🎨 Blöcke",
        "📊 Wahrscheinlichkeiten"
    ])

    # ---------------------------------------------------------
    # Kompakte Liste
    # ---------------------------------------------------------
    with tab1:
        st.subheader("Kompakte Liste")
        for i, c in enumerate(coords, start=1):
            if c is None:
                st.write(f"{i}: **keine Koordinate**")
            else:
                k, x, y = c
                st.write(f"{i}: ({format_x_as_k_sqrt3(k)}, {y})")

    # ---------------------------------------------------------
    # Tabelle
    # ---------------------------------------------------------
    with tab2:
        st.subheader("Tabelle")
        rows = []
        for i, c in enumerate(coords, start=1):
            if c is None:
                rows.append([i, "—", "—"])
            else:
                k, x, y = c
                rows.append([i, format_x_as_k_sqrt3(k), y])
        st.table(rows)

    # ---------------------------------------------------------
    # Gruppiert
    # ---------------------------------------------------------
    with tab3:
        st.subheader("Gültige Koordinaten")
        for i, c in enumerate(coords, start=1):
            if c is not None:
                k, x, y = c
                st.write(f"- {i}: ({format_x_as_k_sqrt3(k)}, {y})")

        st.subheader("Keine Koordinate")
        for i, c in enumerate(coords, start=1):
            if c is None:
                st.write(f"- {i}")

    # ---------------------------------------------------------
    # Blöcke
    # ---------------------------------------------------------
    with tab4:
        st.subheader("Farbliche Blöcke")
        for i, c in enumerate(coords, start=1):
            if c is None:
                st.markdown(f"<div style='padding:8px;background:#663366;'>[{i}] — keine —</div>", unsafe_allow_html=True)
            else:
                k, x, y = c
                st.markdown(
                    f"<div style='padding:8px;background:#4b0082;'>[{i}] ({format_x_as_k_sqrt3(k)}, {y})</div>",
                    unsafe_allow_html=True
                )

    # ---------------------------------------------------------
    # Wahrscheinlichkeiten
    # ---------------------------------------------------------
    with tab5:
        st.subheader("Wahrscheinlichkeitstabelle (selten → häufig)")

        weighted_list = []
        total_weight = 0

        for c in coords:
            if c is not None:
                k, x, y = c
                w = weight_function(x, y)
                weighted_list.append((k, y, w))
                total_weight += w

        weighted_list.sort(key=lambda t: t[2])  # selten → häufig

        for k, y, w in weighted_list:
            prob = w / total_weight if total_weight > 0 else 0
            st.write(f"({format_x_as_k_sqrt3(k)}, {y}) — Gewicht: {w:.5f}")
