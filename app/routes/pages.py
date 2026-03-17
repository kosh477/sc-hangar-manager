"""SSR pages for hangar data views."""

from flask import Blueprint, render_template, request

from app.auth import require_auth, require_same_user

from app.models import PartByShip, PartByUser, PartType, Ship, ShipByUser, ShipPart

pages_bp = Blueprint("pages", __name__)


@pages_bp.get("/")
def frontend_index_page():
    """Simple frontend shell for auth and API interaction."""
    return render_template("frontend.html")


@pages_bp.get("/ui/user/<int:user_id>/ships")
@require_auth
def user_ships_page(user_id: int):
    require_same_user(user_id)
    ships = ShipByUser.query.filter_by(userId=user_id, isDeleted=False).join(ShipByUser.ship).all()
    return render_template("user_ships.html", user_id=user_id, ships=[link.ship for link in ships])


@pages_bp.get("/ui/user/<int:user_id>/parts")
@require_auth
def user_parts_page(user_id: int):
    require_same_user(user_id)
    class_filter = request.args.get("class", "")
    size_filter = request.args.get("size", type=int)
    type_filter = request.args.get("type", "")

    query = (
        PartByUser.query.filter_by(userId=user_id, isDeleted=False)
        .join(PartByUser.part)
        .join(ShipPart.part_type)
    )
    if class_filter:
        query = query.filter(ShipPart.class_ == class_filter)
    if size_filter:
        query = query.filter(ShipPart.size == size_filter)
    if type_filter:
        query = query.filter(PartType.type == type_filter)

    parts = [link.part for link in query.all()]
    part_types = [part_type.type for part_type in PartType.query.order_by(PartType.type.asc()).all()]
    return render_template(
        "user_parts.html",
        user_id=user_id,
        parts=parts,
        class_filter=class_filter,
        size_filter=size_filter,
        type_filter=type_filter,
        part_types=part_types,
    )


@pages_bp.get("/ui/ship/<int:ship_id>")
@require_auth
def ship_card_page(ship_id: int):
    ship = Ship.query.get_or_404(ship_id)
    parts = PartByShip.query.filter_by(shipId=ship_id).join(PartByShip.part).all()
    return render_template("ship_card.html", ship=ship, parts=[link.part for link in parts])


@pages_bp.get("/ui/parts-catalog")
@require_auth
def parts_catalog_page():
    part_types = PartType.query.order_by(PartType.id.asc()).all()
    parts = ShipPart.query.join(ShipPart.part_type).order_by(ShipPart.id.asc()).all()
    return render_template("parts_catalog.html", part_types=part_types, parts=parts)
