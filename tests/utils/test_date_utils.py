from datetime import datetime as dt
from cg_lims.utils.date_utils import get_number_of_days


def test_get_number_of_days_no_date():
    # GIVEN a date that is None
    first_date = None
    second_date = dt.today()

    # WHEN counting the number of days between two dates
    nr_days = get_number_of_days(first_date, second_date)

    # THEN assert nr_days is none
    assert nr_days is None


def test_get_number_of_days():
    # GIVEN two date time dates differing by two days
    first_date = dt.strptime('2018-05-31', '%Y-%m-%d')
    second_date = dt.strptime('2018-06-02', '%Y-%m-%d')

    # WHEN counting the number of days between two dates
    nr_days = get_number_of_days(first_date, second_date)

    # THEN assert nr_days == 2
    assert nr_days == 2