# from __future__ import annotations
#
# import gdsfactory as gf
# from gdsfactory.component import Component
# from gdsfactory.typings import CrossSectionSpec
# from gdsfactory.typings import LayerSpec
#
#
# @gf.cell
# def star_coupler(
#     num_ports: int = 6,  # 每侧波导数量
#     body_size: tuple[float, float] = (2.5, 4),  # 椭圆主耦合区域 a和b轴
#     waveguide_length: float = 2.5,  # 每个波导的长度
#     waveguide_width: float = 0.5,  # 波导宽度
#     waveguide_spacing: float = 1.0,  # 波导间距
#     layer: LayerSpec = "WG",  # 图层
# ) -> Component:
#     """生成一个星型耦合器（star coupler）。
#
#     Args:
#         num_ports: 每侧波导的数量。
#         body_size: 椭圆形主耦合区域的尺寸 (长, 宽)。
#         waveguide_length: 连接主区域的波导长度。
#         waveguide_width: 波导宽度。
#         waveguide_spacing: 波导间距。
#         layer: GDS 图层。
#     """
#     c = Component()
#
#     # 1. 创建椭圆形主耦合区域
#     body = c << gf.components.ellipse(radii=body_size, layer=layer)
#
#     # 2. 计算波导的起始位置
#     x_offset = body_size[0] / 2  # 主体的边界 x 坐标
#     y_positions = [
#         -((num_ports - 1) * waveguide_spacing) / 2 + i * waveguide_spacing
#         for i in range(num_ports)
#     ]
#
#     # 3. 在两侧放置多个波导
#     for y in y_positions:
#         # 左侧波导
#         left_wg = c << gf.components.straight(
#             length=waveguide_length, width=waveguide_width, layer=layer
#         )
#         left_wg.dmovex(-x_offset - waveguide_length)
#         left_wg.dmovey(y)
#         c.add_port(name=f"oL{y}", port=left_wg.ports["o2"])
#
#         # 右侧波导
#         right_wg = c << gf.components.straight(
#             length=waveguide_length, width=waveguide_width, layer=layer
#         )
#         right_wg.dmovex(x_offset)
#         right_wg.dmovey(y)
#         c.add_port(name=f"oR{y}", port=right_wg.ports["o1"])
#     c.flatten()
#     return c
#
#
# if __name__ == "__main__":
#     c = star_coupler(num_ports=5)  # 生成一个五对耦合波导的星型耦合器
#     c.show()

import gdsfactory as gf
from gdsfactory.component import Component
from gdsfactory.typings import LayerSpec
import numpy as np

@gf.cell
def star_coupler(
    num_ports: int = 8,  # 波导数量
    body_size: tuple[float, float] = (2.5, 4),  # 椭圆主耦合区域 a和b轴
    waveguide_length: float = 5,  # 波导的长度
    waveguide_width: float = 0.5,  # 波导的宽度
    layer: LayerSpec = "WG",  # GDS 图层
) -> Component:
    """生成一个星型耦合器（star coupler），采用从中心发散的波导。

    Args:
        num_ports: 波导的数量。必须为偶数
        body_size: 中心区域（圆形）的半径。
        waveguide_length: 波导的长度。
        waveguide_width: 波导的宽度。
        layer: GDS 图层。
    """
    c = Component()

    # 1. 生成中心的椭圆或圆形区域
    body = c << gf.components.ellipse(radii=body_size, layer=layer)

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
            print(f"{i}")
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
    print(angles)

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

        # 创建并放置波导
        wg = c << gf.components.straight(
            length=waveguide_length,
            width=waveguide_width,
            layer=layer
        )
        # 移动波导到起点
        wg.dmove((x_start, y_start))
        # 旋转波导使其朝向正确的角度
        wg.drotate(angle, center=(x_start, y_start))

        # 添加端口
        c.add_port(
            name=f"o{i+1}",
            center=(x_end, y_end),
            width=waveguide_width,
            orientation=angle,
            layer=layer,
        )

    c.flatten()

    # body2 = c << gf.components.ellipse(radii=body_size, layer=layer)
    # body = body & body2
    print(f"最终角度分布: {angles}")
    return c


if __name__ == "__main__":
    c = star_coupler(num_ports=8, waveguide_length=3)
    c.show()


