"""
Doctor-AI Collaboration Module
Enables feedback collection and incremental learning
"""

from .doctor_ai_collaboration import (
    DoctorAICollaborationSystem,
    render_collaboration_mode,
    create_annotation_canvas
)

__all__ = [
    "DoctorAICollaborationSystem",
    "render_collaboration_mode",
    "create_annotation_canvas"
]