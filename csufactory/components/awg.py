from __future__ import annotations
import gdsfactory as gf
from gdsfactory.component import Component
from functools import partial
from gdsfactory.typings import ComponentFactory, CrossSectionSpec
from gdsfactory.components.awg import free_propagation_region

@gf.cell
def awg(
        inputs: int = 3,                                      #输入端口数
        arms: int = 10,                                       #阵列波导数量
        outputs: int = 3,                                     #输出端口数
        free_propagation_region_input_function: ComponentFactory = partial(free_propagation_region, width1=2, width2=20.0,length=20,wg_width=0.5),
        free_propagation_region_output_function: ComponentFactory = partial(free_propagation_region, width1=10, width2=20.0,length=20,wg_width=0.5),
        fpr_spacing: float = 50.0,                            #输入/输出FPR的间距
        arm_spacing: float = 1.0,                             #阵列波导间距
        cross_section: CrossSectionSpec = "strip"
)-> Component:
    """生成阵列波导光栅.
      Args:
          inputs:输入端口数量.
          arms:阵列波导数量.
          outputs:输出波导数量.
          free_propagation_region_input_function:输入的星型耦合器尺寸.
          free_propagation_region_output_function:输出的星型耦合器尺寸.
          fpr_spacing:输入输出星型耦合器的阵列波导在x方向上的间距。
          arm_spacing:相邻阵列波导之间y方向上的高度差.
          cross_section:横截面类型，其中包含层类型和层号.
      函数Free propagation region:
      Args:
          width1: 输入区域的宽度.
          width2: 输出区域的宽度.
          length: 自由传播区的长度.
          wg_width:波导宽度.
      .. code::
                   length
                   <-->
                     /|
                    / |
             width1|  | width2
                    \ |
                     \|
      """
    return gf.components.awg(
        inputs = inputs,
        arms=arms,
        outputs= outputs,
        free_propagation_region_input_function= free_propagation_region_input_function,
        free_propagation_region_output_function=free_propagation_region_output_function,
        fpr_spacing= fpr_spacing,
        arm_spacing= arm_spacing,
        cross_section=cross_section
    )


