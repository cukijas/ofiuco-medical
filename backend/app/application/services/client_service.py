"""Client application service."""

import uuid

from fastapi import HTTPException, status

from backend.app.application.dtos.client import (
    CreateClientRequest,
    UpdateClientRequest,
    ClientResponse,
    ClientListResponse,
)
from backend.app.domain.models.client import Client
from backend.app.domain.ports.client_repo import IClientRepo
from backend.app.domain.ports.service_order_repo import IServiceOrderRepo


class ClientService:
    """Service layer for client CRUD operations."""

    def __init__(
        self,
        client_repo: IClientRepo,
        service_order_repo: IServiceOrderRepo,
    ) -> None:
        self.client_repo = client_repo
        self.service_order_repo = service_order_repo

    async def create(self, request: CreateClientRequest) -> ClientResponse:
        """Create a new client.

        Args:
            request: Client creation data.

        Returns:
            Created client response.

        Raises:
            HTTPException 409: If client name already exists.
        """
        # Check unique name (name is the unique constraint in the model)
        existing = await self.client_repo.get_by_name(request.name)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Client with name '{request.name}' already exists",
            )

        client = Client(
            name=request.name,
            email=request.email,
            phone=request.phone,
            address=request.address,
            city=request.city,
            province=request.province,
            postal_code=request.postal_code,
        )
        created = await self.client_repo.create(client)
        return ClientResponse.model_validate(created)

    async def get_by_id(self, client_id: uuid.UUID) -> ClientResponse:
        """Get a client by ID.

        Args:
            client_id: UUID of the client.

        Returns:
            Client response.

        Raises:
            HTTPException 404: If client not found.
        """
        client = await self.client_repo.get_by_id(client_id)
        if not client or not client.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client not found",
            )
        return ClientResponse.model_validate(client)

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 20,
    ) -> ClientListResponse:
        """List active clients with pagination.

        Args:
            skip: Number of records to skip.
            limit: Maximum records to return.

        Returns:
            Paginated client list.
        """
        clients = await self.client_repo.get_all(skip=skip, limit=limit)
        total = await self.client_repo.count_active()
        items = [ClientResponse.model_validate(c) for c in clients if c.is_active]
        return ClientListResponse(
            items=items,
            total=total,
            skip=skip,
            limit=limit,
        )

    async def update(
        self,
        client_id: uuid.UUID,
        request: UpdateClientRequest,
    ) -> ClientResponse:
        """Update a client (partial update).

        Args:
            client_id: UUID of the client to update.
            request: Fields to update (only non-None values applied).

        Returns:
            Updated client response.

        Raises:
            HTTPException 404: If client not found.
            HTTPException 409: If new name conflicts with another client.
        """
        client = await self.client_repo.get_by_id(client_id)
        if not client or not client.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client not found",
            )

        update_data = request.model_dump(exclude_unset=True)

        # Validate name uniqueness if changing
        if "name" in update_data and update_data["name"] != client.name:
            existing = await self.client_repo.get_by_name(update_data["name"])
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Client with name '{update_data['name']}' already exists",
                )

        for field, value in update_data.items():
            setattr(client, field, value)

        updated = await self.client_repo.update(client)
        return ClientResponse.model_validate(updated)

    async def delete(self, client_id: uuid.UUID) -> None:
        """Soft-delete a client.

        Checks that no active service orders reference this client before
        allowing deletion.

        Args:
            client_id: UUID of the client to delete.

        Raises:
            HTTPException 404: If client not found.
            HTTPException 409: If client has active service orders.
        """
        client = await self.client_repo.get_by_id(client_id)
        if not client or not client.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client not found",
            )

        has_orders = await self.service_order_repo.has_active_by_client_id(client_id)
        if has_orders:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cannot delete client with active service orders",
            )

        await self.client_repo.delete(client_id)
