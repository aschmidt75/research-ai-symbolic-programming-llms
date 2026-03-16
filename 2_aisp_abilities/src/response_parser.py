"""
response_parser.py

Parses an AISP document string and extracts the `label` and `confidence`
attributes from the ⟦Ε⟧⟨ ... ⟩ evidence block.

Returns a dict with keys:
  - "label"      : str | None   (e.g. "cls_A" or "cls_B")
  - "confidence" : float | None (e.g. 0.93)
"""

import re


# Matches the evidence block: ⟦Ε⟧⟨ ... ⟩
# The block may span multiple lines and contain arbitrary content.
_EVIDENCE_BLOCK_RE = re.compile(
    r"⟦Ε⟧⟨(.*?)⟩",
    re.DOTALL,
)

# Matches:  label≜cls_A  or  label ≜ cls_A  (with optional spaces)
_LABEL_RE = re.compile(
    r"label\s*[≜=]\s*([^\s,⟩\n\r]+)",
)

# Matches:  confidence≜0.93  or  confidence ≜ 0.93
_CONFIDENCE_RE = re.compile(
    r"confidence\s*[≜=]\s*([0-9]*\.?[0-9]+)",
)


def parse_response(aisp_text: str) -> dict:
    """Extract label and confidence from an AISP evidence block.

    Parameters
    ----------
    aisp_text : str
        The raw string output that is supposed to be an AISP document.

    Returns
    -------
    dict
        {
            "label":      str | None,    # "cls_A", "cls_B", or None if not found
            "confidence": float | None,  # numeric value or None if not found
        }
    """
    result: dict = {"label": None, "confidence": None}

    block_match = _EVIDENCE_BLOCK_RE.search(aisp_text)
    if block_match is None:
        return result

    block_body = block_match.group(1)

    label_match = _LABEL_RE.search(block_body)
    if label_match:
        result["label"] = label_match.group(1).strip()

    confidence_match = _CONFIDENCE_RE.search(block_body)
    if confidence_match:
        try:
            result["confidence"] = float(confidence_match.group(1))
        except ValueError:
            pass

    return result


if __name__ == "__main__":
    # Quick smoke-test against the example output
    sample = """
𝔸1.0.classify_b2c_order@2026-03-15
γ≔llm.behavior.classify

⟦Ε⟧⟨
  label≜cls_A,
  confidence≜0.93,
  ⊢wf,
  τ≜◊⁺⁺
⟩
"""
    print(parse_response(sample))
    # Expected: {'label': 'cls_A', 'confidence': 0.93}
