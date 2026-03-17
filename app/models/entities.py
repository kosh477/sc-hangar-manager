"""Domain ORM entities for hangar manager."""

from sqlalchemy.orm import validates

from app.db import db
from app.models.base import TimestampMixin

ALLOWED_SHIP_PART_CLASSES = (
    "Military",
    "Competition",
    "Civilian",
    "Stealth",
    "Industrial",
)


class Ship(TimestampMixin, db.Model):
    """Base ship catalog entity."""

    __tablename__ = "ships"

    id = db.Column(db.Integer, primary_key=True)
    vendor = db.Column(db.String(128), nullable=False)
    model = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(128), nullable=False)

    user_links = db.relationship("ShipByUser", back_populates="ship", cascade="all, delete-orphan")
    parts_links = db.relationship("PartByShip", back_populates="ship", cascade="all, delete-orphan")
    users = db.relationship(
        "User",
        secondary="shipsByUser",
        primaryjoin="and_(Ship.id == ShipByUser.shipId, ShipByUser.isDeleted.is_(False))",
        secondaryjoin="User.id == ShipByUser.userId",
        viewonly=True,
        overlaps="user_links,ship_links,user",
    )
    parts = db.relationship(
        "ShipPart",
        secondary="partsByShip",
        primaryjoin="Ship.id == PartByShip.shipId",
        secondaryjoin="ShipPart.id == PartByShip.partId",
        viewonly=True,
        overlaps="parts_links,ship_links,part",
    )


class PartType(TimestampMixin, db.Model):
    """Part type dictionary."""

    __tablename__ = "partsTypes"

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(128), nullable=False)
    isReplaceble = db.Column(db.Boolean, nullable=False, default=False)

    parts = db.relationship("ShipPart", back_populates="part_type")


class ShipPart(TimestampMixin, db.Model):
    """Ship part entry in catalog."""

    __tablename__ = "shipsParts"
    __table_args__ = (
        db.CheckConstraint("size >= 1 AND size <= 10", name="ck_shipsParts_size_range"),
        db.CheckConstraint(
            "class IN ('Military', 'Competition', 'Civilian', 'Stealth', 'Industrial')",
            name="ck_shipsParts_class_allowed",
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    vendor = db.Column(db.String(128), nullable=False)
    model = db.Column(db.String(128), nullable=False)
    class_ = db.Column("class", db.String(64), nullable=False)
    size = db.Column(db.Integer, nullable=False)
    partTypeId = db.Column(
        db.Integer,
        db.ForeignKey("partsTypes.id", name="fk_shipsParts_partTypeId_partsTypes"),
        nullable=False,
        index=True,
    )

    part_type = db.relationship("PartType", back_populates="parts")
    user_links = db.relationship("PartByUser", back_populates="part", cascade="all, delete-orphan")
    ship_links = db.relationship("PartByShip", back_populates="part", cascade="all, delete-orphan")
    users = db.relationship(
        "User",
        secondary="partsByUser",
        primaryjoin="and_(ShipPart.id == PartByUser.partId, PartByUser.isDeleted.is_(False))",
        secondaryjoin="User.id == PartByUser.userId",
        viewonly=True,
        overlaps="user_links,part_links,user",
    )
    ships = db.relationship(
        "Ship",
        secondary="partsByShip",
        primaryjoin="ShipPart.id == PartByShip.partId",
        secondaryjoin="Ship.id == PartByShip.shipId",
        viewonly=True,
        overlaps="ship_links,parts_links,ship",
    )

    @validates("size")
    def validate_size(self, key, value):
        if value is None:
            raise ValueError("size is required")
        if not isinstance(value, int):
            raise ValueError("size must be an integer")
        if value < 1 or value > 10:
            raise ValueError("size must be between 1 and 10")
        return value

    @validates("class_")
    def validate_class(self, key, value):
        if value not in ALLOWED_SHIP_PART_CLASSES:
            raise ValueError(
                "class must be one of: Military, Competition, Civilian, Stealth, Industrial"
            )
        return value


class User(TimestampMixin, db.Model):
    """Application user."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True, index=True)
    login = db.Column(db.String(128), nullable=False, unique=True, index=True)
    password = db.Column(db.String(255), nullable=False)

    ship_links = db.relationship("ShipByUser", back_populates="user", cascade="all, delete-orphan")
    part_links = db.relationship("PartByUser", back_populates="user", cascade="all, delete-orphan")
    ships = db.relationship(
        "Ship",
        secondary="shipsByUser",
        primaryjoin="and_(User.id == ShipByUser.userId, ShipByUser.isDeleted.is_(False))",
        secondaryjoin="Ship.id == ShipByUser.shipId",
        viewonly=True,
        overlaps="ship_links,user_links,ship",
    )
    parts = db.relationship(
        "ShipPart",
        secondary="partsByUser",
        primaryjoin="and_(User.id == PartByUser.userId, PartByUser.isDeleted.is_(False))",
        secondaryjoin="ShipPart.id == PartByUser.partId",
        viewonly=True,
        overlaps="part_links,user_links,part",
    )

    @validates("email")
    def validate_email(self, key, value):
        if value is None or not str(value).strip():
            raise ValueError("email is required")
        return value.strip()

    @validates("login")
    def validate_login(self, key, value):
        if value is None or not str(value).strip():
            raise ValueError("login is required")
        return value.strip()


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

    user = db.relationship("User", back_populates="ship_links", overlaps="ships")
    ship = db.relationship("Ship", back_populates="user_links", overlaps="users")


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

    part = db.relationship("ShipPart", back_populates="ship_links", overlaps="ships")
    ship = db.relationship("Ship", back_populates="parts_links", overlaps="parts")


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

    part = db.relationship("ShipPart", back_populates="user_links", overlaps="users")
    user = db.relationship("User", back_populates="part_links", overlaps="parts")
