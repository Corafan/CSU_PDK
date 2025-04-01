#原创:
import gdsfactory as gf
from gdsfactory.component import Component
from gdsfactory.typings import LayerSpec
from gdsfactory.boolean import boolean
from gdsfactory.typings import CrossSectionSpec
import numpy as np

@gf.cell
def star_coupler(
    num_ports: int = 10,  # 波导数量
    body_size: tuple[float, float] = (2.5, 4),  # 椭圆主耦合区域 a和b轴
    waveguide_length: float = 3,  # 波导的长度
    waveguide_width: float = 0.5,  # 波导的宽度
    layer: LayerSpec = "WG",  # GDS 图层
    cross_section: CrossSectionSpec = "strip",
) -> Component:
    """生成一个星型耦合器（star coupler），采用从中心发散的波导。

    Args:
        num_ports: 波导的数量。必须为偶数!
        body_size: 中心区域（圆形）的半径。
        waveguide_length: 波导的长度。
        waveguide_width: 波导的宽度。
        layer: GDS 图层。
    """
    c = gf.Component()

    # 1. 创建基础椭圆
    body1 = gf.components.ellipse(radii=body_size, layer=layer)

    # 2. 创建稍大的椭圆（裁剪边界）
    body2 = gf.components.ellipse(radii=(body_size[0] + 1, body_size[1] + 1), layer=layer)

    # 3. 生成波导（临时组件）
    temp = gf.Component()
    #自己编写
    num_2 = num_ports / 2
    if num_ports <= 2:
        angles = [0, 180]
    # elif 2 < num_ports <= 4:
    #     stat_angles = 360 / num_ports
    #     angles = []
    #     for i in range(num_ports):
    #         angles.append(stat_angles + i * stat_angles)
    elif 2 < num_ports and num_2 % 2 == 0:
        angles = []
        nums = num_ports // 2
        for i in range(nums):
            # print(f"{i}")
            angle_offset = 180 / nums
            angle_0=0 + (0.5+nums/2-1) * angle_offset
            angle_180 = 180 - (0.5+nums/2-1) * angle_offset
            angles.append(angle_0 - angle_offset * i)
            angles.append(angle_180 + angle_offset * i)
    else:
        angles = [0, 180]
        nums = num_ports // 4
        for i in range(1, nums + 1):
            angle_offset = 160 / (num_ports // 2) * i
            angles.append(0 + angle_offset)
            angles.append(0 - angle_offset)
            angles.append(180 + angle_offset)
            angles.append(180 - angle_offset)

    # 规范化角度到0-360度范围
    angles = [angle % 360 for angle in angles]
    angles = sorted(list(set(angles)))  # 去重并排序
    # print(angles)

    # 3. 在每个角度放置波导
    for i, angle in enumerate(angles):
        # 创建波导
        angle_rad = np.radians(angle)  # 角度转换为弧度

        # 计算波导起始位置（中心区域边缘）
        x_start = body_size[0] / 2 * np.cos(angle_rad)
        y_start = body_size[1] / 2 * np.sin(angle_rad)

        # 计算波导终点位置
        x_end = (body_size[0] / 2 + waveguide_length) * np.cos(angle_rad)
        y_end = (body_size[1] / 2 + waveguide_length) * np.sin(angle_rad)

        x = gf.get_cross_section(cross_section, width=waveguide_width)
        # 创建并放置波导
        wg = temp << gf.components.straight(
            length=waveguide_length,
            cross_section=x,
        )
        # 移动波导到起点
        wg.dmove((x_start, y_start))
        # 旋转波导使其朝向正确的角度
        wg.drotate(angle, center=(x_start, y_start))

        # 添加端口
        temp.add_port(
            name=f"o{i+1}",
            center=(x_end, y_end),
            width=waveguide_width,
            orientation=angle,
            layer=layer,
        )

    # 5. 布尔运算
    # 先合并波导和body1
    merged = boolean(temp, body1, operation="or", layer=layer)
    # 再取与body2的交集
    final = boolean(merged, body2, operation="and", layer=layer)

    # 6. 添加到最终组件
    c << final
    c.flatten()

    # # 7. 正确复制端口
    # for i in range(len(angles)):
    #     port_name = f"o{i + 1}"
    #     # 直接从临时组件获取端口
    #     if port_name in temp.ports:
    #         port = temp.ports[port_name]
    #         c.add_port(
    #             name=port_name,
    #             center=port.center,
    #             width=port.width,
    #             orientation=port.orientation,
    #             layer=port.layer
    #         )
    c.add_port(
        name=f"o1",
        center=(-body_size[0] - 1+0.005, 0),
        width=waveguide_width,
        orientation=180,
        layer=layer,
    )
    c.add_port(
        name=f"o2",
        center=(body_size[0] + 1-0.005, 0),
        width=waveguide_width,
        orientation=0,
        layer=layer,
    )

    print(f"最终角度分布: {angles}")
    return c


if __name__ == "__main__":
    c = star_coupler(num_ports=10, waveguide_length=3)
    c.show()
    component_name = ("star_coupler")

    # 无时间戳：
    output_gds_path = fr"C:\Windows\System32\CSU_PDK\csufactory\all_output_files\gds\{component_name}.gds"
    # 有时间戳：
    # timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    # output_gds_path = fr"C:\Windows\System32\CSU_PDK\csufactory\all_output_files\gds\{component_name}_{timestamp}.gds"
    c.write_gds(output_gds_path)
    print(f"GDS 文件已保存至: {output_gds_path}")