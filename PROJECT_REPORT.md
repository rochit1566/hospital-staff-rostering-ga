# HOSPITAL STAFF ROSTERING USING GENETIC ALGORITHM
## BTech / BE Project Report

**Submitted by:** [Student Name]  
**Roll Number:** [Roll Number]  
**Department:** [Department Name]  
**Institution:** [College Name]  
**Academic Year:** [Academic Year]  
**Project Guide:** [Guide Name]

---

## Abstract
Hospital staff rostering is a constrained optimization problem in which staff members must be assigned to shifts while respecting staffing demand, skill requirements, availability, rest periods, and workload fairness. Manual scheduling can be time-consuming and may create uneven workloads or avoidable conflicts. This project develops an educational roster-generation prototype using a Genetic Algorithm (GA), a population-based optimization method inspired by natural selection.

Each candidate solution represents an assignment of staff members to required duty slots. Candidate rosters are evaluated using a fitness function that heavily penalizes hard-constraint violations and then penalizes uneven distributions of total shifts, night shifts, and weekend duties. The algorithm uses tournament selection, one-point crossover, mutation, elitism, and a repair/reconstruction procedure. The project includes a Python scheduling engine, a Streamlit user interface, CSV/Excel export, a fictional sample dataset, and automated tests.

The system is intended as an academic prototype. Any real hospital deployment would require locally approved staffing rules, clinical review, privacy safeguards, and more extensive validation.

## 1. Introduction
Hospitals operate continuously and need appropriately qualified staff across day, evening, and night shifts. A duty roster must cover demand while observing individual constraints and distributing less desirable shifts fairly. The number of possible combinations grows rapidly with staff size and planning horizon, making the problem difficult to solve manually.

Genetic Algorithms are suitable for exploring large search spaces. They maintain a population of candidate solutions and evolve them using selection and variation operators. This project applies GA concepts to a simplified seven-day hospital staffing scenario.

## 2. Problem Statement
Given a set of staff members, their skills and availability, shift definitions, and required staffing counts, generate a weekly roster that:
1. Fills each required staff slot with a qualified and available staff member.
2. Avoids assigning a staff member to overlapping shifts or shifts with insufficient rest.
3. Respects maximum total and night-shift limits.
4. Distributes total duties, night duties, and weekend duties as fairly as possible.

## 3. Objectives
- Implement a Genetic Algorithm in Python.
- Represent weekly duty slots and staff eligibility.
- Define hard and soft scheduling constraints.
- Produce a roster and a separate validation report.
- Visualize workload distribution.
- Export roster data to CSV and Excel.
- Test important parsing, validation, and output behavior.

## 4. Scope and Assumptions
The demonstration uses fictional staff, three eight-hour shifts, and a seven-day planning horizon. The sample requirements request two people for each shift each day. The data is deliberately small enough for a college demonstration. Skills are represented as labels; the example uses the `Nurse` skill as the base coverage requirement. Real clinical roles, unit-specific coverage, approved leave, contracted hours, handover time, fatigue policies, and local regulations are outside this simplified model unless added to the input data and constraints.

## 5. System Requirements
### Hardware
- Standard laptop/desktop
- 4 GB RAM recommended
- Keyboard, display, and network connection for initial package installation

### Software
- Python 3.10+
- Streamlit
- Pandas
- Matplotlib
- OpenPyXL

## 6. System Architecture
The system has five logical modules:
1. **Input module:** reads staff, shift, and staffing requirement CSV files.
2. **Slot generator:** expands each demand row into individual duty slots.
3. **GA engine:** creates and evolves candidate schedules.
4. **Validation and metrics module:** checks hard constraints and calculates workload measures.
5. **Presentation/export module:** displays results and exports CSV/Excel files.

## 7. Methodology
### 7.1 Chromosome representation
A chromosome is a list whose length equals the number of required staffing slots. Each gene contains a staff ID or `None` if a slot cannot be filled.

### 7.2 Initial population
Candidate rosters are constructed in randomized slot order. For each slot, the algorithm selects an eligible staff member who is available, has the required skill, is within shift limits, and has sufficient rest from other assigned shifts where possible.

### 7.3 Fitness function
The fitness function is minimized:

`Fitness = 10000 × number_of_hard_violations + soft_penalty`

