# Saudization AI Consultant

An AI-powered tool that analyzes labor market and worker survey data to provide evidence-based recommendations for increasing Saudization rates across sectors.

---

## Setup (5 steps)

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Add your API key
Copy `.env.example` to `.env` and paste your Anthropic API key:
```
ANTHROPIC_API_KEY=sk-ant-...
```
Get a key at: https://console.anthropic.com/

### 3. Add your data
Place your CSV files in the `/data` folder:
- `labor_market.csv` — sector-level Saudization percentages
- `survey.csv` — your survey responses with sector, satisfaction, hours, etc.

### 4. Update column names
Open `data_loader.py` and update the column name variables at the top of `build_sector_summary()` to match your actual CSV headers.

### 5. Run the app
```bash
streamlit run app.py
```
The app will open in your browser automatically.

---

## Expected CSV formats

### labor_market.csv (example)
| sector       | saudi_pct | non_saudi_pct |
|-------------|-----------|---------------|
| IT          | 23.4      | 76.6          |
| Healthcare  | 41.2      | 58.8          |
| Construction| 8.1       | 91.9          |

### survey.csv (example)
| sector       | satisfaction | work_hours | reason_for_leaving | ... |
|-------------|-------------|------------|-------------------|-----|
| IT          | 3.2         | 52         | low salary        | ... |
| Healthcare  | 4.1         | 48         | good benefits     | ... |

Column names don't need to match exactly — just update the variable names in `data_loader.py`.

---

## Future improvements (when turning into a web app)
- Move from Streamlit to FastAPI + React frontend
- Add user authentication
- Add charts and visualizations of the data
- Allow uploading new data files through the UI
- Add Arabic language UI toggle
