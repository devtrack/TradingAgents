from typer.testing import CliRunner

from cli import main as cli_main
from cli.utils import ModelInfo, ProviderInfo


class RecordingAuthClient:
    last_action = None

    def __init__(self, *_, **__):
        self.logged_out = False

    def login(self, open_browser=True):
        RecordingAuthClient.last_action = "login"

    def logout(self):
        RecordingAuthClient.last_action = "logout"

    def get_session(self):
        return "token"


def test_cli_login(monkeypatch):
    RecordingAuthClient.last_action = None
    monkeypatch.setattr(cli_main, "AuthClient", RecordingAuthClient)

    runner = CliRunner()
    result = runner.invoke(cli_main.app, ["login", "--no-open-browser"], prog_name="tradingagents")

    assert result.exit_code == 0
    assert "Authentification réussie" in result.output
    assert RecordingAuthClient.last_action == "login"


def test_cli_logout(monkeypatch):
    RecordingAuthClient.last_action = None
    monkeypatch.setattr(cli_main, "AuthClient", RecordingAuthClient)

    runner = CliRunner()
    result = runner.invoke(cli_main.app, ["logout"], prog_name="tradingagents")

    assert result.exit_code == 0
    assert "Déconnexion réussie" in result.output
    assert RecordingAuthClient.last_action == "logout"


def test_models_list(monkeypatch):
    RecordingAuthClient.last_action = None
    monkeypatch.setattr(cli_main, "AuthClient", RecordingAuthClient)

    providers = [
        ProviderInfo(
            id="openai",
            display_name="OpenAI",
            base_url="https://api.example.com",
            models=[ModelInfo(id="gpt", display_name="GPT", capabilities={"quick", "deep"})],
        )
    ]
    monkeypatch.setattr(cli_main, "load_model_catalog", lambda client=None: providers)

    runner = CliRunner()
    result = runner.invoke(cli_main.app, ["models", "list"], prog_name="tradingagents")

    assert result.exit_code == 0
    assert "OpenAI" in result.output
    assert "GPT" in result.output
