from gdsfactory.technology import LayerViews

if __name__ == "__main__":


    layer_views_path = "C:\Windows\System32\CSU_PDK\csufactory\generic_tech\layer_views.yaml"
    layer_lyp_path = "C:\Windows\System32\CSU_PDK\csufactory\generic_tech\klayout\salt\layer.lyp"
    #定义LayerViews路径：
    LAYER_VIEWS = LayerViews(filepath=layer_views_path)
    print(f"已从{layer_views_path}中获取层信息")
    LAYER_VIEWS.to_lyp(filepath=layer_lyp_path)  #取消注释可用，将layer_views.yaml转化成了lyp
    print(f"将层信息转为lyp文件保存至{layer_lyp_path}")
    #这个不需要了，因为layerViews是从自己的YAML中导入的，所以只需要生成lyp即可
    # LAYER_VIEWS.to_yaml("C:\Windows\System32\CSU_PDK\csufactory\generic_tech\layer_views.yaml")       #取消注释可用，生成的文件与layer_views.yaml相同

    #从之前保存的 YAML 文件中加载层视图
    c = LAYER_VIEWS.preview_layerset()                    #生成每层的预示图
    c.show()
    #print(LAYER_VIEWS.layer_views["Doping"])             #打印特定层的信息


# #版本1：从gdsfactory的默认路径获取layer_views
# from gdsfactory.technology.layer_views import test_load_lyp
# from gdsfactory.technology import LayerViews
#
# if __name__ == "__main__":
#     test_load_lyp()
#     # import gdsfactory as gf
#     from gdsfactory.generic_tech import get_generic_pdk
#
#     PDK = get_generic_pdk()
#     LAYER_VIEWS = PDK.layer_views                         #从之前保存的 YAML 文件中加载层视图（默认路径）
#     LAYER_VIEWS.to_lyp("C:\Windows\System32\CSU_PDK\csufactory\generic_tech\klayout\salt\layer.lyp")  #将layer_views.yaml转化成了lyp
#     LAYER_VIEWS.to_yaml("C:\Windows\System32\CSU_PDK\csufactory\generic_tech\layer_views.yaml")       #生成的layer_views.yaml文件与导入的layerviews相同
#     #修改路径为自己的layerviews
#     LAYER_VIEWS = LayerViews(filepath="C:\Windows\System32\CSU_PDK\csufactory\generic_tech\layer_views.yaml")
#     #从自己的YAML文件中加载层视图
#     c = LAYER_VIEWS.preview_layerset()                    #生成每层的预示图
#     c.show()
#     #print(LAYER_VIEWS.layer_views["Doping"])             #打印特定层的信息