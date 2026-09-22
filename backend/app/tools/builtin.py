import ast
import operator
from datetime import datetime

from app.rag.database import (
    get_documents,
    get_document,
)

from app.rag.extractor import (
    extract_text,
)

from app.rag.retrieval import (
    retrieve_relevant_documents,
)


# ---------------------------------------------------------
# Calculator
# ---------------------------------------------------------

_ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def _evaluate_expression(node):
    if isinstance(node, ast.Constant):

        if isinstance(
            node.value,
            (int, float),
        ):
            return node.value

        raise ValueError(
            "Only numbers are allowed."
        )

    if isinstance(
        node,
        ast.UnaryOp,
    ):
        operation = _ALLOWED_OPERATORS.get(
            type(node.op)
        )

        if operation is None:
            raise ValueError(
                "Unsupported unary operator."
            )

        return operation(
            _evaluate_expression(node.operand)
        )

    if isinstance(
        node,
        ast.BinOp,
    ):
        operation = _ALLOWED_OPERATORS.get(
            type(node.op)
        )

        if operation is None:
            raise ValueError(
                "Unsupported operator."
            )

        left = _evaluate_expression(
            node.left
        )

        right = _evaluate_expression(
            node.right
        )

        return operation(
            left,
            right,
        )

    raise ValueError(
        "Invalid mathematical expression."
    )


def calculator(expression: str):
    if not expression:
        raise ValueError(
            "Expression is required."
        )

    if len(expression) > 200:
        raise ValueError(
            "Expression is too long."
        )

    tree = ast.parse(
        expression,
        mode="eval",
    )

    result = _evaluate_expression(
        tree.body
    )

    return {
        "expression": expression,
        "result": result,
    }


# ---------------------------------------------------------
# Current time
# ---------------------------------------------------------

def current_time():
    now = datetime.now().astimezone()

    return {
        "datetime": now.isoformat(),
        "timezone": str(
            now.tzinfo
        ),
    }


# ---------------------------------------------------------
# List uploaded documents
# ---------------------------------------------------------

def list_documents():
    documents = get_documents()

    return {
        "documents": documents,
    }


# ---------------------------------------------------------
# Search private documents
# ---------------------------------------------------------

def search_documents(
    query: str,
    limit: int = 5,
):
    if not query:
        raise ValueError(
            "Search query is required."
        )

    limit = max(
        1,
        min(limit, 10),
    )

    results = retrieve_relevant_documents(
        query=query,
        limit=limit,
    )

    return {
        "query": query,
        "results": results,
    }


# ---------------------------------------------------------
# Read uploaded document
# ---------------------------------------------------------

def read_document(
    document_id: int,
):
    document = get_document(
        document_id
    )

    if document is None:
        raise ValueError(
            f"Document {document_id} was not found."
        )

    pages = extract_text(
        document["file_path"]
    )

    return {
        "document_id": document_id,
        "filename": document["filename"],
        "file_type": document["file_type"],
        "pages": pages,
    }