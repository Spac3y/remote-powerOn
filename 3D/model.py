"""Two-part 3D-printed case for a 43 x 43 mm relay PCB.

Short base holds the PCB on its own: four locating pegs through the M2.5
mounting holes plus two snap clips in the side walls hooking over the board
edge. Tall cover press-fits onto the base with an internal lip and carries a
wire slot over the pin headers and a window over the two status LEDs.

Coordinates: origin at PCB centre (XY), Z=0 at the outside bottom of the base.
+Y is the top edge of the board as seen in the KiCad screenshot (the
"Made on earth by humans" side); the pin headers are on the -Y edge.
Print settings assumed: PLA, 0.4 mm nozzle -> walls are multiples of 0.4 mm.
"""
from build123d import *

# --- printing ---
line_w = 0.4                    # nozzle / extrusion width

# --- PCB (from KiCad drawing) ---
pcb_size = 43.0                 # square board edge
pcb_t = 1.6                     # board thickness
pcb_hole_d = 2.7                # mounting hole (M2.5 clearance)
hole_pitch = 35.941             # mounting-hole centre-to-centre (both axes)
tallest = 20.5                  # relay height above PCB top (datasheet)
header_y = -pcb_size / 2 + 3.51                 # header pin row
header_x0 = -pcb_size / 2 + 11.755 - 2.54 / 2   # OUT1 pin 1 (leftmost pin)
header_x1 = pcb_size / 2 - 12.69 + 2.54         # IN1 pin 3 (rightmost pin)
led_y = -10.23                                  # LED row (OUT2, PWR1)
led_x0 = -pcb_size / 2 + 24.8968                # OUT2 centre
led_x1 = pcb_size / 2 - 10.0                    # PWR1 centre
led_d = 5.0                     # 5 mm LEDs

# --- case ---
wall = 5 * line_w               # 2.0 side wall (base and cover)
floor_t = 5 * line_w            # 2.0 floor
lid_t = 5 * line_w              # 2.0 cover top
pcb_gap = 0.5                   # PCB edge to inner wall
corner_r = 3.0                  # outer vertical corner radius
standoff_h = 4.0                # under-board clearance for solder joints
standoff_d = 5.6                # board rests on this ring
peg_d = 2.4                     # locating peg through the PCB hole
peg_above = 1.0                 # straight peg length above PCB top
peg_tip = 0.8                   # conical lead-in on top of the peg
peg_tip_d = 1.4                 # peg tip diameter
base_wall_h = 14.0              # base rim height (cover sits on this)
top_clear = 1.5                 # air gap above relay

# --- snap clips (one in the middle of the -X and +X walls) ---
clip_w = 8.0                    # clip tab width along the wall
clip_t = 3 * line_w             # 1.2 tab thickness (outer part of the wall)
clip_slot = 2 * line_w          # 0.8 side slots and gap behind the tab
clip_root = 2 * line_w          # 0.8 solid bottom the tab grows from
hook_over = 0.5                 # hook overlap onto the PCB top
hook_gap = 0.1                  # vertical play between PCB top and hook
hook_land = 0.6                 # vertical catch face height at the tip

# --- press-fit cover ---
lip_h = 3.0                     # lip depth into the base
lip_t = 3 * line_w              # 1.2 lip wall
fit = 0.1                       # lip-to-wall clearance per side (press fit)
header_slot_w = 3.6             # passes 2.54 mm Dupont housings
header_slot_margin = 0.6        # slot end-centre beyond outer pins
led_slot_w = led_d + 0.6        # one slot spanning both LEDs

# --- derived ---
inner = pcb_size + 2 * pcb_gap
outer = inner + 2 * wall
inner_r = corner_r - wall
pcb_z = floor_t + standoff_h                     # PCB bottom face
pcb_top = pcb_z + pcb_t
cover_top = pcb_top + tallest + top_clear + lid_t
lip_outer = inner - 2 * fit
lip_inner = lip_outer - 2 * lip_t
lip_inner_r = max(inner_r - fit - lip_t, 0.2)
hook_z = pcb_top + hook_gap                      # catch face
hook_tip_x = pcb_size / 2 - hook_over            # |x| of hook tip
clip_in_x = inner / 2 + clip_slot                # |x| of tab inner face
hook_top_z = hook_z + hook_land + (clip_in_x - hook_tip_x)   # 45 deg ramp

