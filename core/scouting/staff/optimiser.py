"""Coach candidate loading and optimisation helpers."""

from math import floor

import pandas as pd
from highspy import Highs, HighsModelStatus

from core.memory.staff import build_staff_table_for_uids, read_current_manager_staff_row
from core.scouting.staff.roles import COACHING_AREA_COLUMNS
from core.scouting.staff.shortlist import load_staff_shortlist_dataframe
from core.uids import normalise_uid

RAW_SCORE_COLUMNS = {area: f"{area} Raw" for area in COACHING_AREA_COLUMNS}


def normalise_uid_values(uids):
    return {normalise_uid(uid) for uid in uids or [] if pd.notna(uid)}


def normalise_club_value(value):
    if value is None or (pd.isna(value) if not isinstance(value, str) else False):
        return None

    text = str(value).strip()
    return None if not text else text.casefold()


def coach_role_score_to_stars(role_score):
    return floor((role_score + 30) / 30) / 2


def validate_uid_constraints(included_uids=None, excluded_uids=None):
    overlapping_uids = sorted(normalise_uid_values(included_uids) & normalise_uid_values(excluded_uids))
    if overlapping_uids:
        raise ValueError(f"UIDs cannot be both included and excluded: {', '.join(str(uid) for uid in overlapping_uids)}")


def normalise_training_area(area):
    return area.value if hasattr(area, "value") else str(area)


def get_active_coaching_areas(excluded_areas=None):
    excluded_area_values = {normalise_training_area(area) for area in excluded_areas or []}
    invalid_areas = sorted(excluded_area_values - set(COACHING_AREA_COLUMNS))
    if invalid_areas:
        raise ValueError(f"Unknown coaching area(s) in EXCLUDED_AREAS: {', '.join(invalid_areas)}")

    active_areas = [area for area in COACHING_AREA_COLUMNS if area not in excluded_area_values]
    if not active_areas:
        raise ValueError("EXCLUDED_AREAS removed every coaching area")

    return active_areas


def sort_staff_candidates(staff_df):
    sort_columns = []
    ascending = []

    for column in ["Best Stars Raw", "Full Qual CA", "CA", "PA"]:
        if column in staff_df.columns:
            sort_columns.append(column)
            ascending.append(False)
    for column in ["Age", "Name", "UID"]:
        if column in staff_df.columns:
            sort_columns.append(column)
            ascending.append(True)

    if not sort_columns:
        return staff_df.reset_index(drop=True)
    return staff_df.sort_values(sort_columns, ascending=ascending, kind="stable").reset_index(drop=True)


def dedupe_staff_candidates(staff_df):
    if "UID" not in staff_df.columns:
        return staff_df.reset_index(drop=True)
    return staff_df.drop_duplicates(subset=["UID"], keep="first").reset_index(drop=True)


def filter_staff_candidates(staff_df, *, allowed_clubs=None, include_uids=None, exclude_uids=None):
    filtered = staff_df.copy()
    included_uid_values = normalise_uid_values(include_uids)
    excluded_uid_values = normalise_uid_values(exclude_uids)

    if allowed_clubs:
        allowed_club_values = {normalise_club_value(club) for club in allowed_clubs}
        normalised_clubs = filtered["Club"].map(normalise_club_value)
        filtered = filtered.loc[normalised_clubs.isin(allowed_club_values) | filtered["UID"].isin(included_uid_values)]

    if excluded_uid_values:
        filtered = filtered.loc[~filtered["UID"].isin(excluded_uid_values)]

    return filtered.reset_index(drop=True)


def append_current_manager_candidate(staff_df, process):
    try:
        manager_row = read_current_manager_staff_row(process)
    except Exception as exc:
        return staff_df.copy(), "unavailable", str(exc)

    manager_uid = manager_row["UID"]
    manager_row["Name"] = manager_row.get("Memory Name")
    manager_row["Current Manager"] = "Yes"

    staff_df = staff_df.copy()
    if "Current Manager" not in staff_df.columns:
        staff_df["Current Manager"] = ""

    if manager_uid in set(staff_df["UID"].dropna().astype(int)):
        staff_df.loc[staff_df["UID"] == manager_uid, "Current Manager"] = "Yes"
        if "Name" in staff_df.columns:
            staff_df.loc[staff_df["UID"] == manager_uid, "Name"] = staff_df.loc[staff_df["UID"] == manager_uid, "Name"].fillna(manager_row["Name"])
        return staff_df, "marked", None

    return pd.concat([staff_df, pd.DataFrame([manager_row])], ignore_index=True), "added", None


