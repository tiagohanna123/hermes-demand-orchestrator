"""Tests for the Router module — multi-project detection by keywords."""
from __future__ import annotations

import pytest

from hermes_demand_orchestrator.router import detect_project


class TestDetectProject:
    """Tests for detect_project()."""

    def test_detect_portfolio(self):
        """Portfolio keywords should detect portfolio-dev."""
        assert detect_project("portfolio pessoal") == "portfolio-dev"
        assert detect_project("tiagohanna.com") == "portfolio-dev"
        assert detect_project("site pessoal do tiago") == "portfolio-dev"

    def test_detect_sarau(self):
        """Sarau keywords should detect sarau-secreto."""
        assert detect_project("sarau secreto") == "sarau-secreto"
        assert detect_project("sarau de poesia") == "sarau-secreto"
        assert detect_project("festival cultural") == "sarau-secreto"
        assert detect_project("sarau") == "sarau-secreto"

    def test_detect_music_connect(self):
        """Music Connect keywords should detect music-connect."""
        assert detect_project("music connect app") == "music-connect"
        assert detect_project("khem.app backend") == "music-connect"
        assert detect_project("khem api") == "music-connect"

    def test_detect_hermes_terminal(self):
        """Hermes Terminal keywords should detect hermes-terminal."""
        assert detect_project("hermes terminal") == "hermes-terminal"
        assert detect_project("terminal app") == "hermes-terminal"
        assert detect_project("dashboard de monitoramento") == "hermes-terminal"
        assert detect_project("chat bot") == "hermes-terminal"

    def test_detect_hermes_agent_soul(self):
        """Agent Soul keywords should detect hermes-agent-soul."""
        assert detect_project("hermes agent soul") == "hermes-agent-soul"
        assert detect_project("agent soul integration") == "hermes-agent-soul"
        assert detect_project("hermes-soul config") == "hermes-agent-soul"

    def test_detect_hermes_credential(self):
        """Credential vault keywords should detect hermes-credential."""
        assert detect_project("hermes credential") == "hermes-credential"
        assert detect_project("credential vault") == "hermes-credential"
        assert detect_project("vault de senhas") == "hermes-credential"

    def test_detect_hermes_broker(self):
        """Broker keywords should detect hermes-broker."""
        assert detect_project("hermes broker setup") == "hermes-broker"
        assert detect_project("message broker") == "hermes-broker"
        assert detect_project("fila de mensagens") == "hermes-broker"

    def test_detect_hermes_orchestrator(self):
        """Orchestrator keywords should detect hermes-demand-orchestrator."""
        assert detect_project("orquestrador de demandas") == "hermes-demand-orchestrator"
        assert detect_project("orchestrator") == "hermes-demand-orchestrator"
        assert detect_project("demanda urgente") == "hermes-demand-orchestrator"
        assert detect_project("demand pipeline") == "hermes-demand-orchestrator"
        assert detect_project("write-ahead log") == "hermes-demand-orchestrator"
        assert detect_project("cascade") == "hermes-demand-orchestrator"
        assert detect_project("journal") == "hermes-demand-orchestrator"

    def test_case_insensitive(self):
        """Detection should be case insensitive."""
        assert detect_project("SARAU SECRETO") == "sarau-secreto"
        assert detect_project("Portfolio") == "portfolio-dev"
        assert detect_project("MUSIC CONNECT") == "music-connect"
        assert detect_project("KHEM") == "music-connect"
        assert detect_project("HerMes TerMiNaL") == "hermes-terminal"

    def test_no_project_found(self):
        """Descriptions without matching keywords should return None."""
        assert detect_project("comprar leite") is None
        assert detect_project("agendar reunião") is None
        assert detect_project("texto aleatório sem relação") is None

    def test_empty_string(self):
        """Empty string should return None."""
        assert detect_project("") is None

    def test_whitespace_only(self):
        """Only whitespace should return None."""
        assert detect_project("   ") is None

    @pytest.mark.parametrize(
        ("desc", "expected"),
        [
            # Longest keyword wins — "sarau secreto" (12) > "sarau" (5)
            ("sarau secreto festival", "sarau-secreto"),
            # "site pessoal" (13) > "portfolio" (9)
            ("portfolio site pessoal", "portfolio-dev"),
            # "hermes terminal" (14) > "terminal" (8) and "dashboard" (9)
            ("hermes terminal dashboard", "hermes-terminal"),
            # "khem" (4) vs "music connect" (13) — longer is "music connect"
            ("khem music connect", "music-connect"),
            # "sarau secreto" (12) > "sarau" (5)
            ("organizar sarau secreto de poesia", "sarau-secreto"),
        ],
    )
    def test_longest_keyword_wins(self, desc: str, expected: str):
        """When multiple keywords match across projects, the longest one wins."""
        assert detect_project(desc) == expected

    def test_word_boundary_matching(self):
        """Keywords should match only as whole words via \\b regex boundaries."""
        # "terminal" should NOT match inside "determinall" (no word boundary)
        assert detect_project("determinall") is None
        # "khem" should NOT match inside "khemistry"
        assert detect_project("khemistry") is None
        # But "khem" should match in "khem.app" (dot is word boundary)
        assert detect_project("khem.app") == "music-connect"
        # "portfolio" should NOT match inside "portfolios"
        assert detect_project("portfolios") is None
        # "terminal" should NOT match inside "terminalize"
        assert detect_project("terminalize") is None
