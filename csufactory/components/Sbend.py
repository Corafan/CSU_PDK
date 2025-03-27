from __future__ import annotations

import gdsfactory as gf
from gdsfactory.component import Component
from gdsfactory.typings import CrossSectionSpec, Delta
from gdsfactory.components.bend_s import bend_s

@gf.cell
def Sbend(
    bend: ComponentSpec = bend_s,
    width: float = 0.5,
    gap: float = 0.234,
    dy: Delta = 4.0,
    dx: Delta = 10.0,
    cross_section: CrossSectionSpec = "strip",
) -> Component:
    r"""generate sbends.

    Args:
        bend: bend spec.
        width: width of bend.
        gap: in um.
        dy: port to port vertical spacing.
        dx: bend length in x direction.
        cross_section: section.

    .. code::

                       dx
                    |-----|
                       ___ o3
                      /       |
             o2 _____/        |dy


    """
    c = Component()
    x = gf.get_cross_section(cross_section,width=width)
    width1 = x.width
    dy = (dy - gap - width1) / 2

    bend_component = gf.get_component(
        bend,
        size=(dx, dy),
        cross_section=x,
    )
    top_bend = c << bend_component
    bend_ports = top_bend.ports.filter(port_type="optical")
    bend_port1_name = bend_ports[0].name
    bend_port2_name = bend_ports[1].name

    w = bend_component[bend_port1_name].dwidth
    y = w + gap
    y /= 2

    top_bend.dmovey(+y)

    c.add_port("o1", port=top_bend[bend_port1_name])
    c.add_port("o2", port=top_bend[bend_port2_name])


    c.info["length"] = bend_component.info["length"]
    c.info["min_bend_radius"] = bend_component.info["min_bend_radius"]
    return c


if __name__ == "__main__":
    c=Sbend(width=1,dx=20,dy=15)
    component_name = "sbend"
    # 无时间戳：
    output_gds_path = fr"C:\Windows\System32\CSU_PDK\csufactory\all_output_files\gds\{component_name}.gds"
    # 有时间戳：
    # timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    # output_gds_path = fr"D:\ProgramData\anaconda3\Lib\site-packages\gdsfactory\all_output_files\gds\{component_name}_{timestamp}.gds"
    c.write_gds(output_gds_path)
    print(f"GDS 文件已保存至: {output_gds_path}")
    c.show()