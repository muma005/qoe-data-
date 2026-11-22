"""
Level 4: Financial Databook (FDB) & Analytical Calculation Engine (fdb-calc).

Public surface for the headless calculation DAG, Row 1 check bars, PVM waterfall,
replacement-cost engine, anti-double-dipping checker, sandboxed worker, and the
proto-shaped FdbCalculationService facade.
"""

from .formula_graph import (
    CHECK_BAR_FORMULAS,
    CheckBarStatus,
    Cell,
    CycleDetectedError,
    Databook,
    DoubleDipChecker,
    ExcelFormulaEvaluator,
    FormulaGraph,
    HyperFormulaBackend,
    HyperFormulaSidecarClient,
    PVMProduct,
    PVMWaterfallEngine,
    ReplacementCostEngine,
)
from .check_bars import (
    RGB,
    RGB_USAGE,
    CheckBarResult,
    CheckBarEngine,
    ModelingHygieneLinter,
)
from .sandbox_worker import (
    SandboxWorker,
    XLSXSerializer,
    FdbCalculationService,
)

__all__ = [
    "CHECK_BAR_FORMULAS",
    "CheckBarStatus",
    "Cell",
    "CycleDetectedError",
    "Databook",
    "DoubleDipChecker",
    "ExcelFormulaEvaluator",
    "FormulaGraph",
    "HyperFormulaBackend",
    "HyperFormulaSidecarClient",
    "PVMProduct",
    "PVMWaterfallEngine",
    "ReplacementCostEngine",
    "RGB",
    "RGB_USAGE",
    "CheckBarResult",
    "CheckBarEngine",
    "ModelingHygieneLinter",
    "SandboxWorker",
    "XLSXSerializer",
    "FdbCalculationService",
]
