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
    # --- thin rollable body ---
    CLEARANCE=1.0,        # gap around the board in the pocket
    WALL=2.5,             # lip wall thickness
    LIP_H=8.0,            # lip height above the base plane (covers steel edge + lower sidewall)
    LINER_T=3.0,          # liner floor thickness
    SKIN_T=1.0,           # flexible skin thickness
    SHELF_W=10.0,         # edge shelf width (steel edges rest on this)
    RECESS=1.0,           # base relief depth inside the shelf
    GROOVE_PITCH=30.0, GROOVE_W=3.0, GROOVE_D=1.5,   # transverse flex-relief grooves under the floor
    WEDGE_PITCH=25.0, WEDGE_TOP=8.0, WEDGE_BOT=1.0,  # V-notches in the lip so it compresses when rolled
    # --- scales ---
    SCALE_L=30.0, SCALE_W=19.4, SCALE_T=2.0, SCALE_PITCH=22.0, SCALE_GAP=0.6,
    SCALE_TILT=7.0,       # deg; PITCH*tan(tilt) must exceed SCALE_T/cos(tilt) so neighbours nest
    SCALE_CHAMFER=0.6, SCALE_MARGIN=1.5,
    STUD_R=2.0, STUD_H=1.3, STUD_X=4.0,
    # --- tip / tail protectors (removable hard cups with soft lining) ---
    CAP_LEN=120.0,        # how far each cap reaches back from the tip / tail
    ROOF_LEN=60.0,        # roof over the top of the nose / tail
    CAP_CLEAR=0.5, CAP_LINER_T=2.0, CAP_SHELL_T=2.5, CAP_WALL_ABOVE=1.0,
    # --- straps ---
    STRAP_W=25.0, STRAP_T=1.2,
    TAB_LEN=39.0, TAB_OUT=24.0, TAB_T=2.0, SLOT_W=3.5,
    STATIONS=[-520.0, -260.0, 0.0, 260.0, 520.0],    # strap stations along the body
    DENSITY=dict(scales=1.15e-3, skin=1.2e-3, liner=0.25e-3, cap_shell=1.15e-3),  # g/mm3 (nylon/PETG, TPU, TPU lattice)
)

if True:
    lib.build(PARAMS, here)
