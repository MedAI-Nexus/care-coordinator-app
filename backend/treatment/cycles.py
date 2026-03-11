"""Treatment cycle templates verified against PDF cycle sheets."""

CYCLE_TEMPLATES = {
    "tmz28": {
        "name": "Temozolomide 28-Day Cycle",
        "length": 28,
        "days": {
            # Days 1-5: Drug days
            **{d: "drug" for d in range(1, 6)},
            # Days 6-21: Rest
            **{d: "rest" for d in range(6, 22)},
            # Day 22: Bloodwork
            22: "bloodwork",
            # Days 23-28: Rest
            **{d: "rest" for d in range(23, 29)},
        },
        "drug_name": "Temozolomide (TMZ)",
    },
    "etoposide28": {
        "name": "Etoposide 28-Day Cycle",
        "length": 28,
        "days": {
            # Days 1-10: Drug days
            **{d: "drug" for d in range(1, 11)},
            # Days 11-21: Rest
            **{d: "rest" for d in range(11, 22)},
            # Day 22: Bloodwork
            22: "bloodwork",
            # Days 23-28: Rest
            **{d: "rest" for d in range(23, 29)},
        },
        "drug_name": "Etoposide",
    },
}
