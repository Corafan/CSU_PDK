#有个端口无法删去。。。。
from __future__ import annotations

import gdsfactory as gf
from gdsfactory.component import Component
from gdsfactory.typings import CrossSectionSpec, Delta
from gdsfactory.components.bend_s import bend_s

@gf.cell
def ybranch(
    width: float = 1,
    length: float = 10,
    gap: float = 0,
    dy: Delta = 10,
    dx: Delta = 20,
    cross_section: CrossSectionSpec = "strip",
) -> Component:
    r"""y_branch.

    Args:
        gap: in um.
        width: width of the straight in um.
        length: length of the straight in um.
        dy: port to port vertical spacing.
        dx: bend length in x direction.
        cross_section: section.

    .. code::

                       dx
             /----------------|
                       ___ o2
       length         /       |
     o1_____o4_______/        |dy
      width2         \        |
                      \___    |
                           o3

    """

    c = Component()
    width1=width/2
    x = gf.get_cross_section(cross_section, width=width1)
    dy_ = (dy - gap - width1) / 2

    bend_component=bend_s(size=(dx, dy_),cross_section=x,)
    top_bend = c << bend_component
    bot_bend = c << bend_component
    bend_ports = top_bend.ports.filter(port_type="optical")
    bend_port1_name = bend_ports[0].name
    bend_port2_name = bend_ports[1].name

    #计算偏移量,dwidth是端口的宽度
    w = bend_component[bend_port1_name].dwidth
    y = w + gap
    y /= 2

    bot_bend.dmirror_y()
    top_bend.dmovey(+y)
    bot_bend.dmovey(-y)

    port1=bot_bend[bend_port1_name]
    port2=top_bend[bend_port1_name]

    # 计算 port1 和 port2 的中心位置
    x_new = (port1.center[0] + port2.center[0]) / 2
    y_new = (port1.center[1] + port2.center[1]) / 2
    # 添加合并的新端口
    c.add_port(
        name="o4",
        center=(x_new, y_new),
        orientation=port1.orientation,  # 方向与原端口相同
        width=2*w,  # 宽度取其中之一
        layer=port1.layer  # 层信息
    )
    c.info["length"] = bend_component.info["length"]
    c.info["min_bend_radius"] = bend_component.info["min_bend_radius"]

    # 直波导组件，确保 cross_section 也使用 width2
    x_straight = gf.get_cross_section(cross_section, width=width)
    wg_input = c << gf.components.straight(length=length, cross_section=x_straight)

    # 连接直波导 wg_input 到 o4 端口
    wg_input.connect("o1", c.ports["o4"])

    c.add_port("o1", port=wg_input.ports["o2"])
    c.add_port("o2", port=top_bend[bend_port2_name])
    c.add_port("o3", port=bot_bend[bend_port2_name])

    c.flatten()
    # print(type(c))  # 打印 c 的类型
    return c


if __name__ == "__main__":
    c=ybranch()
    component_name = "ybranch_new"
    # 无时间戳：
    output_gds_path = fr"C:\Windows\System32\CSU_PDK\csufactory\all_output_files\gds\{component_name}.gds"
    # 有时间戳：
    # timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    # output_gds_path = fr"D:\ProgramData\anaconda3\Lib\site-packages\gdsfactory\all_output_files\gds\{component_name}_{timestamp}.gds"
    c.write_gds(output_gds_path)
    print(f"GDS 文件已保存至: {output_gds_path}")
    c.show()