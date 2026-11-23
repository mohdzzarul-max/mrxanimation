"""Environments and props. All signage / labels are fictional."""
import math, os, random
import bpy
from mathutils import Vector
from lib import (mat, emission_mat, decal_mat, sphere, cyl, box, rbox, torus, plane, poly_prism, area, point, spot,
                 world_color, empty, TEX, curve_tube, obj_key, set_mat, text_obj)

T = lambda n: os.path.join(TEX, n)
GOLD = (0.95, 0.68, 0.25)


def glass_mat(name, tint=(1, 1, 1), rough=0.02):
    m = mat(name, tint, rough=rough)
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Transmission Weight"].default_value = 1.0
    p.inputs["IOR"].default_value = 1.45
    return m


def liquid_mat(name, color):
    m = mat(name, color, rough=0.05)
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Transmission Weight"].default_value = 0.9
    p.inputs["IOR"].default_value = 1.33
    return m


# ===================================================================== props
def perfume_bottle(name, loc=(0, 0, 0), s=1.0, liquid=(0.9, 0.45, 0.08), cap="gold", label="bottle_label.png",
                   style="premium"):
    """Faceted premium bottle (MAHKOTA) or simple round dupe bottle. Returns root empty; z=0 is bottom."""
    root = empty(name, loc)
    root.empty_display_size = 0.05
    if style == "premium":
        b = box(f"{name}_glass", (0, 0, 0.055 * s), (0.08 * s, 0.045 * s, 0.11 * s), m=glass_mat("glass"),
                bevel=0.012 * s, seg=1)
        lq = box(f"{name}_liq", (0, 0, 0.05 * s), (0.068 * s, 0.035 * s, 0.085 * s), m=liquid_mat(f"liq_{name}", liquid),
                 bevel=0.008 * s, seg=1)
        neck = cyl(f"{name}_neck", (0, 0, 0.117 * s), 0.012 * s, 0.016 * s, m=mat("gold", GOLD, rough=0.18, metal=1))
        cp = box(f"{name}_cap", (0, 0, 0.142 * s), (0.05 * s, 0.05 * s, 0.035 * s),
                 m=mat("capblack", (0.01, 0.01, 0.012), rough=0.08, coat=1) if cap != "gold" else
                 mat("gold", GOLD, rough=0.18, metal=1), bevel=0.006 * s, seg=2)
        lab = plane(f"{name}_label", (0, -0.0226 * s, 0.055 * s), (0.06 * s, 0.06 * s),
                    m=decal_mat("lab_" + label, T(label), emit_strength=0.3), rot=(math.pi / 2, 0, 0))
        parts = [b, lq, neck, cp, lab]
    else:
        b = cyl(f"{name}_glass", (0, 0, 0.05 * s), 0.035 * s, 0.10 * s, m=glass_mat("glass"))
        lq = cyl(f"{name}_liq", (0, 0, 0.042 * s), 0.03 * s, 0.075 * s, m=liquid_mat(f"liq_{name}", liquid))
        cp = cyl(f"{name}_cap", (0, 0, 0.118 * s), 0.02 * s, 0.035 * s, m=mat("silver", (0.8, 0.8, 0.82), rough=0.2,
                                                                                metal=1))
        lab = plane(f"{name}_label", (0, -0.0352 * s, 0.05 * s), (0.045 * s, 0.045 * s),
                    m=decal_mat("lab_" + label, T(label)), rot=(math.pi / 2, 0, 0))
        parts = [b, lq, cp, lab]
    for p in parts:
        p.parent = root
        p.location = Vector(p.location)
    root["cap"] = parts[3].name if style == "premium" else parts[2].name
    return root


