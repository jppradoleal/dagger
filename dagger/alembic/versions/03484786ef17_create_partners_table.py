"""create partners table

Revision ID: 03484786ef17
Revises: e2aa5f22a763
Create Date: 2023-06-29 15:00:45.254186

"""
import sqlalchemy as sa
from alembic import op
from geoalchemy2 import Geometry

# revision identifiers, used by Alembic.
revision = "03484786ef17"
down_revision = "e2aa5f22a763"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_geospatial_table(
        "partners",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("trading_name", sa.String(), nullable=False),
        sa.Column("owner_name", sa.String(), nullable=False),
        sa.Column("document", sa.String(), nullable=False),
        sa.Column(
            "coverage_area",
            Geometry(
                geometry_type="MULTIPOLYGON",
                spatial_index=False,
                from_text="ST_GeomFromEWKT",
                name="geometry",
            ),
            nullable=False,
        ),
        sa.Column(
            "address",
            Geometry(
                geometry_type="POINT",
                spatial_index=False,
                from_text="ST_GeomFromEWKT",
                name="geometry",
            ),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("document"),
        schema="public",
    )
    op.create_geospatial_index(
        "idx_partners_address",
        "partners",
        ["address"],
        unique=False,
        schema="public",
        postgresql_using="gist",
        postgresql_ops={},
    )
    op.create_geospatial_index(
        "idx_partners_coverage_area",
        "partners",
        ["coverage_area"],
        unique=False,
        schema="public",
        postgresql_using="gist",
        postgresql_ops={},
    )
    op.create_index(
        op.f("ix_public_partners_id"), "partners", ["id"], unique=False, schema="public"
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_public_partners_id"), table_name="partners", schema="public")
    op.drop_geospatial_index(
        "idx_partners_coverage_area",
        table_name="partners",
        schema="public",
        postgresql_using="gist",
        column_name="coverage_area",
    )
    op.drop_geospatial_index(
        "idx_partners_address",
        table_name="partners",
        schema="public",
        postgresql_using="gist",
        column_name="address",
    )
    op.drop_geospatial_table("partners", schema="public")
    # ### end Alembic commands ###
