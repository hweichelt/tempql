"""Error classes for the temporal query language."""


class ParseError(Exception):
    """Parse error."""

    def __init__(self, message: str, start: int, end: int) -> None:
        """Initialize a parsing error with a message and start/end positions."""
        super().__init__(message)
        self.message, self.start, self.end = message, start, end
