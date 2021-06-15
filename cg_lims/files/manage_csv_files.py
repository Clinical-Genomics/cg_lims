import csv
import string
from pathlib import Path
from typing import List
import pandas as pd


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
    """Sort csv.
    columns: list of columns to sort on.

    well_columns: Optional. Sub set of columns! Will be sorted by second field:
                (A1, B1, C1, A2, B2, C2), not (A1, A2, B1, B2, C1, C2).
    """

    data = pd.read_csv(file.absolute(), delimiter=",")
    print(data)
    temp_sort_columns = []
    sort_columns = []
    for column in columns:
        if column in well_columns:
            well_row = f"{column}_row"
            well_col = f"{column}_col"
            data[well_row] = data[column].transform(lambda x: x[0])
            data[well_col] = data[column].transform(lambda x: int(x[1:]))
            sort_columns += [well_col, well_row]
            temp_sort_columns += [well_col, well_row]
        else:
            sort_columns.append(column)
    print(data)
    data.sort_values(by=sort_columns, inplace=True)
    print(data)
    sorted_data = data.drop(temp_sort_columns, axis=1)
    print(sorted_data)
    sorted_data.to_csv(file.absolute(), index=False)
