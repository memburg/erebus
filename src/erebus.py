import sys
import random
import argparse
import tkinter as tk

from enum import IntEnum
from pathlib import Path

from ascii import print_logo
from dataclasses import dataclass


class Direction(IntEnum):
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3


@dataclass(frozen=True, slots=True)
class Step:
    direction: Direction  # up (0), down (1), left (2), right (3)
    moves: int  # amount to shift (toroidal)
    pivot: int  # row index (LEFT/RIGHT) or column index (UP/DOWN)


@dataclass(frozen=True, slots=True)
class LoadedImage:
    root: "tk.Tk"
    image: "tk.PhotoImage"


def load_image_tk(image_path: str) -> LoadedImage:
    root = tk.Tk()
    root.withdraw()
    try:
        img = tk.PhotoImage(master=root, file=str(image_path))
    except tk.TclError as e:
        root.destroy()
        raise ValueError(f"Failed to load image '{image_path}': {e}") from e
    return LoadedImage(root=root, image=img)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Erebus image cipher/decipher")
    parser.add_argument("image_path", type=Path, help="Path to the image")
    parser.add_argument("seed", type=int, help="Random seed")
    parser.add_argument(
        "iterations", type=int, help="Number of steps to generate/apply"
    )
    parser.add_argument(
        "-m",
        "--mode",
        choices=["cipher", "decipher"],
        default="cipher",
        help="Operation to perform (default: cipher)",
    )
    args = parser.parse_args()
    if args.iterations < 1:
        parser.error("iterations must be a positive integer")
    return args


def generate_sequence(
    rng: random.Random, iterations: int, w: int, h: int, pivot: int | None = None
) -> list[Step]:
    # Each step picks a random direction and a valid pivot in that axis
    steps: list[Step] = []
    for _ in range(iterations):
        direction = Direction(rng.randint(0, 3))
        if direction in (Direction.UP, Direction.DOWN):
            max_moves = h
            pivot_size = w  # column index range
        else:
            max_moves = w
            pivot_size = h  # row index range
        step_pivot = (
            rng.randint(0, pivot_size - 1) if pivot is None else (pivot % pivot_size)
        )
        steps.append(Step(direction, rng.randint(1, max_moves), step_pivot))
    return steps


def move_row(im: LoadedImage, direction: Direction, pivot: int, moves: int):
    # Move a single row left or right by the given amount (toroidal)
    img = im.image
    w, h = img.width(), img.height()

    if w == 0 or h == 0:
        return

    if direction not in (Direction.LEFT, Direction.RIGHT):
        raise ValueError("move_row supports only LEFT or RIGHT directions")

    y = pivot % h

    shift = moves % w
    if shift == 0:
        return

    # Shifting right by N == shifting left by (w - N)
    if direction == Direction.RIGHT:
        shift = (w - shift) % w

    def _to_color_string(value):
        if isinstance(value, str):
            return value
        if isinstance(value, tuple):
            if len(value) >= 3:
                r, g, b = value[0], value[1], value[2]
                return f"#{int(r):02x}{int(g):02x}{int(b):02x}"
        # Fallback to string conversion
        return str(value)

    row = [img.get(x, y) for x in range(w)]
    rotated = row[shift:] + row[:shift]
    for x, color in enumerate(rotated):
        img.put(_to_color_string(color), (x, y))


def move_column(im: LoadedImage, direction: Direction, pivot: int, moves: int):
    # Move a single column up or down by the given amount (toroidal)
    img = im.image
    w, h = img.width(), img.height()

    if w == 0 or h == 0:
        return

    if direction not in (Direction.UP, Direction.DOWN):
        raise ValueError("move_column supports only UP or DOWN directions")

    x = pivot % w

    shift = moves % h
    if shift == 0:
        return

    # Shifting down by N == shifting up by (h - N)
    if direction == Direction.DOWN:
        shift = (h - shift) % h

    def _to_color_string(value):
        if isinstance(value, str):
            return value
        if isinstance(value, tuple):
            if len(value) >= 3:
                r, g, b = value[0], value[1], value[2]
                return f"#{int(r):02x}{int(g):02x}{int(b):02x}"
        return str(value)

    col = [img.get(x, y) for y in range(h)]
    rotated = col[shift:] + col[:shift]
    for y, color in enumerate(rotated):
        img.put(_to_color_string(color), (x, y))


def inverse_direction(direction: Direction) -> Direction:
    if direction == Direction.LEFT:
        return Direction.RIGHT
    if direction == Direction.RIGHT:
        return Direction.LEFT
    if direction == Direction.UP:
        return Direction.DOWN
    if direction == Direction.DOWN:
        return Direction.UP
    raise ValueError(f"Unsupported direction: {direction}")


def apply_step(im: LoadedImage, step: Step) -> None:
    if step.direction in (Direction.LEFT, Direction.RIGHT):
        move_row(im, step.direction, step.pivot, step.moves)
    elif step.direction in (Direction.UP, Direction.DOWN):
        move_column(im, step.direction, step.pivot, step.moves)
    else:
        raise ValueError(f"Unsupported direction: {step.direction}")


def cipher(
    im: LoadedImage, seed: int, iterations: int, pivot: int | None = None
) -> None:
    rng = random.Random(seed)
    sequence = generate_sequence(
        rng, iterations, im.image.width(), im.image.height(), pivot
    )
    for step in sequence:
        apply_step(im, step)


def decipher(
    im: LoadedImage, seed: int, iterations: int, pivot: int | None = None
) -> None:
    rng = random.Random(seed)
    sequence = generate_sequence(
        rng, iterations, im.image.width(), im.image.height(), pivot
    )
    for step in reversed(sequence):
        inv = Step(
            direction=inverse_direction(step.direction),
            moves=step.moves,
            pivot=step.pivot,
        )
        apply_step(im, inv)


def main() -> None:
    args = parse_args()
    print_logo()

    try:
        loaded = load_image_tk(args.image_path)
    except ValueError as e:
        print(e, file=sys.stderr)
        sys.exit(1)
    else:
        print(f"Image size: {loaded.image.width()}x{loaded.image.height()}")
        if args.mode == "cipher":
            cipher(loaded, args.seed, args.iterations)
        else:
            decipher(loaded, args.seed, args.iterations)

        # Save output image next to input with c-/d- prefix
        prefix = "c-" if args.mode == "cipher" else "d-"
        orig_ext = args.image_path.suffix.lower()
        ext_no_dot = orig_ext[1:] if orig_ext.startswith(".") else orig_ext
        supported = {"png", "gif", "ppm", "pgm"}
        if ext_no_dot in supported and orig_ext:
            out_filename = f"{prefix}{args.image_path.name}"
            out_format = ext_no_dot
        else:
            out_filename = f"{prefix}{args.image_path.stem}.png"
            out_format = "png"
        out_path = args.image_path.with_name(out_filename)
        try:
            loaded.image.write(str(out_path), format=out_format)
            print(f"Wrote output to: {out_path}")
        except Exception as e:
            print(f"Failed to write output image: {e}", file=sys.stderr)

        loaded.root.destroy()


if __name__ == "__main__":
    main()
