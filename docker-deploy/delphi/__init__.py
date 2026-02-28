"""Delphi module: loads pre-computed Wideband Delphi simulation results."""

from .loader import load_delphi_data
from .renderer import render_delphi_summary, render_delphi_detail, render_metodologia

__all__ = [
    "load_delphi_data",
    "render_delphi_summary",
    "render_delphi_detail",
    "render_metodologia",
]