# --- base ---
with BuildPart() as base_p:
    with BuildSketch():
        RectangleRounded(outer, outer, corner_r)
    extrude(amount=base_wall_h)
    with BuildSketch(Plane.XY.offset(floor_t)):
        RectangleRounded(inner, inner, inner_r)
    extrude(amount=base_wall_h, mode=Mode.SUBTRACT)
    # standoffs + locating pegs
    with Locations((0, 0, floor_t)):
        with GridLocations(hole_pitch, hole_pitch, 2, 2):
            Cylinder(standoff_d / 2, standoff_h,
                     align=(Align.CENTER, Align.CENTER, Align.MIN))
    peg_straight = pcb_t + peg_above
    with Locations((0, 0, pcb_z)):
        with GridLocations(hole_pitch, hole_pitch, 2, 2):
            Cylinder(peg_d / 2, peg_straight,
                     align=(Align.CENTER, Align.CENTER, Align.MIN))
    with Locations((0, 0, pcb_z + peg_straight)):
        with GridLocations(hole_pitch, hole_pitch, 2, 2):
            Cone(peg_d / 2, peg_tip_d / 2, peg_tip,
                 align=(Align.CENTER, Align.CENTER, Align.MIN))
    # free the clip tabs: side slots through the wall + gap behind the tab
    cut_h = base_wall_h - clip_root
    for sx in (-1, 1):
        wall_mid_x = sx * (inner / 2 + wall / 2)
        for sy in (-1, 1):
            with Locations((wall_mid_x, sy * (clip_w + clip_slot) / 2, clip_root)):
                Box(wall + 0.2, clip_slot, cut_h,
                    align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)
        with Locations((sx * (inner / 2 + clip_slot / 2), 0, clip_root)):
            Box(clip_slot, clip_w, cut_h,
                align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)
    # hooks: 45 deg gusset under the catch (prints without support), flat
    # catch face over the PCB edge, 45 deg lead-in ramp above it
    gusset = clip_in_x - inner / 2
    for sx in (-1, 1):
        with BuildSketch(Plane.XZ.offset(-clip_w / 2)):   # XZ normal is -Y
            Polygon((sx * (clip_in_x + 0.01), hook_z - gusset),
                    (sx * inner / 2, hook_z),
                    (sx * hook_tip_x, hook_z),
                    (sx * hook_tip_x, hook_z + hook_land),
                    (sx * (clip_in_x + 0.01), hook_top_z), align=None)
        extrude(amount=clip_w)
base = base_p.part

# --- cover (modelled in place, sitting on the base rim) ---
cover_h = cover_top - base_wall_h
with BuildPart() as lid_p:
    with BuildSketch(Plane.XY.offset(base_wall_h)):
        RectangleRounded(outer, outer, corner_r)
    extrude(amount=cover_h)
    # cavity: 2 mm walls, with a 45 deg chamfer down to the lip inner face
    chamfer_h = (inner - lip_inner) / 2
    with BuildSketch(Plane.XY.offset(base_wall_h)):
        RectangleRounded(lip_inner, lip_inner, lip_inner_r)
    with BuildSketch(Plane.XY.offset(base_wall_h + chamfer_h)):
        RectangleRounded(inner, inner, inner_r)
    loft(mode=Mode.SUBTRACT)
    with BuildSketch(Plane.XY.offset(base_wall_h + chamfer_h)):
        RectangleRounded(inner, inner, inner_r)
    extrude(amount=cover_h - lid_t - chamfer_h, mode=Mode.SUBTRACT)
    # press-fit lip
    with BuildSketch(Plane.XY.offset(base_wall_h)):
        RectangleRounded(lip_outer, lip_outer, inner_r - fit)
        RectangleRounded(lip_inner, lip_inner, lip_inner_r, mode=Mode.SUBTRACT)
    extrude(amount=-lip_h)
    # wire slot over the pin-header row
    with BuildSketch(Plane.XY.offset(cover_top - lid_t)):
        with Locations(((header_x0 + header_x1) / 2, header_y)):
            SlotCenterToCenter(header_x1 - header_x0 + 2 * header_slot_margin,
                               header_slot_w)
    extrude(amount=lid_t, mode=Mode.SUBTRACT)
    # status window over both LEDs
    with BuildSketch(Plane.XY.offset(cover_top - lid_t)):
        with Locations(((led_x0 + led_x1) / 2, led_y)):
            SlotCenterToCenter(led_x1 - led_x0, led_slot_w)
    extrude(amount=lid_t, mode=Mode.SUBTRACT)
lid = lid_p.part

# --- reference bodies for clearance checks (not exported) ---
with BuildPart() as pcb_p:
    with Locations((0, 0, pcb_z)):
        Box(pcb_size, pcb_size, pcb_t, align=(Align.CENTER, Align.CENTER, Align.MIN))
    with Locations((0, 0, pcb_top)):
        with GridLocations(hole_pitch, hole_pitch, 2, 2):
            Hole(radius=pcb_hole_d / 2, depth=pcb_t)
pcb = pcb_p.part
relay_x, relay_y = (-13.97, -2.52), (-12.57, 15.41)   # silkscreen outline
relay = Box(relay_x[1] - relay_x[0], relay_y[1] - relay_y[0], tallest,
            align=(Align.MIN, Align.MIN, Align.MIN)).move(
    Location((relay_x[0], relay_y[0], pcb_top)))

lid_print = lid.rotate(Axis.X, 180)                   # print orientation
lid_print = lid_print.move(Location((0, 0, -lid_print.bounding_box().min.Z)))

show(lid, "lid")
show(lid_print, "lid_print")
show(pcb, "pcb")
show(relay, "relay")
show(base, "base")
result = base
