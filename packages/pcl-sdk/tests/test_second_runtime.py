from pcl_sdk.client import Client


def test_second_runtime_client_shape():
    c = Client("http://127.0.0.1:9", "tok")
    assert c.base.endswith("")
