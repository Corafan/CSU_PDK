from gdsfactory.technology.layer_views import test_load_lyp
from gdsfactory.technology import LayerViews

if __name__ == "__main__":
    test_load_lyp()
    # import gdsfactory as gf
    from gdsfactory.generic_tech import get_generic_pdk

    PDK = get_generic_pdk()
    LAYER_VIEWS = PDK.layer_views                         #从之前保存的 YAML 文件中加载层视图
    LAYER_VIEWS.to_lyp("C:\Windows\System32\CSU_PDK\csufactory\generic_tech\klayout\salt\layer.lyp")  #取消注释可用，将layer_views.yaml转化成了lyp
    LAYER_VIEWS.to_yaml("C:\Windows\System32\CSU_PDK\csufactory\generic_tech\layer_views.yaml")       #取消注释可用，生成的文件与layer_views.yaml相同
    LAYER_VIEWS = LayerViews(filepath="C:\Windows\System32\CSU_PDK\csufactory\generic_tech\layer_views.yaml")
    #从之前保存的 YAML 文件中加载层视图
    c = LAYER_VIEWS.preview_layerset()                    #生成每层的预示图
    c.show()
    #print(LAYER_VIEWS.layer_views["Doping"])             #打印特定层的信息

