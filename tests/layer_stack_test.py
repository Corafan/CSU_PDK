if __name__ == "__main__":
    from csufactory.generic_tech.layer_stack import get_layer_stack
    from csufactory.generic_tech.layer_stack import WAFER_STACK
    from csufactory.generic_tech.layer_stack import get_process
    from csufactory.technology.get_klayout_3d_script import get_klayout_3d_script
    # from gdsfactory.technology import LayerStack
    # # from gdsfactory.technology.layer_stack import get_layer_to_material
    # # from gdsfactory.technology.layer_stack import get_layer_to_thickness


    ls = get_layer_stack(thickness_substrate=50.0)
    script = get_klayout_3d_script(ls)
    print(f"打印3d层栈信息：")
    print(script)
    print("打印层材料：")
    print(ls.get_layer_to_material())
    print("打印层厚度：")
    print(ls.get_layer_to_thickness())

    print("打印层指定信息：")
    for layername, layer in WAFER_STACK.layers.items():
        print(layername, layer.thickness,layer.material,layer.info.get("refractive_index", "none"))

    process_steps = get_process()  # 获取制造步骤
    print("已获取制造步骤")
    print("打印步骤名称：")
    for step in process_steps:
        print(f"Processing step: {step.name}")