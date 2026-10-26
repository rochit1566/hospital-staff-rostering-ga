from pathlib import Path
import io
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from ga_scheduler import load_inputs, run_ga, roster_metrics

BASE = Path(__file__).resolve().parent
st.set_page_config(page_title="Hospital Staff Rostering GA", page_icon="🏥", layout="wide")
st.title("🏥 Hospital Staff Rostering Using Genetic Algorithm")
st.caption("Educational prototype • Python + Genetic Algorithm")

staff, shifts, requirements = load_inputs(BASE / "data")
with st.sidebar:
    st.header("Algorithm settings")
    population = st.slider("Population size", 20, 200, 80, 10)
    generations = st.slider("Generations", 20, 500, 150, 10)
    mutation = st.slider("Mutation rate", 0.01, 0.30, 0.08, 0.01)
    rest = st.slider("Minimum rest (hours)", 8, 16, 10, 1)
    seed = st.number_input("Random seed", min_value=0, max_value=999999, value=42, step=1)
    run = st.button("Generate roster", type="primary", use_container_width=True)

st.subheader("Input overview")
c1, c2, c3 = st.columns(3)
c1.metric("Staff members", len(staff))
c2.metric("Required staffing slots", sum(r[3] for r in requirements))
c3.metric("Planning period", "7 days")
with st.expander("View sample staff and staffing requirements"):
    staff_df = pd.read_csv(BASE / "data" / "staff.csv")
    req_df = pd.read_csv(BASE / "data" / "requirements.csv")
    st.markdown("**Staff data**")
    st.dataframe(staff_df, use_container_width=True)
    st.markdown("**Requirements**")
    st.dataframe(req_df, use_container_width=True)

if run or "result" not in st.session_state:
    with st.spinner("Searching for a roster..."):
        st.session_state.result = run_ga(
            staff, shifts, requirements,
            population_size=population, generations=generations,
            mutation_rate=mutation, rest_hours=rest, seed=int(seed)
        )
result = st.session_state.result
roster = result.roster
metrics = roster_metrics(roster, staff)
st.subheader("Generated roster")
m1, m2, m3 = st.columns(3)
m1.metric("Fitness score", f"{result.fitness:.2f}")
m2.metric("Hard violations", len(result.hard_violations))
m3.metric("Filled slots", f"{(roster['Staff ID'] != 'UNFILLED').sum()}/{len(roster)}")
st.dataframe(roster, use_container_width=True, hide_index=True)
if result.hard_violations:
    st.warning("Review the constraints below. Do not use this schedule operationally until all violations are resolved.")
    st.write(result.hard_violations)
else:
    st.success("No hard-constraint violations detected by the prototype validator.")
st.subheader("Workload fairness")
st.dataframe(metrics, use_container_width=True, hide_index=True)
fig, ax = plt.subplots()
ax.bar(metrics["Name"], metrics["Total Shifts"])
ax.set_ylabel("Number of assigned shifts")
ax.set_title("Total shifts per staff member")
ax.tick_params(axis="x", rotation=45)
fig.tight_layout()
st.pyplot(fig)
csv_data = roster.to_csv(index=False).encode("utf-8")
st.download_button("Download roster as CSV", csv_data, "hospital_roster.csv", "text/csv")
excel_buffer = io.BytesIO()
with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
    roster.to_excel(writer, sheet_name="Roster", index=False)
    metrics.to_excel(writer, sheet_name="Workload Metrics", index=False)
st.download_button("Download roster and metrics as Excel", excel_buffer.getvalue(),
                   "hospital_roster.xlsx",
                   "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
st.info("This is an educational demonstration with fictional data. Clinical scheduling requires local policy review and independent validation.")
