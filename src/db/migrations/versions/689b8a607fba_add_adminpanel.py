"""add adminpanel

Revision ID: 689b8a607fba
Revises: 1bc7f6401892
Create Date: 2025-04-04 12:36:06.549267

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '689b8a607fba'
down_revision = '1bc7f6401892'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('flows',
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('screen_name', sa.String(), nullable=False),
    sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text("(now() at time zone 'utc')"), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_flows_id'), 'flows', ['id'], unique=False)
    op.create_table('partners',
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text("(now() at time zone 'utc')"), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_partners_id'), 'partners', ['id'], unique=False)
    op.create_table('tariffs',
    sa.Column('payment_amount', sa.Integer(), nullable=False),
    sa.Column('access_days', sa.Integer(), nullable=False),
    sa.Column('payment_interval', sa.String(), nullable=False),
    sa.Column('payment_period', sa.Integer(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text("(now() at time zone 'utc')"), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('payment_amount')
    )
    op.create_index(op.f('ix_tariffs_id'), 'tariffs', ['id'], unique=False)
    op.create_table('flow_variants',
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('feature_name', sa.String(), nullable=False),
    sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
    sa.Column('flow_id', sa.Integer(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text("(now() at time zone 'utc')"), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['flow_id'], ['flows.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_flow_variants_id'), 'flow_variants', ['id'], unique=False)
    op.create_table('referrals',
    sa.Column('id', sa.String(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('partner_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text("(now() at time zone 'utc')"), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['partner_id'], ['partners.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_referrals_id'), 'referrals', ['id'], unique=False)
    op.create_table('flowvariant_user_association',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('flow_variant_id', sa.Integer(), nullable=False),
    sa.Column('screen_name', sa.String(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text("(now() at time zone 'utc')"), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['flow_variant_id'], ['flow_variants.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_flowvariant_user_association_id'), 'flowvariant_user_association', ['id'], unique=False)
    op.add_column('subscriptions', sa.Column('renewal_enabled', sa.Boolean(), server_default=sa.text('true'), nullable=False))
    op.create_foreign_key(None, 'subscriptions', 'tariffs', ['tariff_id'], ['id'], ondelete='CASCADE')
    op.add_column('trackings', sa.Column('approved', sa.Boolean(), server_default=sa.text('false'), nullable=False))
    op.add_column('users', sa.Column('telegram_username', sa.String(), nullable=True))
    op.add_column('users', sa.Column('telegram_name', sa.String(), nullable=True))
    op.add_column('users', sa.Column('referral_id', sa.String(), nullable=True))
    op.create_foreign_key(None, 'users', 'referrals', ['referral_id'], ['id'], ondelete='SET NULL')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'users', type_='foreignkey')
    op.drop_column('users', 'referral_id')
    op.drop_column('users', 'telegram_name')
    op.drop_column('users', 'telegram_username')
    op.drop_column('trackings', 'approved')
    op.drop_constraint(None, 'subscriptions', type_='foreignkey')
    op.drop_column('subscriptions', 'renewal_enabled')
    op.drop_index(op.f('ix_flowvariant_user_association_id'), table_name='flowvariant_user_association')
    op.drop_table('flowvariant_user_association')
    op.drop_index(op.f('ix_referrals_id'), table_name='referrals')
    op.drop_table('referrals')
    op.drop_index(op.f('ix_flow_variants_id'), table_name='flow_variants')
    op.drop_table('flow_variants')
    op.drop_index(op.f('ix_tariffs_id'), table_name='tariffs')
    op.drop_table('tariffs')
    op.drop_index(op.f('ix_partners_id'), table_name='partners')
    op.drop_table('partners')
    op.drop_index(op.f('ix_flows_id'), table_name='flows')
    op.drop_table('flows')
    # ### end Alembic commands ###

