"""empty message

Revision ID: 001
Revises: 
Create Date: 2026-02-04

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create tracks table
    op.create_table(
        'tracks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('artist', sa.String(), nullable=False),
        sa.Column('album', sa.String(), nullable=True),
        sa.Column('genre', sa.String(), nullable=True),
        sa.Column('duration', sa.Float(), nullable=False),
        sa.Column('file_path', sa.String(), nullable=False),
        sa.Column('file_format', sa.String(), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('bpm', sa.Float(), nullable=True),
        sa.Column('key', sa.String(), nullable=True),
        sa.Column('energy', sa.Float(), nullable=True),
        sa.Column('danceability', sa.Float(), nullable=True),
        sa.Column('waveform_data', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tracks_id'), 'tracks', ['id'], unique=False)
    
    # Create track_analysis table
    op.create_table(
        'track_analysis',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('track_id', sa.Integer(), nullable=True),
        sa.Column('bpm', sa.Float(), nullable=True),
        sa.Column('key', sa.String(), nullable=True),
        sa.Column('camelot_key', sa.String(), nullable=True),
        sa.Column('energy_level', sa.Float(), nullable=True),
        sa.Column('structure', sa.JSON(), nullable=True),
        sa.Column('beat_positions', sa.JSON(), nullable=True),
        sa.Column('spectral_centroid', sa.Float(), nullable=True),
        sa.Column('spectral_rolloff', sa.Float(), nullable=True),
        sa.Column('analyzed_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['track_id'], ['tracks.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('track_id')
    )
    op.create_index(op.f('ix_track_analysis_id'), 'track_analysis', ['id'], unique=False)
    
    # Create cue_points table
    op.create_table(
        'cue_points',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('track_id', sa.Integer(), nullable=True),
        sa.Column('position', sa.Float(), nullable=False),
        sa.Column('label', sa.String(), nullable=True),
        sa.Column('color', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['track_id'], ['tracks.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_cue_points_id'), 'cue_points', ['id'], unique=False)
    
    # Create mixes table
    op.create_table(
        'mixes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('duration', sa.Float(), nullable=False),
        sa.Column('tracklist', sa.JSON(), nullable=False),
        sa.Column('transitions', sa.JSON(), nullable=True),
        sa.Column('export_path', sa.String(), nullable=True),
        sa.Column('export_format', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_mixes_id'), 'mixes', ['id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_mixes_id'), table_name='mixes')
    op.drop_table('mixes')
    op.drop_index(op.f('ix_cue_points_id'), table_name='cue_points')
    op.drop_table('cue_points')
    op.drop_index(op.f('ix_track_analysis_id'), table_name='track_analysis')
    op.drop_table('track_analysis')
    op.drop_index(op.f('ix_tracks_id'), table_name='tracks')
    op.drop_table('tracks')
