import copy

import pytest

from base import LettersGameBase, CardType
from fakes import LettersGameFake


@pytest.fixture()
def standard_deck() -> list[CardType]:
    """
    Fixture that return a standard deck of Letters cards.
    Note: when laid out in a 3x4 tableau, all cards will
    have the letter "A" in them, so any three cards
    will be a fit (according to the fake rules, not according
    to the actual rules of Letters)
    """
    letters = ["A", "B", "C"]
    numbers = ["1", "2", "3"]
    colors = ["red", "green", "blue"]
    fonts = ["serif", "sans-serif", "monospace"]

    all_cards = [
        {"letter": letter, "number": number, "color": color, "font": font}
        for letter in letters
        for number in numbers
        for color in colors
        for font in fonts
    ]

    return all_cards


@pytest.fixture()
def twelve_cards() -> list[CardType]:
    """
    Fixture that returns a deck with twelve cards that,
    when laid out in a 3x4 grid, will have at least the
    following cards that are *not* a fit:

    - (0, 0), (0, 1), and (0, 2)
    - (0, 0), (1, 0), and (2, 0)
    - (2, 0), (2, 1), and (2, 2) <- This is an example of
      three cards where the cards are pairwise a fit (they
      have at least one feature with the same value), but not
      a fit when considered as a group of three.
    """
    return [
        {"letter": "A", "number": "1", "color": "red", "font": "serif"},
        {"letter": "B", "number": "2", "color": "green", "font": "sans-serif"},
        {"letter": "B", "number": "2", "color": "green", "font": "monospace"},
        {"letter": "A", "number": "1", "color": "green", "font": "serif"},
        {"letter": "C", "number": "1", "color": "green", "font": "sans-serif"},
        {"letter": "A", "number": "1", "color": "green", "font": "monospace"},
        {"letter": "A", "number": "1", "color": "blue", "font": "serif"},
        {"letter": "A", "number": "1", "color": "blue", "font": "sans-serif"},
        {"letter": "C", "number": "3", "color": "blue", "font": "monospace"},
        {"letter": "A", "number": "2", "color": "green", "font": "serif"},
        {"letter": "B", "number": "2", "color": "red", "font": "sans-serif"},
        {"letter": "C", "number": "3", "color": "red", "font": "monospace"},
    ]


def test_inheritance() -> None:
    """Test that LettersGameFake inherits from LettersGameBase"""
    assert issubclass(
        LettersGameFake, LettersGameBase
    ), "LettersGameFake should inherit from LettersGameBase"


def test_init(standard_deck: list[CardType]) -> None:
    """Test that a LettersGameFake object is constructed correctly"""
    LettersGameFake(standard_deck, 3, (3, 4), 2)


def test_init_properties(standard_deck: list[CardType]) -> None:
    """
    Test the properties of a LettersGameFake object after it is constructed
    (except tableau, card_at, and non_empty_positions)
    """
    game = LettersGameFake(standard_deck, 3, (3, 4), 2)

    assert game.nrows == 3
    assert game.ncols == 4
    assert game.fit_size == 3
    assert game.num_players == 2
    assert game.lightning is False
    assert game.moonshot is False
    assert game.active_players == {1, 2}
    assert not game.done
    assert game.outcome == set()
    assert game.scores == {1: 0, 2: 0}


def test_init_tableau(standard_deck: list[CardType]) -> None:
    """
    Test the tableau and non_empty_positions properties, as well as the
    card_at method, of a LettersGameFake object after it is constructed
    (to ensure it returns values consistent with the deck that was passed
    to the constructor)
    """
    game = LettersGameFake(standard_deck, 3, (3, 4), 2)

    tableau = game.tableau
    assert len(tableau) == 3
    assert all(len(row) == 4 for row in tableau)
    for r in range(3):
        for c in range(4):
            assert tableau[r][c] == standard_deck[r * 4 + c]

    non_empty_positions = game.non_empty_positions
    assert len(non_empty_positions) == 12
    for r in range(3):
        for c in range(4):
            assert (r, c) in non_empty_positions

    for r in range(3):
        for c in range(4):
            assert game.card_at((r, c)) == standard_deck[r * 4 + c]


def test_init_deck(standard_deck: list[CardType]) -> None:
    """
    Check that the constructor doesn't modify the list of cards
    (it should create its own copy of the list)
    """
    deck_copy = copy.deepcopy(standard_deck)
    LettersGameFake(standard_deck, 3, (3, 4), 2)

    assert len(standard_deck) == 81, (
        "The list of cards passed to the constructor has been modified."
        "Make sure the constructor creates a copy of the list."
    )

    for c1, c2 in zip(standard_deck, deck_copy):
        assert c1 == c2, (
            "The list of cards passed to the constructor has been modified."
            "Make sure the constructor creates a copy of the list."
        )


