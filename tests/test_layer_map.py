from csufactory.generic_tech.layer_map import CSULAYER

def test_layer_map():
    assert CSULAYER.get_layer("WG") == (200, 0)
    assert CSULAYER.get_layer("Metal_Al") == (13, 0)
    assert CSULAYER.get_layer("MOPT") is None  # 不存在的层应返回 None

if __name__ == "__main__":
    test_layer_map()
    print("LayerMap 测试通过！")
