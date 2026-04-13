import logging
from uuid import UUID

import litellm

from app.core.config import settings
from app.repositories.run_repository import RunRepository

logger = logging.getLogger(__name__)


def _summarize_metrics(rows: list) -> dict:
    """Compute aggregate stats from RunResponse objects."""
    left = [r for r in rows if r.foot == "left"]
    right = [r for r in rows if r.foot == "right"]

    def avg(lst: list, key: str) -> float | None:
        vals = [getattr(r, key) for r in lst]
        return round(sum(vals) / len(vals), 1) if vals else None

    avg_gct_l = avg(left, "gct_ms")
    avg_gct_r = avg(right, "gct_ms")
    avg_ft_l = avg(left, "flight_ms")
    avg_ft_r = avg(right, "flight_ms")

    gct_asym = None
    if avg_gct_l and avg_gct_r:
        mean = (avg_gct_l + avg_gct_r) / 2
        gct_asym = round(abs(avg_gct_l - avg_gct_r) / mean * 100, 1)

    ft_asym = None
    if avg_ft_l and avg_ft_r:
        mean = (avg_ft_l + avg_ft_r) / 2
        ft_asym = round(abs(avg_ft_l - avg_ft_r) / mean * 100, 1)

    gct_drift = None
    all_gct = [r.gct_ms for r in rows]
    if len(all_gct) >= 8:
        q = len(all_gct) // 4
        early = sum(all_gct[:q]) / q
        late = sum(all_gct[-q:]) / q
        gct_drift = round((late - early) / early * 100, 1) if early else None

    return {
        "total_strides": len(rows),
        "avg_gct_left_ms": avg_gct_l,
        "avg_gct_right_ms": avg_gct_r,
        "avg_ft_left_ms": avg_ft_l,
        "avg_ft_right_ms": avg_ft_r,
        "gct_asymmetry_pct": gct_asym,
        "ft_asymmetry_pct": ft_asym,
        "gct_drift_pct": gct_drift,
    }


def _build_prompt(event_type: str, stats: dict) -> str:
    """Build a compact coach-style prompt from summary stats."""

    def fmt(val: float | None, unit: str) -> str:
        return f"{val}{unit}" if val is not None else "N/A"

    data = (
        f"Event: {event_type}\n"
        f"Total strides: {stats['total_strides']}\n"
        f"Avg GCT left: {fmt(stats['avg_gct_left_ms'], 'ms')} | right: {fmt(stats['avg_gct_right_ms'], 'ms')}\n"
        f"Avg flight time left: {fmt(stats['avg_ft_left_ms'], 'ms')} | right: {fmt(stats['avg_ft_right_ms'], 'ms')}\n"
        f"GCT asymmetry: {fmt(stats['gct_asymmetry_pct'], '%')}\n"
        f"Flight time asymmetry: {fmt(stats['ft_asymmetry_pct'], '%')}\n"
        f"GCT drift (fatigue indicator): {fmt(stats['gct_drift_pct'], '%')}"
    )

    return (
        "You are a concise track and field coach. "
        "Given the following run metrics, write exactly 2 sentences: "
        "first, a brief summary of the athlete's performance; "
        "second, one specific actionable improvement tip. "
        "No bullet points or headers. Under 60 words total.\n\n"
        f"{data}"
    )


class FeedbackService:
    def __init__(self, repository: RunRepository, coach_id: UUID) -> None:
        self.repository = repository
        self.coach_id = coach_id

    async def get_feedback(self, run_id: UUID) -> str:
        logger.info(f"FeedbackService: generating feedback for run {run_id}")

        await self.repository.verify_run_belongs_to_coach(run_id, self.coach_id)
        meta = await self.repository.get_run_meta(run_id)
        rows = await self.repository.get_run_metrics(run_id)

        stats = _summarize_metrics(rows)
        prompt = _build_prompt(str(meta.event_type), stats)

        response = await litellm.acompletion(
            model=settings.llm_model,
            api_key=settings.llm_api_key,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=120,
            temperature=0.4,
        )

        feedback = response.choices[0].message.content.strip()
        logger.info(f"FeedbackService: feedback generated for run {run_id}")
        return feedback
