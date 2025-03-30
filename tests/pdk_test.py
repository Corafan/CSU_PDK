"""FabC example."""

from __future__ import annotations

import sys
from functools import partial
from typing import Any

import gdsfactory as gf
from gdsfactory.cross_section import get_cross_sections, strip
from gdsfactory.get_factories import get_cells
from gdsfactory.port import select_ports
from gdsfactory.technology import LayerLevel, LayerStack, LogicalLayer
from gdsfactory.typings import Layer


#定义 LAYER 层 (LayerEnum)
class LAYER(gf.LayerEnum):
    layout = gf.constant(gf.kcl.layout)

    WG: Layer = (10, 1)
    WG_CLAD: Layer = (10, 2)
    WGN: Layer = (34, 0)
    WGN_CLAD: Layer = (36, 0)
    PIN: Layer = (1, 10)

# 定义波导宽度，这些值用于 cross_section 定义，确保所有器件使用统一的参数。
#C-band (1530-1565nm) 用于长距离光通信。
#O-band (1260-1360nm) 用于短距离传输。
WIDTH_SILICON_CBAND = 0.5
WIDTH_SILICON_OBAND = 0.4

WIDTH_NITRIDE_OBAND = 0.9
WIDTH_NITRIDE_CBAND = 1.0

#义一个函数 select_ports_optical，用于选择器件中的端口（ports），并且排除指定的层（layers）。
select_ports_optical = partial(select_ports, layers_excluded=((100, 0),))

# 定义 LayerStack，用于定义每一层的 z 方向位置和厚度。--3D 渲染、光学仿真、EBeam 光刻工艺优化。
def get_layer_stack_fab_c(thickness: float = 350.0) -> LayerStack:
    """Returns generic LayerStack."""
    return LayerStack(
        layers=dict(
            wg=LayerLevel(
                layer=LogicalLayer(layer=LAYER.WG),
                zmin=0.0,
                thickness=0.22,
            ),
            wgn=LayerLevel(
                layer=LogicalLayer(layer=LAYER.WGN),
                zmin=0.22 + 0.1,
                thickness=0.4,
            ),
        )
    )


# avoid registering the function add pins using _underscore
_add_pins = partial(gf.add_pins.add_pins_inside1nm, pin_length=0.5, layer=LAYER.PIN)
# _add_pins 用于自动在器件端口（ports）上添加 PIN 标记。
# partial() 预设 gf.add_pins.add_pins_inside1nm() 的参数：
# pin_length=0.5 → PIN 长度为 0.5 μm。
# layer=LAYER.PIN → PIN 绘制在 LAYER.PIN（GDS 层 1,10）。
#_add_pins 变量名前加 _，表示不注册到 PDK，仅供 @_cell 内部使用。避免 get_cells() 时把 _add_pins 误当成器件。



######################
# cross_sections
######################
bbox_layers = (LAYER.WG,)
bbox_offsets = (3,)

#定义光波导横截面 (Cross Section)
strip_sc = partial(
    strip,
    width=WIDTH_SILICON_CBAND,
    layer=LAYER.WG,
    bbox_layers=bbox_layers,
    bbox_offsets=bbox_offsets,
)
strip_so = partial(
    strip_sc,
    width=WIDTH_SILICON_OBAND,
)

strip_nc = partial(
    strip,
    width=WIDTH_NITRIDE_CBAND,
    layer=LAYER.WGN,
    bbox_layers=bbox_layers,
    bbox_offsets=bbox_offsets,
)
strip_no = partial(
    strip_nc,
    width=WIDTH_NITRIDE_OBAND,
)

strip = strip_sc()
xs_so = strip_so()
xs_nc = strip_nc()
xs_no = strip_no()

######################
# LEAF COMPONENTS with pins
######################

#定义光子器件,@_cell：表示该函数创建的是 GDSII 组件，并支持参数缓存。
# customize the cell decorator for this PDK
_cell = gf.cell(post_process=(_add_pins,), info=dict(pdk="fab_c"))
# 创建 @_cell 装饰器，用于 PDK 内所有器件。(即用@_cell，都会自动添加PIN并且添加 pdk="。。。"命名)
# gf.cell() 定义所有 cell 生成后要执行的 post_process：
# post_process=(_add_pins,) → 所有器件在生成后都会自动添加 PIN。
# info=dict(pdk="fab_c")：
# 在 cell 的 metadata（信息字典）里添加 pdk="fab_c"，方便调试或数据管理。


#straight_sc 生成直波导，使用 "strip_nc" 作为横截面。
@_cell
def straight_sc(cross_section: str = "strip_nc", **kwargs: Any) -> gf.Component:
    return gf.components.straight(cross_section=cross_section, **kwargs)