def perfume_box(name, loc=(0, 0, 0), s=1.0, open_lid=False):
    root = empty(name, loc)
    blk = mat("boxblack", (0.012, 0.012, 0.014), rough=0.35, coat=0.4)
    b = box(f"{name}_body", (0, 0, 0.09 * s), (0.11 * s, 0.07 * s, 0.18 * s), m=blk, bevel=0.003)
    front = plane(f"{name}_front", (0, -0.0352 * s, 0.09 * s), (0.105 * s, 0.175 * s),
                  m=decal_mat("boxfront", T("box_front.png"), emit_strength=0.15, rough=0.3), rot=(math.pi / 2, 0, 0))
    trim = mat("gold", GOLD, rough=0.18, metal=1)
    t1 = box(f"{name}_trim", (0, 0, 0.181 * s), (0.112 * s, 0.072 * s, 0.006 * s), m=trim)
    lid = box(f"{name}_lid", (0, 0, 0.19 * s), (0.114 * s, 0.074 * s, 0.014 * s), m=blk, bevel=0.002)
    for p in (b, front, t1, lid):
        p.parent = root
    root["lid"] = lid.name
    return root


def money_stack(name, loc=(0, 0, 0), n=6, s=1.0, m=None):
    root = empty(name, loc)
    note = m or mat("note", (0.55, 0.35, 0.62), rough=0.6)
    band = mat("noteband", (0.85, 0.8, 0.7), rough=0.6)
    for i in range(n):
        p = box(f"{name}_n{i}", (random.uniform(-0.004, 0.004), random.uniform(-0.004, 0.004), i * 0.0035 * s),
                (0.15 * s, 0.07 * s, 0.003 * s), m=note, rot=(0, 0, random.uniform(-0.06, 0.06)))
        p.parent = root
    bd = box(f"{name}_band", (0, 0, n * 0.0018 * s), (0.03 * s, 0.072 * s, n * 0.0037 * s + 0.002), m=band)
    bd.parent = root
    return root


def note_single(name, loc=(0, 0, 0), s=1.0, rot=(0, 0, 0)):
    o = box(name, loc, (0.15 * s, 0.07 * s, 0.002 * s), m=mat("note", (0.55, 0.35, 0.62), rough=0.6), rot=rot)
    return o


def phone(name, loc=(0, 0, 0), rot=(0, 0, 0)):
    root = empty(name, loc)
    root.rotation_euler = rot
    body = box(f"{name}_body", (0, 0, 0), (0.08, 0.16, 0.009), m=mat("phoneblk", (0.01, 0.01, 0.012), rough=0.2,
                                                                     coat=1), bevel=0.008, seg=3)
    off = plane(f"{name}_off", (0, 0, 0.0051), (0.072, 0.15), m=decal_mat("phoneoff", T("phone_off.png"),
                                                                          emit_strength=0.4, rough=0.05))
    on = plane(f"{name}_on", (0, 0, 0.0052), (0.072, 0.15), m=decal_mat("phoneon", T("phone_screen.png"),
                                                                        emit_strength=4.0, rough=0.05))
    for p in (body, off, on):
        p.parent = root
    on.hide_render = True
    on.hide_viewport = True
    root["on"] = on.name
    root["off"] = off.name
    return root


def drum(name, loc, label="drum_label_1.png", color=(0.08, 0.22, 0.6), s=1.0, rot_z=0.0):
    root = empty(name, loc)
    root.rotation_euler = (0, 0, rot_z)
    plastic = mat(f"drum_{color}", color, rough=0.45, coat=0.2, bump=0.05)
    b = cyl(f"{name}_body", (0, 0, 0.45 * s), 0.29 * s, 0.9 * s, m=plastic, bevel=0.02, verts=48)
    for z in (0.28, 0.62):
        r = torus(f"{name}_rib{z}", (0, 0, z * s), 0.292 * s, 0.012 * s, m=plastic)
        r.parent = root
    lid = cyl(f"{name}_bung", (0.12 * s, 0, 0.905 * s), 0.035 * s, 0.025 * s, m=plastic)
    lab = curved_label(f"{name}_label", 0.296 * s, 0.30 * s, 1.3, T(label), z=0.45 * s)
    for p in (b, lid, lab):
        p.parent = root
    return root


