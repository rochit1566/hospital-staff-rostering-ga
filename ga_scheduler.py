"""Genetic Algorithm scheduler for an educational hospital rostering project."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple
import random
import pandas as pd

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

@dataclass(frozen=True)
class Staff:
    staff_id: str
    name: str
    skills: frozenset[str]
    available_days: frozenset[str]
    max_shifts: int
    max_nights: int

@dataclass(frozen=True)
class Shift:
    shift_id: str
    shift_name: str
    start_hour: int
    duration_hours: int
    is_night: bool
    is_weekend: bool = False

@dataclass(frozen=True)
class Slot:
    day: str
    shift_id: str
    skill: str
    slot_no: int

@dataclass
class ScheduleResult:
    roster: pd.DataFrame
    fitness: float
    hard_violations: List[str]
    soft_penalty: float
    generations: int

def load_inputs(data_dir: str | Path):
    data_dir = Path(data_dir)
    staff_df = pd.read_csv(data_dir / "staff.csv").fillna("")
    shifts_df = pd.read_csv(data_dir / "shifts.csv").fillna("")
    req_df = pd.read_csv(data_dir / "requirements.csv").fillna("")
    staff = []
    for r in staff_df.to_dict("records"):
        staff.append(Staff(
            staff_id=str(r["staff_id"]), name=str(r["name"]),
            skills=frozenset(x.strip() for x in str(r["skills"]).split("|") if x.strip()),
            available_days=frozenset(x.strip() for x in str(r["available_days"]).split("|") if x.strip()),
            max_shifts=int(r["max_shifts"]), max_nights=int(r["max_nights"])
        ))
    shifts = {}
    for r in shifts_df.to_dict("records"):
        shifts[str(r["shift_id"])] = Shift(
            shift_id=str(r["shift_id"]), shift_name=str(r["shift_name"]),
            start_hour=int(r["start_hour"]), duration_hours=int(r["duration_hours"]),
            is_night=bool(int(r["is_night"])), is_weekend=bool(int(r.get("is_weekend", 0) or 0))
        )
    requirements = []
    for r in req_df.to_dict("records"):
        requirements.append((str(r["day"]), str(r["shift_id"]), str(r["skill"]), int(r["required"])))
    return staff, shifts, requirements

def build_slots(requirements):
    slots = []
    for day, shift_id, skill, required in requirements:
        for i in range(required):
            slots.append(Slot(day, shift_id, skill, i + 1))
    return slots

def _start_abs(day: str, shift: Shift) -> int:
    return DAYS.index(day) * 24 + shift.start_hour

def _overlap_or_insufficient_rest(slot_a: Slot, slot_b: Slot, shifts: Dict[str, Shift], rest_hours: int) -> bool:
    a_start = _start_abs(slot_a.day, shifts[slot_a.shift_id])
    b_start = _start_abs(slot_b.day, shifts[slot_b.shift_id])
    a_end = a_start + shifts[slot_a.shift_id].duration_hours
    b_end = b_start + shifts[slot_b.shift_id].duration_hours
    if b_start < a_start:
        a_start, b_start = b_start, a_start
        a_end, b_end = b_end, a_end
    return b_start < a_end + rest_hours

def validate_assignment(assignments, slots, staff, shifts, rest_hours=10):
    violations = []
    counts = {s.staff_id: 0 for s in staff}
    nights = {s.staff_id: 0 for s in staff}
    by_staff = {s.staff_id: [] for s in staff}
    staff_map = {s.staff_id: s for s in staff}
    for i, staff_id in enumerate(assignments):
        slot = slots[i]
        if staff_id is None:
            violations.append(f"Unfilled slot: {slot.day} {slot.shift_id} ({slot.skill})")
            continue
        person = staff_map[staff_id]
        counts[staff_id] += 1
        if shifts[slot.shift_id].is_night:
            nights[staff_id] += 1
        by_staff[staff_id].append(slot)
        if slot.day not in person.available_days:
            violations.append(f"{person.name} assigned on unavailable day {slot.day}")
        if slot.skill not in person.skills:
            violations.append(f"{person.name} lacks required skill {slot.skill}")
    for person in staff:
        if counts[person.staff_id] > person.max_shifts:
            violations.append(f"{person.name} exceeds max shifts ({counts[person.staff_id]} > {person.max_shifts})")
        if nights[person.staff_id] > person.max_nights:
            violations.append(f"{person.name} exceeds max nights ({nights[person.staff_id]} > {person.max_nights})")
        assigned = sorted(by_staff[person.staff_id], key=lambda sl: _start_abs(sl.day, shifts[sl.shift_id]))
        for a, b in zip(assigned, assigned[1:]):
            if _overlap_or_insufficient_rest(a, b, shifts, rest_hours):
                violations.append(f"{person.name} has overlapping/insufficient-rest assignments: {a.day} {a.shift_id} and {b.day} {b.shift_id}")
    return violations, counts, nights

def soft_penalty(assignments, slots, staff, shifts):
    counts = {s.staff_id: 0 for s in staff}
    nights = {s.staff_id: 0 for s in staff}
    weekend = {s.staff_id: 0 for s in staff}
    for i, sid in enumerate(assignments):
        if sid is None:
            continue
        counts[sid] += 1
        shift = shifts[slots[i].shift_id]
        if shift.is_night:
            nights[sid] += 1
        if slots[i].day in ("Sat", "Sun") or shift.is_weekend:
            weekend[sid] += 1
    def variance(values):
        if not values:
            return 0.0
        avg = sum(values) / len(values)
        return sum((v - avg) ** 2 for v in values) / len(values)
    return 2.0 * variance(list(counts.values())) + 3.0 * variance(list(nights.values())) + 1.5 * variance(list(weekend.values()))

def fitness(assignments, slots, staff, shifts, rest_hours=10):
    violations, _, _ = validate_assignment(assignments, slots, staff, shifts, rest_hours)
    penalty = soft_penalty(assignments, slots, staff, shifts)
    # Hard violations dominate all soft preferences.
    return 10000 * len(violations) + penalty, violations, penalty

def _candidate_ids(slot, staff):
    return [s.staff_id for s in staff if slot.skill in s.skills and slot.day in s.available_days]

def make_individual(slots, staff, shifts, rng, rest_hours=10):
    # Construct a schedule slot-by-slot, preferring eligible staff with fewer duties.
    assignments = []
    staff_map = {s.staff_id: s for s in staff}
    counts = {s.staff_id: 0 for s in staff}
    nights = {s.staff_id: 0 for s in staff}
    assigned_slots = {s.staff_id: [] for s in staff}
    order = list(range(len(slots)))
    rng.shuffle(order)
    result = [None] * len(slots)
    for idx in order:
        slot = slots[idx]
        candidates = _candidate_ids(slot, staff)
        rng.shuffle(candidates)
        feasible = []
        for sid in candidates:
            person = staff_map[sid]
            if counts[sid] >= person.max_shifts:
                continue
            if shifts[slot.shift_id].is_night and nights[sid] >= person.max_nights:
                continue
            if any(_overlap_or_insufficient_rest(old, slot, shifts, rest_hours) for old in assigned_slots[sid]):
                continue
            feasible.append(sid)
        if feasible:
            feasible.sort(key=lambda sid: counts[sid] + 0.6 * nights[sid] + rng.random() * 0.25)
            chosen = feasible[0]
            result[idx] = chosen
            counts[chosen] += 1
            nights[chosen] += int(shifts[slot.shift_id].is_night)
            assigned_slots[chosen].append(slot)
        else:
            result[idx] = None
    return result

def run_ga(staff, shifts, requirements, population_size=100, generations=250,
           mutation_rate=0.08, elite_count=4, rest_hours=10, seed=42):
    if not staff:
        raise ValueError("At least one staff member is required.")
    slots = build_slots(requirements)
    if not slots:
        raise ValueError("Requirements contain no staffing slots.")
    rng = random.Random(seed)
    population = [make_individual(slots, staff, shifts, rng, rest_hours) for _ in range(population_size)]
    def score(ind):
        return fitness(ind, slots, staff, shifts, rest_hours)[0]
    best = min(population, key=score)
    best_score = score(best)
    for _ in range(generations):
        population.sort(key=score)
        next_population = [p[:] for p in population[:elite_count]]
        while len(next_population) < population_size:
            # Tournament selection
            def tournament():
                contestants = rng.sample(population, min(4, len(population)))
                return min(contestants, key=score)
            p1, p2 = tournament(), tournament()
            if len(slots) > 1:
                cut = rng.randrange(1, len(slots))
                child = p1[:cut] + p2[cut:]
            else:
                child = p1[:]
            for i in range(len(child)):
                if rng.random() < mutation_rate:
                    candidates = _candidate_ids(slots[i], staff)
                    child[i] = rng.choice(candidates) if candidates else None
            # Repair: greedily resolve assignments that are ineligible or conflict.
            child = repair(child, slots, staff, shifts, rng, rest_hours)
            next_population.append(child)
        population = next_population
        current = min(population, key=score)
        current_score = score(current)
        if current_score < best_score:
            best, best_score = current[:], current_score
    hard, _, soft = fitness(best, slots, staff, shifts, rest_hours)
    roster_rows = []
    staff_map = {s.staff_id: s for s in staff}
    for i, slot in enumerate(slots):
        sid = best[i]
        sh = shifts[slot.shift_id]
        roster_rows.append({
            "Day": slot.day, "Shift": sh.shift_name, "Shift ID": slot.shift_id,
            "Required Skill": slot.skill, "Slot": slot.slot_no,
            "Staff ID": sid or "UNFILLED",
            "Staff Name": staff_map[sid].name if sid in staff_map else "UNFILLED",
            "Start": f"{sh.start_hour:02d}:00",
            "Duration (hours)": sh.duration_hours,
            "Night Shift": "Yes" if sh.is_night else "No"
        })
    roster = pd.DataFrame(roster_rows)
    violations, _, _ = validate_assignment(best, slots, staff, shifts, rest_hours)
    return ScheduleResult(roster, best_score, violations, soft, generations)

def repair(assignments, slots, staff, shifts, rng, rest_hours=10):
    """Repair invalid assignments by rebuilding the schedule in a randomized order."""
    # Rebuild from scratch rather than trusting potentially conflicting crossover genes.
    # This keeps the GA chromosome valid whenever the input constraints allow it.
    return make_individual(slots, staff, shifts, rng, rest_hours)

def roster_metrics(roster, staff):
    assigned = roster[roster["Staff ID"] != "UNFILLED"].copy()
    if assigned.empty:
        return pd.DataFrame(columns=["Staff ID", "Name", "Total Shifts", "Night Shifts", "Weekend Shifts"])
    metrics = []
    for s in staff:
        mine = assigned[assigned["Staff ID"] == s.staff_id]
        metrics.append({
            "Staff ID": s.staff_id, "Name": s.name,
            "Total Shifts": len(mine),
            "Night Shifts": int((mine["Night Shift"] == "Yes").sum()),
            "Weekend Shifts": int(mine["Day"].isin(["Sat", "Sun"]).sum())
        })
    return pd.DataFrame(metrics)

def main():
    here = Path(__file__).resolve().parent
    staff, shifts, requirements = load_inputs(here / "data")
    result = run_ga(staff, shifts, requirements)
    result.roster.to_csv(here / "roster_output.csv", index=False)
    print("=== Hospital Staff Rostering Using Genetic Algorithm ===")
    print(f"Fitness score: {result.fitness:.2f}")
    print(f"Unfilled/constraint violations: {len(result.hard_violations)}")
    for v in result.hard_violations[:20]:
        print("-", v)
    print(f"Roster saved to: {here / 'roster_output.csv'}")
    print(result.roster.to_string(index=False))

if __name__ == "__main__":
    main()
