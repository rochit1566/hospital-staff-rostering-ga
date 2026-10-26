# PowerPoint Outline: Hospital Staff Rostering Using Genetic Algorithm

## Slide 1 — Title
- Hospital Staff Rostering Using Genetic Algorithm
- Student name, roll number, department, college, guide

## Slide 2 — Introduction
- Hospitals operate 24/7
- Staff must be assigned to shifts
- Manual scheduling is time-consuming and can be unfair

## Slide 3 — Problem Statement
- Cover every required shift
- Respect skills, availability, shift limits, and rest periods
- Balance night and weekend duties

## Slide 4 — Objectives
- Implement GA in Python
- Generate weekly roster
- Validate constraints
- Measure workload fairness
- Export results

## Slide 5 — Existing vs Proposed System
- Existing: manual assignment, difficult to scale, errors possible
- Proposed: automated search, configurable inputs, explicit validation
- Note: algorithm assists scheduling; it does not replace human approval

## Slide 6 — Technologies
- Python
- Genetic Algorithm
- Pandas
- Streamlit
- Matplotlib
- CSV/Excel

## Slide 7 — System Architecture
Input CSVs → Slot Generator → Genetic Algorithm → Constraint Validator → Dashboard and Export

## Slide 8 — Genetic Algorithm
- Chromosome: staff assignment for every slot
- Fitness: hard-constraint penalty + fairness penalty
- Selection: tournament
- Crossover: one-point
- Mutation: random gene changes
- Elitism: retain best candidates

## Slide 9 — Constraints
Hard:
- Skill eligibility
- Staff availability
- Maximum shifts and nights
- Minimum rest
- No unfilled slots

Soft:
- Total duty balance
- Night duty balance
- Weekend duty balance

## Slide 10 — Application Screenshots
- Add screenshot of input overview
- Add screenshot of generated roster
- Add screenshot of workload chart

## Slide 11 — Results and Testing
- Report actual fitness and violation count
- Show filled slots / total slots
- Show unit test output
- Do not insert invented values

## Slide 12 — Conclusion and Future Work
- Demonstrates GA-based scheduling
- Future: leave management, multi-ward support, monthly planning, advanced optimization

## Slide 13 — References
- Holland (1975)
- Goldberg (1989)
- Mitchell (1998)
- Python, Streamlit, and pandas documentation
