from __future__ import annotations

import gdsfactory as gf
from gdsfactory.component import Component
from gdsfactory.typings import ComponentSpec,LayerSpec


@gf.cell
def ring_coupler(
    gap: float = 0.2,
    radius: float = 5.0,
    width: float = 1.5,
    layer: LayerSpec = "WG",
    port_type: str | None = None,
) -> Component:
    r"""Coupler for ring.

    Args:
        gap: spacing between ring and straight waveguides.
        radius: of the outside circle.
        width: width of the ring and straight waveguides.
        layer:layer spec.
        port_type:port_type.

    .. code::
        o2    length_x   o3
           ---=========---
            /           \
           |             |
            \           /
             \         /
           ---=========---
        o1    length_x   o4

    """
    c = gf.Component()
    width_wg = width
    length_wg = 3*radius
    wg_bottom = c << gf.components.rectangle(size=(width_wg,length_wg),layer=layer)
    wg_top = c << gf.components.rectangle(size=(width_wg,length_wg),layer=layer)
    wg_bottom.dcenter = (0, 0)
    wg_top.dcenter = (0, 0)
    wg_bottom.rotate(90)
    wg_top.rotate(90)
    gap_=gap+radius+width/2
    wg_bottom.movey(-gap_)
    wg_top.movey(gap_)

    circle_outer=  gf.components.circle(radius=radius,layer=layer)
    circle_inner=  gf.components.circle(radius=radius-width,layer=layer)
    ring= gf.boolean(circle_outer, circle_inner, operation="xor", layer=layer)
    c << ring

    if port_type:
        prefix = "o" if port_type == "optical" else "e"
    #输入端口
        c.add_port(f"{prefix}1", port=wg_bottom.ports["e2"])
        c.add_port(f"{prefix}2", port=wg_top.ports["e2"])
    #输出端口
        c.add_port(f"{prefix}3",port=wg_top.ports["e4"])
        c.add_port(f"{prefix}4",port=wg_bottom.ports["e4"])
    c.flatten()
    return c

if __name__ == "__main__":
    c = ring_coupler(port_type="optical")
    c.show()
    component_name = ("ring_coupler")

    # 无时间戳：
    output_gds_path = fr"C:\Windows\System32\CSU_PDK\csufactory\all_output_files\gds\{component_name}.gds"
    # 有时间戳：
    # timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    # output_gds_path = fr"C:\Windows\System32\CSU_PDK\csufactory\all_output_files\gds\{component_name}_{timestamp}.gds"
    c.write_gds(output_gds_path)
    print(f"GDS 文件已保存至: {output_gds_path}")