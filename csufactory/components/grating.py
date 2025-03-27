import gdsfactory as gf
from gdsfactory.component import Component
from gdsfactory.typings import LayerSpec

@gf.cell
def grating(
    size_center:tuple[float, float]=(20,4),
    num_wg: int = 5,  # 波导数量
    layer: LayerSpec = "WG",
    port_type: str | None = None,
) -> Component:
    """生成一个光栅（grating）。

    Args:
        size_center:中心波导的尺寸。
        num_wg: 波导的数量。
        layer:层类型。
        port_type:端口类型。
    """
    waveguide_length= 2*size_center[1]                 # 波导的长度
    waveguide_width= size_center[1]/3                  # 波导的宽度

    c = gf.Component()
    wg_center = c << gf.components.rectangle(size=size_center, layer=layer)
    wg_center.dcenter = (0, 0)
    wg_ = gf.components.straight(length=waveguide_width,width=waveguide_length,layer=layer)

    # if num_wg % 2 == 0:      #如果波导是偶数
    for i in range(num_wg):
        # 创建波导
        delta_y= (size_center[0])/(num_wg+1)
        x_start= - size_center[0]/2 + delta_y

        # 计算波导起始位置（中心区域边缘）
        x = x_start + i * delta_y

        # 创建并放置波导
        wg = c << wg_
        wg.dcenter = (0, 0)
        # 移动波导到起点
        wg.dmove((x,0))

    if port_type:
        prefix = "o" if port_type == "optical" else "e"
    #输入端口
        c.add_port(f"{prefix}1", port=wg_center.ports["e1"])
    #输出端口
        c.add_port(f"{prefix}2",port=wg_center.ports["e3"])

    c.flatten()
    return c

if __name__ == "__main__":
    c = grating(port_type="optical")
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

