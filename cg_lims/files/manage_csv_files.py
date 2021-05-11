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


def sort_csv(file: Path, columns: List[str]):
    df = pd.read_csv(file.absolute(), delimiter=",")
    df = df.sort_values(columns)
    df.to_csv(file.absolute(), index=False)
