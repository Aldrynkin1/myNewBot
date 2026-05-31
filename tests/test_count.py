from app.utils.count.count import check_winner


def test_check_winner_prefers_closer_answer():
    result = check_winner(2.1862464183381087, 1, 2.0, 2, 2.5)
    assert result["Победитель: "] == 1


def test_check_winner_returns_tie_for_equal_distance():
    result = check_winner(2.0, 1, 1.5, 2, 2.5)
    assert result["Победитель: "] == 0
