import pytest
from src.evaluator import text_sim


def test_text_sim_identical_tokens():
    assert text_sim("Buy milk", "buy milk") == 1.0


def test_text_sim_order_insensitive():
    assert text_sim("buy milk", "milk buy") == 1.0


def test_text_sim_partial_overlap():
    score = text_sim("buy milk today", "buy milk")
    assert score == pytest.approx(0.8)


def test_text_sim_no_overlap():
    assert text_sim("send invoice", "book travel") == 0.0


def test_text_sim_ignores_punctuation():
    assert text_sim("email, Bob!", "email bob") == 1.0
