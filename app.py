import streamlit as st
import pickle
import sys
import subprocess
import pandas as pd

from main import run_full_system, grid

st.set_page_config(page_title="🚗 Path Optimizer", layout="wide")

st.title("🚗 Intelligent Path Optimization System")

def to_label(r, c):
    return f"{chr(65 + r)}{c+1}"

def from_label(label):
    row = ord(label[0].upper()) - 65
    col = int(label[1:]) - 1
    return (row, col)

def display_grid(grid):
    visual = []

    for r in range(len(grid)):
        row = []
        for c in range(len(grid[0])):
            cell = grid[r][c]
            label = to_label(r, c)

            if cell == 'X':
                row.append("⬛")
            elif cell == 'A':
                row.append("🟢 A")
            elif cell == 'B':
                row.append("🔴 B")
            elif cell == 'S':
                row.append("🏫")
            elif cell == 'M':
                row.append("🏬")
            elif cell == 'T':
                row.append("🚦")
            else:
                row.append(label)

        visual.append(row)

    df = pd.DataFrame(visual)
    st.dataframe(df, use_container_width=True)

col1, col2 = st.columns([1, 1.2])

with col1:

    st.subheader("⚙️ Trip Configuration")

    time_of_day = st.selectbox(
        "🕒 Time of Day",
        ["morning", "afternoon", "evening", "night"]
    )

    day_of_week = st.selectbox(
        "📅 Day Type",
        ["weekday", "weekend"]
    )

    weather = st.selectbox(
        "🌦 Weather",
        ["sunny", "rain", "fog"]
    )

    locations = []
    for r in range(len(grid)):
        for c in range(len(grid[0])):
            if grid[r][c] not in ['X','S','M']:
                locations.append(to_label(r, c))

    start_label = st.selectbox("📍 Start Location", locations)
    end_label = st.selectbox("🏁 End Location", locations)

    start_tuple = from_label(start_label)
    end_tuple = from_label(end_label)

    if st.button("🚀 Find Optimal Path", use_container_width=True):

        try:
            with st.spinner("Calculating best route... ⏳"):

                path, total_time = run_full_system(
                    start_tuple,
                    end_tuple,
                    time_of_day,
                    day_of_week,
                    weather
                )

            st.success("✅ Path Found!")

            st.markdown(f"**📍 Path:** `{path}`")
            st.markdown(f"**⏱ Total Time:** `{round(total_time, 2)} sec`")

            # Save for animation
            with open("path_data.pkl", "wb") as f:
                pickle.dump((path, total_time), f)

            st.session_state["path_ready"] = True

        except Exception as e:
            st.error(f"❌ Error: {e}")

    if st.session_state.get("path_ready"):
        if st.button("🎬 Show Animation", use_container_width=True):
            subprocess.run([sys.executable, "visual.py"])

with col2:
    st.subheader("🗺️ City Grid Map")

    st.caption("Legend: ⬛ Blocked | 🚦 Signal | 🏫 School | 🏬 Mall")

    display_grid(grid)
