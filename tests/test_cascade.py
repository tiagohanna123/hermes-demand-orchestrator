"""Tests for cascade module — classify_task()."""

from __future__ import annotations

import pytest

from hermes_demand_orchestrator.cascade import (
    CASCADE_WORDS,
    DEEP_WORDS,
    DIRECT_WORDS,
    CascadeDecision,
    classify_task,
)


class TestDirectKeywords:
    """Each DIRECT_WORD alone should return 'direct'."""

    @pytest.mark.parametrize("word", sorted(DIRECT_WORDS))
    def test_each_direct_word(self, word: str) -> None:
        assert classify_task(word) == "direct"

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
            "mudar a configuracao",
            "editar o arquivo de config",
        ],
    )
    def test_direct_in_full_sentence(self, description: str) -> None:
        assert classify_task(description) == "direct"

    def test_direct_keyword_wins_over_cascade(self) -> None:
        """Direct keyword takes priority even when cascade words are present."""
        assert classify_task("listar deploy test") == "direct"


class TestCascadeKeywords:
    """Single cascade word (not deep) should return 'cascade'."""

    EXCLUSIVE_CASCADE = sorted(set(CASCADE_WORDS) - set(DEEP_WORDS))

    @pytest.mark.parametrize("word", EXCLUSIVE_CASCADE)
    def test_each_cascade_word(self, word: str) -> None:
        assert classify_task(word) == "cascade"

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
        assert classify_task(description) == "cascade"


class TestCascadeDeep:
    """Two or more deep words should return 'cascade-deep'."""

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
    def test_two_or_more_deep_words(self, description: str) -> None:
        assert classify_task(description) == "cascade-deep"

    def test_single_deep_word_is_cascade(self) -> None:
        """A single deep word (no second deep match) → 'cascade'."""
        assert classify_task("deploy da aplicacao") == "cascade"

    def test_many_cascade_words_but_only_one_deep(self) -> None:
        """Multiple cascade words but only one deep → 'cascade', not deep."""
        assert classify_task("deploy criar build") == "cascade"


class TestEdgeCases:
    """Edge cases: empty, case, substrings, mixed."""

    def test_empty_description(self) -> None:
        assert classify_task("") == "direct"

    def test_case_insensitivity(self) -> None:
        assert classify_task("LISTAR") == "direct"
        assert classify_task("DePlOy") == "cascade"
        assert classify_task("DEPLOY E TEST") == "cascade-deep"

    def test_substring_does_not_false_match(self) -> None:
        """
        classify_task uses set(description.lower().split()), which splits
        on whitespace only. 'teste' != 'test', so no false match.
        """
        assert classify_task("teste") == "direct"
        assert classify_task("testing") == "direct"
        assert classify_task("deployer") == "direct"

    def test_keyword_in_middle_of_sentence(self) -> None:
        assert classify_task("voce pode listar todos os usuarios?") == "direct"
        assert classify_task("precisamos fazer deploy hoje") == "cascade"
        assert classify_task("vou deploy e test agora") == "cascade-deep"

    def test_punctuation_attached_to_keyword(self) -> None:
        """
        split() treats punctuation as part of the token, so
        'listar!' != 'listar' → no match.
        This is a known limitation of the simple split approach.
        """
        assert classify_task("listar!") == "direct"
        assert classify_task("(deploy)") == "direct"  # '(deploy)' != 'deploy'
        assert classify_task("test?") == "direct"

    def test_direct_plus_deep_returns_direct(self) -> None:
        """Direct word wins even against cascade-deep."""
        assert classify_task("status do deploy com test") == "direct"
        assert classify_task("ver deploy test refatorar") == "direct"

    def test_multiple_spaces(self) -> None:
        """Excess whitespace is collapsed by split()."""
        assert classify_task("deploy    test") == "cascade-deep"
        assert classify_task("listar   usuarios") == "direct"

    def test_newlines_and_tabs(self) -> None:
        """split() splits on any whitespace including \\n and \\t."""
        assert classify_task("deploy\ntest") == "cascade-deep"
        assert classify_task("listar\tusuarios") == "direct"

    def test_unknown_description(self) -> None:
        """No keywords at all defaults to 'direct'."""
        assert classify_task("bom dia") == "direct"
        assert classify_task("qualquer coisa aleatoria") == "direct"

    def test_return_type(self) -> None:
        result = classify_task("deploy test")
        assert result in ("direct", "cascade", "cascade-deep")
        # Verify it matches the Literal type alias
        _verify: CascadeDecision = result
        assert _verify == "cascade-deep"

    def test_word_order_does_not_matter(self) -> None:
        assert classify_task("test deploy") == "cascade-deep"
        assert classify_task("refatorar test deploy criar") == "cascade-deep"
