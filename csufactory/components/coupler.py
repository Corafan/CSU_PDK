from __future__ import annotations

import gdsfactory as gf
from gdsfactory.component import Component
from gdsfactory.typings import CrossSectionSpec, Delta
from gdsfactory.components.bend_s import bend_s

@gf.cell
def coupler_straight(
    length: float = 10.0,
    gap: float = 0.27,
    cross_section: CrossSectionSpec = "strip",
) -> Component:
    """Coupler_straight with two parallel straights.

    Args:
        length: of straight.
        gap: between straights.
        cross_section: specification (CrossSection, string or dict).

    .. code::

        o2──────▲─────────o3
                │gap
        o1──────▼─────────o4
    """
    c = gf.Component()
    straight = gf.components.straight(length=length, cross_section=cross_section)

    top = c << straight
    bot = c << straight

    w = straight.ports[0].dwidth
    y = w + gap

    top.dmovey(+y)

    c.add_port("o1", port=bot.ports[0])
    c.add_port("o2", port=top.ports[0])
    c.add_port("o3", port=bot.ports[1])
    c.add_port("o4", port=top.ports[1])
    c.auto_rename_ports()
    c.draw_ports()
    return c

@gf.cell
def coupler_symmetric(
    gap: float = 0.234,
    dy: Delta = 4.0,
    dx: Delta = 10.0,
    cross_section: CrossSectionSpec = "strip",
) -> Component:
    r"""Two coupled straights with bends.

    Args:
        bend: bend spec.
        gap: in um.
        dy: port to port vertical spacing.
        dx: bend length in x direction.
        cross_section: section.

    .. code::

                       dx
                    |-----|
                       ___ o3
                      /       |
             o2 _____/        |
                              |
             o1 _____         |  dy
                     \        |
                      \___    |
                           o4

    """
    bend= bend_s,
    c = Component()
    x = gf.get_cross_section(cross_section)
    width = x.width
    dy = (dy - gap - width) / 2

    bend_component = gf.get_component(
        bend,
        size=(dx, dy),
        cross_section=cross_section,
    )
    top_bend = c << bend_component
    bot_bend = c << bend_component
    bend_ports = top_bend.ports.filter(port_type="optical")
    bend_port1_name = bend_ports[0].name
    bend_port2_name = bend_ports[1].name

    w = bend_component[bend_port1_name].dwidth
    y = w + gap
    y /= 2

    bot_bend.dmirror_y()
    top_bend.dmovey(+y)
    bot_bend.dmovey(-y)

    c.add_port("o1", port=bot_bend[bend_port1_name])
    c.add_port("o2", port=top_bend[bend_port1_name])
    c.add_port("o3", port=top_bend[bend_port2_name])
    c.add_port("o4", port=bot_bend[bend_port2_name])

    c.info["length"] = bend_component.info["length"]
    c.info["min_bend_radius"] = bend_component.info["min_bend_radius"]
    return c

@gf.cell
def coupler(
        gap: float = 0.5,
        length: float = 0.5,
        dy: Delta = 8,
        dx: Delta = 10.0,
        cross_section: CrossSectionSpec = "strip",  # 这里表示横截面类型，实际上还包含layer:LayerSpec="WG",width,radius.radius_min
        allow_min_radius_violation: bool = False,
) -> Component:
    r"""Symmetric coupler.

    Args:
        gap: between straights in um.
        length: of coupling region in um.
        dy: port to port vertical spacing in um.
        dx: length of bend in x direction in um.
        cross_section: spec (CrossSection, string or dict).
        allow_min_radius_violation: if True does not check for min bend radius.

    .. code::

               dx                                 dx
            |------|                           |------|
         o2 ________                           ______o3
                    \                         /           |
                     \        length         /            |
                      ======================= gap         | dy
                     /                       \            |
            ________/                         \_______    |
         o1                                          o4

                        coupler_straight  coupler_symmetric
    """
    c = Component()
    sbend = gf.components.coupler_symmetric(gap=gap, dy=dy, dx=dx, cross_section=cross_section)

    sr = c << sbend
    sl = c << sbend
    cs = c << coupler_straight(length=length, gap=gap, cross_section=cross_section)
    sl.connect("o2", other=cs.ports["o1"])
    sr.connect("o1", other=cs.ports["o4"])

    c.add_port("o1", port=sl.ports["o3"])
    c.add_port("o2", port=sl.ports["o4"])
    c.add_port("o3", port=sr.ports["o3"])
    c.add_port("o4", port=sr.ports["o4"])

    c.info["length"] = sbend.info["length"]
    c.info["min_bend_radius"] = sbend.info["min_bend_radius"]
    c.auto_rename_ports()

    x = gf.get_cross_section(cross_section)
    x.add_bbox(c)
    c.flatten()
    if not allow_min_radius_violation:
        x.validate_radius(x.radius)
    return c


if __name__ == "__main__":
    from csufactory.generic_tech.layer_stack import get_layer_stack
    c = gf.Component()

    coupler_= c << coupler()
    component_name = ("coupler")
    # n = c.get_netlist()
    c.show()

    # 无时间戳：
    output_gds_path = fr"C:\Windows\System32\CSU_PDK\csufactory\all_output_files\gds\{component_name}.gds"
    # 有时间戳：
    # timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    # output_gds_path = fr"C:\Windows\System32\CSU_PDK\csufactory\all_output_files\gds\{component_name}_{timestamp}.gds"
    c.write_gds(output_gds_path)
    print(f"GDS 文件已保存至: {output_gds_path}")

    s=c.to_3d(layer_stack=get_layer_stack(thickness_wg=220e-3))
    s.show()
