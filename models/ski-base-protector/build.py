"""Ski-pair base protector (air-travel) - parametric FreeCAD build. Units: mm.

Two skis side by side, bases facing the same way, tips aligned, one liner pocket each with a divider rib.
Rebuild: scripts/run.sh models/ski-base-protector/build.py
"""
import os
import sys

here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, here)
import protector_lib as lib

PARAMS = dict(
    NAME="ski-base-protector",
    # --- skis (flat reference; camber/rocker not modelled) ---
    LENGTH=1700.0,
    TIP_W=125.0,
    WAIST_W=85.0,
    TAIL_W=105.0,
    CAP=120.0,
    CENTERS_Y=[-66.5, 66.5],   # ski centrelines; divider rib = 2*(66.5 - 62.5 - CLEARANCE) = 6 mm at the widest point
    GEAR_T=12.0,
    # --- liner / skin ---
    CLEARANCE=1.0,
    WALL=4.0,
    LIP_H=14.0,
    LINER_T=6.0,
    SKIN_T=1.5,
    SHELF_W=10.0,
    RECESS=1.5,
    GROOVE_PITCH=40.0, GROOVE_W=3.0, GROOVE_D=3.0,
    # --- scales (same system as the snowboard) ---
    SCALE_L=34.0, SCALE_W=21.4, SCALE_T=2.5, SCALE_PITCH=24.0, SCALE_GAP=0.6,
    SCALE_TILT=8.0,
    SCALE_CHAMFER=0.8, SCALE_MARGIN=1.5,
    STUD_R=2.2, STUD_H=1.6, STUD_X=4.0,
)

lib.build(PARAMS, here)
