"""Semantics of the Temporal Query Language."""

import re
from pathlib import Path
from types import MappingProxyType

from tempql.ast import BinaryOperator, UnaryOperator
from tempql.utils import DEFAULT_SYMBOL_MAPPING, SymbolMapping

ENCODING_SEMANTICS = Path(__file__).parent / "encodings" / "semantics.lp"
SYMBOL_MAPPING_TEMPLATE = MappingProxyType(
    {
        "__negation__": UnaryOperator.NOT,
        "__next__": UnaryOperator.NEXT,
        "__previous__": UnaryOperator.PREV,
        "__always__": UnaryOperator.ALWAYS,
        "__eventually__": UnaryOperator.EVENTUALLY,
        "__conjunction__": BinaryOperator.AND,
        "__disjunction__": BinaryOperator.OR,
        "__until__": BinaryOperator.UNTIL,
        "__since__": BinaryOperator.SINCE,
    }
)
MODEL_TEMPLATE = "__model__"
DEFAULT_MODEL = "foil"


def semantics(mapping: SymbolMapping = DEFAULT_SYMBOL_MAPPING, model: str = DEFAULT_MODEL) -> str:
    """Return the semantic ASP rules of the Temporal Query Language."""
    with open(ENCODING_SEMANTICS) as f:
        text = f.read().strip()

        mappings = {**{t: mapping[o] for t, o in SYMBOL_MAPPING_TEMPLATE.items()}, MODEL_TEMPLATE: model}
        mappings = {re.escape(k): v for k, v in mappings.items()}
        pattern = re.compile("|".join(mappings))

        return pattern.sub(lambda m: mappings[re.escape(m.group(0))], text)
