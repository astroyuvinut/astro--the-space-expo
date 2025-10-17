# astro--the-space-expo

Predicts satellite passes - tells you exactly when satellites like the International Space Station (ISS) will fly overhead and be visible from your specific location. Uses live satellite data (TLE - Two-Line Elements) from Celestrak to get real-time orbital information.

## Quickstart (Windows PowerShell)

1. Create a virtual environment and install deps:
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

2. Run the pass predictor (CLI, defaults to ISS NORAD ID 25544):
```powershell
python -m src.orbits.pass_predictor --lat 28.6139 --lon 77.2090 --hours 24 --min-elev 5
```

3. Streamlit UI (optional):
```powershell
streamlit run app/streamlit_app.py
```

## Project layout
- `src/` – library code
- `src/orbits/pass_predictor.py` – CLI + functions to compute passes
- `app/streamlit_app.py` – simple UI for the pass predictor
- `notebooks/` – exploratory work (starter provided soon)
- `data/` – local data (git-ignored)

## Next steps
- Choose a track (EO / Orbits / Astro) and we can add the corresponding mini-project next.
- If you pick Orbits, we can extend this into a ground-track visualizer and a simple tasking scheduler.

## 👨‍💻 About the Developer

**Name:** Yuva  
**Email:** astroyuvinut@gmail.com

Yuva is a computer science student and aspiring AI specialist with a focus on space exploration technologies. He is the creator of Space Exploration AI – Satellite Pass Predictor, a project that integrates orbital mechanics, real-time satellite data, and AI-driven analytics to provide accurate satellite visibility predictions.

**Technical Skills:** Python, NumPy, Pandas, SciPy, Skyfield, Streamlit, Typer, Rich

**Vision:** To leverage artificial intelligence to enhance astrodynamics and satellite observation, making space exploration more accessible and efficient.

---
