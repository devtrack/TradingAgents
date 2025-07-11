from datetime import datetime

from tradingagents.dataflows.utils import get_next_weekday


def test_get_next_weekday_saturday_to_monday():
    result = get_next_weekday('2024-04-06')
    assert result == datetime(2024, 4, 8)


def test_get_next_weekday_weekday_unchanged():
    result = get_next_weekday('2024-04-09')
    assert result == datetime(2024, 4, 9)
