#原创:
from __future__ import annotations

import gdsfactory as gf
from gdsfactory.component import Component
from gdsfactory.typings import LayerSpec
from gdsfactory.typings import CrossSectionSpec


@gf.cell
def crossing(
    length: float = 10.0,
    width: float = 2.0,
    layer: LayerSpec = "WG",
    port_type: str | None = None,
    cross_section: CrossSectionSpec = "strip",
) -> Component:
    """生成一个十字crossing.
    Args:
        length:从中心正方形到任意一个端口的距离。
        width:十字crossing的宽度。
        layer:层，（层号，层类型）
        port_type: 电信号端口或光信号端口，electrical或optical.
        （ports按顺时针旋转，o1在左侧）
    """
    layer = gf.get_layer(layer)
    c = gf.Component()

    width_center=width+2   # 确保中心波导略大，防止重叠
    x1 = gf.get_cross_section(cross_section, width=width_center)
    R = c<<gf.components.straight(length=width_center,cross_section=x1)
    R.dcenter = (0, 0)
    # dcenter="""Returns the coordinate center of the bounding box.返回边界框的中心坐标"""

    x2 = gf.get_cross_section(cross_section, width=width)
    r = gf.components.straight(length=length, cross_section=x2)
    r1 = c.add_ref(r)                     #右
    r2 = c.add_ref(r).drotate(90)         #上
    r3 = c.add_ref(r).drotate(180)        #左
    r4 = c.add_ref(r).drotate(270)        #下

    # # 移动四个波导，使它们各自对准中心正方形的四个方向
    r1.dmovex( width_center / 2)   # 右方波导
    r2.dmovey(width_center / 2)    # 上侧波导
    r3.dmovex(- width_center / 2)  # 左方波导
    r4.dmovey(-width_center / 2)   # 下侧波导
    # c.flatten()

    c.add_port(
        f"o1",
        width=width,
        layer=layer,
        orientation=180,
        center=(-length - width_center / 2, 0),
        )
    c.add_port(
        f"o2",
        width=width,
        layer=layer,
        orientation=90,
        center=(0, +length + width_center / 2),
        )
    c.add_port(
        f"o3",
        width=width,
        layer=layer,
        orientation=0,
        center=(+length + width_center / 2, 0),
        )
    c.add_port(
        f"o4",
        width=width,
        layer=layer,
        orientation=270,
        center=(0, -length - width_center / 2),
        )
    return c


if __name__ == "__main__":
    c = crossing()
    c.show()

    # c.pprint_ports()
    # cc = gf.routing.add_fiber_array(component=c)
    # cc.show( )

    component_name = ("crossing")
    # 无时间戳：
    output_gds_path = fr"C:\Windows\System32\CSU_PDK\csufactory\all_output_files\gds\{component_name}.gds"
    # 有时间戳：
    # timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    # output_gds_path = fr"C:\Windows\System32\CSU_PDK\csufactory\all_output_files\gds\{component_name}_{timestamp}.gds"
    c.write_gds(output_gds_path)
    print(f"GDS 文件已保存至: {output_gds_path}")