# import numpy as np
# import gdsfactory as gf
# from gdsfactory.component import Component
# from gdsfactory.typings import LayerSpec
#
# @gf.cell
# def star_coupler(
#     num_ports: int = 8,  # 需要放置的波导数量
#     body_size: tuple[float, float] = (2.5, 4),  # 椭圆中心区域的大小 (a, b)
#     waveguide_length: float = 10,  # 波导的长度
#     waveguide_width: float = 0.5,  # 波导的宽度
#     layer: LayerSpec = "WG",  # GDS 图层
# ) -> Component:
#     """生成一个星型耦合器（star coupler），采用从中心发散的波导，且左右对称，去除最上和最下的波导。
#
#     Args:
#         num_ports: 需要放置的波导数量（总数需为偶数）。
#         body_size: 中心区域的 (a, b) 半径，默认是椭圆形。
#         waveguide_length: 每个波导的长度。
#         waveguide_width: 波导的宽度。
#         layer: GDS 图层。
#     """
#     c = Component()
#
#     # 1. 生成中心区域（椭圆）
#     body = c << gf.components.ellipse(radii=body_size, layer=layer)
#
#     # 2. 计算波导的角度（去除 90° 和 270°，保证左右对称）
#     num_ports_half = num_ports // 2  # 左右各一半
#     angles = np.linspace(10, 80, num_ports_half)  # 只取 10° 到 80°，去掉 90°
#
#     for i, angle in enumerate(angles):
#         angle_rad = np.radians(angle)  # 角度转换为弧度
#
#         # 右侧波导
#         x_start = body_size[0] * np.cos(angle_rad)
#         y_start = body_size[1] * np.sin(angle_rad)
#         x_end = x_start + waveguide_length
#         y_end = y_start
#
#         wg = c << gf.components.straight(length=waveguide_length, width=waveguide_width, layer=layer)
#         wg.dmove((x_start, y_start))
#         wg.drotate(angle, center=(x_start, y_start))
#
#         c.add_port(
#             name=f"o{i+1}",
#             center=(x_end, y_end),
#             width=waveguide_width,
#             orientation=angle,
#             layer=layer,
#         )
#
#         # 左侧波导（镜像）
#         x_start_mirror = -x_start
#         x_end_mirror = -x_end
#
#         wg_mirror = wg
#         wg_mirror.dmirror_x()
#
#         c.add_port(
#             name=f"o{i+1+num_ports_half}",
#             center=(x_end_mirror, y_end),
#             width=waveguide_width,
#             orientation=180 - angle,  # 镜像角度
#             layer=layer,
#         )
#
#     c.flatten()
#     return c
#
# if __name__ == "__main__":
#     c = star_coupler(num_ports=8, waveguide_length=10)
#     c.show()


# import gdsfactory as gf
# from gdsfactory.component import Component
# from gdsfactory.typings import LayerSpec
# import numpy
#
#
# @gf.cell
# def star_coupler(
#         num_ports: int = 8,
#         body_radius: float = 5,
#         waveguide_length: float = 10,
#         waveguide_width: float = 0.5,
#         layer: LayerSpec = "WG",
# ) -> Component:
#     """Generates a symmetric star coupler with evenly distributed waveguides.
#
#     Args:
#         num_ports: Total number of waveguides (excluding top and bottom).
#         body_radius: Radius of the central region.
#         waveguide_length: Length of each waveguide.
#         waveguide_width: Width of the waveguides.
#         layer: Layer specification.
#
#     Returns:
#         A gdsfactory Component representing the star coupler.
#     """
#
#     c = gf.Component()
#
#     # Create the central body (ellipse or rectangle)
#     body = c << gf.components.ellipse(radii=(body_radius, body_radius), layer=layer)
#
#     # Define angles for symmetry (exclude top and bottom)
#     num_ports_half = num_ports // 2
#     angles = [i * (180 / (num_ports_half + 1)) for i in range(1, num_ports_half + 1)]
#
#     for angle in angles:
#         # Create waveguide component
#         wg = c << gf.components.straight(length=waveguide_length, width=waveguide_width, layer=layer)
#
#         # Compute waveguide start and end points (right side)
#         x_start = body_radius
#         y_start = body_radius * numpy.tan(numpy.radians(angle))
#         x_end = x_start + waveguide_length
#         y_end = y_start
#
#         # Move and rotate waveguide
#         wg.dmove((x_start, y_start))
#         wg.drotate(0, center=(x_start, y_start))
#
#         # Mirror waveguide for left side
#         wg_mirror = c << gf.components.straight(length=waveguide_length, width=waveguide_width, layer=layer)
#         wg_mirror.dmirror_x()
#
#         # Add ports
#         c.add_port(
#             name=f"o{len(c.ports) + 1}",
#             center=(x_end, y_end),
#             width=waveguide_width,
#             orientation=0,
#             layer=layer,
#         )
#         c.add_port(
#             name=f"o{len(c.ports) + 1}",
#             center=(-x_end, y_end),
#             width=waveguide_width,
#             orientation=180,
#             layer=layer,
#         )
#     c.flatten()
#     return c
#
#
# if __name__ == "__main__":
#     c = star_coupler(num_ports=8, body_radius=5, waveguide_length=10)
#     c.show()
