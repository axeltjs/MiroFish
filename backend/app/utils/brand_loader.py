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

# Separate cache for the vision product hint.
_cached_products: Optional[str] = None
_cache_products_mtime: float = 0.0


def load_brand_knowledge(force: bool = False) -> Optional[str]:
    """
    Return the formatted brand knowledge string, or None if:
    - the file doesn't exist
    - enabled = false (unless force=True)
    - no meaningful content has been filled in

    force=True ignores the `enabled` flag. Used when the user explicitly
    turns on Brand Mode in the UI — that toggle is itself the opt-in, so the
    TOML `enabled` flag (which gates any automatic/implicit usage) is bypassed.
    """
    global _cached_text, _cache_mtime

    if not os.path.exists(_TOML_PATH):
        return None

    # Explicit opt-in: parse fresh, ignore the enabled flag and the cache.
    if force:
        return _parse_toml(ignore_enabled=True)

    mtime = os.path.getmtime(_TOML_PATH)
    if mtime == _cache_mtime:
        return _cached_text

    _cache_mtime = mtime
    _cached_text = _parse_toml()
    return _cached_text


def get_brand_meta() -> dict:
    """
    Lightweight metadata about the configured brand, for display in the UI.
    Reads name and product count regardless of the `enabled` flag (so the
    brand-mode panel can confirm what would be loaded).

    Returns:
        {"configured": bool, "name": str, "tagline": str,
         "product_count": int, "enabled": bool}
    """
    empty = {"configured": False, "name": "", "tagline": "", "product_count": 0, "enabled": False}
    if not os.path.exists(_TOML_PATH):
        return empty
    try:
        with open(_TOML_PATH, "rb") as f:
            data = tomllib.load(f)
    except Exception:
        return empty

    brand = data.get("brand", {})
    name = brand.get("name", "").strip()
    if not name:
        return empty

    products = [p for p in brand.get("products", []) if p.get("name", "").strip()]
    return {
        "configured": True,
        "name": name,
        "tagline": brand.get("tagline", "").strip(),
        "product_count": len(products),
        "enabled": bool(data.get("enabled", False)),
    }


def load_brand_products_hint() -> Optional[str]:
    """
    Return a compact hint listing the brand's products, for use in the
    image/vision prompt so the model can match a photographed product
    against the known catalog.

    NOTE: Unlike load_brand_knowledge(), this intentionally does NOT require
    enabled = true. Matching a photographed product against a factual catalog
    is a low-risk aid for image extraction, separate from the brand-consultant
    persona (which still respects the enabled flag).

    Returns None if the file is missing or no products with names are defined.
    """
    global _cached_products, _cache_products_mtime

    if not os.path.exists(_TOML_PATH):
        return None

    mtime = os.path.getmtime(_TOML_PATH)
    if mtime == _cache_products_mtime:
        return _cached_products

    _cache_products_mtime = mtime
    _cached_products = _parse_products_hint()
    return _cached_products


def _parse_products_hint() -> Optional[str]:
    try:
        with open(_TOML_PATH, "rb") as f:
            data = tomllib.load(f)
    except Exception:
        return None

    brand = data.get("brand", {})
    brand_name = brand.get("name", "").strip()
    products = [p for p in brand.get("products", []) if p.get("name", "").strip()]
    if not products:
        return None

    label = f"{brand_name} products" if brand_name else "known brand products"
    lines = [
        f"KNOWN {label.upper()} (for visual matching): If a product or vehicle in the "
        "image closely resembles one of the following, identify which one it most likely "
        "is and explain the cues that led you there. If none match, say so rather than "
        "forcing a match.",
    ]
    for p in products:
        line = f"  • {p['name']}"
        if p.get("description"):
            line += f" — {p['description']}"
        lines.append(line)

    return "\n".join(lines)


def _parse_toml(ignore_enabled: bool = False) -> Optional[str]:
    try:
        with open(_TOML_PATH, "rb") as f:
            data = tomllib.load(f)
    except Exception:
        return None

    if not ignore_enabled and not data.get("enabled", False):
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