def test_validate_enough_cards(standard_deck: list[CardType]) -> None:
    """
    Test that the constructor raises a ValueError if the number of cards
    in the deck is less than nrows * ncols
    """
    with pytest.raises(ValueError):
        LettersGameFake(standard_deck[:10], 3, (3, 4), 2)


def test_validate_tableau_size(standard_deck: list[CardType]) -> None:
    """
    Test that the constructor raises a ValueError if the number of cards
    in one tableau is less than the fit size.
    """
    with pytest.raises(ValueError):
        LettersGameFake(standard_deck, 3, (1, 1), 2)


def test_validate_cards_same_features(standard_deck: list[CardType]) -> None:
    """
    Test that the constructor raises a ValueError if the cards in the deck
    do not all have the same feature names
    """
    standard_deck[1] = {"letter": "A", "color": "red", "font": "serif"}
    standard_deck[-1] = {"foo": "1", "bar": "2", "baz": "3"}

    with pytest.raises(ValueError):
        LettersGameFake(standard_deck, 3, (3, 4), 2)


def test_validate_number_of_feature_values(
    standard_deck: list[CardType],
) -> None:
    """
    Test that the constructor raises a ValueError if the cards
    do not have, for each feature, exactly `fit_size` distinct values.
    (across all card)
    """
    standard_deck[1]["letter"] = "D"
    standard_deck[7]["letter"] = "E"
    standard_deck[10]["color"] = "off white"
    standard_deck[20]["color"] = "cerulean"

    with pytest.raises(ValueError):
        LettersGameFake(standard_deck, 3, (3, 4), 2)


def test_validate_no_duplicate_cards(standard_deck: list[CardType]) -> None:
    """
    Test that the constructor raises a ValueError if the deck
    contains duplicate cards
    """
    standard_deck[1] = standard_deck[0]
    standard_deck[10] = standard_deck[20]

    with pytest.raises(ValueError):
        LettersGameFake(standard_deck, 3, (3, 4), 2)


def test_validate_card_at(standard_deck: list[CardType]) -> None:
    """
    Test that card_at raises a ValueError if the position is invalid
    """
    game = LettersGameFake(standard_deck, 3, (3, 4), 2)

    with pytest.raises(ValueError):
        game.card_at((-1, 0))

    with pytest.raises(ValueError):
        game.card_at((3, 0))

    with pytest.raises(ValueError):
        game.card_at((0, -1))

    with pytest.raises(ValueError):
        game.card_at((0, 4))


def test_call_fit_is_fit(standard_deck: list[CardType]) -> None:
    """
    Test that call_fit returns the correct value when called with
    cards that are a fit
    """
    game = LettersGameFake(standard_deck, 3, (3, 4), 2)

    fit = game.call_fit(1, [(0, 0), (0, 1), (0, 2)])

    assert fit, "Expected call_fit to return True when cards are a fit"


def test_call_fit_is_not_fit(twelve_cards: list[CardType]) -> None:
    """
    Test that call_fit returns the correct value when called with
    cards that are not fit
    """
    game = LettersGameFake(twelve_cards, 3, (3, 4), 2)

    fit = game.call_fit(1, [(0, 0), (0, 1), (0, 2)])

    assert (
        not fit
    ), "Expected call_fit to return False when cards are not a fit"


def test_call_fit_replacement(standard_deck: list[CardType]) -> None:
    """
    Test that call_fit replaces cards after a valid fit is called
    """
    game = LettersGameFake(standard_deck, 3, (3, 4), 2)

    fit = game.call_fit(1, [(0, 0), (0, 1), (0, 2)])

    assert fit, "Expected call_fit to return True when cards are a fit"

    # Check that the cards were replaced with the next cards in the
    # standard deck
    assert game.card_at((0, 0)) == standard_deck[12]
    assert game.card_at((0, 1)) == standard_deck[13]
    assert game.card_at((0, 2)) == standard_deck[14]

    # Check this on the tableau property as well
    tableau = game.tableau
    assert tableau[0][0] == standard_deck[12]
    assert tableau[0][1] == standard_deck[13]
    assert tableau[0][2] == standard_deck[14]

    assert len(game.non_empty_positions) == 12, (
        "Expected 12 non-empty positions because cards should've been replaced"
        " after a fit"
    )


