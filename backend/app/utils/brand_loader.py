"""
Brand knowledge loader.
Reads brand_knowledge.toml from the backend directory and formats
its content into a text block suitable for injection into the LLM prompt.
"""

import os
import tomllib
from typing import Optional

_TOML_PATH = os.path.join(os.path.dirname(__file__), "../../brand_knowledge.toml")

# Simple cache so we don't re-read the file on every chat request.
_cached_text: Optional[str] = None
_cache_mtime: float = 0.0


def load_brand_knowledge() -> Optional[str]:
    """
    Return the formatted brand knowledge string, or None if:
    - the file doesn't exist
    - enabled = false
    - no meaningful content has been filled in
    """
    global _cached_text, _cache_mtime

    if not os.path.exists(_TOML_PATH):
        return None

    mtime = os.path.getmtime(_TOML_PATH)
    if mtime == _cache_mtime:
        return _cached_text

    _cache_mtime = mtime
    _cached_text = _parse_toml()
    return _cached_text


def _parse_toml() -> Optional[str]:
    try:
        with open(_TOML_PATH, "rb") as f:
            data = tomllib.load(f)
    except Exception:
        return None

    if not data.get("enabled", False):
        return None

    brand = data.get("brand", {})
    if not brand:
        return None

    parts: list[str] = []

    # ── Identity ──────────────────────────────────────────────
    name = brand.get("name", "").strip()
    if not name:
        return None  # brand name is required

    parts.append(f"Brand: {name}")

    if brand.get("tagline"):
        parts.append(f"Tagline: {brand['tagline']}")
    if brand.get("industry"):
        parts.append(f"Industry: {brand['industry']}")
    if brand.get("founded"):
        parts.append(f"Founded: {brand['founded']}")
    if brand.get("website"):
        parts.append(f"Website: {brand['website']}")

    # ── Products ──────────────────────────────────────────────
    products = [p for p in brand.get("products", []) if p.get("name", "").strip()]
    if products:
        parts.append("\nProducts / Services:")
        for p in products:
            line = f"  • {p['name']}"
            if p.get("description"):
                line += f" — {p['description']}"
            attrs = []
            if p.get("target_segment"):
                attrs.append(f"target: {p['target_segment']}")
            if p.get("price_tier"):
                attrs.append(f"tier: {p['price_tier']}")
            if p.get("key_benefit"):
                attrs.append(f"benefit: {p['key_benefit']}")
            if attrs:
                line += f" ({', '.join(attrs)})"
            parts.append(line)

    # ── Positioning ───────────────────────────────────────────
    pos = brand.get("positioning", {})
    if any(pos.get(k) for k in ("value_proposition", "competitive_advantage", "personality", "tone_of_voice")):
        parts.append("\nPositioning:")
        if pos.get("value_proposition"):
            parts.append(f"  Value Proposition: {pos['value_proposition']}")
        if pos.get("competitive_advantage"):
            parts.append(f"  Competitive Advantage: {pos['competitive_advantage']}")
        if pos.get("personality"):
            parts.append(f"  Brand Personality: {', '.join(pos['personality'])}")
        if pos.get("tone_of_voice"):
            parts.append(f"  Tone of Voice: {pos['tone_of_voice']}")

    # ── Audience ──────────────────────────────────────────────
    aud = brand.get("audience", {})
    if any(aud.get(k) for k in ("primary", "secondary", "key_pain_points", "key_desires")):
        parts.append("\nTarget Audience:")
        if aud.get("primary"):
            parts.append(f"  Primary: {aud['primary']}")
        if aud.get("secondary"):
            parts.append(f"  Secondary: {aud['secondary']}")
        if aud.get("key_pain_points"):
            parts.append(f"  Pain Points: {', '.join(aud['key_pain_points'])}")
        if aud.get("key_desires"):
            parts.append(f"  Desires: {', '.join(aud['key_desires'])}")

    # ── Competitors ───────────────────────────────────────────
    competitors = [c for c in brand.get("competitors", []) if c.get("name", "").strip()]
    if competitors:
        parts.append("\nCompetitors:")
        for c in competitors:
            line = f"  • {c['name']}"
            if c.get("our_differentiator"):
                line += f" → our edge: {c['our_differentiator']}"
            parts.append(line)

    # ── Goals ─────────────────────────────────────────────────
    goals = brand.get("goals", {})
    if goals.get("short_term") or goals.get("long_term"):
        parts.append("\nBrand Goals:")
        if goals.get("short_term"):
            parts.append(f"  Short-term: {goals['short_term']}")
        if goals.get("long_term"):
            parts.append(f"  Long-term: {goals['long_term']}")

    # ── Additional context ────────────────────────────────────
    ctx = brand.get("context", {})
    if ctx.get("current_challenges"):
        parts.append(f"\nCurrent Challenges: {ctx['current_challenges']}")
    if ctx.get("recent_campaigns"):
        parts.append(f"Recent Campaigns: {ctx['recent_campaigns']}")
    if ctx.get("sensitive_topics"):
        parts.append(f"Topics to avoid: {', '.join(ctx['sensitive_topics'])}")
    if ctx.get("additional_notes"):
        parts.append(f"Additional Notes: {ctx['additional_notes']}")

    return "\n".join(parts) if len(parts) > 1 else None
