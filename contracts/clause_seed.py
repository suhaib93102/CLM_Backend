from __future__ import annotations

import re
from typing import Iterable, Optional

from django.db import transaction

from .models import Clause


_DEFAULT_CONTRACT_TYPES: list[str] = [
    "nda",
    "msa",
    "sow",
    "employment",
    "general",
]


def _slug(s: str) -> str:
    s = (s or "").strip().lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    return re.sub(r"_+", "_", s).strip("_") or "item"


def ensure_tenant_clause_library_seeded(
    *,
    tenant_id,
    user_id,
    contract_type: Optional[str] = None,
    min_count: int = 50,
) -> None:
    """Ensure a tenant has a usable clause library.

    This seeds `contracts.Clause` using the existing built-in Review clause library.

    Notes:
    - Seeding is tenant-scoped.
    - If `contract_type` is provided, we seed only that contract type.
    - If omitted and tenant has no clauses, we seed a few common contract types.
    """

    if not tenant_id or not user_id:
        return

    def _seed_for_type(ct: str) -> None:
        existing = Clause.objects.filter(tenant_id=tenant_id, status="published", contract_type=ct).count()
        if existing >= min_count:
            return

        # Local import to avoid eager import costs / circular deps.
        from reviews.clause_library_data import CLAUSE_LIBRARY

        # Deterministic IDs so we can safely re-run.
        target: Iterable[dict] = CLAUSE_LIBRARY

        with transaction.atomic():
            created = 0
            for entry in target:
                key = str(entry.get("key") or "")
                title = str(entry.get("title") or "Untitled Clause")
                content = str(entry.get("content") or "")
                category = str(entry.get("category") or "General")

                clause_id = f"{_slug(ct)}-{_slug(key)}".upper()
                Clause.objects.get_or_create(
                    tenant_id=tenant_id,
                    clause_id=clause_id,
                    version=1,
                    defaults={
                        "name": title,
                        "contract_type": ct,
                        "content": content,
                        "status": "published",
                        "is_mandatory": False,
                        "alternatives": [],
                        "tags": [category],
                        "source_template": "built_in_review_library",
                        "source_template_version": 1,
                        "created_by": user_id,
                    },
                )
                created += 1
                if created >= min_count:
                    break

    if contract_type:
        _seed_for_type(str(contract_type))
        return

    # No contract type filter: only seed if tenant has nothing at all.
    any_existing = Clause.objects.filter(tenant_id=tenant_id, status="published").exists()
    if any_existing:
        return

    for ct in _DEFAULT_CONTRACT_TYPES:
        _seed_for_type(ct)
