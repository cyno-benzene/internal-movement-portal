"""Add enhanced employee profile fields and work experience table

Revision ID: 002_enhanced_profiles
Revises: 001_initial_migration
Create Date: 2024-01-10 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002_enhanced_profiles'
down_revision = '001_initial_migration'
branch_labels = None
depends_on = None


def upgrade():
    # Add new fields to employees table
    op.add_column('employees', sa.Column('date_of_joining', sa.Date(), nullable=True))
    op.add_column('employees', sa.Column('reporting_officer_id', sa.String(50), nullable=True))
    op.add_column('employees', sa.Column('rep_officer_name', sa.String(255), nullable=True))
    op.add_column('employees', sa.Column('months', sa.Integer(), nullable=True, default=0))
    op.add_column('employees', sa.Column('months_experience', sa.Integer(), nullable=True, default=0))
    
    # Create foreign key for reporting_officer_id
    op.create_foreign_key(
        'fk_employees_reporting_officer_id', 
        'employees', 
        'employees', 
        ['reporting_officer_id'], 
        ['employee_id']
    )
    
    # Update existing years_experience to months_experience (multiply by 12)
    op.execute("UPDATE employees SET months_experience = COALESCE(years_experience * 12, 0) WHERE years_experience IS NOT NULL")
    
    # Drop the old years_experience column
    op.drop_column('employees', 'years_experience')
    
    # Create work_experiences table
    op.create_table('work_experiences',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('employee_id', sa.String(50), nullable=False),
        sa.Column('company_name', sa.String(255), nullable=False),
        sa.Column('job_title', sa.String(255), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('is_current', sa.Boolean(), nullable=True, default=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('key_achievements', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('skills_used', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('technologies_used', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('location', sa.String(255), nullable=True),
        sa.Column('employment_type', sa.String(50), nullable=True),
        sa.Column('duration_months', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.employee_id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_work_experiences_id'), 'work_experiences', ['id'], unique=False)


def downgrade():
    # Drop work_experiences table
    op.drop_index(op.f('ix_work_experiences_id'), table_name='work_experiences')
    op.drop_table('work_experiences')
    
    # Add back years_experience column
    op.add_column('employees', sa.Column('years_experience', sa.Integer(), nullable=True, default=0))
    
    # Convert months_experience back to years_experience (divide by 12)
    op.execute("UPDATE employees SET years_experience = COALESCE(months_experience / 12, 0) WHERE months_experience IS NOT NULL")
    
    # Drop foreign key constraint
    op.drop_constraint('fk_employees_reporting_officer_id', 'employees', type_='foreignkey')
    
    # Drop new columns from employees table
    op.drop_column('employees', 'months_experience')
    op.drop_column('employees', 'months')
    op.drop_column('employees', 'rep_officer_name')
    op.drop_column('employees', 'reporting_officer_id')
    op.drop_column('employees', 'date_of_joining')
