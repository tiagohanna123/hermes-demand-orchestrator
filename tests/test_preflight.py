"""Tests for preflight module — preflight_classify()."""

from __future__ import annotations

import pytest

from hermes_demand_orchestrator.preflight import (
    CASCADE_DEEP_KEYWORDS,
    CASCADE_KEYWORDS,
    DIRECT_KEYWORDS,
    PreflightResult,
    preflight_classify,
)


class TestDirectKeywords:
    """Each DIRECT_KEYWORD alone should return 'direct'."""

    @pytest.mark.parametrize("keyword", DIRECT_KEYWORDS)
    def test_each_direct_keyword(self, keyword: str) -> None:
        assert preflight_classify(keyword) == "direct"

    @pytest.mark.parametrize(
        "description",
        [
            "listar usuarios do sistema",
            "mostrar relatorio de vendas",
            "ver status do servidor",
            "qual e o horario atual",
            "como funciona o modulo de cascade",
            "ajustar padding do botao",
            "corrigir typo no texto",
            "remover arquivo temporario",
            "mudar cor do fundo",
            "editar a fonte do titulo",
        ],
    )
    def test_direct_in_full_sentence(self, description: str) -> None:
        assert preflight_classify(description) == "direct"

    def test_direct_keyword_wins_over_cascade(self) -> None:
        """Direct keyword takes priority even when cascade keywords are present."""
        assert preflight_classify("listar deploy test") == "direct"


class TestCascadeKeywords:
    """Single cascade keyword (that is not deep) should return 'cascade'."""

    # Deep keywords also appear in CASCADE_KEYWORDS, so test only
    # keywords that are *exclusively* cascade (not in deep list).
    EXCLUSIVE_CASCADE = sorted(
        set(CASCADE_KEYWORDS) - set(CASCADE_DEEP_KEYWORDS)
    )

    @pytest.mark.parametrize("keyword", EXCLUSIVE_CASCADE)
    def test_each_cascade_keyword(self, keyword: str) -> None:
        assert preflight_classify(keyword) == "cascade"

    @pytest.mark.parametrize(
        "description",
        [
            "precisamos criar um novo modulo",
            "configurar o ambiente de producao",
            "implementar a feature de login",
            "instalar as dependencias do projeto",
            "migrar o banco de dados",
            "publicar a nova versao",
            "fazer release da versao 2.0",
        ],
    )
    def test_cascade_in_full_sentence(self, description: str) -> None:
        assert preflight_classify(description) == "cascade"


class TestCascadeDeep:
    """Two or more deep keywords should return 'cascade-deep'."""

    @pytest.mark.parametrize(
        "description",
        [
            "deploy com test",
            "test e refatorar tudo",
            "deploy e refatorar componente",
            "refatorar o deploy do servico",
            "test deploy refatorar",
        ],
    )
    def test_two_or_more_deep_keywords(self, description: str) -> None:
        assert preflight_classify(description) == "cascade-deep"

    def test_single_deep_keyword_is_cascade(self) -> None:
        """A single deep keyword (no second deep match) → 'cascade'."""
        assert preflight_classify("deploy da aplicacao") == "cascade"

    def test_many_cascade_keywords_but_only_one_deep(self) -> None:
        """Multiple cascade keywords but only one deep → 'cascade', not deep."""
        assert preflight_classify("deploy criar build") == "cascade"


class TestEdgeCases:
    """Edge cases: empty, case, substrings, mixed."""

    def test_empty_description(self) -> None:
        assert preflight_classify("") == "direct"

    def test_case_insensitivity(self) -> None:
        assert preflight_classify("LISTAR") == "direct"
        assert preflight_classify("DePlOy") == "cascade"
        assert preflight_classify("DEPLOY E TEST") == "cascade-deep"

    def test_substring_does_not_false_match(self) -> None:
        """'teste' or 'testing' should not match keyword 'test' via \\b boundary."""
        assert preflight_classify("teste") == "direct"
        assert preflight_classify("testing") == "direct"
        assert preflight_classify("deployer") == "direct"

    def test_keyword_in_middle_of_sentence(self) -> None:
        assert preflight_classify("voce pode listar todos os usuarios?") == "direct"
        assert preflight_classify("precisamos fazer deploy hoje") == "cascade"
        assert preflight_classify("vou deploy e test agora") == "cascade-deep"

    def test_punctuation_around_keyword(self) -> None:
        """Keywords with surrounding punctuation should still match via \\b."""
        assert preflight_classify("listar!") == "direct"
        assert preflight_classify("(deploy)") == "cascade"
        assert preflight_classify("test? sim, deploy!") == "cascade-deep"

    def test_direct_plus_deep_returns_direct(self) -> None:
        """Direct keyword wins even against cascade-deep."""
        assert preflight_classify("status do deploy com test") == "direct"
        assert preflight_classify("ver deploy test refatorar") == "direct"

    def test_multiple_spaces(self) -> None:
        assert preflight_classify("deploy    test") == "cascade-deep"
        assert preflight_classify("listar   usuarios") == "direct"

    def test_newlines_and_tabs(self) -> None:
        assert preflight_classify("deploy\ntest") == "cascade-deep"
        assert preflight_classify("listar\tusuarios") == "direct"

    def test_unknown_description(self) -> None:
        """No keywords at all defaults to 'direct'."""
        assert preflight_classify("bom dia") == "direct"
        assert preflight_classify("qualquer coisa aleatoria") == "direct"

    def test_return_type(self) -> None:
        result = preflight_classify("deploy test")
        assert result in ("direct", "cascade", "cascade-deep")
        # Verify it matches the Literal type alias
        _verify: PreflightResult = result
        assert _verify == "cascade-deep"