def curved_label(name, r, h, arc, img, z):
    """Cylindrical label patch facing -Y."""
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=h, vertices=64, end_fill_type="NOTHING", location=(0, 0, z))
    o = bpy.context.object
    o.name = name
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(o.data)
    kill = [v for v in bm.verts if math.atan2(v.co.x, -v.co.y) > arc / 2 + 1e-3 or math.atan2(v.co.x, -v.co.y) < -arc / 2 - 1e-3]
    bmesh.ops.delete(bm, geom=kill, context="VERTS")
    uv = bm.loops.layers.uv.verify()
    for f in bm.faces:
        for l in f.loops:
            a = math.atan2(l.vert.co.x, -l.vert.co.y)
            l[uv].uv = (a / arc + 0.5, (l.vert.co.z / h) + 0.5)
    bm.to_mesh(o.data)
    bm.free()
    m = mat("lbl_" + os.path.basename(img), (1, 1, 1), rough=0.5, img=img)
    # use UV coordinates explicitly
    nt = m.node_tree
    tn = [n for n in nt.nodes if n.type == "TEX_IMAGE"][0]
    uvn = nt.nodes.new("ShaderNodeUVMap")
    nt.links.new(uvn.outputs[0], tn.inputs[0])
    set_mat(o, m)
    for p in o.data.polygons:
        p.use_smooth = True
    return o


def bokeh_field(n, center, spread, colors, size=(0.02, 0.06), seed=3, strength=6):
    rnd = random.Random(seed)
    objs = []
    for i in range(n):
        c = rnd.choice(colors)
        o = sphere(f"bokeh{i}", (center[0] + rnd.uniform(-spread[0], spread[0]),
                                 center[1] + rnd.uniform(-spread[1], spread[1]),
                                 center[2] + rnd.uniform(-spread[2], spread[2])),
                   rnd.uniform(*size), m=emission_mat(f"bk_{c}", c, strength), seg=12, rings=6)
        o.visible_shadow = False
        objs.append(o)
    return objs


