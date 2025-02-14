"""
Abstract base class for Letters game
"""

from abc import ABC, abstractmethod


# A card has a set of features, with string names and
# string values, which we represent as a dictionary.
#
# For example, in a standard game of Letters, cards
# have four features: "letter", "font", "color",
# and "number". The following dictionary would
# represent one specific card:
#
#     {"letter": "A", "font": "Serif",
#      "color": "red", "number": "3"}
#
# However, generally speaking, there are no constraints
# on the number of features (and the number of possible
# values for each feature).
CardType = dict[str, str]

# A tableau is a 2D list of cards. Each entry in the
# tableau is either a card or the value None (to
# represent the absence of a card)
TableauType = list[list[CardType | None]]

# A position on the tableau is a (row, column) pair
PositionType = tuple[int, int]


class LettersGameBase(ABC):
    """
    Class for representing a Letters game.
    """

    #
    # PRIVATE ATTRIBUTES
    #

    # Number of players
    _num_players: int

    # Fit size
    _fit_size: int

    # Tableau size
    _tableau_size: tuple[int, int]

    # Lightning mode
    _lightning: bool

    # Moonshot mode
    _moonshot: bool

    #
    # CONSTRUCTOR
    #

    def __init__(
        self,
        cards: list[CardType],
        fit_size: int,
        tableau_size: tuple[int, int],
        num_players: int,
        lightning: bool = False,
    ) -> None:
        """
        Constructor

        In the game, cards will be dealt in the order they are
        provided in the `cards` parameter (for the initial tableau,
        they will be dealt in row-major order). If the cards
        need to be shuffled, this should be done before calling
        this constructor.

        No validation is performed in this base constructor, but
        child classes are expected to validate the following:

        - The number of cards is, at least, equal to the number of rows
          times the number of columns in the tableau.
        - The number of cards in one tableau is, at least, equal to the
          fit size.
        - All cards have the same feature names
        - For each feature, there are exactly `fit_size` distinct values
          across all the cards.
        - There are no duplicate cards

        Args:
            cards: List of cards to use in the game
            fit_size: Fit size
            tableau_size: Number of rows and columns of cards in the tableau
            num_players: Number of players
            lightning: Whether the game is being played in lightning mode

        Raises:
            ValueError: If the provided parameters fail any of the
                checks described above.
        """
        self._fit_size = fit_size
        self._num_players = num_players
        self._tableau_size = tableau_size
        self._lightning = lightning
        self._moonshot = False

    #
    # PROPERTIES
    #

    @property
    def nrows(self) -> int:
        """
        Returns the number of rows in the tableau
        """
        return self._tableau_size[0]

    @property
    def ncols(self) -> int:
        """
        Returns the number of columns of cards
        """
        return self._tableau_size[1]

    @property
    def fit_size(self) -> int:
        """
        Returns the fit size
        """
        return self._fit_size

    @property
    def num_players(self) -> int:
        """
        Returns the number of players
        """
        return self._num_players

    @property
    def lightning(self) -> bool:
        """
        Returns whether the game is being played in lightning mode
        """
        return self._lightning

    @property
    def moonshot(self) -> bool:
        """
        Returns whether the game is being played in moonshot mode
        """
        return self._moonshot

    @property
    @abstractmethod
    def active_players(self) -> set[int]:
        """
        Returns the set of players who are active in the game
        (when playing in lightning mode, some players may be
        eliminated)
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def tableau(self) -> TableauType:
        """
        Returns the layout of the cards on the board
        as a 2D list of dictionaries (where some positions
        may be None to indicate the absence of a card)
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def non_empty_positions(self) -> set[PositionType]:
        """
        Returns a set of non-empty positions on the tableau
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def done(self) -> bool:
        """
        Returns True if the game is over, False otherwise.

        In a non-lightning game, the game is over by consensus
        of the players (see end_game method for more details)

        In a lightning game, the game is over after a player
        finds a fit or shoots the moon successfully.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def outcome(self) -> set[int]:
        """
        Returns the list of winners for the game, assuming the
        game is considered to be over.

        If the game is done, it will return a set of player numbers
        (players are numbered from 1). If there is a single winner,
        the set will contain a single integer. If there is a tie,
        the set will contain more than one integer (representing
        the players who tied)

        If the game is not yet done, returns an empty set.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def scores(self) -> dict[int, int]:
        """
        Returns the scores for each player
        (in a dictionary mapping player numbers to scores)
        """
        raise NotImplementedError

    #
    # METHODS
    #

    @abstractmethod
    def card_at(self, pos: PositionType) -> CardType | None:
        """
        Returns the card at the given position in the tableau

        Args:
            pos: Position on the tableau

        Raises:
            ValueError: If the specified position is outside
            the bounds of the board.

        Returns: The card at the given position, or None if there
            is no card at that position
        """
        raise NotImplementedError

    @abstractmethod
    def call_fit(self, player: int, positions: list[PositionType]) -> bool:
        """
        Used when a player calls a fit.

        If the fit is successful, the player will be awarded
        points, and the method will return True. If the fit
        is unsuccessful, the player will be deducted points,
        and the method will return False.

        This method can be called in lightning/non-lightning
        mode, as well as moonshot/non-moonshot mode. See the
        game rules for more information on how calling a fit
        affects the game in each of these cases.

        Args:
            player: Player calling the fit
            positions: List of card positions

        Raises:
            ValueError: If any of the following is true:
             - A specified position is outside the bounds of the board
             - A specified position does not contain a card
             - The same position is specified more than once
             - The number of positions is not equal to the fit size
             - The player number is invalid
             - In lightning mode, the player has been eliminated

        Returns: None
        """
        raise NotImplementedError

    @abstractmethod
    def moonshot_start(self, player: int) -> None:
        """
        Switches the game to moonshot mode (called by the given player)

        While moonshot mode is in effect, the semantics of calling a fit
        will be different.

        Args:
            player: Player shooting the moon

        Raises:
            ValueError: If any of the following is true:
             - The game is already in moonshot mode
             - The tableau has empty positions
             - The player number is invalid
             - In lightning mode, the player has been eliminated

        Returns: None
        """
        raise NotImplementedError

    @abstractmethod
    def moonshot_end(self) -> None:
        """
        Reverts the game from moonshot mode back to normal play,
        awarding points to the player who called the moonshot.

        Args: None

        Raises:
            ValueError: If any of the following is true:
             - The game was not in moonshot mode
             - In lightning mode, the player has been eliminated

        Returns: None
        """
        raise NotImplementedError

    @abstractmethod
    def end_game(self) -> None:
        """
        In non-lightning mode, ends the game.

        The end of the game is determined by consensus of the players.
        How this consensus is achieved is left to any UI implemented
        on top of this class (that UI must ultimately call end_game
        when the game can be ended)

        Args: None

        Raises:
            ValueError: If any of the following is true:
             - If called in lightning mode
             - If the game is already over

        Returns: None
        """
        raise NotImplementedError
