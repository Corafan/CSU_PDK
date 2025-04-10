# # #关于路径的文件
# # from __future__ import annotations
# # import warnings
# # import kfactory as kf
# #
# # def add_ref(
# #         self,
# #         component: Component,
# #         name: str | None = None,
# #         columns: int = 1,
# #         rows: int = 1,
# #         spacing: "Spacing | None" = None,
# #         alias: str | None = None,
# #         column_pitch: float = 0.0,
# #         row_pitch: float = 0.0,
# # ) -> ComponentReference:
# #     """Adds a component instance reference to a Component.
# #
# #     Args:
# #         component: The referenced component.
# #         name: Name of the reference.
# #         columns: Number of columns in the array.
# #         rows: Number of rows in the array.
# #         spacing: pitch between adjacent columns and adjacent rows. Deprecated.
# #         alias: Deprecated. Use name instead.
# #         column_pitch: column pitch.
# #         row_pitch: row pitch.
# #     """
# #     if spacing is not None:
# #         warnings.warn(
# #             "spacing is deprecated, use column_pitch and row_pitch instead"
# #         )
# #         column_pitch, row_pitch = spacing
# #
# #     if rows > 1 or columns > 1:
# #         if rows > 1 and row_pitch == 0:
# #             raise ValueError(f"rows = {rows} > 1 require {row_pitch=} > 0")
# #
# #         if columns > 1 and column_pitch == 0:
# #             raise ValueError(f"columns = {columns} > 1 require {column_pitch} > 0")
# #
# #         column_pitch_dbu = self.kcl.to_dbu(column_pitch)
# #         row_pitch_dbu = self.kcl.to_dbu(row_pitch)
# #
# #         a = kf.kdb.Vector(column_pitch_dbu, 0)
# #         b = kf.kdb.Vector(0, row_pitch_dbu)
# #
# #         inst = self.create_inst(
# #             component,
# #             na=columns,
# #             nb=rows,
# #             a=a,
# #             b=b,
# #         )
# #     else:
# #         inst = self.create_inst(component)
# #
# #     if alias:
# #         warnings.warn("alias is deprecated, use name instead")
# #         inst.name = alias
# #     elif name:
# #         inst.name = name
# #     return ComponentReference(inst)
#
#
# # !/usr/bin/python
# # -*- coding: UTF-8 -*-
#
# # # Python3.x 导入方法
# # from tkinter import *
# # root = Tk()  # 创建窗口对象的背景色
# # # 创建两个列表
# # li = ['C', 'python', 'php', 'html', 'SQL', 'java']
# # movie = ['CSS', 'jQuery', 'Bootstrap']
# # movie2 = ['CSS', 'jQuery', 'Bootstrap']
# # listb = Listbox(root)  # 创建两个列表组件
# # listb2 = Listbox(root)
# # listb3 = Listbox(root)
# #
# # for item in li:  # 第一个小部件插入数据
# #     listb.insert(0, item)
# #
# # for item in movie:  # 第二个小部件插入数据
# #     listb2.insert(0, item)
# #
# # for item in movie2:  # 第二个小部件插入数据
# #     listb3.insert(0, item)
# #
# # listb.pack()  # 将小部件放置到主窗口中
# # listb2.pack()
# # listb3.pack()
# # root.mainloop()  # 进入消息循环
#
# import os
# from kfactory.kcell import kdb,lay
#
# def gds_to_png_klayout(gds_path, png_path, resolution=2048):
#     """
#     使用 KLayout Python API 将 GDS 文件转换为 PNG 图片
#
#     参数:
#         gds_path: 输入的 GDS 文件路径
#         png_path: 输出的 PNG 文件路径
#         resolution: 输出图片的分辨率（宽度和高度，默认 2048x2048）
#     """
#     try:
#         # 1. 创建布局对象并加载 GDS 文件
#         layout = kdb.Layout()
#         layout.read(gds_path)
#
#         # 2. 创建视图对象
#         view = lay.LayoutView()
#
#         # 3. 显示布局（选择第一个顶层单元）
#         cell = layout.top_cell()
#         view.cell = cell
#
#         # 4. 设置显示选项
#         view.max_hier = 1  # 显示层级深度
#         view.set_config("background-color", "#FFFFFF")  # 白色背景
#
#         # 5. 自动缩放以适合内容
#         view.zoom_fit()
#
#         # 6. 保存为图片
#         view.save_image(png_path, resolution, resolution)
#
#         print(f"成功将 {gds_path} 转换为 {png_path}")
#         return True
#
#     except Exception as e:
#         print(f"转换失败: {str(e)}")
#         return False
#
#
# # 使用示例
# gds_file = r"C:\Windows\System32\CSU_PDK\csufactory\all_output_files\gds\awg.gds"
# png_file = os.path.splitext(gds_file)[0] + "_klayout.png"
# gds_to_png_klayout(gds_file, png_file, resolution=4096)