# ===================================================================== BOOTH
def booth():
    """Luxury perfume booth in a mall. Uncle stands at (0, 0.55) behind counter (top z=0.52).
    Customer spot: (0, -0.45). Returns dict of handles."""
    world_color((0.012, 0.01, 0.012), 1)
    H = {}
    floor_m = mat("mall_floor", (0.05, 0.045, 0.045), rough=0.18, coat=0.5)
    plane("floor", (0, 0, 0), (30, 30), m=floor_m)
    wall_m = mat("booth_wall", (0.025, 0.022, 0.022), rough=0.5, bump=0.1)
    box("backwall", (0, 1.25, 1.4), (3.2, 0.1, 2.8), m=wall_m)
    led = emission_mat("led_gold", (1.0, 0.62, 0.22), 12)
    for x in (-1.5, -0.75, 0.75, 1.5):
        box(f"ledstrip{x}", (x, 1.19, 1.3), (0.02, 0.02, 2.2), m=led)
    # shelves with bottles
    shelf_m = mat("shelf", (0.02, 0.02, 0.022), rough=0.15, coat=1)
    rnd = random.Random(7)
    liquids = [(0.95, 0.5, 0.1), (0.9, 0.25, 0.3), (0.95, 0.85, 0.6), (0.5, 0.12, 0.05), (0.85, 0.65, 0.2)]
    for side in (-1, 1):
        for k, z in enumerate((0.75, 1.15, 1.55)):
            box(f"shelf{side}{k}", (side * 1.12, 1.1, z), (0.6, 0.22, 0.025), m=shelf_m)
            box(f"shelfled{side}{k}", (side * 1.12, 1.0, z - 0.016), (0.58, 0.01, 0.006), m=led)
            for j in range(4):
                x = side * 1.12 + (j - 1.5) * 0.13
                b = perfume_bottle(f"shelfbottle{side}{k}{j}", (x, 1.08, z + 0.013), s=rnd.uniform(0.8, 1.1),
                                   liquid=rnd.choice(liquids), cap=rnd.choice(["gold", "black"]))
    # counter (black lacquer with gold edge)
    box("counter", (0, 0.25, 0.26), (1.7, 0.5, 0.52), m=mat("counter", (0.008, 0.008, 0.01), rough=0.08, coat=1),
        bevel=0.01)
    box("counter_top", (0, 0.25, 0.53), (1.74, 0.54, 0.025), m=mat("countertop", (0.02, 0.018, 0.018), rough=0.05,
                                                                    coat=1), bevel=0.005)
    box("counter_trim", (0, -0.015, 0.515), (1.74, 0.012, 0.012), m=led)
    box("counter_trim2", (0, -0.015, 0.03), (1.74, 0.012, 0.012), m=led)
    plane("counter_logo", (0, -0.0055, 0.28), (0.4, 0.4), m=decal_mat("x_gold", T("x_gold.png"), emit_strength=0.6),
          rot=(math.pi / 2, 0, 0))
    # display: hero bottles on counter on little plinths
    for i, x in enumerate((-0.62, -0.42, 0.42, 0.62)):
        cyl(f"plinth{i}", (x, 0.25, 0.575), 0.07, 0.07, m=shelf_m, bevel=0.005)
        perfume_bottle(f"counterbottle{i}", (x, 0.25, 0.61), s=1.0, liquid=liquids[i % 5])
    for i, x in enumerate((-0.25, 0.25)):
        perfume_box(f"counterbox{i}", (x, 0.12, 0.54), s=0.9)
    # sign
    plane("sign", (0, 1.19, 2.05), (1.6, 0.4), m=decal_mat("booth_sign", T("booth_sign.png"), emit_strength=2.0),
          rot=(math.pi / 2, 0, 0))
    plane("banner", (-1.15, 0.2, 0.6), (0.45, 0.9), m=decal_mat("promo_banner", T("promo_banner.png"),
                                                               emit_strength=0.8), rot=(math.pi / 2, 0, 0.35))
    box("banner_stand", (-1.15, 0.22, 0.02), (0.3, 0.12, 0.04), m=shelf_m)
    # mall background bokeh (warm + cool) behind camera side and far sides
    bokeh_field(40, (0, -6, 2.0), (6, 1.5, 1.5), [(1.0, 0.6, 0.25), (0.4, 0.55, 1.0), (1.0, 0.8, 0.5)], seed=5)
    bokeh_field(30, (-4.5, 0, 1.6), (0.5, 4, 1.2), [(1.0, 0.6, 0.25), (0.4, 0.55, 1.0)], seed=6)
    bokeh_field(30, (4.5, 0, 1.6), (0.5, 4, 1.2), [(1.0, 0.6, 0.25), (0.4, 0.55, 1.0)], seed=8)
    # lighting: warm key, gold top, cool rim
    H["key"] = area("booth_key", (1.2, -1.6, 2.2), (0, 0.3, 0.9), energy=260, color=(1.0, 0.78, 0.55), size=1.2)
    H["top"] = area("booth_top", (0, 0.4, 2.6), (0, 0.4, 0), energy=220, color=(1.0, 0.7, 0.4), size=1.5)
    H["rim"] = area("booth_rim", (-1.4, 1.0, 1.8), (0, 0, 0.9), energy=180, color=(0.45, 0.6, 1.0), size=0.8)
    H["fill"] = area("booth_fill", (-1.5, -1.8, 1.0), (0, 0, 0.8), energy=50, color=(0.5, 0.6, 0.9), size=2.0)
    return H