def append_extra_uid_candidates(staff_df, process, extra_uids=None):
    requested_uids = sorted(normalise_uid_values(extra_uids))
    if not requested_uids:
        return staff_df, []

    extra_df = build_staff_table_for_uids(requested_uids, process)
    if extra_df.empty:
        return staff_df, requested_uids

    extra_df = extra_df.loc[extra_df["Memory Name"].notna()].copy()
    extra_df["Name"] = extra_df["Memory Name"]
    found_uids = set(extra_df["UID"].dropna().astype(int))
    missing_uids = sorted(requested_uids - found_uids)

    return pd.concat([staff_df, extra_df], ignore_index=True), missing_uids


def load_coach_candidates(shortlist_path, process, *, allowed_clubs=None, included_uids=None, excluded_uids=None, extra_uids=None):
    staff_df = load_staff_shortlist_dataframe(shortlist_path, process)
    shortlist_count = len(staff_df)
    staff_df, missing_extra_uids = append_extra_uid_candidates(staff_df, process, extra_uids=extra_uids)
    staff_df, manager_status, manager_error = append_current_manager_candidate(staff_df, process)
    filtered_df = dedupe_staff_candidates(
        sort_staff_candidates(filter_staff_candidates(staff_df, allowed_clubs=allowed_clubs, include_uids=included_uids, exclude_uids=excluded_uids))
    )

    return filtered_df, {
        "shortlist_count": shortlist_count,
        "manager_status": manager_status,
        "manager_error": manager_error,
        "missing_extra_uids": missing_extra_uids,
    }


def solve_best_coach_assignments(staff_df, area_columns, *, included_uids=None, show_solver_log=False):
    if len(staff_df) < len(area_columns):
        raise ValueError(
            f"Need at least {len(area_columns)} candidate coaches to cover every coaching area once. "
            f"Filtered pool only has {len(staff_df)} coach(es)."
        )

    included_uid_values = normalise_uid_values(included_uids)
    included_staff_indices = [
        staff_index for staff_index, uid in enumerate(staff_df["UID"].astype("Int64")) if not pd.isna(uid) and int(uid) in included_uid_values
    ]
    missing_included_uids = sorted(included_uid_values - set(staff_df.loc[included_staff_indices, "UID"].astype(int)))
    if missing_included_uids:
        raise ValueError("Included UIDs were not present in the filtered candidate pool: " + ", ".join(str(uid) for uid in missing_included_uids))
    if len(included_staff_indices) > len(area_columns):
        raise ValueError(f"Cannot force {len(included_staff_indices)} included coach(es) into only {len(area_columns)} coaching area(s).")

    role_score_matrix = staff_df[[RAW_SCORE_COLUMNS[area] for area in area_columns]].fillna(0).to_numpy(dtype=int)

    model = Highs()
    model.setOptionValue("output_flag", show_solver_log)
    assign_vars = {}

    for staff_index in range(len(staff_df)):
        for area_index, area in enumerate(area_columns):
            role_score = int(role_score_matrix[staff_index, area_index])
            assign_vars[(staff_index, area_index)] = model.addBinary(obj=role_score, name=f"assign_{staff_index}_{area}")

    for area_index, area in enumerate(area_columns):
        model.addConstr(sum(assign_vars[(staff_index, area_index)] for staff_index in range(len(staff_df))) == 1, name=f"assign_area_{area}")

    for staff_index in range(len(staff_df)):
        model.addConstr(
            sum(assign_vars[(staff_index, area_index)] for area_index in range(len(area_columns))) <= 1, name=f"assign_coach_once_{staff_index}"
        )

    for staff_index in included_staff_indices:
        model.addConstr(
            sum(assign_vars[(staff_index, area_index)] for area_index in range(len(area_columns))) == 1, name=f"force_include_{staff_index}"
        )

    model.maximize()
    if model.getModelStatus() != HighsModelStatus.kOptimal:
        raise RuntimeError(f"HiGHS did not find an optimal solution: {model.getModelStatus()}")

    selected_area_indices = {}
    role_score_by_area = {}

    for area_index, area in enumerate(area_columns):
        assigned_staff_index = next(
            staff_index for staff_index in range(len(staff_df)) if model.variableValue(assign_vars[(staff_index, area_index)]) > 0.5
        )
        selected_area_indices[area] = assigned_staff_index
        role_score_by_area[area] = int(role_score_matrix[assigned_staff_index, area_index])

    return {
        "selected_area_indices": selected_area_indices,
        "role_score_by_area": role_score_by_area,
        "total_role_score": sum(role_score_by_area.values()),
    }


def build_assignment_table(staff_df, result, area_columns):
    assignments = []

    for area in area_columns:
        coach_row = staff_df.iloc[result["selected_area_indices"][area]]
        role_score = result["role_score_by_area"][area]
        assignments.append(
            {
                "Area": area,
                "Coach": coach_row["Name"],
                "UID": coach_row["UID"],
                "Club": coach_row.get("Club", ""),
                "Role Score": role_score,
                "Stars": coach_role_score_to_stars(role_score),
            }
        )

    return pd.DataFrame(assignments)
