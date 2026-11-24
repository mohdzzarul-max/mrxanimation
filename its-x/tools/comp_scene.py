"""2D/2.5D compositing in Blender: painted layers at different depths (real parallax), a drawn
character image sequence, a keyframed camera, optional glow. Flat colours stay exact
(Standard view transform, emission shading, no lighting).

  xvfb-run -a blender -b -noaudio --python its-x/tools/comp_scene.py -- CONFIG.json

CONFIG.json (paths relative to the config file):
{
  "frames": 120, "fps": 24, "preview": 1.0,          # preview 0.5 = half-res test render
  "layers": [                                          # far -> near; each fills the frame at its depth
    {"name": "bg",  "image": "bg.png",  "depth": 30, "margin": 1.15},
    {"name": "fg",  "image": "fg.png",  "depth": 6,  "margin": 1.3}
  ],
  "character": {"frames_dir": "char", "first": 1, "depth": 12, "height": 0.75, "x": 0.15, "y": -0.05},
  "camera": [[1, 0, 0, 50], [120, 0.4, 0.1, 55]],      # [frame, x, y, focal mm] in scene units, ease in/out
  "glow": {"threshold": 0.85, "size": 7},              # or null
  "out": "render/frame_####.png"
}
Character frames: PNG with alpha named 0001.png, 0002.png ... (one per output frame; holds are
already resolved by xsheet.py). The character plane keeps the drawings' aspect ratio.
"""
import bpy, json, math, os, sys

cfg_path = os.path.abspath(sys.argv[sys.argv.index('--') + 1]); base = os.path.dirname(cfg_path)
C = json.load(open(cfg_path)); P = lambda p: os.path.join(base, p)
scn = bpy.context.scene
for o in list(bpy.data.objects): bpy.data.objects.remove(o)
scn.frame_start, scn.frame_end = 1, C['frames']; scn.render.fps = C.get('fps', 24)
scn.render.resolution_x, scn.render.resolution_y = 1920, 1080
scn.render.resolution_percentage = round(100 * C.get('preview', 1.0))
scn.render.engine = 'BLENDER_EEVEE_NEXT'
scn.view_settings.view_transform = 'Standard'; scn.view_settings.look = 'None'
scn.render.film_transparent = False
scn.world = bpy.data.worlds.new('W'); scn.world.color = (0.02, 0.015, 0.05)

cam_data = bpy.data.cameras.new('Cam'); cam_data.sensor_fit = 'HORIZONTAL'; cam_data.sensor_width = 36
cam = bpy.data.objects.new('Cam', cam_data); scn.collection.objects.link(cam); scn.camera = cam
lens0 = C['camera'][0][3]

def frame_size(depth, lens):  # visible width/height of the frame at this depth
    w = depth * cam_data.sensor_width / lens; return w, w * 1080 / 1920

def flat_material(name, img, seq=False, n=1):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
    tex = nt.nodes.new('ShaderNodeTexImage'); tex.image = img; tex.interpolation = 'Linear'
    if seq:
        tex.image_user.frame_duration = n; tex.image_user.frame_start = 1; tex.image_user.use_auto_refresh = True
    em = nt.nodes.new('ShaderNodeEmission'); tr = nt.nodes.new('ShaderNodeBsdfTransparent')
    mix = nt.nodes.new('ShaderNodeMixShader'); out = nt.nodes.new('ShaderNodeOutputMaterial')
    nt.links.new(tex.outputs['Color'], em.inputs['Color'])
    nt.links.new(tex.outputs['Alpha'], mix.inputs['Fac'])
    nt.links.new(tr.outputs[0], mix.inputs[1]); nt.links.new(em.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs['Surface'])
    m.surface_render_method = 'BLENDED'
    return m

def size_of(img):  # Blender loads pixels lazily; force it so .size is valid
    if not img.size[0]: img.reload(); _ = img.pixels[0]
    return img.size[0], img.size[1]

def plane(name, w, h, x, y, z, mat):
    bpy.ops.mesh.primitive_plane_add(size=1, location=(x, y, -z))
    ob = bpy.context.active_object; ob.name = name; ob.scale = (w, h, 1); ob.data.materials.append(mat)
    return ob

for L in C['layers']:
    img = bpy.data.images.load(P(L['image'])); img.alpha_mode = 'STRAIGHT'
    fw, fh = frame_size(L['depth'], lens0); mg = L.get('margin', 1.15)
    iw, ih = size_of(img); ia = iw / ih; w, h = (fw * mg, fw * mg / ia) if ia < fw / fh else (fh * mg * ia, fh * mg)
    plane(L['name'], w, h, 0, 0, L['depth'], flat_material(L['name'], img))

ch = C.get('character')
if ch:
    d = P(ch['frames_dir']); files = sorted(f for f in os.listdir(d) if f.endswith('.png'))
    img = bpy.data.images.load(os.path.join(d, files[0])); iw, ih = size_of(img)
    img.source = 'SEQUENCE'; img.alpha_mode = 'STRAIGHT'
    fw, fh = frame_size(ch['depth'], lens0); h = fh * ch['height']; w = h * iw / ih
    ob = plane('character', w, h, ch.get('x', 0) * fw, ch.get('y', 0) * fh, ch['depth'],
               flat_material('character', img, True, len(files)))
    # keep the character between layers by depth order; draw order follows depth with BLENDED

for f, x, y, lens in C['camera']:
    cam.location = (x, y, 0); cam_data.lens = lens
    cam.keyframe_insert('location', frame=f); cam_data.keyframe_insert('lens', frame=f)

if C.get('glow'):
    scn.use_nodes = True; nt = scn.node_tree; nt.nodes.clear()
    rl = nt.nodes.new('CompositorNodeRLayers'); gl = nt.nodes.new('CompositorNodeGlare'); co = nt.nodes.new('CompositorNodeComposite')
    gl.glare_type = 'FOG_GLOW'; gl.quality = 'HIGH'
    try: gl.threshold = C['glow']['threshold']; gl.size = C['glow']['size']
    except AttributeError:  # 4.5 moved these to sockets
        gl.inputs['Threshold'].default_value = C['glow']['threshold']; gl.inputs['Size'].default_value = C['glow']['size'] / 9
    nt.links.new(rl.outputs['Image'], gl.inputs['Image']); nt.links.new(gl.outputs['Image'], co.inputs['Image'])

scn.render.image_settings.file_format = 'PNG'; scn.render.filepath = P(C['out'])
bpy.ops.render.render(animation=True)
print('COMP_OK', C['frames'], 'frames ->', P(C['out']))
