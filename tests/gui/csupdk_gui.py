import sys
import os
import importlib
import inspect
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QPushButton, QComboBox, QLineEdit, QFileDialog
)
import csufactory.components as components  # 你的 PDK 组件库
import gdsfactory as gf


class CSUDesigner(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("CSU PDK 器件生成器")
        self.setGeometry(100, 100, 500, 300)

        # 器件选择
        self.device_label = QLabel("选择器件:")
        self.device_combo = QComboBox()
        self.device_combo.addItems(self.list_components())
        self.device_combo.currentTextChanged.connect(self.load_parameters)

        # 参数输入区
        self.param_layout = QVBoxLayout()

        # 生成 & 导出按钮
        self.generate_button = QPushButton("生成 GDS")
        self.generate_button.clicked.connect(self.generate_gds)

        self.save_button = QPushButton("保存 GDS")
        self.save_button.setEnabled(False)
        self.save_button.clicked.connect(self.save_gds)

        # 布局
        layout = QVBoxLayout()
        layout.addWidget(self.device_label)
        layout.addWidget(self.device_combo)
        layout.addLayout(self.param_layout)
        layout.addWidget(self.generate_button)
        layout.addWidget(self.save_button)
        self.setLayout(layout)

        self.selected_component = None  # 当前选中的器件
        self.component_params = {}  # 参数输入框字典

        self.load_parameters()  # 加载默认器件参数

    def list_components(self):
        """ 获取 components 目录下的所有器件 """
        comp_dir = os.path.dirname(components.__file__)
        return [
            f[:-3] for f in os.listdir(comp_dir)
            if f.endswith(".py") and f != "__init__.py"
        ]

    def load_parameters(self):
        """ 根据选中的器件，动态创建参数输入框 """
        for i in reversed(range(self.param_layout.count())):
            self.param_layout.itemAt(i).widget().deleteLater()

        device_name = self.device_combo.currentText()
        module = importlib.import_module(f"csufactory.components.{device_name}")

        func = getattr(module, device_name, None)
        if func:
            sig = inspect.signature(func)
            self.selected_component = func
            self.component_params.clear()

            for param, value in sig.parameters.items():
                label = QLabel(f"{param}:")
                input_field = QLineEdit()
                input_field.setText(str(value.default) if value.default is not inspect.Parameter.empty else "")
                self.component_params[param] = input_field

                param_row = QHBoxLayout()
                param_row.addWidget(label)
                param_row.addWidget(input_field)
                self.param_layout.addLayout(param_row)

    # def generate_gds(self):
    #     """ 生成器件 GDS """
    #     if not self.selected_component:
    #         return
    #
    #     try:
    #         # 获取用户输入的参数
    #         params = {k: eval(v.text()) if v.text() else None for k, v in self.component_params.items()}
    #         component = self.selected_component(**params)
    #
    #         # 生成 GDS
    #         self.gds_path = f"{self.device_combo.currentText()}.gds"
    #         component.export_gds(self.gds_path)
    #
    #         self.save_button.setEnabled(True)
    #         print(f"GDS 生成成功: {self.gds_path}")
    #
    #     except Exception as e:
    #         print(f"生成失败: {e}")

    def generate_gds(self):
        """ 生成器件 GDS 并保存到指定路径 """
        if not self.selected_component:
            return

        try:
            # 获取用户输入的参数
            params = {k: eval(v.text()) if v.text() else None for k, v in self.component_params.items()}

            # 获取器件类并创建器件实例
            component = self.selected_component(**params)  # 动态生成器件实例

            # 检查组件是否是 gdsfactory 的 Component 实例
            if isinstance(component, gf.Component):
                # 指定保存 GDS 文件的目录和文件名
                gdspath = "C:/Windows/System32/CSU_PDK/csufactory/all_output_files/gds"
                os.makedirs(gdspath, exist_ok=True)  # 确保目录存在

                # 设置 GDS 文件路径
                gds_filename = f"{self.device_combo.currentText()}.gds"
                gds_file_path = os.path.join(gdspath, gds_filename)  # 完整的文件路径

                # 使用 gdsfactory 的 write_gds 方法保存 GDS 文件到指定路径
                component.write_gds(gds_file_path)  # 保存 GDS 文件

                # 展示 GDS 文件
                component.show(gdspath=gdspath)  # 展示 GDS 文件

                self.save_button.setEnabled(True)
                print(f"GDS 生成成功: {gds_file_path}")
            else:
                raise ValueError(f"组件 {self.device_combo.currentText()} 不是有效的 gdsfactory 组件")

        except Exception as e:
            print(f"生成失败: {e}")

    def save_gds(self):
        """ 让用户选择路径保存 GDS 文件 """
        file_path, _ = QFileDialog.getSaveFileName(self, "保存 GDS", "", "GDS Files (*.gds)")
        if file_path:
            os.rename(self.gds_path, file_path)
            print(f"GDS 已保存至 {file_path}")


# 运行 GUI
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CSUDesigner()
    window.show()
    sys.exit(app.exec())
