from pathlib import Path

SOURCE = (Path(__file__).resolve().parents[1] / "native/hybris_connect/hybris_connect.c").read_text()


def test_vuid_cameras_get_pc_client_post_live_sequence():
    live = SOURCE.index('"livestream.cgi?streamid=10&substream=2&"')
    params = SOURCE.index("send_cgi(client_write_cgi, client, VUID_PARAMS_COMMAND)")
    status = SOURCE.index("send_cgi(client_write_cgi, client, vuid_status_command)")
    light = SOURCE.index("send_cgi(client_write_cgi, client, VUID_LIGHT_COMMAND)")
    assert live < params < status < light
    assert '"get_status.cgi?vuid=%s&"' in SOURCE
    assert "if (stream_start_sent && vuid_status_command[0] != 0)" in SOURCE


def test_vuid_status_command_is_wiped_after_use():
    assert "memset(vuid_status_command, 0, sizeof(vuid_status_command));" in SOURCE