# ===================================================================== BEDROOM
def bedroom():
    """MR X's bedroom. Desk on +X wall (desk top z=0.42, front edge y=-0.1, chair at (0.9,-0.45)).
    Bed on -X side (top z=0.36). Window on back wall (y=1.6)."""
    world_color((0.01, 0.012, 0.02), 1)
    H = {}
    wood = mat("wood", (0.22, 0.12, 0.06), rough=0.35, bump=0.15, bump_scale=8, coat=0.2)
    # planks via wave texture
    nt = wood.node_tree
    wv = nt.nodes.new("ShaderNodeTexWave")
    wv.inputs["Scale"].default_value = 3.0
    wv.inputs["Distortion"].default_value = 6
    wv.inputs["Detail"].default_value = 3
    cr = nt.nodes.new("ShaderNodeValToRGB")
    cr.color_ramp.elements[0].color = (0.12, 0.065, 0.035, 1)
    cr.color_ramp.elements[1].color = (0.26, 0.15, 0.08, 1)
    nt.links.new(wv.outputs["Fac"], cr.inputs[0])
    nt.links.new(cr.outputs[0], nt.nodes["Principled BSDF"].inputs["Base Color"])
    plane("floor", (0, 0, 0), (8, 8), m=wood)
    wall = mat("bedwall", (0.11, 0.13, 0.18), rough=0.8, bump=0.08, bump_scale=30)
    box("wall_back", (0, 1.65, 1.5), (5, 0.1, 3), m=wall)
    box("wall_left", (-2.0, 0, 1.5), (0.1, 5, 3), m=wall)
    box("wall_right", (2.0, 0, 1.5), (0.1, 5, 3), m=wall)
    box("skirting", (0, 1.59, 0.04), (4, 0.02, 0.08), m=mat("skirt", (0.05, 0.05, 0.06), rough=0.4))
    # window with night city glow
    box("window_frame", (-0.6, 1.6, 1.45), (1.0, 0.06, 0.9), m=mat("wframe", (0.05, 0.05, 0.06), rough=0.3),
        bevel=0.01)
    plane("window_sky", (-0.6, 1.58, 1.45), (0.9, 0.8), m=emission_mat("nightsky", (0.12, 0.22, 0.55), 1.6),
          rot=(math.pi / 2, 0, 0))
    box("window_bar", (-0.6, 1.57, 1.45), (0.02, 0.02, 0.8), m=mat("wframe", (0.05, 0.05, 0.06)))
    bokeh_field(18, (-0.6, 1.62, 1.3), (0.4, 0.001, 0.25), [(1.0, 0.75, 0.35), (0.6, 0.8, 1.0)], size=(0.006, 0.014),
                seed=9, strength=10)
    # curtains
    cur = mat("curtain", (0.08, 0.12, 0.25), rough=0.9, sheen=0.3)
    for x in (-1.2, 0.0):
        rbox(f"curtain{x}", (x, 1.52, 1.45), (0.22, 0.08, 1.2), m=cur, round_=0.4)
    # bed
    bedm = mat("bedframe", (0.06, 0.04, 0.03), rough=0.4)
    box("bed_frame", (-1.35, 0.4, 0.13), (1.1, 1.9, 0.26), m=bedm, bevel=0.02)
    rbox("mattress", (-1.35, 0.4, 0.31), (1.05, 1.85, 0.14), m=mat("sheet", (0.75, 0.75, 0.8), rough=0.85), round_=0.3)
    rbox("blanket", (-1.35, 0.1, 0.38), (1.08, 1.2, 0.07), m=mat("blanket", (0.08, 0.1, 0.22), rough=0.9, sheen=0.4),
         round_=0.4)
    rbox("pillow", (-1.35, 1.1, 0.42), (0.6, 0.3, 0.12), m=mat("pillow", (0.85, 0.85, 0.88), rough=0.9), round_=0.6)
    box("headboard", (-1.35, 1.36, 0.45), (1.1, 0.06, 0.6), m=bedm, bevel=0.02)
    # desk + chair
    dm = mat("desk", (0.03, 0.03, 0.035), rough=0.3, coat=0.3)
    box("desk_top", (0.95, 0.2, 0.42), (1.3, 0.6, 0.04), m=dm, bevel=0.005)
    for x in (0.35, 1.55):
        box(f"desk_leg{x}", (x, 0.2, 0.2), (0.04, 0.55, 0.4), m=dm)
    rbox("chair_seat", (0.9, -0.42, 0.22), (0.4, 0.38, 0.06), m=mat("chair", (0.5, 0.12, 0.08), rough=0.6), round_=0.4)
    cyl("chair_post", (0.9, -0.42, 0.1), 0.025, 0.2, m=mat("chrome", (0.8, 0.8, 0.8), rough=0.15, metal=1))
    # desk lamp (warm practical)
    lampm = mat("lamp", (0.9, 0.55, 0.1), rough=0.3, coat=0.5)
    cyl("lamp_base", (1.45, 0.35, 0.45), 0.07, 0.02, m=lampm)
    curve_tube("lamp_arm", [(1.45, 0.35, 0.45), (1.48, 0.38, 0.7), (1.3, 0.2, 0.78)], 0.012, m=lampm)
    cyl("lamp_shade", (1.27, 0.17, 0.75), 0.07, 0.09, m=lampm, rot=(0.5, -0.4, 0))
    sphere("lamp_bulb", (1.25, 0.15, 0.71), 0.03, m=emission_mat("bulb", (1.0, 0.75, 0.45), 30))
    H["lamp"] = point("lamp_light", (1.22, 0.12, 0.68), energy=25, color=(1.0, 0.7, 0.4), radius=0.05)
    # shelf above desk with perfume collection (old dupe bottle hero at x=0.7)
    box("shelf", (0.95, 0.42, 0.95), (1.1, 0.2, 0.025), m=dm)
    rnd = random.Random(2)
    for j, x in enumerate((0.5, 0.62, 0.86, 1.0, 1.15, 1.3)):
        perfume_bottle(f"collect{j}", (x, 0.42, 0.963), s=rnd.uniform(0.8, 1.0),
                       liquid=rnd.choice([(0.9, 0.4, 0.1), (0.3, 0.5, 0.9), (0.9, 0.3, 0.4)]),
                       style=rnd.choice(["premium", "round"]), cap=rnd.choice(["gold", "black"]))
    H["dupe"] = perfume_bottle("dupe_bottle", (0.74, 0.42, 0.963), s=1.05, liquid=(0.92, 0.48, 0.1), style="round",
                               label="dupe_label.png")
    plane("poster", (0.95, 1.59, 1.35), (0.5, 0.7), m=decal_mat("poster", T("poster.png"), emit_strength=0.2),
          rot=(math.pi / 2, 0, 0))
    rbox("rug", (-0.2, -0.3, 0.005), (1.6, 1.1, 0.01), m=mat("rug", (0.35, 0.2, 0.12), rough=0.95, bump=0.3,
                                                             bump_scale=100), round_=0.3)
    # lighting: blue moonlight from window, warm lamp, soft fill
    H["moon"] = area("moon", (-0.6, 2.4, 1.6), (0, -0.3, 0.5), energy=220, color=(0.45, 0.6, 1.0), size=1.0)
    H["warm"] = area("warm_key", (1.6, -1.2, 1.6), (0.6, 0.0, 0.6), energy=110, color=(1.0, 0.72, 0.45), size=1.0)
    H["fill"] = area("bed_fill", (-1.0, -2.0, 1.5), (0, 0, 0.6), energy=45, color=(0.55, 0.65, 1.0), size=2.5)
    H["top"] = area("bed_top", (0, 0, 2.8), (0, 0, 0), energy=60, color=(0.9, 0.85, 0.8), size=2.0)
    return H


