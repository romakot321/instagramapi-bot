"""add followers

Revision ID: 1bc7f6401892
Revises: fc765a1fff1d
Create Date: 2025-04-03 20:53:08.630925

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1bc7f6401892'
down_revision = 'fc765a1fff1d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tracking_medias', sa.Column('like_count', sa.Integer(), nullable=True))
    op.add_column('tracking_medias', sa.Column('comment_count', sa.Integer(), nullable=True))
    op.drop_constraint('tracking_media_uq', 'tracking_medias', type_='unique')
    op.create_unique_constraint('tracking_media_uq', 'tracking_medias', ['instagram_username', 'instagram_id'])
    op.drop_constraint('tracking_medias_creator_telegram_id_fkey', 'tracking_medias', type_='foreignkey')
    op.drop_column('tracking_medias', 'creator_telegram_id')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tracking_medias', sa.Column('creator_telegram_id', sa.BIGINT(), autoincrement=False, nullable=False))
    op.create_foreign_key('tracking_medias_creator_telegram_id_fkey', 'tracking_medias', 'users', ['creator_telegram_id'], ['telegram_id'], ondelete='CASCADE')
    op.drop_constraint('tracking_media_uq', 'tracking_medias', type_='unique')
    op.create_unique_constraint('tracking_media_uq', 'tracking_medias', ['creator_telegram_id', 'instagram_username', 'instagram_id'])
    op.drop_column('tracking_medias', 'comment_count')
    op.drop_column('tracking_medias', 'like_count')
    # ### end Alembic commands ###

