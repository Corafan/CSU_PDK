# import inspect  # 添加这行
# from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QLineEdit,
#                             QPushButton, QWidget, QLabel, QComboBox, QFormLayout)
# from PyQt5.QtCore import Qt
# import csufactory
# import importlib
#
# class DeviceGeneratorGUI(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("CSFactory 光子器件生成系统")
#         self.resize(800, 600)
#
#         # 初始化UI
#         self.init_ui()
#         self.current_component = None
#
#         self.preview = PreviewWindow()
#         layout.addWidget(self.preview)
#
#
#
#     def init_ui(self):
#         layout = QVBoxLayout()
#
#         # 器件选择
#         self.component_combo = QComboBox()
#         self.component_combo.addItems(csufactory.list_components())
#         self.component_combo.currentTextChanged.connect(self.load_component_params)
#         layout.addWidget(QLabel("选择器件:"))
#         layout.addWidget(self.component_combo)
#
#         # 参数表单（动态生成）
#         self.param_form = QFormLayout()
#         self.param_widgets = {}
#         layout.addLayout(self.param_form)
#
#         # 生成按钮
#         self.generate_btn = QPushButton("生成器件 (Ctrl+G)")
#         self.generate_btn.setShortcut("Ctrl+G")
#         self.generate_btn.clicked.connect(self.generate_device)
#         layout.addWidget(self.generate_btn)
#
#         # 容器
#         container = QWidget()
#         container.setLayout(layout)
#         self.setCentralWidget(container)
#
#         # 首次加载默认器件参数
#         self.load_component_params()
#
#     def load_component_params(self):
#         """动态加载所选器件的参数表单"""
#         # 清空旧表单
#         while self.param_form.rowCount() > 0:
#             self.param_form.removeRow(0)
#         self.param_widgets.clear()
#
#         # 获取器件模块
#         component_name = self.component_combo.currentText()
#         module = importlib.import_module(f"csufactory.components.{component_name}")
#
#         # 获取器件函数和参数注解
#         component_func = getattr(module, component_name)
#         sig = inspect.signature(component_func)
#
#         # 为每个参数创建输入控件
#         for name, param in sig.parameters.items():
#             if name == 'self': continue
#
#             label = QLabel(f"{name}:")
#             input_widget = QLineEdit(str(param.default) if param.default != param.empty else "")
#             input_widget.setPlaceholderText(f"Type: {param.annotation.__name__}")
#             self.param_form.addRow(label, input_widget)
#             self.param_widgets[name] = input_widget
#
#     def generate_device(self):
#         """生成器件并保存"""
#         try:
#             component_name = self.component_combo.currentText()
#             module = importlib.import_module(f"csufactory.components.{component_name}")
#             component_func = getattr(module, component_name)
#
#             # 收集参数
#             params = {}
#             for name, widget in self.param_widgets.items():
#                 value = widget.text()
#                 # 基本类型转换（实际项目需更健壮的验证）
#                 if value.isdigit():
#                     params[name] = int(value)
#                 elif value.replace('.', '', 1).isdigit():
#                     params[name] = float(value)
#                 else:
#                     params[name] = value
#
#             # 生成器件
#             component = component_func(**params)
#             gds_path = f"{component_name}_custom.gds"
#             component.write_gds(gds_path)
#
#             # 显示成功消息
#             self.statusBar().showMessage(f"成功生成器件并保存到 {gds_path}", 5000)
#             self.preview.update_preview(component)
#
#         except Exception as e:
#             self.statusBar().showMessage(f"错误: {str(e)}", 5000)
#
#
# def run_gui():
#     import sys
#     app = QApplication(sys.argv)
#     window = DeviceGeneratorGUI()
#     window.show()
#     sys.exit(app.exec_())

import inspect
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QLineEdit,
                             QPushButton, QWidget, QLabel, QComboBox)
import csufactory as cf

class DeviceGenerator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("光子器件生成器")

        # 组件列表（从 csufactory的components中 自动获取）
        self.available_components = [
            "arc",
            "awg",
            "Bend",
            "coupler",
            "crossing",
            "grating",
            "MMI",
            "ring_coupler",
            "ring_resonator",
            "Sbend",
            "StarCoupler",
            "YBranch",
            "ybranch_new",
        ]

        # 创建UI
        self.layout = QVBoxLayout()

        # 器件选择
        self.component_dropdown = QComboBox()
        self.component_dropdown.addItems(self.available_components)
        self.layout.addWidget(QLabel("选择器件类型:"))
        self.layout.addWidget(self.component_dropdown)

        # 参数输入（动态生成）
        self.param_inputs = {}
        self.layout.addWidget(QLabel("输入参数:"))

        # 生成按钮
        self.generate_btn = QPushButton("生成器件")
        self.generate_btn.clicked.connect(self.generate_device)
        self.layout.addWidget(self.generate_btn)

        # 预览区域
        self.preview_label = QLabel("预览将显示在这里")
        self.layout.addWidget(self.preview_label)

        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

    def generate_device(self):
        """根据用户输入生成器件"""
        component_name = self.component_dropdown.currentText()
        try:
            # 获取参数化函数
            component_func = getattr(cf.components, component_name)

            # 从UI收集参数（实际开发中需要更复杂的参数映射）
            params = {
                "length": float(self.param_inputs["length"].text()),
                "width": float(self.param_inputs["width"].text()),
                # 其他参数...
            }

            # 生成器件
            component = component_func(**params)

            # 保存GDS
            component.write_gds(f"{component_name}_custom.gds")

            # 显示预览（需要转换为图片）
            self.show_preview(component)

        except Exception as e:
            self.preview_label.setText(f"错误: {str(e)}")

    def show_preview(self, component):
        """简单预览（实际可用matplotlib渲染）"""
        # 这里简化为文本显示，实际应渲染器件图像
        info = f"已生成: {component.name}\n" \
               f"面积: {component.area()} um²\n" \
               f"端口: {list(component.ports.keys())}"
        self.preview_label.setText(info)

    def update_parameter_fields(self, component_name):
        """根据器件类型动态创建参数输入框"""
        # 清空旧输入
        for input_widget in self.param_inputs.values():
            self.layout.removeWidget(input_widget)
            input_widget.deleteLater()
        self.param_inputs.clear()

        # 获取器件函数的参数信息
        component_func = getattr(cf.components, component_name)
        signature = inspect.signature(component_func)

        # 为每个参数创建输入框
        for param_name, param in signature.parameters.items():
            if param_name == "kwargs": continue

            label = QLabel(f"{param_name} ({param.annotation.__name__}):")
            input_box = QLineEdit(str(param.default) if param.default != param.empty else "")
            self.layout.addWidget(label)
            self.layout.addWidget(input_box)
            self.param_inputs[param_name] = input_box


app = QApplication([])
window = DeviceGenerator()
window.show()
app.exec_()