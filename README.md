# Hospital Staff Rostering Using Genetic Algorithm

BTech/BE college project implemented in Python. It generates a weekly hospital duty roster using a Genetic Algorithm (GA), checks the resulting roster against explicit constraints, and provides a Streamlit interface for demonstration.

## Features
- Staff, skill, availability, and shift definitions in editable CSV files
- Genetic Algorithm with population initialization, tournament selection, crossover, mutation, and elitism
- Hard-constraint validation: required skill coverage, availability, no same-day double assignment, and minimum rest between shifts
- Soft-constraint scoring: workload balance, night-shift balance, and weekend-duty balance
- CSV and Excel-compatible export
- Streamlit dashboard with roster table and workload chart
- Unit tests for key scheduling constraints

## Project structure
```text
hospital_staff_rostering_ga/
├── app.py
├── ga_scheduler.py
├── requirements.txt
├── README.md
├── PROJECT_REPORT.md
├── PRESENTATION_OUTLINE.md
├── data/
│   ├── staff.csv
│   ├── shifts.csv
│   └── requirements.csv
└── tests/
    └── test_scheduler.py
```

## Requirements
- Python 3.10 or later
- Internet access only for installing the listed Python packages (not required while running the app after installation)

## Setup
Open a terminal in this folder and run:

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

## Run the application
```bash
streamlit run app.py
```
Open the local URL printed in the terminal by Streamlit.

## Run the scheduler from the command line
```bash
python ga_scheduler.py
```
This generates `roster_output.csv` and prints a validation summary. The result depends on the random seed and GA settings.

## Run tests
```bash
python -m unittest discover -s tests -v
```

## Input data format
- `staff.csv`: `staff_id,name,skills,available_days,max_shifts,max_nights`
  - `skills` and `available_days` are pipe-separated, e.g. `Nurse|ICU` and `Mon|Tue|Wed`.
- `shifts.csv`: `shift_id,shift_name,start_hour,duration_hours,is_night,is_weekend`
  - `start_hour` uses a 24-hour clock; duration may extend into the next day.
- `requirements.csv`: `day,shift_id,skill,required`
  - Each row states how many people with a given skill are required for that day and shift.

## Important assumptions and limitations
This is an educational prototype, not a clinical deployment system. The sample roster uses fictional staff and simplified rules. Real deployments require review by hospital operations, HR, labor/legal specialists, and clinical leadership. Actual fatigue-risk rules, qualifications, leave, contractual limits, handover time, local labor law, and emergency coverage must be modeled and validated before operational use. A GA is stochastic and may not find a feasible solution for every input; always review the validation report.

## Reproducibility
The command-line example uses a fixed random seed by default. Change the `seed` argument when calling `run_ga(...)` to explore different candidate rosters.
