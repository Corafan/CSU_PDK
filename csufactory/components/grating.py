import gdsfactory as gf
from gdsfactory.component import Component
from gdsfactory.typings import ComponentSpec,LayerSpec

@gf.cell
def grating(
    width:float =4,
    length:float =20,
    num_wg: int = 5,  # 波导数量
    cross_section: ComponentSpec = "strip",
) -> Component:
    """生成一个光栅（grating）。

    Args:
        num_wg: 波导的数量。
        layer:层类型。
    """
    c = gf.Component()

    waveguide_length= 2*width                 # 波导的长度
    waveguide_width= width/3                  # 波导的宽度

    x1= gf.get_cross_section(cross_section, width=width)
    wg_center = c << gf.components.straight(length=length, cross_section=x1)
    wg_center.dcenter = (0, 0)
    x2= gf.get_cross_section(cross_section, width=waveguide_length)
    wg_ = gf.components.straight(length=waveguide_width,cross_section=x2)

    # if num_wg % 2 == 0:      #如果波导是偶数
    for i in range(num_wg):
        # 创建波导
        delta_y= (length)/(num_wg+1)
        x_start= - length/2 + delta_y

        # 计算波导起始位置（中心区域边缘）
        x = x_start + i * delta_y

        # 创建并放置波导
        wg = c << wg_
        wg.dcenter = (0, 0)
        # 移动波导到起点
        wg.dmove((x,0))


    #输入端口
    c.add_port(f"o1", port=wg_center.ports["o1"])
    #输出端口
    c.add_port(f"o2",port=wg_center.ports["o2"])

    c.flatten()
    return c

if __name__ == "__main__":
    c = grating()
    c.show()

    # c.pprint_ports()
    # cc = gf.routing.add_fiber_array(component=c)
    # cc.show( )

    component_name = ("grating")
    # 无时间戳：
    output_gds_path = fr"C:\Windows\System32\CSU_PDK\csufactory\all_output_files\gds\{component_name}.gds"
    # 有时间戳：
    # timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    # output_gds_path = fr"C:\Windows\System32\CSU_PDK\csufactory\all_output_files\gds\{component_name}_{timestamp}.gds"
    c.write_gds(output_gds_path)
    print(f"GDS 文件已保存至: {output_gds_path}")

