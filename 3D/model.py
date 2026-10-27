"""Two-part 3D-printed case for a 43 x 43 mm relay PCB.

Short base locates the PCB with four loose-fit pegs through the M3 mounting
holes. Tall cover press-fits onto the base with an internal lip; four hollow
posts hang from its top down to just above the board at the mounting holes,
trapping the PCB between them and the standoffs (no snap clips to break).
The cover also carries a wire slot over the pin headers and a window over the
two status LEDs.

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
pcb_hole_d = 3.2                # mounting hole (MountingHole_3.2mm_M3)
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
peg_d = 2.8                     # locating peg (0.2 clearance per side)
peg_above = 1.0                 # straight peg length above PCB top
peg_tip = 0.8                   # conical lead-in on top of the peg
peg_tip_d = 1.4                 # peg tip diameter
base_wall_h = 14.0              # base rim height (cover sits on this)
top_clear = 1.5                 # air gap above relay

# --- hold-down posts (hang from the cover onto the mounting-hole corners) ---
post_d = 6.0                    # inside the 6.9 mm hole courtyard
post_bore_d = peg_d + 0.6       # clears the peg tip
post_bore_h = 3.0               # bore depth (peg sticks 1.8 above the PCB)
post_gap = 0.2                  # play between post foot and PCB top
post_rib_t = 3 * line_w         # 1.2 rib tying each post to its wall corner

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
post_z = pcb_top + post_gap                      # post foot

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
base = base_p.part

# --- post ribs: diagonal from each post into the cover corner; below the
# base rim they are trimmed to the lip footprint so they clear the base ---
rib_len = (outer / 2 - hole_pitch / 2) * 2 ** 0.5
rib_mid = (outer / 2 + hole_pitch / 2) / 2
with BuildPart() as ribs_p:
    for sx in (-1, 1):
        for sy in (-1, 1):
            with Locations(Location((sx * rib_mid, sy * rib_mid, post_z),
                                    (0, 0, sx * sy * 45))):
                Box(rib_len, post_rib_t, cover_top - post_z,
                    align=(Align.CENTER, Align.CENTER, Align.MIN))
    with BuildPart(mode=Mode.INTERSECT):
        with BuildSketch(Plane.XY.offset(post_z)):
            RectangleRounded(lip_outer, lip_outer, inner_r - fit)
        extrude(amount=base_wall_h - post_z)
        with BuildSketch(Plane.XY.offset(base_wall_h)):
            RectangleRounded(outer, outer, corner_r)
        extrude(amount=cover_top - base_wall_h)
ribs = ribs_p.part

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
    # hold-down posts, each tied diagonally into its wall corner by a rib
    post_h = cover_top - lid_t - post_z
    with Locations((0, 0, post_z)):
        with GridLocations(hole_pitch, hole_pitch, 2, 2):
            Cylinder(post_d / 2, post_h,
                     align=(Align.CENTER, Align.CENTER, Align.MIN))
    add(ribs)
    with Locations((0, 0, post_z)):
        with GridLocations(hole_pitch, hole_pitch, 2, 2):
            Cylinder(post_bore_d / 2, post_bore_h, mode=Mode.SUBTRACT,
                     align=(Align.CENTER, Align.CENTER, Align.MIN))
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
