"""Snowboard base protector (air-travel) - parametric FreeCAD build. Units: mm.

Rebuild: scripts/run.sh models/snowboard-base-protector/build.py
"""
import os
import sys

here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, here)
import protector_lib as lib

PARAMS = dict(
    NAME="snowboard-base-protector",
    # --- snowboard (flat reference; camber/nose kick not modelled) ---
    LENGTH=1560.0,        # tip to tail
    TIP_W=300.0,          # width at end of sidecut, tip
    WAIST_W=250.0,
    TAIL_W=300.0,
    CAP=180.0,            # length of the rounded nose/tail
    CENTERS_Y=[0.0],      # one board
    GEAR_T=11.0,          # reference board thickness (display only)
    # --- liner / skin ---
    CLEARANCE=1.0,        # gap around the board in the pocket
    WALL=4.0,             # lip wall thickness around the edges
    LIP_H=12.0,           # lip height above the base plane (covers the sidewall + edge)
    LINER_T=6.0,          # liner floor thickness
    SKIN_T=1.5,           # flexible skin thickness
    SHELF_W=12.0,         # edge shelf width (edges rest on this)
    RECESS=1.5,           # base relief depth inside the shelf (P-tex never touches liner)
    GROOVE_PITCH=40.0, GROOVE_W=3.0, GROOVE_D=3.0,   # transverse flex-relief grooves
    # --- scales ---
    SCALE_L=34.0, SCALE_W=21.4, SCALE_T=2.5, SCALE_PITCH=24.0, SCALE_GAP=0.6,
    SCALE_TILT=8.0,       # deg; P*tan(tilt) must exceed SCALE_T/cos(tilt) so neighbours nest
    SCALE_CHAMFER=0.8, SCALE_MARGIN=1.5,
    STUD_R=2.2, STUD_H=1.6, STUD_X=4.0,
)

if True:
    lib.build(PARAMS, here)
