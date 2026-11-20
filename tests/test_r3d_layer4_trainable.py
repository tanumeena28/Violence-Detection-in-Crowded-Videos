def test_trainable():
    layers = {"layer3": False, "layer4": True}
    assert layers["layer4"]
