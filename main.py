import pandas as pd
import random
import networkx as nx

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor

df = pd.read_csv("synthetictraffic_data.csv")

categorical_cols = [
    "time_of_day", "day_of_week", "block_type", "signal_state", "weather"
]

for col in categorical_cols:
    df[col] = df[col].astype(str)

X = df[categorical_cols]
y = df["travel_time"]

preprocessor = ColumnTransformer([
    ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_cols)
])

pipeline = Pipeline([
    ("preprocessor", preprocessor),
    ("model", RandomForestRegressor(n_estimators=100, random_state=42))
])

pipeline.fit(X, y)

grid = [
    ['A','T','0','T','0','0','M','0','0'],
    ['T','X','0','X','0','X','0','0','0'],
    ['0','M','t','0','0','0','0','S','0'],
    ['0','X','S','X','0','X','0','X','T'],
    ['T','0','0','T','0','M','0','0','0'],
    ['0','X','0','X','0','X','S','X','B'],
    ['0','0','0','0','T','0','0','0','0']
]

rows, cols = len(grid), len(grid[0])

time_of_day = "morning"
day_of_week = "weekday"
weather = "sunny"

def generate_signals():
    signal_map = {}
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 'T':
                signal_map[(r, c)] = random.choice(["red", "yellow", "green"])
    return signal_map

def get_weight_ml(cell, r, c, signal_map):

    if cell in ['X', 'S', 'M']:
        return float('inf')

    signal = "none"
    if cell == 'T':
        signal = signal_map.get((r, c), "green")

    sample = pd.DataFrame([{
        "time_of_day": time_of_day,
        "day_of_week": day_of_week,
        "block_type": str(cell),
        "signal_state": signal,
        "weather": weather
    }])

    base_weight = pipeline.predict(sample)[0]

   
    for dr, dc in [(1,0),(-1,0),(0,1),(0,-1)]:
        nr, nc = r + dr, c + dc

        if 0 <= nr < rows and 0 <= nc < cols:

            if grid[nr][nc] == 'S':
                if time_of_day == "morning":
                    base_weight *= 1.8
                elif time_of_day == "afternoon":
                    base_weight *= 1.5
                else:
                    base_weight *= 1.1

            if grid[nr][nc] == 'M':
                if time_of_day == "evening":
                    base_weight *= 1.8
                elif day_of_week == "weekend":
                    base_weight *= 1.6
                else:
                    base_weight *= 1.2

    if cell == 'T':
        if signal == "red":
            base_weight *= 4
        elif signal == "yellow":
            base_weight *= 2

    return base_weight

def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def run_full_system(start_input, end_input, time_of_day_input, day_input, weather_input):

    global time_of_day, day_of_week, weather

    time_of_day = time_of_day_input
    day_of_week = day_input
    weather = weather_input

    signal_map = generate_signals()

    G = nx.Graph()

    for r in range(rows):
        for c in range(cols):

            if grid[r][c] not in ['X', 'S', 'M']:
                G.add_node((r, c))

                for dr, dc in [(1,0),(-1,0),(0,1),(0,-1)]:
                    nr, nc = r + dr, c + dc

                    if 0 <= nr < rows and 0 <= nc < cols:
                        if grid[nr][nc] not in ['X', 'S', 'M']:
                            weight = get_weight_ml(grid[nr][nc], nr, nc, signal_map)
                            G.add_edge((r, c), (nr, nc), weight=weight)

    path = nx.astar_path(G, start_input, end_input, heuristic=heuristic, weight='weight')

    total_time = sum(
        G[path[i]][path[i+1]]['weight'] for i in range(len(path)-1)
    )

    return path, total_time

if __name__ == "__main__":
    path, time = run_full_system((0,0), (6,8), "morning", "weekday", "sunny")
    print("Path:", path)
    print("Time:", round(time, 2))