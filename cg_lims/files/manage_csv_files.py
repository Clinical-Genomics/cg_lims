import csv
import string
from pathlib import Path
from typing import List
import pandas as pd

from cg_lims.exceptions import CSVColumnError


def make_plate_file(
    file: str,
    rows: dict,
    headers: list,
    col_range: int = 13,
    row_range: int = 8,
    newline="\n",
    delimiter=",",
):
    """Creating a plate file.

    Arguments:
        file: file path
        headers: Header list.
        rows: dict of rows
            keys: plate position: eg A1, B1, E4, H2...
            values: list of file rows. Same length as the headers list."""

    with open(file, "w", newline=newline) as hamilton_csv:
        wr = csv.writer(hamilton_csv, delimiter=delimiter)
        wr.writerow(headers)
        for col in range(1, col_range):
            for row in string.ascii_uppercase[0:row_range]:
                row = rows.get(f"{row}{col}")
                if row:
                    wr.writerow(row)


def build_csv(rows: List[List[str]], file: Path, headers: List[str]) -> Path:
    """Build csv."""

    with open(file.absolute(), "w", newline="\n") as new_csv:
        wr = csv.writer(new_csv, delimiter=",")
        wr.writerow(headers)
        wr.writerows(rows)

    return file


def sort_csv(file: Path, columns: List[str], well_columns: List[str] = []):
    """This function sorts a csv file based on the list of columns given.

    columns: list of columns to sort on.
        - eg: [ "Destination Container", "Sample Well" ]

    well_columns: Optional. Sub set of columns!
        - eg: ["Sample Well"]
        - Assumed well format like A1, B1 etc. Not A:1, B:1!
        - Will first be sorted numerically by second field. then alphabetically on the first field:
          (A1, B1, C1, A2, B2, C2), not (A1, A2, B1, B2, C1, C2).
    """

    csv_data_frame = pd.read_csv(file.absolute(), delimiter=",")
    temp_sort_columns = []
    sort_columns = []  # columns to sort on

    if not set(well_columns).issubset(set(columns)):
        raise CSVColumnError(message="well_columns must be subset of columns")

    for column in columns:
        if column not in csv_data_frame.columns:
            raise CSVColumnError(message=f"Column {column} is not in the csv file.")
        if column not in well_columns:
            # If the column is not a well_column, just append it to sort_columns
            sort_columns.append(column)
            continue
        # Splitting the well_column into two temporary sort columns that are added to the data frame and to sort_columns
        well_row = f"{column}_row"
        well_col = f"{column}_col"
        csv_data_frame[well_row] = csv_data_frame[column].transform(lambda x: x[0])
        csv_data_frame[well_col] = csv_data_frame[column].transform(lambda x: int(x[1:]))
        sort_columns += [well_col, well_row]
        temp_sort_columns += [well_col, well_row]

    # Now the data frame has two extra sort columns for each well column

    # sorting by sort_columns
    csv_data_frame.sort_values(by=sort_columns, inplace=True)

    # dropping the temp_sort_columns
    sorted_data = csv_data_frame.drop(temp_sort_columns, axis=1)

    sorted_data.to_csv(file.absolute(), index=False)
