from csufactory.csupdk.layer_map import LayerMap

def test_layer_map():
    assert LayerMap.get_layer("WG") == (200, 0)
    assert LayerMap.get_layer("Metal_Al") == (13, 0)
    assert LayerMap.get_layer("MOPT") is None  # 不存在的层应返回 None

if __name__ == "__main__":
    test_layer_map()
    print("LayerMap 测试通过！")
