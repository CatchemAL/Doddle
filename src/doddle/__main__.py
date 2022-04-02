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
