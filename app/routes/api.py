"""API endpoints for users, ships, parts and assignments."""

from __future__ import annotations

from flask import Blueprint, jsonify, request
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError

from app.auth import AuthError, create_access_token, hash_password, require_auth, require_same_user, verify_password
from app.db import db
from app.models import PartByShip, PartType, Ship, ShipPart, User
from app.models.entities import PartByUser, ShipByUser
from app.schemas import (
    AuthResponse,
    PartCreateRequest,
    PartResponse,
    PartTypeCreateRequest,
    PartTypeResponse,
    ShipCreateRequest,
    ShipPartAssignmentRequest,
    ShipResponse,
    UserCreateRequest,
    UserLoginRequest,
    UserPartAssignmentRequest,
    UserResponse,
    UserShipAssignmentRequest,
)

api_bp = Blueprint("api", __name__)


class ApiError(Exception):
    """API error with status code."""

    def __init__(self, status_code: int, message: str, details: list[str] | None = None):
        super().__init__(message)
        self.status_code = status_code
        self.message = message
        self.details = details


def _parse_schema(schema_cls):
    payload = request.get_json(silent=True)
    if payload is None:
        raise ApiError(400, "JSON body is required")
    try:
        return schema_cls.model_validate(payload)
    except ValidationError as exc:
        raise ApiError(400, "Invalid request data", [err["msg"] for err in exc.errors()]) from exc


def _ship_to_dict(ship: Ship):
    return ShipResponse.model_validate(ship).model_dump()


def _user_to_dict(user: User):
    return UserResponse.model_validate(user).model_dump()


def _part_type_to_dict(part_type: PartType):
    return PartTypeResponse.model_validate(part_type).model_dump()


def _part_to_dict(part: ShipPart):
    data = {
        "id": part.id,
        "vendor": part.vendor,
        "model": part.model,
        "class": part.class_,
        "size": part.size,
        "partTypeId": part.partTypeId,
        "partType": _part_type_to_dict(part.part_type),
    }
    return PartResponse.model_validate(data).model_dump(by_alias=True)


def _get_or_404(model, entity_id: int, entity_name: str):
    entity = db.session.get(model, entity_id)
    if entity is None:
        raise ApiError(404, f"{entity_name} not found")
    return entity


def _build_auth_response(user: User):
    payload = {
        "accessToken": create_access_token(user.id),
        "tokenType": "Bearer",
        "user": _user_to_dict(user),
    }
    return AuthResponse.model_validate(payload).model_dump()


@api_bp.errorhandler(ApiError)
def handle_api_error(err: ApiError):
    payload = {"error": err.message}
    if err.details:
        payload["details"] = err.details
    return jsonify(payload), err.status_code


@api_bp.errorhandler(AuthError)
def handle_auth_error(err: AuthError):
    return jsonify({"error": err.message}), err.status_code


@api_bp.errorhandler(ValidationError)
def handle_validation_error(err: ValidationError):
    return jsonify({"error": "Invalid request data", "details": [e["msg"] for e in err.errors()]}), 400


@api_bp.errorhandler(IntegrityError)
def handle_integrity_error(err: IntegrityError):
    db.session.rollback()
    return jsonify({"error": "Duplicate or conflicting data"}), 409


@api_bp.post("/auth/register")
def register_user():
    payload = _parse_schema(UserCreateRequest)
    duplicate = User.query.filter((User.email == payload.email) | (User.login == payload.login)).first()
    if duplicate is not None:
        raise ApiError(409, "User with same email or login already exists")

    user = User(
        name=payload.name.strip(),
        email=payload.email.strip(),
        login=payload.login.strip(),
        password=hash_password(payload.password),
    )
    db.session.add(user)
    db.session.commit()
    return jsonify(_build_auth_response(user)), 201


@api_bp.post("/auth/login")
def login_user():
    payload = _parse_schema(UserLoginRequest)
    user = User.query.filter_by(login=payload.login.strip()).first()
    if user is None or not verify_password(payload.password, user.password):
        raise ApiError(401, "Invalid login or password")
    return jsonify(_build_auth_response(user)), 200


@api_bp.get("/users")
@require_auth
def list_users():
    users = User.query.order_by(User.id.asc()).all()
    return jsonify([_user_to_dict(user) for user in users]), 200


@api_bp.post("/users")
def create_user():
    return register_user()


@api_bp.get("/ships")
def list_ships():
    ships = Ship.query.order_by(Ship.id.asc()).all()
    return jsonify([_ship_to_dict(ship) for ship in ships]), 200


@api_bp.post("/ships")
@require_auth
def create_ship():
    payload = _parse_schema(ShipCreateRequest)
    duplicate = Ship.query.filter_by(
        vendor=payload.vendor.strip(), model=payload.model.strip(), name=payload.name.strip()
    ).first()
    if duplicate is not None:
        raise ApiError(409, "Ship already exists")

    ship = Ship(vendor=payload.vendor.strip(), model=payload.model.strip(), name=payload.name.strip())
    db.session.add(ship)
    db.session.commit()
    return jsonify(_ship_to_dict(ship)), 201


@api_bp.get("/ship/<int:ship_id>/parts")
def list_ship_parts(ship_id: int):
    _get_or_404(Ship, ship_id, "Ship")
    links = PartByShip.query.filter_by(shipId=ship_id).join(PartByShip.part).all()
    return jsonify([_part_to_dict(link.part) for link in links]), 200


