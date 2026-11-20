def test_conf_bounds():
    conf = [max(0.0, min(1.0, x)) for x in [1.2, -0.1]]
    assert conf[0] == 1.0 and conf[1] == 0.0
