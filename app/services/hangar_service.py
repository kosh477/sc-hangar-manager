"""Service layer for users, ships and parts bindings."""

from app.db import db
from app.models import PartByShip, PartByUser, ShipByUser


class HangarService:
    """Operations on hangar assignments and lookups."""

    @staticmethod
    def get_user_ships(user_id: int):
        """Return active ships for user."""
        links = (
            ShipByUser.query.filter_by(userId=user_id, isDeleted=False)
            .join(ShipByUser.ship)
            .all()
        )
        return [link.ship for link in links]

    @staticmethod
    def get_ship_parts(ship_id: int):
        """Return parts currently installed on ship."""
        links = PartByShip.query.filter_by(shipId=ship_id).join(PartByShip.part).all()
        return [link.part for link in links]

    @staticmethod
    def assign_ship_to_user(user_id: int, ship_id: int):
        """Assign ship to user and reuse soft-deleted relation when possible."""
        link = ShipByUser.query.filter_by(userId=user_id, shipId=ship_id).first()
        if link is None:
            link = ShipByUser(userId=user_id, shipId=ship_id, isDeleted=False)
            db.session.add(link)
        else:
            link.isDeleted = False

        db.session.commit()
        return link

    @staticmethod
    def unassign_ship_from_user(user_id: int, ship_id: int):
        """Soft-delete ship assignment from user."""
        link = ShipByUser.query.filter_by(
            userId=user_id,
            shipId=ship_id,
            isDeleted=False,
        ).first()
        if link is None:
            return False

        link.isDeleted = True
        db.session.commit()
        return True

    @staticmethod
    def assign_part_to_user(user_id: int, part_id: int):
        """Assign part to user and reuse soft-deleted relation when possible."""
        link = PartByUser.query.filter_by(userId=user_id, partId=part_id).first()
        if link is None:
            link = PartByUser(userId=user_id, partId=part_id, isDeleted=False)
            db.session.add(link)
        else:
            link.isDeleted = False

        db.session.commit()
        return link

    @staticmethod
    def unassign_part_from_user(user_id: int, part_id: int):
        """Soft-delete part assignment from user."""
        link = PartByUser.query.filter_by(
            userId=user_id,
            partId=part_id,
            isDeleted=False,
        ).first()
        if link is None:
            return False

        link.isDeleted = True
        db.session.commit()
        return True

    @staticmethod
    def assign_part_to_ship(ship_id: int, part_id: int):
        """Install part to ship if relation absent."""
        link = PartByShip.query.filter_by(shipId=ship_id, partId=part_id).first()
        if link is None:
            link = PartByShip(shipId=ship_id, partId=part_id)
            db.session.add(link)
            db.session.commit()
        return link

    @staticmethod
    def unassign_part_from_ship(ship_id: int, part_id: int):
        """Remove installed part from ship."""
        link = PartByShip.query.filter_by(shipId=ship_id, partId=part_id).first()
        if link is None:
            return False

        db.session.delete(link)
        db.session.commit()
        return True
