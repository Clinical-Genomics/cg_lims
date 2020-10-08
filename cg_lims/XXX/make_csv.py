import string


def make_plate_file(file: str, rows: dict, headers: list, col_range: int=13, row_range: int=8):
    """Creating a plate file.
    
    Arguments:
        file: file path
        headers: Header list. 
        rows: dict of rows
            keys: plate position: eg A1, B1, E4, H2...
            values: list of file rows. Same length as the headers list."""

    hamilton_csv = open( file , 'w')
    wr = csv.writer(file)
    wr.writerow(headers)
    for col in range(1,col_range):
        for row in string.ascii_uppercase[0:row_range]:
            row = file_rows.get(f"{row}{col}")
            if row:
                wr.writerow(row)
