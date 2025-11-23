from enum import Enum, auto

class TokenType(Enum):
    # Identifiers
    IDENTIFIER   = auto()

    # Literals
    NUMBER       = auto()
    STRING       = auto()
    BOOL_LITERAL = auto()  # true / false

    # Keywords
    VAR    = auto()
    CONST  = auto()
    FUNC   = auto()
    IF     = auto()
    ELSE   = auto()
    LOOP   = auto()
    IMPORT = auto()
    TRUE   = auto()
    FALSE  = auto()
    AND    = auto()
    OR     = auto()
    NOT    = auto()

    # Type names
    TYPE_NUMBER = auto()
    TYPE_STRING = auto()
    TYPE_BOOL   = auto()

    # Operators
    PLUS          = auto()  # +
    MINUS         = auto()  # -
    STAR          = auto()  # *
    SLASH         = auto()  # /
    PERCENT       = auto()  # %
    CARET         = auto()  # ^
    HASH          = auto()  # #
    EQUAL_EQUAL   = auto()  # ==
    BANG_EQUAL    = auto()  # !=
    LESS          = auto()  # <
    LESS_EQUAL    = auto()  # <=
    GREATER       = auto()  # >
    GREATER_EQUAL = auto()  # >=
    EQUAL         = auto()  # =

    # Punctuation
    LPAREN    = auto()  # (
    RPAREN    = auto()  # )
    LBRACE    = auto()  # {
    RBRACE    = auto()  # }
    COMMA     = auto()  # ,
    SEMICOLON = auto()  # ;

    # Line terminators
    EOL       = auto()

    # Special
    EOF       = auto()
