"""Build an HTML scouting report for a staff shortlist export."""

import pandas as pd

from core.memory.process import open_fm_process
from core.scouting.html import build_sortable_table_html
from core.scouting.money import format_currency, parse_money_text
from core.scouting.staff.roles import COACHING_AREA_COLUMNS, StaffArea
from core.scouting.staff.shortlist import DEFAULT_STAFF_SHORTLIST_PATH, load_staff_shortlist_dataframe

SHORTLIST_PATH = DEFAULT_STAFF_SHORTLIST_PATH
OUTPUT_PATH = "staff_table.html"


def main():
    process = open_fm_process()
    staff_df = load_staff_shortlist_dataframe(SHORTLIST_PATH, process)
    if staff_df.empty:
        raise ValueError(f"No staff were loaded from {SHORTLIST_PATH!r}")

    wage_sort_values = staff_df["Wage"].apply(parse_money_text).tolist() if "Wage" in staff_df.columns else None
    if "Wage" in staff_df.columns and pd.api.types.is_numeric_dtype(staff_df["Wage"]):
        staff_df["Wage"] = staff_df["Wage"].apply(format_currency)

    column_sort_values = {
        "Best Stars": staff_df["Best Stars Raw"].tolist(),
        **{role: staff_df[f"{role} Raw"].tolist() for role in COACHING_AREA_COLUMNS},
    }
    if wage_sort_values is not None:
        column_sort_values["Wage"] = wage_sort_values

    display_columns = [
        column
        for column in [
            "Nationality",
            "Club",
            "Wage",
            "Age",
            "Name",
            "Qualification",
            "Studying",
            "CA",
            "PA",
            "Full Qual CA",
            "Best Role",
            "Best Stars",
            *COACHING_AREA_COLUMNS,
        ]
        if column in staff_df.columns
    ]
    staff_df = staff_df[display_columns]

    for column in ["Age", "CA", "PA", "Full Qual CA"]:
        if column in staff_df.columns:
            staff_df[column] = staff_df[column].astype("Int64")

    score_columns = COACHING_AREA_COLUMNS
    html = build_sortable_table_html(
        staff_df,
        title="FM Staff Scan",
        subtitle=f"{len(staff_df):,} shortlisted staff scored across {len(score_columns)} coaching areas.",
        roles=[StaffArea(column) for column in score_columns],
        score_columns=score_columns,
        default_sort_column="Best Stars",
        column_sort_values=column_sort_values,
        score_style_min=0,
        score_style_max=300,
    )
    with open(OUTPUT_PATH, "w", encoding="utf-8") as output_file:
        output_file.write(html)


if __name__ == "__main__":
    main()