@api_bp.post("/ship/<int:ship_id>/parts")
@require_auth
def assign_ship_part(ship_id: int):
    _get_or_404(Ship, ship_id, "Ship")
    payload = _parse_schema(ShipPartAssignmentRequest)
    _get_or_404(ShipPart, payload.partId, "Part")

    link = PartByShip.query.filter_by(shipId=ship_id, partId=payload.partId).first()
    if link is not None:
        raise ApiError(409, "Part already assigned to ship")

    link = PartByShip(shipId=ship_id, partId=payload.partId)
    db.session.add(link)
    db.session.commit()
    return jsonify({"shipId": ship_id, "partId": payload.partId}), 201


@api_bp.get("/user/<int:user_id>/ships")
@require_auth
def list_user_ships(user_id: int):
    require_same_user(user_id)
    _get_or_404(User, user_id, "User")
    links = ShipByUser.query.filter_by(userId=user_id, isDeleted=False).join(ShipByUser.ship).all()
    return jsonify([_ship_to_dict(link.ship) for link in links]), 200


@api_bp.post("/user/<int:user_id>/ships")
@require_auth
def assign_user_ship(user_id: int):
    require_same_user(user_id)
    _get_or_404(User, user_id, "User")
    payload = _parse_schema(UserShipAssignmentRequest)
    _get_or_404(Ship, payload.shipId, "Ship")

    link = ShipByUser.query.filter_by(userId=user_id, shipId=payload.shipId).first()
    if payload.isDeleted:
        if link is None or link.isDeleted:
            raise ApiError(404, "User does not have this ship")
        link.isDeleted = True
    else:
        if link is None:
            link = ShipByUser(userId=user_id, shipId=payload.shipId, isDeleted=False)
            db.session.add(link)
        elif not link.isDeleted:
            raise ApiError(409, "Ship already assigned to user")
        else:
            link.isDeleted = False

    db.session.commit()
    return jsonify({"userId": user_id, "shipId": payload.shipId, "isDeleted": link.isDeleted}), 200


@api_bp.get("/user/<int:user_id>/parts")
@require_auth
def list_user_parts(user_id: int):
    require_same_user(user_id)
    _get_or_404(User, user_id, "User")

    query = (
        PartByUser.query.filter_by(userId=user_id, isDeleted=False)
        .join(PartByUser.part)
        .join(ShipPart.part_type)
    )
    class_filter = request.args.get("class")
    size_filter = request.args.get("size", type=int)
    type_filter = request.args.get("type")

    if class_filter:
        query = query.filter(ShipPart.class_ == class_filter)
    if size_filter:
        query = query.filter(ShipPart.size == size_filter)
    if type_filter:
        query = query.filter(PartType.type == type_filter)

    links = query.all()
    return jsonify([_part_to_dict(link.part) for link in links]), 200


@api_bp.post("/user/<int:user_id>/parts")
@require_auth
def assign_user_part(user_id: int):
    require_same_user(user_id)
    _get_or_404(User, user_id, "User")
    payload = _parse_schema(UserPartAssignmentRequest)
    _get_or_404(ShipPart, payload.partId, "Part")

    link = PartByUser.query.filter_by(userId=user_id, partId=payload.partId).first()
    if payload.isDeleted:
        if link is None or link.isDeleted:
            raise ApiError(404, "User does not have this part")
        link.isDeleted = True
    else:
        if link is None:
            link = PartByUser(userId=user_id, partId=payload.partId, isDeleted=False)
            db.session.add(link)
        elif not link.isDeleted:
            raise ApiError(409, "Part already assigned to user")
        else:
            link.isDeleted = False

    db.session.commit()
    return jsonify({"userId": user_id, "partId": payload.partId, "isDeleted": link.isDeleted}), 200


@api_bp.get("/parts")
def list_parts():
    parts = ShipPart.query.join(ShipPart.part_type).order_by(ShipPart.id.asc()).all()
    return jsonify([_part_to_dict(part) for part in parts]), 200


@api_bp.post("/parts")
@require_auth
def create_part():
    payload = _parse_schema(PartCreateRequest)
    _get_or_404(PartType, payload.partTypeId, "Part type")

    duplicate = ShipPart.query.filter_by(
        vendor=payload.vendor.strip(),
        model=payload.model.strip(),
        class_=payload.class_,
        size=payload.size,
        partTypeId=payload.partTypeId,
    ).first()
    if duplicate is not None:
        raise ApiError(409, "Part already exists")

    part = ShipPart(
        vendor=payload.vendor.strip(),
        model=payload.model.strip(),
        class_=payload.class_,
        size=payload.size,
        partTypeId=payload.partTypeId,
    )
    db.session.add(part)
    db.session.commit()
    db.session.refresh(part)
    return jsonify(_part_to_dict(part)), 201


@api_bp.get("/part-types")
def list_part_types():
    types = PartType.query.order_by(PartType.id.asc()).all()
    return jsonify([_part_type_to_dict(part_type) for part_type in types]), 200


@api_bp.post("/part-types")
@require_auth
def create_part_type():
    payload = _parse_schema(PartTypeCreateRequest)
    duplicate = PartType.query.filter_by(type=payload.type.strip()).first()
    if duplicate is not None:
        raise ApiError(409, "Part type already exists")

    part_type = PartType(type=payload.type.strip(), isReplaceble=payload.isReplaceble)
    db.session.add(part_type)
    db.session.commit()
    return jsonify(_part_type_to_dict(part_type)), 201
