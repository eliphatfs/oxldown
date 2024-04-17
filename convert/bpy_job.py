import sys

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
    with open(output + '.success', "w") as fo:
        pass
except Exception:
    sys.exit(1)
