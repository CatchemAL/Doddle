def build_chart(histogram: dict[int, int]) -> str:

    CHARS = 50

    worst_score = max(histogram.keys())
    largest = max(histogram.values())
    increment = largest / CHARS

    stars: list[str] = []
    for i in range(worst_score):
        value = histogram.get(i + 1, 0)
        num = round(value / increment)
        stars.append("*" * num)

    max_stars = max(len(star) for star in stars)

    rows: list[str] = []
    for i, star in enumerate(stars):
        value = histogram.get(i + 1, 0)
        counts = f"({value:,})".rjust(9, " ")
        padded_star = star.ljust(max_stars, " ")
        row = f"{i+1} | {padded_star}{counts}"
        rows.append(row)

    return "\n".join(rows)


histogram = {
    1: 1,
    2: 76,
    3: 1242,
    4: 1096,
    5: 54,
}

chart = build_chart(histogram)
print(chart)

if __name__ == "__main__":  # pragma: no cover
    from .cli import main as _main

    _main()