# """AWG v0001"""
# from __future__ import annotations
# from functools import partial
#
# import numpy as np
#
# import gdsfactory as gf
# from gdsfactory.component import Component
# from gdsfactory.typings import ComponentFactory, CrossSectionSpec
# from sympy.physics.units import length
#
# from csufactory.generic_tech.layer_map import CSULAYER as LAYER  #没用到，layer由crosssection决定的
#
#
# #输入/输出端口和阵列波导之间的过渡区域，用于分束和合束
# @gf.cell
# def free_propagation_region(
#     width1: float = 2,
#     width2: float = 20.0,
#     length: float = 20.0,
#     wg_width: float = 0.5,
#     inputs: int = 1,
#     outputs: int = 9,
#     cross_section: CrossSectionSpec = "strip",
#     # layer: tuple = LAYER.WG,    #LAYER是由上面的crosssection决定的
# ) -> Component:
#     r"""Free propagation region.
#     Args:
#         width1: 输入区域的宽度.
#         width2: 输出区域的宽度.
#         length: 自由传播区的长度.
#         wg_width:波导宽度.
#         inputs:输入波导数量.
#         outputs:输出波导数量.
#         cross_section:横截面类型，其中包含层类型和层号.
#     .. code::
#                  length
#                  <-->
#                    /|
#                   / |
#            width1|  | width2
#                   \ |
#                    \|
#     """
#     y1 = width1 / 2
#     y2 = width2 / 2
#     xs = gf.get_cross_section(cross_section)
#     o = 0
#     layer = xs.layer
#
#     #这个是没有旋转之前的
#     xpts = [0, length, length, 0]   #0，20，20，0,(x坐标)
#     ypts = [y1, y2, -y2, -y1]       #1，10，-10，-1,(y坐标)
#
#     c = gf.Component()
#     c.add_polygon(list(zip(xpts, ypts)), layer=layer)  #生成多边形，耦合器
#
#     #输入端口命名：
#     if inputs == 1:
#         c.add_port(
#             "o1",
#             center=(0, 0),
#             width=wg_width,
#             orientation=180,
#             layer=layer,
#         )
#     else:
#         y = np.linspace(-width1 / 2 + wg_width / 2, width1 / 2 - wg_width / 2, inputs)
#         y = gf.snap.snap_to_grid(y)
#         for i, yi in enumerate(y):
#             c.add_port(
#                 f"W{i}",
#                 center=(0, yi),
#                 width=wg_width,
#                 orientation=180,
#                 layer=layer,
#             )
#
#     #输出端口命名：
#     y = np.linspace(-width2 / 2 + wg_width / 2, width2 / 2 - wg_width / 2, outputs)
#     y = gf.snap.snap_to_grid(y)
#     for i, yi in enumerate(y):
#         c.add_port(
#             f"E{i}",
#             center=(length, yi),
#             width=wg_width,
#             orientation=0,
#             layer=layer,
#         )
#
#     ypts = [y1 + o, y2 + o, -y2 - o, -y1 - o]
#
#     c.info["length"] = length
#     c.info["width1"] = width1
#     c.info["width2"] = width2
#     # c.draw_ports()
#     return c
#
#
# # free_propagation_region_input = partial(free_propagation_region, inputs=1)
#
# # free_propagation_region_output = partial(free_propagation_region, inputs=10, width1=10, width2=20.0)
#
# ##定义连接输入输出的波导
# # @gf.cell
# # def wg(length=5, width=0.5, layer=LAYER.WG):
# #     c = gf.Component()
# #     c.add_polygon([(-width, 0), (0, 0), (0, length), (-width, length)], layer=layer)
# #     c.add_port(
# #         name="g1", center=[-width / 2, 0], width=width, orientation=270, layer=layer
# #     )
# #     #定义每个多边形在左右两边都有一个中心center，将这个连接的线按不同的情况设置
# #     c.add_port(
# #         name="g2", center=[-width/2 , length], width=width, orientation=90, layer=layer
# #     )
# #     c.draw_ports()
# #     return c
#
# #AWG由输入FPR、阵列波导、输出FPR组成，用于波长选择和信号分束/合束。
# @gf.cell
# def awg(
#     inputs: int = 3,                                      #输入端口数
#     arms: int = 10,                                       #阵列波导数量
#     outputs: int = 3,                                     #输出端口数
#     free_propagation_region_input_function: ComponentFactory = partial(free_propagation_region, width1=2, width2=20.0,length=20,wg_width=0.5),
#     free_propagation_region_output_function: ComponentFactory = partial(free_propagation_region, width1=10, width2=20.0,length=20,wg_width=0.5),
#     fpr_spacing: float = 50.0,                            #输入/输出FPR的间距
#     arm_spacing: float = 1.0,                             #阵列波导间距
#     cross_section: CrossSectionSpec = "strip",
# ) -> Component:
#     """生成阵列波导光栅.
#     Args:
#         inputs:输入端口数量.
#         arms:阵列波导数量.
#         outputs:输出波导数量.
#         free_propagation_region_input_function:输入的星型耦合器尺寸.
#         free_propagation_region_output_function:输出的星型耦合器尺寸.
#         fpr_spacing:输入输出星型耦合器的阵列波导在x方向上的间距。
#         arm_spacing:阵列波导y方向上的高度差.
#         cross_section:横截面类型，其中包含层类型和层号.
#     函数Free propagation region:
#     Args:
#         width1: 输入区域的宽度.
#         width2: 输出区域的宽度.
#         length: 自由传播区的长度.
#         wg_width:波导宽度.
#     .. code::
#                  length
#                  <-->
#                    /|
#                   / |
#            width1|  | width2
#                   \ |
#                    \|
#     """
#     c = gf.Component()
#     fpr_in = free_propagation_region_input_function(
#         inputs=inputs,
#         outputs=arms,
#         cross_section=cross_section,
#     )
#     fpr_out = free_propagation_region_output_function(
#         inputs=outputs,
#         outputs=arms,
#         cross_section=cross_section,
#     )
#
#     fpr_in_ref = c.add_ref(fpr_in)
#     fpr_out_ref = c.add_ref(fpr_out)
#
#     fpr_in_ref.drotate(90)
#     fpr_out_ref.drotate(90)
#
#     fpr_out_ref.dx += fpr_spacing     #让fpr_out_ref（输出的自由传播区）在x方向上向右移动fpr_spacing的距离。
#     _ = gf.routing.route_bundle(
#         c,
#         gf.port.get_ports_list(fpr_out_ref, prefix="E"),
#         gf.port.get_ports_list(fpr_in_ref, prefix="E"),
#         sort_ports=True,
#         separation=arm_spacing,
#         cross_section=cross_section,
#         radius=10, #弯曲半径默认是10
#         bend=gf.components.bend_circular  # Change here, if bend_euler is not available
#     )
#
#     #修改：
#     #重新为AWG的输入输出端口命名，用于后续与其他器件连接：
#     #输入IN：
#     if inputs == 1:
#         c.add_port(
#             "I1",
#             port=fpr_in_ref.ports["o1"]
#         )
#     else:
#         for i, port in enumerate(gf.port.get_ports_list(fpr_in_ref, prefix="W")):
#             c.add_port(f"I{i}", port=port)
#     #输出OUT:
#     if outputs == 1:
#         c.add_port(
#             "O1",
#             port=fpr_out_ref.ports["o1"]
#         )
#     else:
#         for i, port in enumerate(gf.port.get_ports_list(fpr_out_ref, prefix="W")):
#             c.add_port(f"O{i}", port=port)
#
#     # c.draw_ports()
#     return c
#
#
# #运行函数生成awg器件：
# if __name__ == "__main__":
#     # c = free_propagation_region(inputs=4, outputs=4)
#     c = awg(
#         inputs=1,
#         arms=9,  # 阵列波导数量
#         outputs=1,
#         free_propagation_region_input_function=partial(free_propagation_region, width1=2, width2=20.0),
#         free_propagation_region_output_function=partial(free_propagation_region, width1=2, width2=20.0),
#         fpr_spacing=50,  # 输入/输出FPR的间距
#         arm_spacing=1,
#         #阵列波导间距
# )
#
#     # wg1 = c << wg(length=10)
#     # wg2 = c << wg(length=10)
#     # wg1.connect("g2",awg.ports["I1"])
#     # wg2.connect("g2",awg.ports["O1"])
#
#     # print(wg1.ports)
#     # print(wg2.ports)
#     print(c.ports)
#
#     component_name = "awg"
#     # 无时间戳：
#     output_gds_path = fr"C:\Windows\System32\CSU_PDK\examples\{component_name}.gds"
#     # 有时间戳：
#     # timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
#     # output_gds_path = fr"D:\ProgramData\anaconda3\Lib\site-packages\gdsfactory\all_output_files\gds\{component_name}_{timestamp}.gds"
#     c.write_gds(output_gds_path)
#     print(f"GDS 文件已保存至: {output_gds_path}")
#     c.show()


from csufactory.components.awg import awg
from csufactory.technology.save_gds import save_gds
from csufactory.components.generate_Para.component_layer_stack import Si_zp75_LayerStack
from csufactory.technology.export_layer_stack_info import export_layer_stack_info
if __name__ == "__main__":
    export_layer_stack_info(Si_zp75_LayerStack)


