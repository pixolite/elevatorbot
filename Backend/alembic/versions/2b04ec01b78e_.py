"""empty message

Revision ID: 2b04ec01b78e
Revises: ef97c8cef951
Create Date: 2022-06-01 16:16:48.372839+00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2b04ec01b78e'
down_revision = 'ef97c8cef951'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('rolesRecords',
    sa.Column('_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('role_id', sa.BigInteger(), nullable=True),
    sa.Column('bungie_id', sa.BigInteger(), nullable=False),
    sa.Column('inverse', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['role_id'], ['roles.role_id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('_id')
    )
    op.create_table('rolesActivityAllowTimePeriod',
    sa.Column('_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('role_activity_id', sa.Integer(), nullable=True),
    sa.Column('start_time', sa.DateTime(timezone=True), nullable=False),
    sa.Column('end_time', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['role_activity_id'], ['rolesActivity._id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('_id')
    )
    op.create_table('rolesActivityDisallowTimePeriod',
    sa.Column('_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('role_activity_id', sa.Integer(), nullable=True),
    sa.Column('start_time', sa.DateTime(timezone=True), nullable=False),
    sa.Column('end_time', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['role_activity_id'], ['rolesActivity._id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('_id')
    )
    op.drop_table('rolesActivityTimePeriod')
    op.drop_table('rolesTriumphs')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('rolesTriumphs',
    sa.Column('_id', sa.INTEGER(), server_default=sa.text('nextval(\'"rolesTriumphs__id_seq"\'::regclass)'), autoincrement=True, nullable=False),
    sa.Column('role_id', sa.BIGINT(), autoincrement=False, nullable=True),
    sa.Column('bungie_id', sa.BIGINT(), autoincrement=False, nullable=False),
    sa.Column('inverse', sa.BOOLEAN(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['role_id'], ['roles.role_id'], name='rolesTriumphs_role_id_fkey', onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('_id', name='rolesTriumphs_pkey')
    )
    op.create_table('rolesActivityTimePeriod',
    sa.Column('_id', sa.INTEGER(), server_default=sa.text('nextval(\'"rolesActivityTimePeriod__id_seq"\'::regclass)'), autoincrement=True, nullable=False),
    sa.Column('role_activity_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('start_time', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
    sa.Column('end_time', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['role_activity_id'], ['rolesActivity._id'], name='rolesActivityTimePeriod_role_activity_id_fkey', onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('_id', name='rolesActivityTimePeriod_pkey')
    )
    op.drop_table('rolesActivityDisallowTimePeriod')
    op.drop_table('rolesActivityAllowTimePeriod')
    op.drop_table('rolesRecords')
    # ### end Alembic commands ###