def test_call_fit_no_replacement(twelve_cards: list[CardType]) -> None:
    """
    Test that call_fit does not replace cards after an invalid fit is called
    """
    game = LettersGameFake(twelve_cards, 3, (3, 4), 2)

    card1_before = game.card_at((0, 0))
    card2_before = game.card_at((0, 1))
    card3_before = game.card_at((0, 2))

    fit = game.call_fit(1, [(0, 0), (0, 1), (0, 2)])

    assert (
        not fit
    ), "Expected call_fit to return False when cards are not a fit"

    # Check that the cards were not replaced
    assert game.card_at((0, 0)) == card1_before
    assert game.card_at((0, 1)) == card2_before
    assert game.card_at((0, 2)) == card3_before

    # Check this on the tableau property as well
    tableau = game.tableau
    assert tableau[0][0] == card1_before
    assert tableau[0][1] == card2_before
    assert tableau[0][2] == card3_before

    assert len(game.non_empty_positions) == 12, (
        "Expected 12 non-empty positions (there was no fit, so no cards"
        " were replaced"
    )


def test_call_fit_replacement_empty(twelve_cards: list[CardType]) -> None:
    """
    Test that, if a fit is called, and there are no more cards in the deck,
    the positions in the tableau become empty.
    """
    game = LettersGameFake(twelve_cards, 3, (3, 4), 2)

    fit = game.call_fit(1, [(1, 1), (1, 2), (1, 3)])

    assert fit, "Expected call_fit to return True when cards are a fit"

    # Check that the positions no longer have cards
    assert game.card_at((1, 1)) is None
    assert game.card_at((1, 2)) is None
    assert game.card_at((1, 3)) is None

    # Check this on the tableau property as well
    tableau = game.tableau
    assert tableau[1][1] is None
    assert tableau[1][2] is None
    assert tableau[1][3] is None

    non_empty_positions = game.non_empty_positions
    assert len(non_empty_positions) == 9, (
        "Expected 9 non-empty positions (since three cards were removed"
        " without replacement"
    )
    assert (1, 1) not in non_empty_positions
    assert (1, 2) not in non_empty_positions
    assert (1, 3) not in non_empty_positions


def test_call_fit_validate_position_outside_tableau(
    standard_deck: list[CardType],
) -> None:
    """
    Test that call_fit raises a ValueError if any of the positions
    in the list are outside the bounds of the tableau
    """
    game = LettersGameFake(standard_deck, 3, (3, 4), 2)

    with pytest.raises(ValueError):
        game.call_fit(1, [(-1, 0), (0, 1), (0, 2)])

    with pytest.raises(ValueError):
        game.call_fit(1, [(0, 1), (0, 4), (0, 2)])

    with pytest.raises(ValueError):
        game.call_fit(1, [(7, 7), (-5, -6), (-1, -1)])


def test_call_fit_validate_position_not_empty(
    twelve_cards: list[CardType],
) -> None:
    """
    Test that call_fit raises a ValueError if any of the positions
    in the list are not empty
    """
    game = LettersGameFake(twelve_cards, 3, (3, 4), 2)

    # With the 12-card deck, this will result in these three
    # cards being removed and not replaced
    game.call_fit(1, [(1, 0), (1, 1), (1, 2)])

    with pytest.raises(ValueError):
        game.call_fit(1, [(1, 0), (1, 1), (1, 2)])

    with pytest.raises(ValueError):
        game.call_fit(1, [(0, 0), (1, 0), (2, 0)])

    with pytest.raises(ValueError):
        game.call_fit(1, [(0, 0), (0, 1), (1, 2)])


def test_call_fit_validate_repeated_position(
    standard_deck: list[CardType],
) -> None:
    """
    Test that call_fit raises a ValueError if any of the positions
    in the list are repeated
    """
    game = LettersGameFake(standard_deck, 3, (3, 4), 2)

    with pytest.raises(ValueError):
        game.call_fit(1, [(0, 0), (0, 1), (0, 1)])

    with pytest.raises(ValueError):
        game.call_fit(1, [(0, 0), (0, 1), (0, 0)])

    with pytest.raises(ValueError):
        game.call_fit(1, [(0, 0), (0, 0), (0, 0)])


def test_call_fit_validate_fit_size(standard_deck: list[CardType]) -> None:
    """
    Test that call_fit raises a ValueError if the number of positions
    in the list is not equal to the fit size
    """
    game = LettersGameFake(standard_deck, 3, (3, 4), 2)

    with pytest.raises(ValueError):
        game.call_fit(1, [(0, 0), (0, 1)])

    with pytest.raises(ValueError):
        game.call_fit(1, [(0, 0), (0, 1), (0, 2), (0, 3)])

    with pytest.raises(ValueError):
        game.call_fit(1, [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4)])


