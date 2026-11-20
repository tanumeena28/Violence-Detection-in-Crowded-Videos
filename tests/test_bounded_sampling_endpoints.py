def test_sampling_bounds():
    idx = [int(i * 100 / 31) for i in range(32)]
    assert len(idx) == 32 and idx[-1] == 100
