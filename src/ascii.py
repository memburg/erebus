ascii_logo = [
    "███████╗██████╗ ███████╗██████╗ ██╗   ██╗███████╗\n",
    "██╔════╝██╔══██╗██╔════╝██╔══██╗██║   ██║██╔════╝\n",
    "█████╗  ██████╔╝█████╗  ██████╔╝██║   ██║███████╗\n",
    "██╔══╝  ██╔══██╗██╔══╝  ██╔══██╗██║   ██║╚════██║\n",
    "███████╗██║  ██║███████╗██████╔╝╚██████╔╝███████║\n",
    "╚══════╝╚═╝  ╚═╝╚══════╝╚═════╝  ╚═════╝ ╚══════╝\n",
]


def _bar_label(pct: int) -> str:
    # One leading space + right-aligned 3-digit percent
    return " " + f"{pct:>3d}%"


def _make_bar_line(pct: int, width: int = 44) -> str:
    filled = int(round(width * pct / 100.0))
    if filled < 0:
        filled = 0
    if filled > width:
        filled = width
    return "█" * filled + "░" * (width - filled) + _bar_label(pct) + "\n"


zero_percent = [_make_bar_line(0)]
ten_percent = [_make_bar_line(10)]
twenty_percent = [_make_bar_line(20)]
thirty_percent = [_make_bar_line(30)]
forty_percent = [_make_bar_line(40)]
fifty_percent = [_make_bar_line(50)]
sixty_percent = [_make_bar_line(60)]
seventy_percent = [_make_bar_line(70)]
eighty_percent = [_make_bar_line(80)]
ninety_percent = [_make_bar_line(90)]
hundred_percent = [_make_bar_line(100)]


def _lerp(a, b, t):
    return int(a + (b - a) * t)


def print_gradient(lines, start=(255, 0, 128), end=(0, 255, 255)):
    # Horizontal gradient: color per column left to right
    max_len = 0
    for s in lines:
        l = len(s.rstrip("\n"))
        if l > max_len:
            max_len = l
    if max_len == 0:
        return

    out = []
    for s in lines:
        line = s.rstrip("\n")
        for j, ch in enumerate(line):
            t = j / (max_len - 1) if max_len > 1 else 0.0
            r = _lerp(start[0], end[0], t)
            g = _lerp(start[1], end[1], t)
            b = _lerp(start[2], end[2], t)
            out.append(f"\x1b[38;2;{r};{g};{b}m{ch}")
        out.append("\x1b[0m\n")
    print("".join(out), end="")


def print_logo(start=(255, 0, 128), end=(0, 255, 255)) -> None:
    print_gradient(ascii_logo, start=start, end=end)


def _demo() -> None:
    print_gradient(ascii_logo)
    for b in [
        zero_percent,
        ten_percent,
        twenty_percent,
        thirty_percent,
        forty_percent,
        fifty_percent,
        sixty_percent,
        seventy_percent,
        eighty_percent,
        ninety_percent,
        hundred_percent,
    ]:
        print_gradient(b)


if __name__ == "__main__":
    _demo()
