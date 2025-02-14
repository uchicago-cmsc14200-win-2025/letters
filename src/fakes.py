"""
Fake implementations of LetterGameBase.

We provide a LettersGameStub implementation, and you must
implement a LettersGameFake implementation.
"""

import copy

from base import LettersGameBase, CardType, PositionType, TableauType


class LettersGameStub(LettersGameBase):
    """
    Stub implementation of LettersGameBase.

    This stub implementation behaves according to the following rules:

    - The game must be created with exactly enough cards for one tableau.
    - The constructor does not validate its parameters in any way (except
      to check the requirement in the above bullet point)
    - When a player calls a fit, if the fit includes at least one card
      in an odd-numbered row (with rows numbered from 0), the fit is
      considered valid, and the cards are removed from the tableau
      (and not replaced) Otherwise, the fit is considered invalid.
    - The game is over when the end_game() method is called.
    - When the game is over, the stub will only report at most two winners
      (even if a larger number of players was passed to the constructor):
       - If the top-left position (0, 0) and the bottom-right position
         (rows-1, cols-1) are both empty or both have a card, the game is a
         tie between Players 1 and 2.
       - If the top-left position is empty, but the bottom-right position
         has a card, Player 1 wins.
       - If the top-left position has a card, but the bottom-right position
         is empty, Player 2 wins.
    - The score for each player is equal to 100 times the player number.
    - Neither moonshot mode or lightning mode have any effect on the game.
    """

    _cards: list[CardType | None]
    _done: bool

    def __init__(
        self,
        cards: list[CardType],
        fit_size: int,
        tableau_size: tuple[int, int],
        num_players: int,
        lightning: bool = False,
    ) -> None:
        assert len(cards) == tableau_size[0] * tableau_size[1], (
            "Stub implementation requires the number of cards to be"
            "enough for exactly one tableau"
        )

        super().__init__(cards, fit_size, tableau_size, num_players, lightning)

        self._cards = []
        for c in cards:
            self._cards.append(c.copy())
        self._done = False

    @property
    def active_players(self) -> set[int]:
        """
        See LettersGameBase.active_players
        """
        return set(range(1, self._num_players + 1))

    @property
    def tableau(self) -> TableauType:
        """
        See LettersGameBase.tableau
        """
        tableau: TableauType = []
        for r in range(self.nrows):
            tableau.append(self._cards[r * self.ncols : (r + 1) * self.ncols])
        return tableau

    @property
    def non_empty_positions(self) -> set[PositionType]:
        """
        Returns a list of non-empty positions on the tableau
        """
        positions = set()
        for r in range(self.nrows):
            for c in range(self.ncols):
                i = r * self.ncols + c
                if self._cards[i] is not None:
                    positions.add((r, c))
        return positions

    @property
    def done(self) -> bool:
        """
        See LettersGameBase.done
        """
        return self._done

    @property
    def outcome(self) -> set[int]:
        """
        See LettersGameBase.outcome
        """
        if not self.done:
            return set()
        else:
            top_left = self.card_at((0, 0))
            bottom_right = self.card_at((self.nrows - 1, self.ncols - 1))

            if top_left is None and bottom_right is not None:
                return {1}
            elif top_left is not None and bottom_right is None:
                return {2}
            else:
                return {1, 2}

    @property
    def scores(self) -> dict[int, int]:
        """
        See LettersGameBase.scores
        """
        return {p: p * 100 for p in range(1, self._num_players + 1)}

    def card_at(self, pos: PositionType) -> CardType | None:
        """
        See LettersGameBase.card_at
        """
        r, c = pos
        return self._cards[r * self.ncols + c]

    def call_fit(self, player: int, positions: list[PositionType]) -> bool:
        """
        See LettersGameBase.call_fit
        """
        valid = False
        for pos in positions:
            r, c = pos
            if r % 2 == 1:
                valid = True
                break

        if not valid:
            return False

        for pos in positions:
            r, c = pos
            self._cards[r * self.ncols + c] = None

        return True

    def moonshot_start(self, player: int) -> None:
        """
        See LettersGameBase.moonshot_start
        """
        pass

    def moonshot_end(self) -> None:
        """
        See LettersGameBase.moonshot_end
        """
        pass

    def end_game(self) -> None:
        """
        See LettersGameBase.end_game
        """
        self._done = True


#
# Your LettersGameFake implementation goes here
#
