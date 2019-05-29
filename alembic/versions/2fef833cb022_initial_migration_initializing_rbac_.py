"""initial migration: initializing rbac, users, post

Revision ID: 2fef833cb022
Revises: 
Create Date: 2019-05-29 14:50:13.930762

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2fef833cb022'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('rbac_action',
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('name', sa.UnicodeText(), nullable=False),
    sa.Column('description', sa.UnicodeText(), nullable=True),
    sa.PrimaryKeyConstraint('name')
    )
    op.create_table('rbac_endpoint',
    sa.Column('name', sa.UnicodeText(), nullable=False),
    sa.Column('description', sa.UnicodeText(), nullable=True),
    sa.PrimaryKeyConstraint('name')
    )
    op.create_table('rbac_object',
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('name', sa.UnicodeText(), nullable=False),
    sa.Column('description', sa.UnicodeText(), nullable=True),
    sa.PrimaryKeyConstraint('name')
    )
    op.create_table('rbac_role',
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('name', sa.UnicodeText(), nullable=False),
    sa.Column('description', sa.UnicodeText(), nullable=True),
    sa.PrimaryKeyConstraint('name')
    )
    op.create_table('users',
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('id', sa.String(length=32), nullable=False),
    sa.Column('name', sa.String(length=32), nullable=False),
    sa.Column('email', sa.String(length=256), nullable=False),
    sa.Column('h_pass', sa.UnicodeText(), nullable=False),
    sa.Column('confirmed', sa.Boolean(), server_default='true', nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('name')
    )
    op.create_table('post',
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('id', sa.String(length=32), nullable=False),
    sa.Column('author_id', sa.String(length=32), nullable=True),
    sa.Column('title', sa.UnicodeText(), nullable=False),
    sa.Column('body', sa.UnicodeText(), nullable=False),
    sa.ForeignKeyConstraint(['author_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('rbac_permission',
    sa.Column('id', sa.String(length=32), nullable=False),
    sa.Column('object_name', sa.String(length=32), nullable=False),
    sa.Column('action_name', sa.String(length=32), nullable=False),
    sa.ForeignKeyConstraint(['action_name'], ['rbac_action.name'], ),
    sa.ForeignKeyConstraint(['object_name'], ['rbac_object.name'], ),
    sa.PrimaryKeyConstraint('object_name', 'action_name'),
    sa.UniqueConstraint('id')
    )
    op.create_table('rbac_user_role',
    sa.Column('id', sa.String(length=32), nullable=False),
    sa.Column('user_id', sa.String(length=32), nullable=False),
    sa.Column('role_name', sa.String(length=32), nullable=False),
    sa.ForeignKeyConstraint(['role_name'], ['rbac_role.name'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('user_id', 'role_name'),
    sa.UniqueConstraint('id')
    )
    op.create_table('rbac_endpoint_permission',
    sa.Column('id', sa.String(length=32), nullable=False),
    sa.Column('endpoint_name', sa.String(length=32), nullable=False),
    sa.Column('permission_id', sa.String(length=32), nullable=False),
    sa.ForeignKeyConstraint(['endpoint_name'], ['rbac_endpoint.name'], ),
    sa.ForeignKeyConstraint(['permission_id'], ['rbac_permission.id'], ),
    sa.PrimaryKeyConstraint('endpoint_name', 'permission_id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('rbac_role_permission',
    sa.Column('id', sa.String(length=32), nullable=False),
    sa.Column('role_name', sa.String(length=32), nullable=False),
    sa.Column('permission_id', sa.String(length=32), nullable=False),
    sa.ForeignKeyConstraint(['permission_id'], ['rbac_permission.id'], ),
    sa.ForeignKeyConstraint(['role_name'], ['rbac_role.name'], ),
    sa.PrimaryKeyConstraint('role_name', 'permission_id'),
    sa.UniqueConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('rbac_role_permission')
    op.drop_table('rbac_endpoint_permission')
    op.drop_table('rbac_user_role')
    op.drop_table('rbac_permission')
    op.drop_table('post')
    op.drop_table('users')
    op.drop_table('rbac_role')
    op.drop_table('rbac_object')
    op.drop_table('rbac_endpoint')
    op.drop_table('rbac_action')
    # ### end Alembic commands ###