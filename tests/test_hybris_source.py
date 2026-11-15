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


def test_eye4_authentication_runs_after_login_before_live_or_probe():
    login = SOURCE.index("authenticated = login_response_received && login_result == 0;")
    eye4 = SOURCE.index("eye4_auth = eye4_authenticate(client_read, client_write_cgi, client);")
    probe = SOURCE.index("if (connected && authenticated && channel_probe)")
    live = SOURCE.index("if (connected && authenticated && live_mode)")
    assert login < eye4 < probe < live
    assert '"eye4_authentication.cgi?loginAccount=%s&loginToken=%s&"' in SOURCE


def test_account_token_is_wiped_and_dash_means_no_vuid():
    assert "memset(account_token, 0, strlen(account_token));" in SOURCE
    assert "memset(eye4_auth_command, 0, sizeof(eye4_auth_command));" in SOURCE
    assert 'strcmp(virtual_uid, "-") != 0' in SOURCE
