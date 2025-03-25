#这个函数是需要修改的！！！（输出的参数）

from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING

from gdsfactory.technology import DerivedLayer,LogicalLayer

if TYPE_CHECKING:
    from gdsfactory.technology import LayerViews



# 生成 KLayout 中 2.5D 视图 的脚本，该脚本可用于 KLayout 的 tech.lyt 文件，方便用户在 KLayout 中查看芯片结构的 3D 渲染效果。
def get_klayout_3d_script(
        self,
        layer_views: LayerViews | None = None,
        dbu: float | None = 0.001,
) -> str:
    """Returns script for 2.5D view in KLayout.

    You can include this information in your tech.lyt

    Args:
        self:形参，layer_stack。若未指定，则是默认的get_layer_stack()方法获取.
        #可以指定，如先定义一个ls=WAFER_STACK,再使用get_klayout_3d_script(ls)
        layer_views: optional layer_views. 指定KLayout中的图层视图，如果未提供，则使用默认的 get_layer_views()方法获取。
        #可以用layer_views= LayerViews(filepath="C:\Windows\System32\CSU_PDK\csufactory\generic_tech\layer_views.yaml")指定
        dbu: Optional database unit. Defaults to 1nm.
    """
    from gdsfactory.pdk import get_layer_views

    layers = self.layers or {}  #self.layers获取LayerStack里的层信息，如果None，则赋值为空字典{}。
    layer_views = layer_views or get_layer_views()  # 获取layer_views，如果未提供则获取get_layer_views()默认视图

    # 获取刻蚀层etch_layers和非刻蚀层unetch_layers
    # 如果一开始定义"SiO2": LayerLevel(layer=DerivedLayer(...)),则它会被加入到刻蚀层，反之，被加入到非刻蚀层（LogicalLayer）
    # DerivedLayer(刻蚀层，即etched_layer) 表示 由多个基础层组合而成的衍生层，如 蚀刻区域（Etched Regions），即表示刻蚀层。
    # etch_layers存储所有DerivedLayer类型的LayerLevel名称。
    etch_layers = [
        layer_name
        for layer_name, level in layers.items()   #对于layers中的所有项目，遍历layer_name和level
        if isinstance(level.layer, DerivedLayer)  #layer的level是不是DerivedLayer
    ]
    # LogicalLayer(非刻蚀层，即unetched_layer) 代表的是实际制造的 GDS 层，通常表示未蚀刻的材料区域。
    # unetched_layers 存储所有 LogicalLayer 类型的 LayerLevel 名称。
    unetched_layers = [
        layer_name
        for layer_name, level in layers.items()    #对于layers中的所有项目，遍历layer_name和level
        if isinstance(level.layer, LogicalLayer)   #layer的level是不是LogicalLayer
    ]
    # 解释：
    # 若：
    #     layers = {
    #     "SiO2": LayerLevel(layer=DerivedLayer(...)),
    #     "Si": LayerLevel(layer=LogicalLayer(...)),
    # }
    # 则（生成两个包含字符串的集合）
    # etch_layers = ["SiO2"]
    # unetched_layers = ["Si"]


    # 生成klayout输入层(input) ------input(layer, datatype)
    # layer[0]: GDSII 层号 , layer[1]: 数据类型（datatype）。
    # print("DerivedLayer(刻蚀层)：")
    out = "\n".join(
        [
            f"input: {layer_name} = ({level.derived_layer.layer[0]}, {level.derived_layer.layer[1]})"
            for layer_name, level in layers.items()
            if level.derived_layer
        ]
    )
    out += "\n\n"

    #Remove all etched layers from the grown layers，移除被蚀刻的层：
    unetched_layers_dict = defaultdict(list)    #记录被蚀刻层
    for layer_name in etch_layers:              #在etch_layers这个集合中的所有layer_name（所有DerivedLayer）
        level = layers[layer_name]
        if level.derived_layer:
            unetched_layers_dict[level.derived_layer.layer].append(layer_name)
            # 储存被刻蚀层
            if level.derived_layer.layer in unetched_layers:
                # 若本身在非刻蚀层，则从非刻蚀层移除
                unetched_layers.remove(level.derived_layer.layer)

    out += "\n".join(
        [
            f" input: {layer_name} =({level.layer.layer[0]}, {level.layer.layer[1]})"
            for layer_name, level in layers.items()
            if hasattr(level.layer, "layer")
        ]
    )
    out += "\n\n"

    #貌似没有参考意义：
    # # 构建 layer_map 反向字典
    # from csufactory.generic_tech.layer_map import CSULAYER
    # layer_map_dict = {v: k for k, v in CSULAYER.__dict__.items() if isinstance(v, tuple)}
    # # 定义unetched层
    # for layer_name_etched, etching_layers in unetched_layers_dict.items():
    #     etching_layers_str = " - ".join(etching_layers)
    #     layer_name_prefix = layer_map_dict.get(layer_name_etched, f"Unknown{layer_name_etched}")
    #     out += f"unetched_{layer_name_prefix}{layer_name_etched} = {layer_name_prefix}{layer_name_etched} - {etching_layers_str}\n"
    #     #但这里输出的{layer_name_etched}是（10，0）？？？
    # out += "\n"

    # # Define slabs，暂时用不到
    # for layer_name, level in layers.items():
    #     if level.derived_layer:
    #         derived_layer = level.derived_layer.layer
    #         for i, layer1 in enumerate(derived_layer):
    #             out += f"slab_{layer1}_{layer_name}_{i} = {layer1} & {layer_name}\n"
    #
    # out += "\n"

    #定义 z 坐标
    for layer_name, level in layers.items():
        layer = level.layer
        zmin = level.zmin
        zmax = zmin + level.thickness
        if dbu:
            rnd_pl = len(str(dbu).split(".")[-1])
            zmin = round(zmin, rnd_pl)
            zmax = round(zmax, rnd_pl)

        if layer is None:
            continue

        # 这部分是slab的：
        # elif level.derived_layer:
        #     derived_layer = level.derived_layer.layer
        #     for i, layer1 in enumerate(derived_layer):
        #         slab_layer_name = f"slab_{layer1}_{layer_name}_{i}"
        #         slab_zmin = zmin
        #         slab_zmax = zmax - level.thickness
        #         if isinstance(layer1, list | tuple) and len(layer1) == 2:
        #             name = f"{slab_layer_name}: {level.material} {layer1[0]}/{layer1[1]}"
        #         else:
        #             name = f"{slab_layer_name}: {level.material}"
        #         txt = (
        #             f"z("
        #             f"{slab_layer_name}, "
        #             f"zstart: {slab_zmin}, "
        #             f"zstop: {slab_zmax}, "
        #             f"name: '{name}'"
        #         )
        #         if layer_views:
        #             txt += ", "
        #             if layer1 in layer_views:
        #                 props = layer_views.get_from_tuple(layer1)
        #                 if hasattr(props, "color"):
        #                     if props.color.fill == props.color.frame:
        #                         txt += f"color: {props.color.fill}"
        #                     else:
        #                         txt += (
        #                             f"fill: {props.color.fill}, "
        #                             f"frame: {props.color.frame}"
        #                         )
        #         txt += ")"
        #         out += f"{txt}\n"

        #定义 z()
        elif layer_name in unetched_layers:
            layer_tuple = layer.layer
            if isinstance(layer_tuple, list | tuple) and len(layer_tuple) == 2:
                name = f"{layer_name}: {level.material} {layer_tuple[0]}/{layer_tuple[1]}"
            else:
                name = f"{layer_name}: {level.material}"
            txt = (
                f"z("
                f"{layer_name}, "
                f"zstart: {zmin}, "
                f"zstop: {zmax}, "
                f"name: '{name}'"  #这里是把上面一部分的name代入进来了
            )
            if layer_views:
                txt += ", "
                props = layer_views.get_from_tuple(layer_tuple)
                if hasattr(props, "color"):
                    if props.color.fill == props.color.frame:
                        txt += f"color: {props.color.fill}"
                    else:
                        txt += (
                            f"fill: {props.color.fill}, "
                            f"frame: {props.color.frame}"
                        )

            txt += ")"
            out += f"{txt}\n"

    return out


