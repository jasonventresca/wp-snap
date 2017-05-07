import pytest
from datetime import datetime, timezone

from expiry import ExpiryChecker


TEST_DATA = (
    (
        'weekly_expire_very',
        {
            'candidate_dt': datetime(2016, 1, 1, tzinfo=timezone.utc),
            'period': 'weekly',
            'n_periods_to_keep': 1,
            'now': datetime(2017, 1, 1, tzinfo=timezone.utc),
        },
        True,
    ),
    (
        'weekly_expire',
        {
            'candidate_dt': datetime(2017, 1, 1, tzinfo=timezone.utc),
            'period': 'weekly',
            'n_periods_to_keep': 1,
            'now': datetime(2017, 1, 8, 0, 0, 1, tzinfo=timezone.utc),
        },
        True,
    ),
    (
        'weekly_keep_edge',
        {
            'candidate_dt': datetime(2017, 1, 1, tzinfo=timezone.utc),
            'period': 'weekly',
            'n_periods_to_keep': 1,
            'now': datetime(2017, 1, 8, tzinfo=timezone.utc),
        },
        False,
    ),
    (
        'weekly_keep_edge',
        {
            'candidate_dt': datetime(2017, 1, 1, tzinfo=timezone.utc),
            'period': 'weekly',
            'n_periods_to_keep': 1,
            'now': datetime(2017, 1, 7, tzinfo=timezone.utc),
        },
        False,
    ),
    (
        'daily_keep',
        {
            'candidate_dt': datetime(2017, 1, 1, tzinfo=timezone.utc),
            'period': 'daily',
            'n_periods_to_keep': 3,
            'now': datetime(2017, 1, 4, tzinfo=timezone.utc),
        },
        False,
    ),
    (
        'daily_expire',
        {
            'candidate_dt': datetime(2017, 1, 1, tzinfo=timezone.utc),
            'period': 'daily',
            'n_periods_to_keep': 3,
            'now': datetime(2017, 1, 5, tzinfo=timezone.utc),
        },
        True,
    ),
    (
        'monthly_keep',
        {
            'candidate_dt': datetime(2017, 1, 1, tzinfo=timezone.utc),
            'period': 'monthly',
            'n_periods_to_keep': 1,
            'now': datetime(2017, 2, 1, tzinfo=timezone.utc),
        },
        False,
    ),
    (
        'monthly_expire',
        {
            'candidate_dt': datetime(2017, 1, 1, tzinfo=timezone.utc),
            'period': 'monthly',
            'n_periods_to_keep': 1,
            'now': datetime(2017, 2, 2, tzinfo=timezone.utc),
        },
        True,
    ),
    (
        'multi_monthly_keep',
        {
            'candidate_dt': datetime(2016, 12, 30, tzinfo=timezone.utc),
            'period': 'monthly',
            'n_periods_to_keep': 2,
            'now': datetime(2017, 3, 1, tzinfo=timezone.utc),
        },
        False,
    ),
    (
        'multi_monthly_expire',
        {
            'candidate_dt': datetime(2016, 12, 28, tzinfo=timezone.utc),
            'period': 'monthly',
            'n_periods_to_keep': 2,
            'now': datetime(2017, 3, 1, tzinfo=timezone.utc),
        },
        True,
    ),
)


@pytest.mark.parametrize(['label', 'input_data',  'expected'], TEST_DATA)
def test_is_expired(label, input_data, expected):
    expiry = ExpiryChecker(
            input_data['period'],
            input_data['n_periods_to_keep'],
            input_data['now']
    )
    assert expected == expiry.is_expired(input_data['candidate_dt'])
