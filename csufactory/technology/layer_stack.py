#这个函数是需要修改的！！！（输出的参数）

from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING

from gdsfactory.technology import DerivedLayer,LogicalLayer

if TYPE_CHECKING:
    from gdsfactory.technology import LayerViews

#这部分用来测试该函数
import gdsfactory as gf
from csufactory.generic_tech.layer_stack import get_layer_stack
from csufactory.components.YBranch import Ybranch_1x2

# 生成 KLayout 中 2.5D 视图 的脚本，该脚本可用于 KLayout 的 tech.lyt 文件，方便用户在 KLayout 中查看芯片结构的 3D 渲染效果。
def get_klayout_3d_script(
        self,
        # 指定 KLayout 中的 图层视图，如果未提供，则使用默认的 get_layer_views() 方法获取。
        layer_views: LayerViews | None = None,
        dbu: float | None = 0.001,
) -> str:
    """Returns script for 2.5D view in KLayout.

    You can include this information in your tech.lyt

    Args:
        layer_views: optional layer_views.
        dbu: Optional database unit. Defaults to 1nm.
    """
    from gdsfactory.pdk import get_layer_views

    layers = self.layers or {}  # 获取当前的 LayerStack 层，如果为空则设为空字典
    layer_views = layer_views or get_layer_views()  # 获取 layer_views，如果未提供则获取默认视图

    # Collect etch layers and unetched layers
    # 这部分的意思是，如果一开始定义"SiO2": LayerLevel(layer=DerivedLayer(...)),则它会被加入到刻蚀层，反之，被加入到非刻蚀层（LogicalLayer）

    # DerivedLayer 表示 由多个基础层组合而成的衍生层，如 蚀刻区域（Etched Regions），即表示刻蚀层。
    # etch_layers 存储所有 DerivedLayer 类型的 LayerLevel 名称。
    etch_layers = [
        layer_name
        for layer_name, level in layers.items()
        if isinstance(level.layer, DerivedLayer)
    ]
    # LogicalLayer 代表的是实际制造的 GDS 层，通常表示未蚀刻的材料区域。
    # unetched_layers 存储所有 LogicalLayer 类型的 LayerLevel 名称。
    unetched_layers = [
        layer_name
        for layer_name, level in layers.items()
        if isinstance(level.layer, LogicalLayer)
    ]

    # Define input layers，生成klayout输入层
    # input(layer, datatype) 是 KLayout 中 读取 GDSII 层的语法。
    # layer[0]: GDSII 层号,layer[1]: 数据类型（datatype）。
    out = "\n".join(
        [
            f"{layer_name} = input({level.derived_layer.layer[0]}, {level.derived_layer.layer[1]})"
            for layer_name, level in layers.items()
            if level.derived_layer
        ]
    )
    out += "\n\n"

    # Remove all etched layers from the grown layers
    unetched_layers_dict = defaultdict(list)
    for layer_name in etch_layers:
        level = layers[layer_name]
        if level.derived_layer:
            unetched_layers_dict[level.derived_layer.layer].append(layer_name)
            # 储存被刻蚀层
            if level.derived_layer.layer in unetched_layers:
                # 若本身在非刻蚀层，则从非刻蚀层移除
                unetched_layers.remove(level.derived_layer.layer)

    # Define layers
    out += "\n".join(
        [
            f"{layer_name} = input({level.layer.layer[0]}, {level.layer.layer[1]})"
            for layer_name, level in layers.items()
            if hasattr(level.layer, "layer")
        ]
    )
    out += "\n\n"

    # Define unetched layers
    for layer_name_etched, etching_layers in unetched_layers_dict.items():
        etching_layers_str = " - ".join(etching_layers)
        out += f"unetched_{layer_name_etched} = {layer_name_etched} - {etching_layers_str}\n"

    out += "\n"

    # Define slabs
    for layer_name, level in layers.items():
        if level.derived_layer:
            derived_layer = level.derived_layer.layer
            for i, layer1 in enumerate(derived_layer):
                out += f"slab_{layer1}_{layer_name}_{i} = {layer1} & {layer_name}\n"

    out += "\n"

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

        elif level.derived_layer:
            derived_layer = level.derived_layer.layer
            for i, layer1 in enumerate(derived_layer):
                slab_layer_name = f"slab_{layer1}_{layer_name}_{i}"
                slab_zmin = zmin
                slab_zmax = zmax - level.thickness
                if isinstance(layer1, list | tuple) and len(layer1) == 2:
                    name = f"{slab_layer_name}: {level.material} {layer1[0]}/{layer1[1]}"
                else:
                    name = f"{slab_layer_name}: {level.material}"
                txt = (
                    f"z("
                    f"{slab_layer_name}, "
                    f"zstart: {slab_zmin}, "
                    f"zstop: {slab_zmax}, "
                    f"name: '{name}'"
                )
                if layer_views:
                    txt += ", "
                    if layer1 in layer_views:
                        props = layer_views.get_from_tuple(layer1)
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
                f"name: '{name}'"
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
    c=gf.Component()
    z= c << Ybranch_1x2()
    s =c.to_3d(layer_stack=get_layer_stack(thickness_wg=220e-3)) #取220nm
    s.show()      #生成3d视图
    c.show()      #生成gds视图