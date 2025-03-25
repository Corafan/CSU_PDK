"""测试LayerViews这个类，看是否可以引用自己的LayerViews"""

#导入Class LayerViews
from gdsfactory.technology import LayerViews

#将LayerViews改为自己的路径
LAYER_VIEWS = LayerViews(filepath="C:\Windows\System32\CSU_PDK\csufactory\generic_tech\layer_views.yaml")
# 从之前保存的 YAML 文件中加载层视图
c = LAYER_VIEWS.preview_layerset()  # 生成每层的预示图
c.show()

#测试结果显示，可以引用自己的LayerViews