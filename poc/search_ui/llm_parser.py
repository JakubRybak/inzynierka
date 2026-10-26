"""Two-step LLM query parser (poc/scripts/query_parser.py) exposed to the server as --parser llm."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from query_parser import QueryParser  # noqa: E402

_parser = QueryParser()
try:
    _parser.session                  # authenticate at startup rather than on the first query
except Exception as e:
    print(f"Parser authentication failed ({type(e).__name__}), retrying on the first query")
NAME = f"query_parser.py ({_parser.model}, thinking {_parser.thinking})"


def parse(query):
    return _parser.parse(query).to_dict()
