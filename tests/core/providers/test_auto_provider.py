import importlib
import pytest

from web3.auto import (
    infura,
)
from web3.exceptions import (
    InfuraKeyNotFound,
)
from web3.providers import (
    HTTPProvider,
    IPCProvider,
    WebsocketProvider,
)
from web3.providers.auto import (
    load_provider_from_environment,
)


@pytest.mark.parametrize(
    'uri, expected_type, expected_attrs',
    (
        ('', type(None), {}),
        ('http://1.2.3.4:5678', HTTPProvider, {'endpoint_uri': 'http://1.2.3.4:5678'}),
        ('https://node.ontheweb.com', HTTPProvider, {'endpoint_uri': 'https://node.ontheweb.com'}),
        ('file:///root/path/to/file.ipc', IPCProvider, {'ipc_path': '/root/path/to/file.ipc'}),
        ('ws://1.2.3.4:5679', WebsocketProvider, {'endpoint_uri': 'ws://1.2.3.4:5679'})
    ),
)
def test_load_provider_from_env(monkeypatch, uri, expected_type, expected_attrs):
    monkeypatch.setenv('WEB3_PROVIDER_URI', uri)
    provider = load_provider_from_environment()
    assert isinstance(provider, expected_type)
    for attr, val in expected_attrs.items():
        assert getattr(provider, attr) == val


def test_web3_auto_infura_empty_key(monkeypatch, caplog):
    monkeypatch.setenv('WEB3_INFURA_SCHEME', 'https')
    monkeypatch.setenv('WEB3_INFURA_API_KEY', '')
    monkeypatch.setenv('WEB3_INFURA_PROJECT_ID', '')

    with pytest.raises(InfuraKeyNotFound):
        importlib.reload(infura)


def test_web3_auto_infura_deleted_key(monkeypatch, caplog):
    monkeypatch.setenv('WEB3_INFURA_SCHEME', 'https')
    importlib.reload(infura)
    monkeypatch.delenv('WEB3_INFURA_API_KEY', raising=False)
    monkeypatch.delenv('WEB3_INFURA_PROJECT_ID', raising=False)

    with pytest.raises(InfuraKeyNotFound):
        importlib.reload(infura)


def test_web3_auto_infura_websocket_empty_key(monkeypatch, caplog):
    monkeypatch.setenv('WEB3_INFURA_API_KEY', '')
    monkeypatch.setenv('WEB3_INFURA_PROJECT_ID', '')

    with pytest.raises(InfuraKeyNotFound):
        importlib.reload(infura)


@pytest.mark.parametrize('environ_name', ['WEB3_INFURA_API_KEY', 'WEB3_INFURA_PROJECT_ID'])
def test_web3_auto_infura_websocket_deleted_key(monkeypatch, caplog, environ_name):
    monkeypatch.setenv(environ_name, '1234')
    importlib.reload(infura)

    monkeypatch.delenv('WEB3_INFURA_API_KEY', raising=False)
    monkeypatch.delenv('WEB3_INFURA_PROJECT_ID', raising=False)

    with pytest.raises(InfuraKeyNotFound):
        importlib.reload(infura)


def test_web3_auto_infura_websocket_deleted_key_api_key(monkeypatch, caplog):
    monkeypatch.delenv('WEB3_INFURA_API_KEY', raising=False)
    monkeypatch.delenv('WEB3_INFURA_PROJECT_ID', raising=False)

    with pytest.raises(InfuraKeyNotFound):
        importlib.reload(infura)


@pytest.mark.parametrize('environ_name', ['WEB3_INFURA_API_KEY', 'WEB3_INFURA_PROJECT_ID'])
def test_web3_auto_infura(monkeypatch, caplog, environ_name):
    monkeypatch.setenv('WEB3_INFURA_SCHEME', 'https')
    API_KEY = 'aoeuhtns'
    monkeypatch.delenv('WEB3_INFURA_API_KEY', raising=False)
    monkeypatch.delenv('WEB3_INFURA_PROJECT_ID', raising=False)
    monkeypatch.setenv(environ_name, API_KEY)
    expected_url = 'https://%s/v3/%s' % (infura.INFURA_MAINNET_DOMAIN, API_KEY)

    importlib.reload(infura)
    assert len(caplog.record_tuples) == 0

    w3 = infura.w3
    assert isinstance(w3.provider, HTTPProvider)
    assert getattr(w3.provider, 'endpoint_uri') == expected_url


@pytest.mark.parametrize('environ_name', ['WEB3_INFURA_API_KEY', 'WEB3_INFURA_PROJECT_ID'])
def test_web3_auto_infura_websocket_default(monkeypatch, caplog, environ_name):
    monkeypatch.delenv('WEB3_INFURA_API_KEY', raising=False)
    monkeypatch.delenv('WEB3_INFURA_PROJECT_ID', raising=False)
    monkeypatch.setenv('WEB3_INFURA_SCHEME', 'wss')
    API_KEY = 'aoeuhtns'
    monkeypatch.setenv(environ_name, API_KEY)
    expected_url = 'wss://%s/ws/v3/%s' % (infura.INFURA_MAINNET_DOMAIN, API_KEY)

    importlib.reload(infura)
    assert len(caplog.record_tuples) == 0

    w3 = infura.w3
    assert isinstance(w3.provider, WebsocketProvider)
    assert getattr(w3.provider, 'endpoint_uri') == expected_url
