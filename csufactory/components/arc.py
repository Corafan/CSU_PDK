from __future__ import annotations
#启用 Python 类型注解（来自 __future__ 模块）。允许我们在函数签名（参数和返回值）中使用前向引用，即在函数定义时使用尚未完全定义的类型。

from functools import partial
from typing import Literal, overload
#Literal限制参数取值范围，例如 Literal[True] 仅允许 True，Literal["strip", "slab"] 仅允许 "strip" 或 "slab"。
#overload用于函数重载，允许根据参数不同提供多个版本的类型注解（但只执行最后一个实现）。

import gdsfactory as gf
from gdsfactory.component import Component, ComponentAllAngle
from gdsfactory.path import arc
from gdsfactory.snap import snap_to_grid
from gdsfactory.typings import CrossSectionSpec, LayerSpec


#Python 本身不会执行 @overload，只是为了给类型检查器（如 mypy）提供提示。
@overload
def _wg_arc(
    radius: float | None = None,
    angle: float = 90.0,
    npoints: int | None = None,
    layer: LayerSpec | None = None,
    width: float | None = None,
    cross_section: CrossSectionSpec = "strip",
    allow_min_radius_violation: bool = False,
    all_angle: Literal[False] = False,
) -> Component: ...
#如果 all_angle=False，返回 Component（标准组件）

@overload
def _wg_arc(
    radius: float | None = None,
    angle: float = 90.0,
    npoints: int | None = None,
    layer: LayerSpec | None = None,
    width: float | None = None,
    cross_section: CrossSectionSpec = "strip",
    allow_min_radius_violation: bool = False,
    all_angle: Literal[True] = True,
) -> ComponentAllAngle: ...
#如果 all_angle=True，返回 ComponentAllAngle（支持任意角度的组件）。

def _wg_arc(
    radius: float | None = None,
    angle: float = 90.0,
    npoints: int | None = None,
    layer: LayerSpec | None = None,
    width: float | None = None,
    cross_section: CrossSectionSpec = "strip",
    allow_min_radius_violation: bool = False,
    all_angle: bool = False,
) -> Component | ComponentAllAngle:
    #创建一个弯曲的波导组件，返回 Component 或 ComponentAllAngle
    """Returns a radial arc.

    Args:
        radius: in um. Defaults to cross_section_radius.
        angle: angle of arc (degrees).
        npoints: number of points.
        layer: layer to use. Defaults to cross_section.layer.
        width: width to use. Defaults to cross_section.width.
        cross_section: spec (CrossSection, string or dict).
        allow_min_radius_violation: if True allows radius to be smaller than cross_section radius.
        all_angle: if True returns a ComponentAllAngle.

    .. code::

                  o2
                  |
                 /
                /
        o1_____/
    """
    x = gf.get_cross_section(cross_section)
    radius = radius or x.radius
    #如果 radius=None，则使用 cross_section 默认的 x.radius。
    assert radius is not None
    #确保 radius 不为空，否则报错。
    if layer and width:
        x = gf.get_cross_section(
            cross_section, layer=layer or x.layer, width=width or x.width
        )
    elif layer:
        x = gf.get_cross_section(cross_section, layer=layer or x.layer)
    elif width:
        x = gf.get_cross_section(cross_section, width=width or x.width)

    #调用arc函数,生成弧形路径,下一步是用cross section挤出路径,生成波导
    p = arc(radius=radius, angle=angle, npoints=npoints)
    c = p.extrude(x, all_angle=all_angle)

    #信息储存:
    c.info["length"] = float(snap_to_grid(p.length()))
    #波导的起点和终点在 X 方向上的差值,abs绝对值保证dy为正
    c.info["dy"] = float(abs(p.points[0][0] - p.points[-1][0]))
    c.info["radius"] = float(radius)
    c.info["width"] = width or x.width

    #确定波导的上下包围框（bounding box）信息。
    #当 angle 为 180°、-180° 或 -90° 时：top = None，表示不添加顶部边界（直线或向下弯曲，不需要额外的顶部边界）,允许其他模块靠近。否则：top = 0，表示需要添加顶部边界。
    #当 angle = -90° 时：bottom = 0，表示需要添加底部边界,防止超出设计区。否则：bottom = None，表示不添加底部边界。
    top = None if int(angle) in {180, -180, -90} else 0
    bottom = 0 if int(angle) in {-90} else None
    x.add_bbox(c, top=top, bottom=bottom)  # type: ignore
    #添加边界框,用于物理约束（保证组件不会超出设计区域）。对齐优化（帮助 KLayout 识别组件的正确边界）。DRC 规则检查（防止制造时的错误）。

    #是否允许波导半径小于最小允许半径,false(默认是false)表示不允许小于最小弯曲半径
    if not allow_min_radius_violation:
        x.validate_radius(radius)
        #检查 radius 是否比 x 的最小允许半径 x.min_radius 小.如果 radius < x.min_radius，抛出错误，避免产生无法制造的设计。

    #给 Component（波导）添加额外的路由信息
    c.add_route_info(
        cross_section=x,
        length=c.info["length"],
        n_bend_90=abs(angle / 90.0),
        min_bend_radius=radius,
    )
    return c


