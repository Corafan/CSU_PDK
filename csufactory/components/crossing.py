from __future__ import annotations

import gdsfactory as gf
from gdsfactory.component import Component
from gdsfactory.typings import LayerSpec


@gf.cell
def crossing(
    length: float = 10.0,
    width: float = 2.0,
    layer: LayerSpec = "WG",
    port_type: str | None = None,
) -> Component:
    """Returns a cross from two rectangles of length and width.

    Args:
        length: float half of Length of the cross from one end to the other.(从中心正方形到端口的距离）
        width: float Width of the arms of the cross.
        layer: layer for geometry.
        port_type: None, optical, electrical.
        （ports按顺时针旋转，o1在左侧）
    """
    layer = gf.get_layer(layer)
    c = gf.Component()

    width_center=width+2   # 确保中心波导略大，防止重叠
    R = c<<gf.components.rectangle(size=(width_center, width_center), layer=layer)
    R.dcenter = (0, 0)
    # dcenter="""Returns the coordinate center of the bounding box.返回边界框的中心坐标"""

    r = gf.components.rectangle(size=(width, length), layer=layer)
    r1 = c.add_ref(r)                     #上
    r2 = c.add_ref(r).drotate(90)         #左
    r3 = c.add_ref(r).drotate(180)        #下
    r4 = c.add_ref(r).drotate(270)        #右

    # 移动四个波导，使它们各自对准中心正方形的四个方向
    r1.dmovex(-width / 2)  # 上方波导
    r2.dmovey(-width / 2)  # 左侧波导
    r3.dmovex(width / 2)   # 下方波导
    r4.dmovey(width / 2)   # 右侧波导
    r1.dmovey( width_center / 2)  # 上方波导
    r2.dmovex(- width_center / 2)  # 左侧波导
    r3.dmovey(- width_center / 2)  # 下方波导
    r4.dmovex(width_center / 2)  # 右侧波导
    # c.flatten()

    if port_type:
        prefix = "o" if port_type == "optical" else "e"
        c.add_port(
            f"{prefix}1",
            width=width,
            layer=layer,
            orientation=180,
            center=(-length - width_center / 2, 0),
            port_type=port_type,
        )
        c.add_port(
            f"{prefix}2",
            width=width,
            layer=layer,
            orientation=90,
            center=(0, +length + width_center / 2),
            port_type=port_type,
        )
        c.add_port(
            f"{prefix}3",
            width=width,
            layer=layer,
            orientation=0,
            center=(+length + width_center / 2, 0),
            port_type=port_type,
        )
        c.add_port(
            f"{prefix}4",
            width=width,
            layer=layer,
            orientation=270,
            center=(0, -length - width_center / 2),
            port_type=port_type,
        )
    return c


if __name__ == "__main__":
    c = crossing(port_type="optical")
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