# ===================================================================== STOREROOM
def storeroom():
    """Hidden storeroom behind the booth. Door at (-1.4, -1.0) on left wall... table at (0, 0.3) top z=0.5.
    Drums lined along the back (y ~ 1.0..1.5)."""
    world_color((0.005, 0.007, 0.012), 1)
    H = {}
    conc = mat("concrete", (0.12, 0.12, 0.13), rough=0.85, bump=0.4, bump_scale=20)
    plane("floor", (0, 0, 0), (10, 10), m=mat("concfloor", (0.08, 0.08, 0.085), rough=0.6, bump=0.3, bump_scale=15))
    box("wall_back", (0, 2.0, 1.5), (6, 0.1, 3), m=conc)
    box("wall_left", (-1.8, 0, 1.5), (0.1, 5, 3), m=conc)
    box("wall_right", (2.2, 0, 1.5), (0.1, 5, 3), m=conc)
    # door opening in left wall with warm light spilling in
    door = box("door", (-1.74, -0.6, 0.75), (0.05, 0.62, 1.45), m=mat("door", (0.06, 0.05, 0.045), rough=0.5),
               bevel=0.01)
    hinge = empty("door_hinge", (-1.74, -0.91, 0.75))
    door.parent = hinge
    door.matrix_parent_inverse = hinge.matrix_world.inverted()
    H["door"] = hinge
    H["doorlight"] = area("doorway_light", (-2.4, -0.6, 1.0), (0, -0.3, 0.4), energy=0, color=(1.0, 0.7, 0.4), size=0.7)
    # drums
    drums = []
    specs = [((-0.9, 1.45), "drum_label_1.png", (0.08, 0.22, 0.6)), ((-0.25, 1.5), "drum_label_2.png",
                                                                       (0.85, 0.85, 0.82)),
             ((0.4, 1.45), "drum_label_3.png", (0.08, 0.22, 0.6)), ((1.05, 1.5), "drum_label_1.png", (0.85, 0.85, 0.82)),
             ((1.6, 1.3), "drum_label_2.png", (0.08, 0.22, 0.6)), ((-0.6, 0.95), "drum_label_3.png", (0.85, 0.85, 0.82)),
             ((1.35, 0.8), "drum_label_1.png", (0.08, 0.22, 0.6))]
    for i, ((x, y), lab, col) in enumerate(specs):
        drums.append(drum(f"drum{i}", (x, y, 0), label=lab, color=col, rot_z=random.Random(i).uniform(-0.25, 0.25)))
    H["drums"] = drums
    # shelves with cartons / packaging
    shelf = mat("metalshelf", (0.25, 0.27, 0.3), rough=0.4, metal=0.8)
    card = mat("carton", (0.42, 0.28, 0.15), rough=0.85, bump=0.2, bump_scale=40)
    for k, z in enumerate((0.35, 0.85, 1.35, 1.85)):
        box(f"rack{k}", (2.0, 0.6, z), (0.35, 1.4, 0.03), m=shelf)
        for j in range(4):
            rbox(f"carton{k}{j}", (2.0, 0.05 + j * 0.36, z + 0.15), (0.3, 0.32, 0.27), m=card, round_=0.05, sub=1)
    for x in (1.84, 2.16):
        for y in (-0.08, 1.28):
            box(f"rackpost{x}{y}", (x, y, 1.0), (0.025, 0.025, 2.0), m=shelf)
    # work table
    tbl = mat("table", (0.18, 0.12, 0.07), rough=0.5, bump=0.2, bump_scale=10)
    box("table_top", (0.0, 0.25, 0.5), (1.3, 0.6, 0.05), m=tbl, bevel=0.005)
    for x in (-0.58, 0.58):
        for y in (0.0, 0.5):
            box(f"tleg{x}{y}", (x, y, 0.24), (0.05, 0.05, 0.48), m=tbl)
    # production setup on the table: empty bottles, boxes, a small decanting can + funnel
    for j in range(5):
        perfume_bottle(f"empty{j}", (0.25 + j * 0.08, 0.42, 0.525), s=1.0, liquid=(0.95, 0.95, 0.95), cap="gold")
    for j in range(3):
        perfume_box(f"flatbox{j}", (-0.45 + j * 0.13, 0.45, 0.525), s=0.9)
    can = cyl("decant_can", (-0.1, 0.45, 0.6), 0.07, 0.16, m=mat("can", (0.6, 0.62, 0.65), rough=0.3, metal=0.9))
    cone = cyl("funnel", (0.6, 0.15, 0.62), 0.04, 0.06, m=mat("funnelm", (0.2, 0.25, 0.3), rough=0.3, metal=0.5))
    # hanging bulb (warm practical) + cool window light
    curve_tube("lamp_wire", [(0.0, 0.25, 3.0), (0.0, 0.25, 1.6)], 0.004, m=mat("wire", (0.01, 0.01, 0.01)))
    cyl("lampshade", (0, 0.25, 1.55), 0.16, 0.08, m=mat("shade", (0.15, 0.17, 0.16), rough=0.4, metal=0.7),
        verts=32)
    sphere("store_bulb", (0, 0.25, 1.48), 0.04, m=emission_mat("bulb", (1.0, 0.75, 0.45), 30))
    H["bulb"] = point("bulb_light", (0, 0.25, 1.42), energy=60, color=(1.0, 0.66, 0.35), radius=0.06)
    H["cool"] = area("store_cool", (1.5, -2.2, 2.6), (0, 0.6, 0.6), energy=120, color=(0.35, 0.5, 1.0), size=1.2)
    H["rim"] = area("store_rim", (-1.0, 2.2, 2.0), (0.2, 0.3, 0.9), energy=120, color=(0.4, 0.55, 1.0), size=1.0)
    H["drumlight"] = area("drum_light", (0.3, 0.2, 2.4), (0.3, 1.4, 0.5), energy=90, color=(1.0, 0.75, 0.45),
                          size=1.0)
    return H


