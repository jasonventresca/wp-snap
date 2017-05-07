import pytest
from datetime import datetime

from expiry import ExpiryChecker


TEST_DATA = (
    (
        'weekly_expire_very',
        {
            'candidate_dt': datetime(2016, 1, 1),
            'period': 'weekly',
            'n_periods_to_keep': 1,
            'utcnow': datetime(2017, 1, 1),
        },
        True,
    ),
    (
        'weekly_expire',
        {
            'candidate_dt': datetime(2017, 1, 1),
            'period': 'weekly',
            'n_periods_to_keep': 1,
            'utcnow': datetime(2017, 1, 8, 0, 0, 1),
        },
        True,
    ),
    (
        'weekly_keep_edge',
        {
            'candidate_dt': datetime(2017, 1, 1),
            'period': 'weekly',
            'n_periods_to_keep': 1,
            'utcnow': datetime(2017, 1, 8),
        },
        False,
    ),
    (
        'weekly_keep_edge',
        {
            'candidate_dt': datetime(2017, 1, 1),
            'period': 'weekly',
            'n_periods_to_keep': 1,
            'utcnow': datetime(2017, 1, 7),
        },
        False,
    ),
    (
        'daily_keep',
        {
            'candidate_dt': datetime(2017, 1, 1),
            'period': 'daily',
            'n_periods_to_keep': 3,
            'utcnow': datetime(2017, 1, 4),
        },
        False,
    ),
    (
        'daily_expire',
        {
            'candidate_dt': datetime(2017, 1, 1),
            'period': 'daily',
            'n_periods_to_keep': 3,
            'utcnow': datetime(2017, 1, 5),
        },
        True,
    ),
    (
        'monthly_keep',
        {
            'candidate_dt': datetime(2017, 1, 1),
            'period': 'monthly',
            'n_periods_to_keep': 1,
            'utcnow': datetime(2017, 2, 1),
        },
        False,
    ),
    (
        'monthly_expire',
        {
            'candidate_dt': datetime(2017, 1, 1),
            'period': 'monthly',
            'n_periods_to_keep': 1,
            'utcnow': datetime(2017, 2, 2),
        },
        True,
    ),
    (
        'multi_monthly_keep',
        {
            'candidate_dt': datetime(2016, 12, 30),
            'period': 'monthly',
            'n_periods_to_keep': 2,
            'utcnow': datetime(2017, 3, 1),
        },
        False,
    ),
    (
        'multi_monthly_expire',
        {
            'candidate_dt': datetime(2016, 12, 28),
            'period': 'monthly',
            'n_periods_to_keep': 2,
            'utcnow': datetime(2017, 3, 1),
        },
        True,
    ),
)


@pytest.mark.parametrize(['label', 'input_data',  'expected'], TEST_DATA)
def test_is_expired(label, input_data, expected):
    expiry = ExpiryChecker(
            input_data['period'],
            input_data['n_periods_to_keep'],
            input_data['utcnow']
    )
    assert expected == expiry.is_expired(input_data['candidate_dt'])
