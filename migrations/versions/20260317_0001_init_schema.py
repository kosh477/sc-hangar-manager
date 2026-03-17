"""create initial schema

Revision ID: 20260317_0001
Revises:
Create Date: 2026-03-17 00:00:01
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260317_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "partsTypes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("type", sa.String(length=128), nullable=False),
        sa.Column("isReplaceble", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "ships",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("vendor", sa.String(length=128), nullable=False),
        sa.Column("model", sa.String(length=128), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("login", sa.String(length=128), nullable=False),
        sa.Column("password", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email", name="uq_users_email"),
        sa.UniqueConstraint("login", name="uq_users_login"),
    )
    op.create_index("ix_users_email", "users", ["email"])
    op.create_index("ix_users_login", "users", ["login"])

    op.create_table(
        "shipsParts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("vendor", sa.String(length=128), nullable=False),
        sa.Column("model", sa.String(length=128), nullable=False),
        sa.Column("class", sa.String(length=64), nullable=False),
        sa.Column("size", sa.Integer(), nullable=False),
        sa.Column("partTypeId", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.CheckConstraint(
            "size >= 1 AND size <= 10",
            name="ck_shipsParts_size_range",
        ),
        sa.CheckConstraint(
            "class IN ('Military', 'Competition', 'Civilian', 'Stealth', 'Industrial')",
            name="ck_shipsParts_class_allowed",
        ),
        sa.ForeignKeyConstraint(["partTypeId"], ["partsTypes.id"], name="fk_shipsParts_partTypeId_partsTypes"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_shipsParts_partTypeId", "shipsParts", ["partTypeId"])

    op.create_table(
        "shipsByUser",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("userId", sa.Integer(), nullable=False),
        sa.Column("shipId", sa.Integer(), nullable=False),
        sa.Column("isDeleted", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["shipId"], ["ships.id"], name="fk_shipsByUser_shipId_ships"),
        sa.ForeignKeyConstraint(["userId"], ["users.id"], name="fk_shipsByUser_userId_users"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_shipsByUser_isDeleted", "shipsByUser", ["isDeleted"])
    op.create_index("ix_shipsByUser_shipId", "shipsByUser", ["shipId"])
    op.create_index("ix_shipsByUser_userId", "shipsByUser", ["userId"])

    op.create_table(
        "partsByShip",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("partId", sa.Integer(), nullable=False),
        sa.Column("shipId", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["partId"], ["shipsParts.id"], name="fk_partsByShip_partId_shipsParts"),
        sa.ForeignKeyConstraint(["shipId"], ["ships.id"], name="fk_partsByShip_shipId_ships"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_partsByShip_partId", "partsByShip", ["partId"])
    op.create_index("ix_partsByShip_shipId", "partsByShip", ["shipId"])

    op.create_table(
        "partsByUser",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("partId", sa.Integer(), nullable=False),
        sa.Column("userId", sa.Integer(), nullable=False),
        sa.Column("isDeleted", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["partId"], ["shipsParts.id"], name="fk_partsByUser_partId_shipsParts"),
        sa.ForeignKeyConstraint(["userId"], ["users.id"], name="fk_partsByUser_userId_users"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_partsByUser_isDeleted", "partsByUser", ["isDeleted"])
    op.create_index("ix_partsByUser_partId", "partsByUser", ["partId"])
    op.create_index("ix_partsByUser_userId", "partsByUser", ["userId"])


def downgrade() -> None:
    op.drop_index("ix_partsByUser_userId", table_name="partsByUser")
    op.drop_index("ix_partsByUser_partId", table_name="partsByUser")
    op.drop_index("ix_partsByUser_isDeleted", table_name="partsByUser")
    op.drop_table("partsByUser")

    op.drop_index("ix_partsByShip_shipId", table_name="partsByShip")
    op.drop_index("ix_partsByShip_partId", table_name="partsByShip")
    op.drop_table("partsByShip")

    op.drop_index("ix_shipsByUser_userId", table_name="shipsByUser")
    op.drop_index("ix_shipsByUser_shipId", table_name="shipsByUser")
    op.drop_index("ix_shipsByUser_isDeleted", table_name="shipsByUser")
    op.drop_table("shipsByUser")

    op.drop_index("ix_shipsParts_partTypeId", table_name="shipsParts")
    op.drop_table("shipsParts")

    op.drop_index("ix_users_login", table_name="users")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")

    op.drop_table("ships")
    op.drop_table("partsTypes")
