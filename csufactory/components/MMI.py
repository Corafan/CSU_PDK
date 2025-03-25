from __future__ import annotations

from gdsfactory.typings import ComponentFactory, CrossSectionSpec
import gdsfactory as gf
from gdsfactory.component import Component



@gf.cell
def mmi(
    inputs: float = 6,
    outputs:  float = 6,
    width_wg: float = 2,
    length_wg: float = 5.0,
    length_mmi: float = 60,
    width_mmi: float = 40.0,
    straight: ComponentFactory = "straight",
    cross_section: CrossSectionSpec = "strip",
) -> Component:
    r"""
    Args:
        inputs: the number of mmi inputs.(uniform)
        outputs: the number of mmi outputs.(uniform)
        width_wg: interface between inputs and outputs straights and mmi region(x).
        length_wg: into the mmi region(y).
        length_mmi: in x direction.
        width_mmi: in y direction.
        straight: straight function.

    .. code::

                   length_mmi
                    <------>
                    ________
                   |        |
                __/          \__
     signal_in  __            __  I_out1
                  \          /_ _ _ _
                  |         | _ _ _ _| gap_mmi
                  |          \__
                  |           __  Q_out1
                  \          /_ _ _ _
                  |         | _ _ _ _| gap_mmi
                __/          \__
        LO_in   __            __  Q_out2
                  \          /_ _ _ _
                  |         | _ _ _ _| gap_mmi
                  |          \__
                  |           __  I_out2
                  |          /
                  | ________|


                 <->
            length_taper
    """
    c = gf.Component()

    gap_mmi_in=(width_mmi-width_wg*inputs)/inputs
    gap_mmi_out=(width_mmi-width_wg*outputs)/outputs
    # gap_mmi = gf.snap.snap_to_grid(gap_mmi, grid_factor=2)
    w_mmi = width_mmi

    wg1=gf.components.straight(width=width_wg,length=length_wg, cross_section=cross_section)

    x = gf.get_cross_section(cross_section)

    _ = c << gf.get_component(
        straight,
        length=length_mmi,
        width=w_mmi,
        cross_section=cross_section,
    )

    y_signal_in_list = [
        - (width_mmi/2) + (gap_mmi_in / 2) + (width_wg / 2) + i * gap_mmi_in + i * width_wg
        for i in range(inputs)
    ]
    y_signal_out_list = [
        (width_mmi / 2) - (gap_mmi_out / 2) - (width_wg / 2) - i * gap_mmi_out - i * width_wg
        for i in range(outputs)
    ]

    # 添加输入端口
    ports = []
    for i, y in enumerate(y_signal_in_list):
        port_name = f"in_{i+1}"  # 唯一端口名（如 in_0, in_1...）
        ports.append(
            gf.Port(
                name=port_name,
                orientation=180,  # 输入方向（向左）
                center=(0, y),
                width=width_wg,
                cross_section=cross_section,
            )
        )
    for i, y in enumerate(y_signal_out_list):
        port_name = f"out_{i+1}"  # 唯一端口名（如 in_0, in_1...）
        ports.append(
            gf.Port(
                name=port_name,
                orientation=0,  # 输入方向（向左）
                center=(length_mmi, y),
                width=width_wg,
                cross_section=cross_section,
            )
        )

    for port in ports:
        wg_ref = c << wg1
        wg_ref.connect(port="o2", other=port)
        c.add_port(name=port.name, port=wg_ref.ports["o1"])

    c.flatten()
    x.add_bbox(c)
    return c


if __name__ == "__main__":
    from csufactory.generic_tech.layer_stack import get_layer_stack
    c = gf.Component()

    mmi_= c << mmi()
    component_name = ("mmi")
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