def test_call_fit_validate_player(standard_deck: list[CardType]) -> None:
    """
    Test that call_fit raises a ValueError if called
    with an invalid player number.
    """
    game = LettersGameFake(standard_deck, 3, (3, 4), 2)

    with pytest.raises(ValueError):
        game.call_fit(3, [(0, 0), (0, 1), (0, 2)])

    with pytest.raises(ValueError):
        game.call_fit(-1, [(0, 0), (0, 1), (0, 2)])


def test_scoring_01(standard_deck: list[CardType]) -> None:
    """
    Test that calling fits is correctly scored
    """
    game = LettersGameFake(standard_deck, 3, (3, 4), 2)

    game.call_fit(1, [(0, 0), (0, 1), (0, 2)])
    game.call_fit(2, [(1, 0), (1, 1), (1, 2)])
    game.call_fit(1, [(2, 0), (2, 1), (2, 2)])

    scores = game.scores
    assert scores[1] == 6
    assert scores[2] == 3


def test_scoring_02(twelve_cards: list[CardType]) -> None:
    """
    Test that calling fits, as well as missing fits, is correctly scored
    """
    game = LettersGameFake(twelve_cards, 3, (3, 4), 2)

    # Not a fit
    game.call_fit(1, [(0, 0), (0, 1), (0, 2)])
    assert game.scores[1] == -3

    # Fit
    game.call_fit(2, [(1, 1), (1, 2), (1, 3)])
    assert game.scores[2] == 3

    # Not a fit
    game.call_fit(1, [(2, 0), (2, 1), (2, 2)])

    scores = game.scores
    assert scores[1] == -6
    assert scores[2] == 3


def test_game_end_player1wins(standard_deck: list[CardType]) -> None:
    """
    Test that ending the game sets the done and outcome properties
    correctly (when Player 1 wins)

    Uses the same setup as test test_scoring_01
    """
    game = LettersGameFake(standard_deck, 3, (3, 4), 2)

    game.call_fit(1, [(0, 0), (0, 1), (0, 2)])
    game.call_fit(2, [(1, 0), (1, 1), (1, 2)])
    game.call_fit(1, [(2, 0), (2, 1), (2, 2)])

    game.end_game()

    assert game.done
    assert game.outcome == {1}


def test_game_end_player2wins(twelve_cards: list[CardType]) -> None:
    """
    Test that ending the game sets the done and outcome properties
    correctly (when Player 2 wins)

    Uses the same setup as test_scoring_02
    """
    game = LettersGameFake(twelve_cards, 3, (3, 4), 2)

    game.call_fit(1, [(0, 0), (0, 1), (0, 2)])
    game.call_fit(2, [(1, 1), (1, 2), (1, 3)])
    game.call_fit(1, [(2, 0), (2, 1), (2, 2)])

    game.end_game()

    assert game.done
    assert game.outcome == {2}


def test_game_end_tie(standard_deck: list[CardType]) -> None:
    """
    Test that ending the game sets the done and outcome properties
    correctly (when both players tie)

    Uses the same setup as test_scoring_02
    """
    game = LettersGameFake(standard_deck, 3, (3, 4), 2)

    game.call_fit(1, [(0, 0), (0, 1), (0, 2)])
    game.call_fit(2, [(1, 0), (1, 1), (1, 2)])
    game.call_fit(1, [(2, 0), (2, 1), (2, 2)])
    game.call_fit(2, [(0, 3), (1, 3), (2, 3)])

    game.end_game()

    assert game.done
    assert game.outcome == {1, 2}


def test_moonshot_valid_fit(standard_deck: list[CardType]) -> None:
    """
    Test that the (fake) moonshot feature works correctly
    when calling a valid fit
    """
    game = LettersGameFake(standard_deck, 3, (3, 4), 2)

    game.call_fit(1, [(0, 0), (0, 1), (0, 2)])
    game.call_fit(2, [(1, 0), (1, 1), (1, 2)])
    game.call_fit(1, [(2, 0), (2, 1), (2, 2)])

    game.moonshot_start(2)
    assert game.moonshot

    game.call_fit(2, [(0, 3), (1, 3), (2, 3)])

    assert game.done
    assert game.outcome == {2}

    scores = game.scores
    assert scores[1] == 6
    assert scores[2] == 103


