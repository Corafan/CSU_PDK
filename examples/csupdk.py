from __future__ import annotations
import sys
from functools import partial
from typing import Any
import gdsfactory as gf
import csufactory as cf

from csufactory.generic_tech.layer_map import CSULAYER as LAYER
from csufactory.components.generate_Para.component_layer_stack import Si_zp45_LayerStack
from gdsfactory.technology import LayerViews

from gdsfactory.cross_section import get_cross_sections, strip
from gdsfactory.get_factories import get_cells


# 定义波导宽度，这些值用于 cross_section 定义，确保所有器件使用统一的参数。
#C-band (1530-1565nm) 用于长距离光通信。
#O-band (1260-1360nm) 用于短距离传输。
WIDTH_SILICON_CBAND = 0.5
WIDTH_SILICON_OBAND = 0.4

WIDTH_NITRIDE_OBAND = 0.9
WIDTH_NITRIDE_CBAND = 1.0

_add_pins = partial(gf.add_pins.add_pins_inside1nm, pin_length=0.5, layer=LAYER.PORT)
# _add_pins 用于自动在器件端口（ports）上添加 PIN 标记。
# partial() 预设 gf.add_pins.add_pins_inside1nm() 的参数：
# pin_length=0.5 → PIN 长度为 0.5 μm。
# layer=LAYER.PIN → PIN 绘制在 LAYER.PIN（GDS 层 1,10）。
#_add_pins 变量名前加 _，表示不注册到 PDK，仅供 @_cell 内部使用。避免 get_cells() 时把 _add_pins 误当成器件。

######################
# cross_sections,定义横截面
######################

#定义光波导横截面 (Cross Section)
strip_sc = partial(
    strip,
    width=WIDTH_SILICON_CBAND,
    layer=LAYER.WG,
)
strip_so = partial(
    strip_sc,
    width=WIDTH_SILICON_OBAND,
)

strip = strip_sc()
xs_so = strip_so()

######################
# LEAF COMPONENTS with pins
######################

#定义光子器件,@_cell：表示该函数创建的是 GDSII 组件，并支持参数缓存。
# customize the cell decorator for this PDK
_cell = gf.cell(post_process=(_add_pins,), info=dict(pdk="csupdk"))
# 创建 @_cell 装饰器，用于 PDK 内所有器件。(即用@_cell，都会自动添加PIN并且添加 pdk="csupdk"命名)
# gf.cell() 定义所有 cell 生成后要执行的 post_process：
# post_process=(_add_pins,) → 所有器件在生成后都会自动添加 PIN。
# info=dict(pdk="csupdk")：
# 在 cell 的 metadata（信息字典）里添加 pdk="fab_c"，方便调试或数据管理。

@_cell
def arc(cross_section: str = "strip_sc", **kwargs: Any) -> gf.Component:
    return cf.components.wg_arc(cross_section=cross_section, **kwargs)

@_cell
def awg(cross_section: str = "strip_sc", **kwargs: Any) -> gf.Component:
    return cf.components.awg(cross_section=cross_section, **kwargs)

# @_cell
# def fpr(cross_section: str = "strip_sc", **kwargs: Any) -> gf.Component:
#     return cf.components.free_propagation_region(cross_section=cross_section, **kwargs)

@_cell
def coupler(cross_section: str = "strip_sc", **kwargs: Any) -> gf.Component:
    return cf.components.coupler(cross_section=cross_section, **kwargs)

@_cell
def crossing(cross_section: str = "strip_so",**kwargs: Any) -> gf.Component:
    return cf.components.crossing(cross_section=cross_section, **kwargs)

@_cell
def grating(cross_section: str = "strip_sc", **kwargs: Any) -> gf.Component:
    return cf.components.grating(cross_section=cross_section, **kwargs)

@_cell
def mmi(cross_section: str = "strip_so", **kwargs: Any) -> gf.Component:
    return cf.components.mmi(cross_section=cross_section, **kwargs)

@_cell
def ring_coupler(cross_section: str = "strip_so", **kwargs: Any) -> gf.Component:
    return cf.components.ring_coupler(cross_section=cross_section, **kwargs)

@_cell
def ring_resonator(cross_section: str = "strip_so", **kwargs: Any) -> gf.Component:
    return cf.components.ring_resonator(cross_section=cross_section, **kwargs)

@_cell
def s_bend(cross_section: str = "strip_so", **kwargs: Any) -> gf.Component:
    return cf.components.Sbend(cross_section=cross_section, **kwargs)

@_cell
def star_coupler(cross_section: str = "strip_so", **kwargs: Any) -> gf.Component:
    return cf.components.star_coupler(cross_section=cross_section, **kwargs)

@_cell
def y_branch(cross_section: str = "strip_sc", **kwargs: Any) -> gf.Component:
    return cf.components.ybranch(cross_section=cross_section, **kwargs)


######################
# PDK
######################
# register all cells in this file
cells = get_cells(sys.modules[__name__])
cross_sections = get_cross_sections(sys.modules[__name__])
#将LayerViews改为自己的路径
LAYER_VIEWS = LayerViews(filepath="C:/Windows/System32/CSU_PDK/csufactory/generic_tech/layer_views.yaml")

#若出现报错可以尝试：
# # 直接在注册 PDK 前定义横截面
# cross_sections = {
#     "strip_sc": strip_sc,  # 这里添加你的横截面
#     "strip_so": strip_so,
# }
# # 其他 cross_sections 的设置可以在这里继续定义

# 注册 PDK
PDK = gf.Pdk(
    name="csupdk",
    version="1.0.0",
    layers=LAYER,
    layer_stack=Si_zp45_LayerStack,
    layer_views= LAYER_VIEWS,
    cross_sections=cross_sections,
)

# 设为默认 PDK
PDK.activate()

if __name__ == "__main__":
    from csufactory.components.awg import free_propagation_region
    c =awg(
    inputs= 1,
    arms= 9,                                   #阵列波导数量
    outputs= 1,
    free_propagation_region_input_function=partial(free_propagation_region, width1=2, width2=20.0),
    free_propagation_region_output_function=partial(free_propagation_region, width1=2, width2=20.0),
    fpr_spacing= 50,                            #输入/输出FPR的间距
    arm_spacing= 1,                             #阵列波导间距
    )
    c=coupler()
    c =y_branch()
    c=mmi()
    c=star_coupler()
    c=arc()
    c=ring_coupler()
    c=ring_resonator()
    c=s_bend()
    c=crossing()
    c=grating()
    c.show()