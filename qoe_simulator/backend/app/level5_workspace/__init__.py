"""
Level 5: User Workspace, VDR Portal & Interaction Surfaces (ui-workspace).

Backend gateway: VDR tree + access control, capability tokens, watermarking,
IRL console, workspace state sync, deliverable compiler, and CloudEvents.
"""

from .vdr import (
    VDRNodeType,
    ReleaseWave,
    CapabilityTokenManager,
    WatermarkEngine,
    VDRTreeBuilder,
    ZeroKnowledgeFilter,
    RateLimiter,
)
from .irl import IRLPriority, IRLConsole
from .gateway import (
    DdeSanitizer,
    CloudEventEmitter,
    WorkspaceGatewayService,
)

__all__ = [
    "VDRNodeType",
    "ReleaseWave",
    "CapabilityTokenManager",
    "WatermarkEngine",
    "VDRTreeBuilder",
    "ZeroKnowledgeFilter",
    "RateLimiter",
    "IRLPriority",
    "IRLConsole",
    "DdeSanitizer",
    "CloudEventEmitter",
    "WorkspaceGatewayService",
]
