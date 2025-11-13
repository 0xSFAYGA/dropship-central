from typing import Dict, List

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.listing import Listing
from backend.app.models.admin import AuditLog
from backend.app.core.exceptions import InvalidListingState
import logging

logger = logging.getLogger(__name__)


class ListingStateMachine:
    states: List[str] = ["Pending", "Active", "Paused", "Ended", "Delisted"]

    transitions: Dict[str, List[str]] = {
        "Pending": ["Active", "Delisted"],
        "Active": ["Paused", "Ended", "Delisted"],
        "Paused": ["Active", "Ended", "Delisted"],
        "Ended": ["Delisted", "Active"],  # can restart
        "Delisted": [],  # terminal state
    }

    async def transition(
        self, listing_id: int, new_state: str, db: AsyncSession, reason: str = ""
    ) -> Listing:
        """
        Transition a listing to a new state.

        Args:
            listing_id: The ID of the listing to transition.
            new_state: The new state.
            db: The database session.
            reason: The reason for the transition.

        Returns:
            The updated listing.

        Raises:
            InvalidListingState: If the transition is not valid.
        """
        listing = await db.get(Listing, listing_id)
        if not listing:
            raise ValueError(f"Listing with id {listing_id} not found.")

        if not self.can_transition(listing.status, new_state):
            raise InvalidListingState(
                f"Cannot transition from {listing.status} to {new_state}"
            )

        old_status = listing.status
        listing.status = new_state
        listing.status_reason = reason

        audit_log_entry = AuditLog(
            user_id=listing.user_id,
            action="transition",
            resource_type="listing",
            resource_id=listing.id,
            old_value={"status": old_status},
            new_value={"status": new_state},
        )
        db.add(audit_log_entry)

        # In a real application, you would publish an event here.
        # For example: await publish_event("listing.transitioned", {"listing_id": listing.id, "new_state": new_state})
        logger.info(
            f"Listing {listing_id} transitioned from {old_status} to {new_state}"
        )

        await db.commit()
        await db.refresh(listing)
        return listing

    def can_transition(self, current_state: str, target_state: str) -> bool:
        """
        Check if a state transition is valid.

        Args:
            current_state: The current state.
            target_state: The target state.

        Returns:
            True if the transition is valid, otherwise False.
        """
        return target_state in self.transitions.get(current_state, [])

    async def pause(
        self, listing_id: int, db: AsyncSession, reason: str = "manual_pause"
    ) -> Listing:
        """
        Pause a listing.

        Args:
            listing_id: The ID of the listing to pause.
            db: The database session.
            reason: The reason for pausing the listing.

        Returns:
            The updated listing.
        """
        return await self.transition(listing_id, "Paused", db, reason)

    async def resume(self, listing_id: int, db: AsyncSession) -> Listing:
        """
        Resume a listing.

        Args:
            listing_id: The ID of the listing to resume.
            db: The database session.

        Returns:
            The updated listing.
        """
        return await self.transition(listing_id, "Active", db, "")

    async def end(
        self, listing_id: int, db: AsyncSession, reason: str = "manual_end"
    ) -> Listing:
        """
        End a listing.

        Args:
            listing_id: The ID of the listing to end.
            db: The database session.
            reason: The reason for ending the listing.

        Returns:
            The updated listing.
        """
        return await self.transition(listing_id, "Ended", db, reason)
