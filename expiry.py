from datetime import datetime, timedelta, timezone

class ExpiryChecker(object):
    def __init__(self, period, n_periods_to_keep, now=None):
        now = now or datetime.now(tz=timezone.utc)
        period_days = self._days_in_period(period)
        n_days_to_keep = period_days * n_periods_to_keep
        self.oldest_to_keep = now - timedelta(days=n_days_to_keep)

    def is_expired(self, dt):
        return dt < self.oldest_to_keep

    @staticmethod
    def _days_in_period(period):
        # Err on the side of caution: assume all months are 31 days and all years are 366 days.
        days = {
                'daily': 1,
                'weekly': 7,
                'monthly': 31,
                'yearly': 366,
        }

        return days[period]