The soft penalty combines workload variance, night-duty variance, and weekend-duty variance. The high hard-violation weight makes constraint satisfaction more important than fairness preferences. The validation function independently reports unfilled slots, skill/availability violations, excess shift counts, excess night counts, and rest conflicts.

### 7.4 Genetic operators
- **Selection:** tournament selection chooses parents from a small random group.
- **Crossover:** one-point crossover combines two parent chromosomes.
- **Mutation:** randomly changes selected genes to eligible staff candidates.
- **Elitism:** preserves a small number of top candidate chromosomes.
- **Repair/reconstruction:** rebuilds the candidate schedule after crossover or mutation to reduce invalid assignments.

### 7.5 Termination
The algorithm stops after a fixed number of generations and returns the best chromosome found. Because a GA is stochastic, different random seeds and settings can produce different rosters.

## 8. Implementation
The core scheduling logic is in `ga_scheduler.py`. The interactive dashboard is in `app.py`. CSV input files are stored in `data/`. Automated checks are in `tests/test_scheduler.py`.

To run the system:
1. Install Python 3.10 or newer.
2. Install dependencies using `pip install -r requirements.txt`.
3. Run `streamlit run app.py`.
4. Adjust the GA settings and select **Generate roster**.
5. Review the roster, validation status, and workload metrics.
6. Download the roster as CSV or Excel.

## 9. Testing Plan
The supplied automated tests check:
- Correct expansion of requirements into 42 weekly slots.
- Correct parsing of skill labels.
- Detection of unfilled slots.
- Correct number of output rows and expected columns after a short GA run.

Before submission, run `python -m unittest discover -s tests -v` and paste the actual output into the final report. Do not claim test success unless the command completes successfully.

## 10. Results and Discussion
The output roster contains one row per required staffing slot, including day, shift, required skill, assigned staff member, start time, and duration. The dashboard reports the fitness score, number of detected hard violations, filled-slot count, and staff workload metrics.

The fitness score is a relative optimization measure for this model, not a clinical safety score. A result with zero detected violations means only that the encoded constraints passed; it does not establish suitability for real hospital use. If a roster contains unfilled slots or violations, change the input requirements or staff capacity, adjust GA settings, and rerun the scheduler.

**Insert screenshots here:**
- Screenshot 1: application input overview
- Screenshot 2: generated weekly roster
- Screenshot 3: workload fairness chart
- Screenshot 4: downloaded CSV/Excel output

**Record actual experiment values here after running the application:**
- Population size: [value]
- Generations: [value]
- Random seed: [value]
- Fitness score: [actual output]
- Hard violations: [actual output]
- Filled slots: [actual output]

## 11. Advantages
- Automates repetitive roster construction.
- Supports configurable input data.
- Provides a transparent constraint-checking report.
- Demonstrates evolutionary optimization concepts.
- Exports results for further review.

## 12. Limitations
- GA does not guarantee a globally optimal schedule.
- Simplified data and rules do not represent every hospital's requirements.
- Reconstructive repair may reduce the diversity and effectiveness of crossover.
- The prototype does not model preferences, approved leave workflows, labor agreements, fairness across multiple weeks, or emergency call-outs.
- A zero-violation result is only as reliable as the rules encoded in the software.

## 13. Future Enhancements
- Add a database and user authentication.
- Support multiple wards and role-specific minimum coverage.
- Add leave requests and staff preferences.
- Optimize across a month or multiple scheduling periods.
- Compare GA with integer linear programming or simulated annealing.
- Add a schedule comparison dashboard and downloadable PDF report.
- Improve repair logic and add a feasibility pre-check.

## 14. Conclusion
This project demonstrates how a Genetic Algorithm can be used to construct hospital duty rosters under simplified staffing constraints. It combines a Python optimization engine, explicit validation, workload metrics, and a user interface. The project provides a practical example of applying evolutionary computation to a real-world scheduling problem while emphasizing that operational deployment requires stronger domain-specific rules and expert review.

## References
1. Holland, J. H. (1975). *Adaptation in Natural and Artificial Systems*. University of Michigan Press.
2. Goldberg, D. E. (1989). *Genetic Algorithms in Search, Optimization, and Machine Learning*. Addison-Wesley.
3. Mitchell, M. (1998). *An Introduction to Genetic Algorithms*. MIT Press.
4. Python documentation: https://docs.python.org/3/
5. Streamlit documentation: https://docs.streamlit.io/
6. pandas documentation: https://pandas.pydata.org/docs/
