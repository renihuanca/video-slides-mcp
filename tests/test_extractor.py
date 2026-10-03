from video_slides_mcp.extractor import format_timestamp


def test_format_timestamp():
    assert format_timestamp(0) == "00:00:00.000"
    assert format_timestamp(61.25) == "00:01:01.250"
