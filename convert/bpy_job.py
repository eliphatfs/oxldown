import sys
import json
import traceback

try:
    import bpy

    argv = sys.argv[1:]
    if len(argv) != 3:
        print("python bpy_job.py input_filename fmt output_basename")
        sys.exit(1)

    input = argv[0]
    fmt = argv[1]
    output = argv[2]

    def clear_scene():
        if len(bpy.context.scene.objects.items()) == 0:
            return
        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.select_all(action="SELECT")
        bpy.ops.object.delete()

    clear_scene()

    if fmt == "obj":
        bpy.ops.wm.obj_import(filepath=input)
    elif fmt == "dae":
        bpy.ops.wm.collada_import(filepath=input)
    elif fmt == "abc":
        bpy.ops.wm.alembic_import(filepath=input)
    elif fmt == "blend":
        bpy.ops.wm.open_mainfile(filepath=input)
    elif fmt == "stl":
        bpy.ops.wm.stl_import(filepath=input)
    elif fmt == "ply":
        bpy.ops.wm.ply_import(filepath=input)
    elif fmt.startswith("usd"):
        bpy.ops.wm.usd_import(filepath=input)
    elif fmt == "gltf":
        bpy.ops.import_scene.gltf(filepath=input)
    elif fmt == "glb":
        bpy.ops.import_scene.gltf(filepath=input)
    elif fmt == "fbx":
        bpy.ops.import_scene.fbx(filepath=input)
    else:
        raise Exception("unknown format", fmt)

    bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(
        filepath=output + '.blend',
        check_existing=False,
    )
    if fmt != 'glb':
        bpy.ops.export_scene.gltf(
            filepath=output + '.glb',
            export_apply=True,
            export_attributes=True,
            check_existing=False,
        )
    num_objects = len(bpy.data.objects)
    try:
        bpy.context.view_layer.update()
        bpy.context.view_layer.objects.active = next(iter(bpy.data.objects.values()))
        bpy.context.view_layer.update()
        bpy.ops.object.mode_set(mode="OBJECT")
        fail_set_mode = False
    except Exception:
        traceback.print_exc()
        fail_set_mode = True
    missing_textures = 0
    num_textures = 0
    for img in bpy.data.images:
        if img.type in ('RENDER_RESULT', 'COMPOSITING'):
            continue
        num_textures += 1
        if img.channels == 0:
            missing_textures += 1
    num_animations = len(bpy.data.actions)
    num_armatures = len(bpy.data.armatures)
    try:
        stats_str = bpy.context.scene.statistics(bpy.context.view_layer)
    except Exception as exc:
        traceback.print_exc()
        stats_str = "[Failed to get statistics]"
    meta = dict(
        stats_str=stats_str,
        num_textures=num_textures,
        missing_textures=missing_textures,
        num_animations=num_animations,
        num_armatures=num_armatures,
        num_objects=num_objects,
        fail_set_mode=fail_set_mode
    )
    with open(output + '.json', "w") as fo:
        json.dump(meta, fo)
except Exception:
    print("Unhandled Exception")
    traceback.print_exc()
    sys.exit(1)
