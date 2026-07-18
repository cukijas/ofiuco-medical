"""Order number generator for service orders.

Generates atomic, collision-safe order numbers in the format OS-XXXXD
where XXXX is a zero-padded 6-digit sequence and D is a check digit.
"""

import re

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.domain.models.service_order import ServiceOrder


ORDER_NUMBER_PATTERN = re.compile(r"^OS-(\d{6})\d$")

MAX_RETRIES = 5


def _extract_sequence(order_number: str) -> int | None:
    """Extract the numeric sequence from an order number like OS-000803D.

    Args:
        order_number: The order number string.

    Returns:
        The integer sequence, or None if format doesn't match.
    """
    match = ORDER_NUMBER_PATTERN.match(order_number)
    if match:
        return int(match.group(1))
    return None


def _compute_check_digit(sequence: int) -> int:
    """Compute the single-digit check digit for a sequence.

    Uses a simple modulo-10 of the sequence sum of digits.

    Args:
        sequence: The numeric sequence.

    Returns:
        A single digit (0-9).
    """
    digit_sum = sum(int(d) for d in str(sequence))
    return digit_sum % 10


def _format_order_number(sequence: int) -> str:
    """Format a sequence into OS-XXXXD order number.

    Args:
        sequence: The numeric sequence.

    Returns:
        Formatted order number string.
    """
    check_digit = _compute_check_digit(sequence)
    return f"OS-{sequence:06d}{check_digit}"


async def generate_order_number(session: AsyncSession) -> str:
    """Generate the next unique order number atomically.

    Queries the maximum existing order number, increments the sequence,
    and formats as OS-XXXXD. Retries on collision up to MAX_RETRIES times.

    Args:
        session: Async database session.

    Returns:
        The next unique order number.

    Raises:
        RuntimeError: If unable to generate a unique number after retries.
    """
    # Get the current max order number
    result = await session.execute(select(func.max(ServiceOrder.order_number)))
    max_number = result.scalar_one_or_none()

    if max_number:
        sequence = _extract_sequence(max_number)
        if sequence is not None:
            next_sequence = sequence + 1
        else:
            # Fallback: if format is unexpected, start from 1
            next_sequence = 1
    else:
        # First order ever
        next_sequence = 1

    for _attempt in range(MAX_RETRIES):
        order_number = _format_order_number(next_sequence)

        # Check for collision (unlikely with proper increments, but safety net)
        existing = await session.execute(
            select(ServiceOrder.id).where(ServiceOrder.order_number == order_number)
        )
        if existing.scalar_one_or_none() is None:
            return order_number

        # Collision — increment and retry
        next_sequence += 1

    raise RuntimeError(
        f"Failed to generate unique order number after {MAX_RETRIES} attempts"
    )