#@gf.cell 只缓存 90° / 180° 组件。@gf.vcell 允许任意角度，但缓存优化较弱。
@gf.cell
def wg_arc(
    radius: float | None = None,
    angle: float = 90.0,
    npoints: int | None = None,
    layer: gf.typings.LayerSpec | None = None,
    width: float | None = None,
    cross_section: CrossSectionSpec = "strip",
    allow_min_radius_violation: bool = False,
) -> Component:
    """Returns a radial arc.

    Args:
        radius: in um. Defaults to cross_section_radius.
        angle: angle of arc (degrees).
        npoints: number of points.
        layer: layer to use. Defaults to cross_section.layer.
        width: width to use. Defaults to cross_section.width.
        cross_section: spec (CrossSection, string or dict).
        allow_min_radius_violation: if True allows radius to be smaller than cross_section radius.
    """
    if angle not in {90, 180}:
        gf.logger.warning(
            f"wg_acr angle should be 90 or 180. Got {angle}. Use wg_arc_all_angle instead."
        )
    return _wg_arc(
        radius=radius,
        angle=angle,
        npoints=npoints,
        layer=layer,
        width=width,
        cross_section=cross_section,
        allow_min_radius_violation=allow_min_radius_violation,
        all_angle=False,
    )


@gf.vcell
def wg_arc_all_angle(
    radius: float | None = None,
    angle: float = 90.0,
    npoints: int | None = None,
    layer: gf.typings.LayerSpec | None = None,
    width: float | None = None,
    cross_section: CrossSectionSpec = "strip",
    allow_min_radius_violation: bool = False,
) -> ComponentAllAngle:
    """Returns a radial arc.

    Args:
        radius: in um. Defaults to cross_section_radius.
        angle: angle of arc (degrees).
        npoints: number of points.
        layer: layer to use. Defaults to cross_section.layer.
        width: width to use. Defaults to cross_section.width.
        cross_section: spec (CrossSection, string or dict).
        allow_min_radius_violation: if True allows radius to be smaller than cross_section radius.
    """
    return _wg_arc(
        radius=radius,
        angle=angle,
        npoints=npoints,
        layer=layer,
        width=width,
        cross_section=cross_section,
        allow_min_radius_violation=allow_min_radius_violation,
        all_angle=True,
    )


wg_arc180 = partial(wg_arc, angle=180)
#即 wg_arc180 是 wg_arc(angle=180, ...) 的固定版本，直接调用时默认 angle=180。


if __name__ == "__main__":
    # c = gf.Component()
    # r = c << wg_arc(angle=45,radius=5)
    # bend = arc_all_angle(radius=5)
    # print(type(bend))
    # r.dmirror()

    c = wg_arc(width=0.5,angle=90,radius=5)
    component_name = "arc"
    # 无时间戳：
    output_gds_path = fr"C:\Windows\System32\CSU_PDK\csufactory\all_output_files\gds\{component_name}.gds"
    # 有时间戳：
    # timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    # output_gds_path = fr"D:\ProgramData\anaconda3\Lib\site-packages\gdsfactory\all_output_files\gds\{component_name}_{timestamp}.gds"
    c.write_gds(output_gds_path)
    print(f"GDS 文件已保存至: {output_gds_path}")
    c.show()
