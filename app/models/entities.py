"""Domain ORM entities for hangar manager."""

from app.db import db
from app.models.base import TimestampMixin


class Ship(TimestampMixin, db.Model):
    """Base ship catalog entity."""

    __tablename__ = "ships"

    id = db.Column(db.Integer, primary_key=True)
    vendor = db.Column(db.String(128), nullable=False)
    model = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(128), nullable=False)


class PartType(TimestampMixin, db.Model):
    """Part type dictionary."""

    __tablename__ = "partsTypes"

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(128), nullable=False)
    isReplaceble = db.Column(db.Boolean, nullable=False, default=False)


class ShipPart(TimestampMixin, db.Model):
    """Ship part entry in catalog."""

    __tablename__ = "shipsParts"

    id = db.Column(db.Integer, primary_key=True)
    vendor = db.Column(db.String(128), nullable=False)
    model = db.Column(db.String(128), nullable=False)
    class_ = db.Column("class", db.String(64), nullable=False)
    size = db.Column(db.String(64), nullable=False)
    partTypeId = db.Column(
        db.Integer,
        db.ForeignKey("partsTypes.id", name="fk_shipsParts_partTypeId_partsTypes"),
        nullable=False,
        index=True,
    )


class User(TimestampMixin, db.Model):
    """Application user."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(255), nullable=False, index=True)
    login = db.Column(db.String(128), nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)


class ShipByUser(TimestampMixin, db.Model):
    """Ownership relation between users and ships."""

    __tablename__ = "shipsByUser"

    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(
        db.Integer,
        db.ForeignKey("users.id", name="fk_shipsByUser_userId_users"),
        nullable=False,
        index=True,
    )
    shipId = db.Column(
        db.Integer,
        db.ForeignKey("ships.id", name="fk_shipsByUser_shipId_ships"),
        nullable=False,
        index=True,
    )
    isDeleted = db.Column(db.Boolean, nullable=False, default=False, index=True)


class PartByShip(TimestampMixin, db.Model):
    """Installed parts per ship."""

    __tablename__ = "partsByShip"

    id = db.Column(db.Integer, primary_key=True)
    partId = db.Column(
        db.Integer,
        db.ForeignKey("shipsParts.id", name="fk_partsByShip_partId_shipsParts"),
        nullable=False,
        index=True,
    )
    shipId = db.Column(
        db.Integer,
        db.ForeignKey("ships.id", name="fk_partsByShip_shipId_ships"),
        nullable=False,
        index=True,
    )


class PartByUser(TimestampMixin, db.Model):
    """Owned parts per user."""

    __tablename__ = "partsByUser"

    id = db.Column(db.Integer, primary_key=True)
    partId = db.Column(
        db.Integer,
        db.ForeignKey("shipsParts.id", name="fk_partsByUser_partId_shipsParts"),
        nullable=False,
        index=True,
    )
    userId = db.Column(
        db.Integer,
        db.ForeignKey("users.id", name="fk_partsByUser_userId_users"),
        nullable=False,
        index=True,
    )
    isDeleted = db.Column(db.Boolean, nullable=False, default=False, index=True)
