"""CSU_PDK - your package description. What is this package for?."""

__version__ = '0.0.1'

# 自动导入所有组件
from importlib import import_module
from pathlib import Path

__all__ = []
_component_names = []

# 动态加载 components/ 下的所有器件
components_dir = Path(__file__).parent / "components"
for py_file in components_dir.glob("*.py"):
    if py_file.name != "__init__.py":
        module_name = f"csufactory.components.{py_file.stem}"
        import_module(module_name)
        __all__.append(py_file.stem)
        _component_names.append(py_file.stem)

# 方便GUI获取器件列表
def list_components():
    return sorted(_component_names)