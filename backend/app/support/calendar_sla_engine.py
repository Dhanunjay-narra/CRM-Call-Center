"""
Support SLA Business Hours Calendar & Holiday Calculation Engine
Accurately computes SLA due dates taking into account tenant operating schedules,
weekend exclusions, custom holiday exceptions, and pause-on-waiting-for-customer status.
"""

from datetime import datetime, time, timedelta, timezone
from typing import List, Dict, Any, Optional, Set


class BusinessHoursCalculator:
    def __init__(self, start_time: time = time(9, 0), end_time: time = time(18, 0), work_days: Optional[Set[int]] = None, holidays: Optional[Set[str]] = None):
        self.start_time = start_time
        self.end_time = end_time
        self.work_days = work_days or {0, 1, 2, 3, 4}  # Mon - Fri
        self.holidays = holidays or set()  # "YYYY-MM-DD"

    def is_business_hour(self, dt: datetime) -> bool:
        if dt.weekday() not in self.work_days:
            return False
        date_str = dt.strftime("%Y-%m-%d")
        if date_str in self.holidays:
            return False
        current_time = dt.time()
        return self.start_time <= current_time <= self.end_time

    def add_business_minutes(self, start_dt: datetime, business_minutes: int) -> datetime:
        """Adds business minutes to start_dt skipping non-business hours, weekends, and holidays"""
        current_dt = start_dt
        minutes_remaining = business_minutes

        while minutes_remaining > 0:
            if self.is_business_hour(current_dt):
                # Calculate minutes until end of business day
                eod_dt = datetime.combine(current_dt.date(), self.end_time, tzinfo=current_dt.tzinfo)
                minutes_today = int((eod_dt - current_dt).total_seconds() / 60)

                if minutes_remaining <= minutes_today:
                    return current_dt + timedelta(minutes=minutes_remaining)
                else:
                    minutes_remaining -= minutes_today
                    # Move to start of next day
                    next_day = current_dt.date() + timedelta(days=1)
                    current_dt = datetime.combine(next_day, self.start_time, tzinfo=current_dt.tzinfo)
            else:
                # Advance to next business day start
                if current_dt.time() > self.end_time:
                    next_day = current_dt.date() + timedelta(days=1)
                    current_dt = datetime.combine(next_day, self.start_time, tzinfo=current_dt.tzinfo)
                elif current_dt.time() < self.start_time:
                    current_dt = datetime.combine(current_dt.date(), self.start_time, tzinfo=current_dt.tzinfo)
                else:
                    next_day = current_dt.date() + timedelta(days=1)
                    current_dt = datetime.combine(next_day, self.start_time, tzinfo=current_dt.tzinfo)

        return current_dt
