"""Helpers for building normalised staff scouting tables from shortlist exports."""

import pandas as pd

from core.memory.staff import build_staff_shortlist_table
from core.scouting.shortlists import approved_shortlist_columns, coalesce_columns, load_shortlist_table

DEFAULT_STAFF_SHORTLIST_PATH = "staff_shortlist.html"
APPROVED_STAFF_SHORTLIST_COLUMNS = {
    "Name": ("Name", "Staff"),
    "Nationality": ("Nationality", "Nat"),
    "Age": ("Age",),
    "Club": ("Club",),
    "Wage": ("Wage",),
    "Qualification": ("Qualification", "Current Licence", "Current License", "Coaching Licence", "Coaching License"),
}
DEFAULT_STAFF_UID_ERROR = "coach shortlist HTML must include a UID column"


def build_staff_shortlist_dataframe(shortlist_df: pd.DataFrame, process) -> pd.DataFrame:
    staff_df = shortlist_df.merge(build_staff_shortlist_table(shortlist_df, process), on="UID")
    shortlist_columns = approved_shortlist_columns(shortlist_df, APPROVED_STAFF_SHORTLIST_COLUMNS)
    staff_df = coalesce_columns(staff_df, "Name", *(column for column in [shortlist_columns["Name"], "Memory Name"] if column))
    staff_df = coalesce_columns(staff_df, "Nationality", *(column for column in [shortlist_columns["Nationality"], "Nationality"] if column))
    staff_df = coalesce_columns(staff_df, "Age", *(column for column in [shortlist_columns["Age"], "Age_x", "Age_y", "Age"] if column))
    staff_df = coalesce_columns(staff_df, "Club", *(column for column in [shortlist_columns["Club"], "Club_x", "Club_y", "Club"] if column))
    staff_df = coalesce_columns(staff_df, "Wage", *(column for column in [shortlist_columns["Wage"], "Wage_x", "Wage_y", "Wage"] if column))
    staff_df = coalesce_columns(staff_df, "Qualification", *(column for column in [shortlist_columns["Qualification"], "Qualification"] if column))

    return staff_df


def load_staff_shortlist_dataframe(shortlist_path: str, process, uid_error: str = DEFAULT_STAFF_UID_ERROR) -> pd.DataFrame:
    shortlist_df = load_shortlist_table(shortlist_path, uid_error=uid_error)
    return build_staff_shortlist_dataframe(shortlist_df, process)