# ===================================================================== RUNWAY (fantasy)
def runway():
    world_color((0.006, 0.004, 0.01), 1)
    H = {}
    plane("rw_floor", (0, 6, 0), (2.0, 20), m=mat("rw_floor", (0.01, 0.01, 0.012), rough=0.06, coat=1))
    plane("rw_ground", (0, 6, -0.01), (40, 40), m=mat("rw_ground", (0.02, 0.015, 0.02), rough=0.6))
    edge = emission_mat("rw_edge", (1.0, 0.7, 0.3), 10)
    for x in (-1.0, 1.0):
        box(f"rw_edge{x}", (x, 6, 0.01), (0.03, 20, 0.02), m=edge)
    # glowing backdrop with big X
    plane("rw_back", (0, 14, 2.5), (8, 5), m=mat("rw_backm", (0.02, 0.015, 0.02), rough=0.5), rot=(math.pi / 2, 0, 0))
    plane("rw_x", (0, 13.9, 2.4), (3.2, 3.2), m=decal_mat("x_gold_glow", T("x_gold.png"), emit_strength=6.0),
          rot=(math.pi / 2, 0, 0))
    # crowd silhouettes on both sides with phone flashes
    crowd = mat("crowd", (0.01, 0.01, 0.012), rough=0.8)
    rnd = random.Random(4)
    flashes = []
    for side in (-1, 1):
        for row in range(2):
            for i in range(14):
                x = side * (1.5 + row * 0.6 + rnd.uniform(-0.1, 0.1))
                y = -1 + i * 0.9 + rnd.uniform(-0.2, 0.2)
                h = rnd.uniform(0.9, 1.2)
                sphere(f"cr_head{side}{row}{i}", (x, y, h + 0.15), 0.17, m=crowd, seg=16, rings=8)
                rbox(f"cr_body{side}{row}{i}", (x, y, h / 2), (0.4, 0.3, h), m=crowd, round_=0.4, sub=1)
                if rnd.random() < 0.45:
                    f = sphere(f"flash{side}{row}{i}", (x - side * 0.2, y, h + 0.25), 0.03,
                               m=emission_mat("flash", (1, 1, 1), 60), seg=8, rings=4)
                    f.visible_shadow = False
                    flashes.append(f)
    H["flashes"] = flashes
    # fake volumetric beams (additive cones)
    beam = bpy.data.materials.new("beam")
    beam.use_nodes = True
    nt = beam.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs[0].default_value = (1.0, 0.85, 0.6, 1)
    em.inputs[1].default_value = 0.05
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    ad = nt.nodes.new("ShaderNodeAddShader")
    nt.links.new(em.outputs[0], ad.inputs[0])
    nt.links.new(tr.outputs[0], ad.inputs[1])
    nt.links.new(ad.outputs[0], out.inputs[0])
    for i, (x, y) in enumerate(((-0.9, 1.5), (0.9, 1.5), (-0.9, 4), (0.9, 4))):
        bpy.ops.mesh.primitive_cone_add(radius1=0.6, radius2=0.03, depth=4.0, location=(x * 0.5, y, 2.0))
        c = bpy.context.object
        c.name = f"beam{i}"
        c.rotation_euler = (0, -x * 0.12, 0)
        set_mat(c, beam)
        c.visible_shadow = False
    H["spot1"] = spot("rw_spot1", (-1.2, -0.5, 3.2), (0, 1.0, 0.6), energy=900, color=(1.0, 0.85, 0.6), angle=28)
    H["spot2"] = spot("rw_spot2", (1.2, -0.5, 3.2), (0, 1.0, 0.6), energy=900, color=(1.0, 0.8, 0.5), angle=28)
    H["rim"] = area("rw_rim", (0, 4, 2.0), (0, 0.5, 0.8), energy=300, color=(0.5, 0.6, 1.0), size=1.0)
    bokeh_field(60, (0, 6, 2.5), (5, 8, 1.5), [(1.0, 0.75, 0.3), (1.0, 0.55, 0.2)], size=(0.01, 0.03), seed=11,
                strength=15)
    return H


# ===================================================================== VOID (graphic shots)
def void(color=(0.0, 0.0, 0.0)):
    world_color(color, 1)
    return {}