#test_example:
if __name__ == "__main__":
    #这部分用来测试该函数
    from csufactory.components.generate_Para.component_layer_stack import Si_zp45_LayerStack
    from csufactory.generic_tech.layer_stack import get_layer_stack
    from gdsfactory.technology import LayerViews

    # print("打印layer_stack.py中默认的layer_stack，layer_views默认：")
    # script = get_klayout_3d_script(get_layer_stack())
    # print(script)


    # print("打印Si_zp45_LayerStack中的，layer_views默认：")
    #
    # script = get_klayout_3d_script(Si_zp45_LayerStack)
    # print(script)

    print("打印Si_zp45_LayerStack中的,layer_views指定：")
    script = get_klayout_3d_script(
        Si_zp45_LayerStack, #self
        layer_views= LayerViews(filepath="C:\Windows\System32\CSU_PDK\csufactory\generic_tech\layer_views.yaml")
    )
    print(script)




# #这个函数是需要修改的！！！（输出的参数）,原版:
#
# from __future__ import annotations
#
# from collections import defaultdict
# from typing import TYPE_CHECKING
#
# from gdsfactory.technology import DerivedLayer,LogicalLayer
#
# if TYPE_CHECKING:
#     from gdsfactory.technology import LayerViews
#
#
#
# # 生成 KLayout 中 2.5D 视图 的脚本，该脚本可用于 KLayout 的 tech.lyt 文件，方便用户在 KLayout 中查看芯片结构的 3D 渲染效果。
# def get_klayout_3d_script(
#         self,
#         # 指定 KLayout 中的 图层视图，如果未提供，则使用默认的 get_layer_views() 方法获取。
#         layer_views: LayerViews | None = None,
#         dbu: float | None = 0.001,
# ) -> str:
#     """Returns script for 2.5D view in KLayout.
#
#     You can include this information in your tech.lyt
#
#     Args:
#         layer_views: optional layer_views.
#         dbu: Optional database unit. Defaults to 1nm.
#     """
#     from gdsfactory.pdk import get_layer_views
#
#     layers = self.layers or {}  # 获取当前的 LayerStack 层，如果为空则设为空字典
#     layer_views = layer_views or get_layer_views()  # 获取 layer_views，如果未提供则获取默认视图
#
#     # Collect etch layers and unetched layers
#     # 这部分的意思是，如果一开始定义"SiO2": LayerLevel(layer=DerivedLayer(...)),则它会被加入到刻蚀层，反之，被加入到非刻蚀层（LogicalLayer）
#
#     # DerivedLayer 表示 由多个基础层组合而成的衍生层，如 蚀刻区域（Etched Regions），即表示刻蚀层。
#     # etch_layers 存储所有 DerivedLayer 类型的 LayerLevel 名称。
#     etch_layers = [
#         layer_name
#         for layer_name, level in layers.items()
#         if isinstance(level.layer, DerivedLayer)
#     ]
#     # LogicalLayer 代表的是实际制造的 GDS 层，通常表示未蚀刻的材料区域。
#     # unetched_layers 存储所有 LogicalLayer 类型的 LayerLevel 名称。
#     unetched_layers = [
#         layer_name
#         for layer_name, level in layers.items()
#         if isinstance(level.layer, LogicalLayer)
#     ]
#
#     # Define input layers，生成klayout输入层
#     # input(layer, datatype) 是 KLayout 中 读取 GDSII 层的语法。
#     # layer[0]: GDSII 层号,layer[1]: 数据类型（datatype）。
#     out = "\n".join(
#         [
#             f"{layer_name} = input({level.derived_layer.layer[0]}, {level.derived_layer.layer[1]})"
#             for layer_name, level in layers.items()
#             if level.derived_layer
#         ]
#     )
#     out += "\n\n"
#
#     # Remove all etched layers from the grown layers
#     unetched_layers_dict = defaultdict(list)
#     for layer_name in etch_layers:
#         level = layers[layer_name]
#         if level.derived_layer:
#             unetched_layers_dict[level.derived_layer.layer].append(layer_name)
#             # 储存被刻蚀层
#             if level.derived_layer.layer in unetched_layers:
#                 # 若本身在非刻蚀层，则从非刻蚀层移除
#                 unetched_layers.remove(level.derived_layer.layer)
#
#     # Define layers
#     out += "\n".join(
#         [
#             f"{layer_name} = input({level.layer.layer[0]}, {level.layer.layer[1]})"
#             for layer_name, level in layers.items()
#             if hasattr(level.layer, "layer")
#         ]
#     )
#     out += "\n\n"
#
#     # Define unetched layers
#     for layer_name_etched, etching_layers in unetched_layers_dict.items():
#         etching_layers_str = " - ".join(etching_layers)
#         out += f"unetched_{layer_name_etched} = {layer_name_etched} - {etching_layers_str}\n"
#
#     out += "\n"
#
#     # Define slabs
#     for layer_name, level in layers.items():
#         if level.derived_layer:
#             derived_layer = level.derived_layer.layer
#             for i, layer1 in enumerate(derived_layer):
#                 out += f"slab_{layer1}_{layer_name}_{i} = {layer1} & {layer_name}\n"
#
#     out += "\n"
#
#     for layer_name, level in layers.items():
#         layer = level.layer
#         zmin = level.zmin
#         zmax = zmin + level.thickness
#         if dbu:
#             rnd_pl = len(str(dbu).split(".")[-1])
#             zmin = round(zmin, rnd_pl)
#             zmax = round(zmax, rnd_pl)
#
#         if layer is None:
#             continue
#
#         elif level.derived_layer:
#             derived_layer = level.derived_layer.layer
#             for i, layer1 in enumerate(derived_layer):
#                 slab_layer_name = f"slab_{layer1}_{layer_name}_{i}"
#                 slab_zmin = zmin
#                 slab_zmax = zmax - level.thickness
#                 if isinstance(layer1, list | tuple) and len(layer1) == 2:
#                     name = f"{slab_layer_name}: {level.material} {layer1[0]}/{layer1[1]}"
#                 else:
#                     name = f"{slab_layer_name}: {level.material}"
#                 txt = (
#                     f"z("
#                     f"{slab_layer_name}, "
#                     f"zstart: {slab_zmin}, "
#                     f"zstop: {slab_zmax}, "
#                     f"name: '{name}'"
#                 )
#                 if layer_views:
#                     txt += ", "
#                     if layer1 in layer_views:
#                         props = layer_views.get_from_tuple(layer1)
#                         if hasattr(props, "color"):
#                             if props.color.fill == props.color.frame:
#                                 txt += f"color: {props.color.fill}"
#                             else:
#                                 txt += (
#                                     f"fill: {props.color.fill}, "
#                                     f"frame: {props.color.frame}"
#                                 )
#                 txt += ")"
#                 out += f"{txt}\n"
#
#         elif layer_name in unetched_layers:
#             layer_tuple = layer.layer
#             if isinstance(layer_tuple, list | tuple) and len(layer_tuple) == 2:
#                 name = f"{layer_name}: {level.material} {layer_tuple[0]}/{layer_tuple[1]}"
#             else:
#                 name = f"{layer_name}: {level.material}"
#             txt = (
#                 f"z("
#                 f"{layer_name}, "
#                 f"zstart: {zmin}, "
#                 f"zstop: {zmax}, "
#                 f"name: '{name}'"
#             )
#             if layer_views:
#                 txt += ", "
#                 props = layer_views.get_from_tuple(layer_tuple)
#                 if hasattr(props, "color"):
#                     if props.color.fill == props.color.frame:
#                         txt += f"color: {props.color.fill}"
#                     else:
#                         txt += (
#                             f"fill: {props.color.fill}, "
#                             f"frame: {props.color.frame}"
#                         )
#
#             txt += ")"
#             out += f"{txt}\n"
#
#     return out
#
#
# #test_example:
# if __name__ == "__main__":
#     #这部分用来测试该函数
#     from csufactory.components.generate_Para.component_layer_stack import Si_zp45_LayerStack
#     from csufactory.generic_tech.layer_stack import get_layer_stack
#     from gdsfactory.technology import LayerViews
#
#     # print("打印layer_stack.py中默认的layer_stack，layer_views默认：")
#     # script = get_klayout_3d_script(get_layer_stack())
#     # print(script)
#
#
#     # print("打印Si_zp45_LayerStack中的，layer_views默认：")
#     #
#     # script = get_klayout_3d_script(Si_zp45_LayerStack)
#     # print(script)
#
#     print("打印Si_zp45_LayerStack中的,layer_views指定：")
#     script = get_klayout_3d_script(
#         Si_zp45_LayerStack, #self
#         layer_views= LayerViews(filepath="C:\Windows\System32\CSU_PDK\csufactory\generic_tech\layer_views.yaml")
#     )
#     print(script)