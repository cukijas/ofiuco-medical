"""PDF generator port."""

from abc import ABC, abstractmethod


class IPdfGenerator(ABC):
    """Abstract PDF generator interface."""

    @abstractmethod
    async def generate_order_pdf(self, order_id: int) -> bytes:
        """Generate PDF for a service order and return bytes."""
        ...
