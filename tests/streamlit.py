# from csufactory.gui.app import run_gui
# run_gui()
import streamlit as st
import importlib
import inspect
import os
import csufactory.components as components


# 获取所有组件（排除 __init__.py）
def list_components():
    comp_dir = os.path.dirname(components.__file__)
    comp_files = [
        f[:-3] for f in os.listdir(comp_dir) if f.endswith(".py") and f != "__init__.py"
    ]
    return comp_files


# 动态获取组件的参数
def get_component_params(component_name):
    module = importlib.import_module(f"csufactory.components.{component_name}")
    func = getattr(module, component_name, None)

    if func:
        sig = inspect.signature(func)
        params = {
            k: v.default if v.default is not inspect.Parameter.empty else None
            for k, v in sig.parameters.items()
        }
        return func, params
    return None, {}


# GUI 部分
st.title("CSU_PDK 器件生成器")

# 选择组件
components_list = list_components()
component_name = st.selectbox("选择器件:", components_list)

if component_name:
    # 获取组件参数
    func, params = get_component_params(component_name)

    if func:
        user_params = {}
        st.subheader(f"{component_name} 参数")

        for param, default in params.items():
            user_params[param] = st.text_input(param, str(default) if default else "")

        # 生成器件
        if st.button("生成 GDS"):
            try:
                # 将输入参数转换为合适的类型
                typed_params = {k: eval(v) if v else None for k, v in user_params.items()}
                component = func(**typed_params)

                # 导出 GDS
                gds_path = f"{component_name}.gds"
                component.export_gds(gds_path)

                st.success(f"成功生成 {component_name}.gds")
                with open(gds_path, "rb") as f:
                    st.download_button("下载 GDS", f, file_name=gds_path)

            except Exception as e:
                st.error(f"生成失败: {e}")
