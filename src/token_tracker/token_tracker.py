"""
Token usage tracking module.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional

from utils.logger import setup_logger
from src.exceptions import TokenTrackingError

logger = setup_logger(__name__)


class TokenTracker:
    """Tracks and persists LLM token usage."""

    def __init__(self, data_dir: Path):
        """
        Initialize token tracker.

        Args:
            data_dir: Directory to store token usage data
        """
        self.data_file = data_dir / "token_usage.json"
        self.data_file.parent.mkdir(parents=True, exist_ok=True)

    def save(self, user_id: str, token_data: Dict[str, int]) -> None:
        """
        Save token usage for a run.

        Args:
            user_id: User identifier
            token_data: Token usage dict with keys: input_tokens, output_tokens, total_tokens

        Raises:
            TokenTrackingError: If saving fails
        """
        try:
            data = self._load_data()

            run_data = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "user_id": user_id,
                "input_tokens": token_data.get("input_tokens", 0),
                "output_tokens": token_data.get("output_tokens", 0),
                "total_tokens": token_data.get("total_tokens", 0)
            }

            data["runs"].append(run_data)

            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            logger.info(f"Token usage saved: {run_data['total_tokens']} tokens")

        except Exception as e:
            raise TokenTrackingError(f"Failed to save token usage: {e}") from e

    def _load_data(self) -> Dict:
        """Load existing token usage data."""
        if self.data_file.exists() and self.data_file.stat().st_size > 0:
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                logger.warning("Token usage file corrupted, creating new one")

        return {"runs": []}

    def get_total_usage(self, user_id: Optional[str] = None) -> Dict[str, int]:
        """
        Get total token usage statistics.

        Args:
            user_id: Optional user ID to filter by

        Returns:
            Dict with total_runs, total_input_tokens, total_output_tokens, total_tokens
        """
        data = self._load_data()
        runs = data.get("runs", [])

        if user_id:
            runs = [r for r in runs if r.get("user_id") == user_id]

        total_input = sum(r.get("input_tokens", 0) for r in runs)
        total_output = sum(r.get("output_tokens", 0) for r in runs)

        return {
            "total_runs": len(runs),
            "total_input_tokens": total_input,
            "total_output_tokens": total_output,
            "total_tokens": total_input + total_output
        }
