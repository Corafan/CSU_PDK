#原创:
from __future__ import annotations

import gdsfactory as gf
from gdsfactory.component import Component
from gdsfactory.typings import CrossSectionSpec

@gf.cell(check_instances=False)
def Ybranch_1x2(
    length1: float = 8,
    length2: float = 7,
    length3: float = 1,
    bend_radius: float = 10,
    width: float = 0.5,
    angle1: float = 30,
    angle2: float = 30,
    cross_section: CrossSectionSpec = "strip",  # 这里是直接使用字符串来表示交叉截面
    allow_min_radius_violation: bool = False,
) -> Component:
    r"""生成y分支.

    Args:
        length1: 第一段输入波导在x方向上的长度.
        length2: 中间段波导在x方向上的长度.
        length3: 输出波导在x向上的长度.
        bend_radius:第一段弯曲波导的半径.
        width:波导的宽度（x）。
        angle1: 第一段分支的角度.
        angle2: 第二段分支的角度.
        cross_section: 横截面类型，不建议修改。
        allow_min_radius_violation: 如果为TRUE,则不检查最小半径，无需修改.


    .. code::
                                                 length3
                                               ______ o2
                                              /
                                 length1     /
                         o1 -----------------  (width)
                                      length2\
                                              \_______ o3

    """
    c = gf.Component()

    # 创建输入波导
    wg_input = c << gf.components.straight(length=length1, width=width,cross_section=cross_section)

    # 创建第一对弯曲波导（用于分支）
    bend_left1 = c << gf.components.bend_euler(angle=angle1, radius=bend_radius, width=width,cross_section=cross_section)
    bend_right1 = c << gf.components.bend_euler(angle=-angle1, radius=bend_radius, width=width,cross_section=cross_section)

    # 创建两个直波导（连接段）
    wg_left1 = c << gf.components.straight(length=length2, width=width,cross_section=cross_section)
    wg_right1 = c << gf.components.straight(length=length2, width=width,cross_section=cross_section)

    # 创建第二对弯曲波导（用于调整输出方向）
    bend_left2 = c << gf.components.bend_euler(angle=-angle2, radius=bend_radius, width=width,cross_section=cross_section)
    bend_right2 = c << gf.components.bend_euler(angle=angle2, radius=bend_radius, width=width,cross_section=cross_section)

    # 创建两个直波导（连接段）
    wg_left2 = c << gf.components.straight(length=length3, width=width,cross_section=cross_section)
    wg_right2 = c << gf.components.straight(length=length3, width=width,cross_section=cross_section)

    # 连接输入波导到第一对弯曲波导
    bend_left1.connect("o1", wg_input.ports["o2"])
    bend_right1.connect("o1", wg_input.ports["o2"])

    # 连接第一对弯曲波导到直波导
    wg_left1.connect("o1", bend_left1.ports["o2"])
    wg_right1.connect("o1", bend_right1.ports["o2"])

    # 连接直波导到第二对弯曲波导
    bend_left2.connect("o1", wg_left1.ports["o2"])
    bend_right2.connect("o1", wg_right1.ports["o2"])

    # 连接第一对弯曲波导到直波导
    wg_left2.connect("o1", bend_left2.ports["o2"])
    wg_right2.connect("o1", bend_right2.ports["o2"])


    #加端口：
    #输入端口
    c.add_port("o1", port=wg_input.ports["o1"])
    #输出端口
    c.add_port("o2", port=wg_left2.ports["o2"])
    c.add_port("o3", port=wg_right2.ports["o2"])
    # c.draw_ports()                     #绘制之后无法隐藏！！
    c.auto_rename_ports()

    x = gf.get_cross_section(cross_section)
    x.add_bbox(c)
    c.flatten()
    if not allow_min_radius_violation:
        x.validate_radius(x.radius)
    return c


if __name__ == "__main__":
    from csufactory.generic_tech.layer_stack import get_layer_stack
    c=gf.Component()

    YBranch = c << Ybranch_1x2()
    component_name = ("YBranch_1x2")
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

    # c_unlocked = c.copy()
    # c_unlocked.flatten()  # 展开所有子组件
    # c_unlocked.show()  # 显示组件