@_cell
def straight_so(cross_section: str = "strip_so", **kwargs: Any) -> gf.Component:
    return gf.components.straight(cross_section=cross_section, **kwargs)


@_cell
def straight_nc(cross_section: str = "strip_nc", **kwargs: Any) -> gf.Component:
    return gf.components.straight(cross_section=cross_section, **kwargs)


@_cell
def straight_no(cross_section: str = "strip_no", **kwargs: Any) -> gf.Component:
    return gf.components.straight(cross_section=cross_section, **kwargs)


######################
# bends
######################

#bend_euler_sc：生成Euler 曲线弯曲波导，用于减少损耗。
@_cell
def bend_euler_sc(cross_section: str = "strip_sc", **kwargs: Any) -> gf.Component:
    return gf.components.bend_euler(cross_section=cross_section, **kwargs)


@_cell
def bend_euler_so(cross_section: str = "strip_so", **kwargs: Any) -> gf.Component:
    return gf.components.bend_euler(cross_section=cross_section, **kwargs)


@_cell
def bend_euler_nc(cross_section: str = "strip_nc", **kwargs: Any) -> gf.Component:
    return gf.components.bend_euler(cross_section=cross_section, **kwargs)


@_cell
def bend_euler_no(cross_section: str = "strip_no", **kwargs: Any) -> gf.Component:
    return gf.components.bend_euler(cross_section=cross_section, **kwargs)


######################
# MMI
######################

#mmi1x2_sc(多模干涉分束器)：创建 1x2 MMI（1个输入、2个输出），常用于功分（Power Splitter）。
@_cell
def mmi1x2_sc(
    width_mmi: float = 3, cross_section: str = "strip_sc", **kwargs: Any
) -> gf.Component:
    return gf.components.mmi1x2(
        cross_section=cross_section, width_mmi=width_mmi, **kwargs
    )


@_cell
def mmi1x2_so(
    width_mmi: float = 3, cross_section: str = "strip_so", **kwargs: Any
) -> gf.Component:
    return gf.components.mmi1x2(
        cross_section=cross_section, width_mmi=width_mmi, **kwargs
    )


@_cell
def mmi1x2_nc(
    width_mmi: float = 3, cross_section: str = "strip_nc", **kwargs: Any
) -> gf.Component:
    return gf.components.mmi1x2(
        cross_section=cross_section, width_mmi=width_mmi, **kwargs
    )


@_cell
def mmi1x2_no(
    width_mmi: float = 3, cross_section: str = "strip_no", **kwargs: Any
) -> gf.Component:
    return gf.components.mmi1x2(
        cross_section=cross_section, width_mmi=width_mmi, **kwargs
    )


######################
# Grating couplers,_gc_nc：光栅耦合器 (GC)，用于将光纤光耦合到波导中。
######################
_gc_nc = partial(
    gf.components.grating_coupler_elliptical,
    grating_line_width=0.6,
    layer_slab=None,
    cross_section="strip_nc",
)


@_cell
def gc_sc(**kwargs: Any) -> gf.Component:
    return _gc_nc(**kwargs)


######################
# HIERARCHICAL COMPONENTS made of leaf components
######################

mzi_nc = partial(
    gf.components.mzi,
    splitter=mmi1x2_nc,
    straight=straight_nc,
    bend=bend_euler_nc,
    cross_section="strip_nc",
)
mzi_no = partial(
    gf.components.mzi,
    splitter=mmi1x2_no,
    straight=straight_no,
    bend=bend_euler_no,
    cross_section="strip_no",
)

######################
# PDK
######################
# register all cells in this file
# get_cells()：自动注册所有 @_cell 组件。自动获取所有 @_cell 组件，并存入 cells：
# 扫描当前模块 __name__，提取所有 @_cell 定义的组件。
cells = get_cells(sys.modules[__name__])
# 自动获取所有 cross_section：
# 提取 strip_sc、strip_nc 等横截面。
cross_sections = get_cross_sections(sys.modules[__name__])


layer_stack = get_layer_stack_fab_c()

PDK = gf.Pdk(
    name="fab_c_demopdk",
    cells=cells,
    cross_sections=cross_sections,
    layer_stack=layer_stack,
    layers=LAYER,
)

#激活 PDK，让 gdsfactory 识别新 PDK。
PDK.activate()  # ✅ 激活 PDK

if __name__ == "__main__":
    # c2 = mmi1x2_nc()
    # d2 = c2.to_dict()

    # from jsondiff import diff

    # d = diff(d1, d2)
    # c.show()

    c = straight_nc()
    # c = mzi_nc()
    # _add_pins(c)
    # gf.add_pins.add_pins(c)
    # c = mmi1x2_sc()
    # c.pprint_ports()
    c.show()
