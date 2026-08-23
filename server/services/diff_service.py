import difflib
from typing import Any, Dict, List, Optional


class DiffService:
    def compute_diff(
        self,
        previous: Dict[str, Any],
        current: Dict[str, Any],
        modes: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        modes = modes or ["gitDiff"]
        prev_text = previous.get("markdown") or previous.get("html") or previous.get("text") or ""
        curr_text = current.get("markdown") or current.get("html") or current.get("text") or ""

        prev_lines = prev_text.splitlines(keepends=True)
        curr_lines = curr_text.splitlines(keepends=True)

        diff_data: Dict[str, Any] = {
            "hasChanges": prev_text != curr_text,
        }

        if "gitDiff" in modes:
            diff_gen = difflib.unified_diff(
                prev_lines,
                curr_lines,
                fromfile="previous",
                tofile="current",
            )
            diff_data["gitDiff"] = "".join(diff_gen)

        if "json" in modes:
            diff_data["json"] = {
                "previousHash": previous.get("contentHash", ""),
                "currentHash": current.get("contentHash", ""),
                "previousLength": len(prev_text),
                "currentLength": len(curr_text),
                "modified": prev_text != curr_text,
            }

        return {
            "success": True,
            "data": diff_data,
        }


diff_service = DiffService()
