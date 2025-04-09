#原创
from __future__ import annotations

import gdsfactory as gf
from gdsfactory.component import Component
from gdsfactory.typings import ComponentSpec,LayerSpec


@gf.cell
def ring_resonator(
    gap: float = 0.3,
    radius: float = 5.0,
    width: float = 1.5,
    layer: LayerSpec = "WG",
    cross_section: ComponentSpec = "strip",
) -> Component:
    r"""生成环形谐振器
    Args:
        gap: 环形和直波导之间的间隙。
        radius: 环形外环的半径。
        width: 直波导（y方向）和环形的宽度。
        layer:层类型（层号，层类型）,可以改变环形的层类型,一般无需修改。
        cross_section:横截面类型，一般无需修改。
    .. code::
             ------------
            /           \
           |             |
            \           /
             \         /
           ---=========--- gap
        o1    length_x   o2
    """
    c = gf.Component()
    width_wg = width
    length_wg = 3 * radius
    x1 = gf.get_cross_section(cross_section, width=width_wg)
    wg_bottom = c << gf.components.straight(length=length_wg, cross_section=x1)
    wg_bottom.dcenter = (0, 0)
    gap_=-gap-radius-width/2
    wg_bottom.movey(gap_)

    circle_outer=  gf.components.circle(radius=radius,layer=layer)
    circle_inner=  gf.components.circle(radius=radius-width,layer=layer)
    ring= gf.boolean(circle_outer, circle_inner, operation="xor", layer=layer)
    c << ring


    #输入端口
    c.add_port(f"o1", port=wg_bottom.ports["o1"])
    #输出端口
    c.add_port(f"o2",port=wg_bottom.ports["o2"])
    c.flatten()
    return c

if __name__ == "__main__":
    c = ring_resonator()
    c.show()
    component_name = ("ring_resonator")

    # 无时间戳：
    output_gds_path = fr"C:\Windows\System32\CSU_PDK\csufactory\all_output_files\gds\{component_name}.gds"
    # 有时间戳：
    # timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    # output_gds_path = fr"C:\Windows\System32\CSU_PDK\csufactory\all_output_files\gds\{component_name}_{timestamp}.gds"
    c.write_gds(output_gds_path)
    print(f"GDS 文件已保存至: {output_gds_path}")