def test_moonshot_invalid_fit(standard_deck: list[CardType]) -> None:
    """
    Test that the (fake) moonshot feature works correctly
    when calling an invalid fit.
    """

    # We tweak the standard deck so that the first call replaces
    # cards (0, 0) and (0, 1) in a way that calling a fit
    # with (0, 0), (0, 1), and (0, 2) will not be a fit
    standard_deck[13] = standard_deck[36]
    standard_deck[14] = standard_deck[80]
    standard_deck.pop(36)
    standard_deck.pop(79)
    game = LettersGameFake(standard_deck, 3, (3, 4), 2)

    game.call_fit(1, [(0, 0), (0, 1), (0, 2)])
    game.call_fit(2, [(1, 1), (1, 2), (1, 3)])

    game.moonshot_start(1)
    assert game.moonshot
    game.call_fit(1, [(0, 0), (0, 1), (0, 2)])

    assert game.done
    assert game.outcome == {1}

    scores = game.scores
    assert scores[1] == 103
    assert scores[2] == 3


def test_moonshot_validate_already_in_moonshot(
    standard_deck: list[CardType],
) -> None:
    """
    Test that moonshot_start raises a ValueError if called
    when the game is already in moonshot mode.
    """
    game = LettersGameFake(standard_deck, 3, (3, 4), 2)

    game.call_fit(1, [(0, 0), (0, 1), (0, 2)])
    game.call_fit(2, [(1, 1), (1, 2), (1, 3)])

    game.moonshot_start(2)

    with pytest.raises(ValueError):
        game.moonshot_start(1)


def test_moonshot_validate_no_empty_positions(
    twelve_cards: list[CardType],
) -> None:
    """
    Test that moonshot_start raises a ValueError if called
    when there are empty positions in the tableau.
    """
    game = LettersGameFake(twelve_cards, 3, (3, 4), 2)

    # With the 12-card deck, this will result in these three
    # cards being removed and not replaced
    game.call_fit(1, [(1, 0), (1, 1), (1, 2)])

    with pytest.raises(ValueError):
        game.moonshot_start(2)


def test_moonshot_validate_player(standard_deck: list[CardType]) -> None:
    """
    Test that moonshot_start raises a ValueError if called
    with an invalid player number.
    """
    game = LettersGameFake(standard_deck, 3, (3, 4), 2)

    with pytest.raises(ValueError):
        game.moonshot_start(3)

    with pytest.raises(ValueError):
        game.moonshot_start(-1)


def test_moonshot_end_validate_in_moonshot_mode(
    standard_deck: list[CardType],
) -> None:
    """
    Test that moonshot_end raises a ValueError if called
    when the game is not in moonshot mode.
    """
    game = LettersGameFake(standard_deck, 3, (3, 4), 2)

    with pytest.raises(ValueError):
        game.moonshot_end()


def test_alternate_deck_01() -> None:
    """
    Test various methods using a different deck with more than
    four features, and fit size larger than 3, to make sure
    the implementation is not hardcoded to only work with
    the standard deck (or decks of 81 cards)
    """
    garments = ["pants", "shirt", "jacket", "sweater"]
    styles = ["formal", "informal", "casual", "sporty"]
    sizes = ["S", "M", "L", "XL"]
    fabrics = ["cotton", "blend", "synthetic", "wool"]
    seasons = ["summer", "fall", "winter", "spring"]

    cards = [
        {
            "garment": garment,
            "style": style,
            "size": size,
            "fabric": fabric,
            "season": season,
        }
        for garment in garments
        for style in styles
        for size in sizes
        for fabric in fabrics
        for season in seasons
    ]

    game = LettersGameFake(cards, 4, (6, 8), 2)

    assert game.nrows == 6
    assert game.ncols == 8
    assert game.fit_size == 4

    tableau = game.tableau
    assert len(tableau) == 6
    assert all(len(row) == 8 for row in tableau)
    for r in range(6):
        for c in range(8):
            assert tableau[r][c] == cards[r * 8 + c]

    non_empty_positions = game.non_empty_positions
    assert len(non_empty_positions) == 48
    for r in range(6):
        for c in range(8):
            assert (r, c) in non_empty_positions

    for r in range(6):
        for c in range(8):
            assert game.card_at((r, c)) == cards[r * 8 + c]

    game.call_fit(1, [(0, 0), (0, 1), (0, 2), (0, 3)])
    game.call_fit(2, [(1, 0), (1, 1), (1, 2), (1, 3)])
    game.call_fit(1, [(2, 0), (2, 1), (2, 2), (2, 3)])

    game.end_game()

    assert game.done

    scores = game.scores
    assert scores[1] == 8
    assert scores[2] == 4

    assert game.outcome == {1}
