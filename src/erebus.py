import sys
import random
import argparse
import tkinter as tk

from enum import IntEnum
from pathlib import Path

from dataclasses import dataclass

from ascii import print_logo, render_progress_bar


SUPPORTED_FORMATS = {"png", "gif", "ppm", "pgm"}
MODE_ALIASES = {
    "cipher": "cipher",
    "encrypt": "cipher",
    "decipher": "decipher",
    "decrypt": "decipher",
}


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


@dataclass(frozen=True, slots=True)
class CliConfig:
    target_path: Path
    seed: int
    iterations: int
    mode: str


@dataclass(frozen=True, slots=True)
class ProcessResult:
    source: Path
    output: Path
    width: int
    height: int


@dataclass(frozen=True, slots=True)
class ProcessFailure:
    source: Path
    error: str


def load_image_tk(image_path: str | Path) -> LoadedImage:
    root = tk.Tk()
    root.withdraw()
    try:
        img = tk.PhotoImage(master=root, file=str(image_path))
    except tk.TclError as e:
        root.destroy()
        raise ValueError(f"Failed to load image '{image_path}': {e}") from e
    return LoadedImage(root=root, image=img)


def normalize_mode(mode: str) -> str:
    normalized = MODE_ALIASES.get(mode.strip().lower())
    if normalized is None:
        raise ValueError(f"Unsupported mode: {mode}")
    return normalized


def parse_args() -> CliConfig:
    parser = argparse.ArgumentParser(description="Erebus image encrypt/decrypt CLI")
    parser.add_argument("image_path", type=Path, help="Path to an image or folder")
    parser.add_argument("seed", type=int, help="Random seed")
    parser.add_argument(
        "iterations", type=int, help="Number of steps to generate/apply"
    )
    parser.add_argument(
        "-m",
        "--mode",
        choices=sorted(MODE_ALIASES),
        default="cipher",
        type=str.lower,
        help="Operation to perform (default: encrypt; cipher/decipher also accepted)",
    )
    args = parser.parse_args()
    if args.iterations < 1:
        parser.error("iterations must be a positive integer")
    return CliConfig(
        target_path=args.image_path,
        seed=args.seed,
        iterations=args.iterations,
        mode=normalize_mode(args.mode),
    )


def prompt_for_existing_path() -> Path:
    while True:
        raw = input("Image or folder path: ").strip()
        if not raw:
            print("Please enter a file or folder path.")
            continue
        candidate = Path(raw).expanduser()
        if candidate.exists():
            return candidate
        print(f"Path does not exist: {candidate}")


def prompt_for_int(prompt: str, minimum: int | None = None) -> int:
    while True:
        raw = input(prompt).strip()
        try:
            value = int(raw)
        except ValueError:
            print("Please enter a valid integer.")
            continue

        if minimum is not None and value < minimum:
            print(f"Value must be at least {minimum}.")
            continue
        return value


def prompt_for_mode() -> str:
    while True:
        raw = input("Mode [encrypt/decrypt] (default: encrypt): ").strip()
        if not raw:
            return "cipher"
        try:
            return normalize_mode(raw)
        except ValueError:
            print("Please choose encrypt or decrypt.")


def prompt_for_config() -> CliConfig:
    print("Interactive mode")
    target_path = prompt_for_existing_path()
    mode = prompt_for_mode()
    iterations = prompt_for_int("Iterations: ", minimum=1)
    seed = prompt_for_int("Seed: ")
    return CliConfig(
        target_path=target_path,
        seed=seed,
        iterations=iterations,
        mode=mode,
    )


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


def output_prefix(mode: str) -> str:
    return "c-" if mode == "cipher" else "d-"


def build_output_path(image_path: Path, mode: str) -> tuple[Path, str]:
    prefix = output_prefix(mode)
    orig_ext = image_path.suffix.lower()
    ext_no_dot = orig_ext[1:] if orig_ext.startswith(".") else orig_ext
    if ext_no_dot in SUPPORTED_FORMATS and orig_ext:
        out_filename = f"{prefix}{image_path.name}"
        out_format = ext_no_dot
    else:
        out_filename = f"{prefix}{image_path.stem}.png"
        out_format = "png"
    return image_path.with_name(out_filename), out_format


def iter_supported_images(folder_path: Path) -> list[Path]:
    return sorted(
        [
            path
            for path in folder_path.iterdir()
            if path.is_file() and path.suffix.lower().lstrip(".") in SUPPORTED_FORMATS
        ],
        key=lambda path: path.name.lower(),
    )


def process_image_path(
    image_path: Path,
    mode: str,
    seed: int,
    iterations: int,
    *,
    show_size: bool = False,
) -> ProcessResult:
    loaded = load_image_tk(image_path)
    try:
        width = loaded.image.width()
        height = loaded.image.height()
        if show_size:
            print(f"Image size: {width}x{height}")

        if mode == "cipher":
            cipher(loaded, seed, iterations)
        else:
            decipher(loaded, seed, iterations)

        out_path, out_format = build_output_path(image_path, mode)
        try:
            loaded.image.write(str(out_path), format=out_format)
        except Exception as e:
            raise ValueError(f"Failed to write output image: {e}") from e
        return ProcessResult(
            source=image_path,
            output=out_path,
            width=width,
            height=height,
        )
    finally:
        loaded.root.destroy()


def update_progress(current: int, total: int) -> None:
    sys.stdout.write("\r" + render_progress_bar(current, total))
    sys.stdout.flush()


def process_single_target(config: CliConfig) -> int:
    try:
        result = process_image_path(
            config.target_path,
            config.mode,
            config.seed,
            config.iterations,
            show_size=True,
        )
    except Exception as e:
        print(e, file=sys.stderr)
        return 1

    print(f"Wrote output to: {result.output}")
    return 0


def process_folder_target(config: CliConfig) -> int:
    image_paths = iter_supported_images(config.target_path)
    if not image_paths:
        print(
            f"No supported image files found in: {config.target_path}",
            file=sys.stderr,
        )
        return 1

    failures: list[ProcessFailure] = []
    total = len(image_paths)
    successes = 0

    print(f"Processing folder: {config.target_path}")
    update_progress(0, total)
    for index, image_path in enumerate(image_paths, start=1):
        try:
            process_image_path(
                image_path,
                config.mode,
                config.seed,
                config.iterations,
            )
            successes += 1
        except Exception as e:
            failures.append(ProcessFailure(source=image_path, error=str(e)))
        update_progress(index, total)

    print()
    print(
        f"Folder summary: {successes} succeeded, {len(failures)} failed, {total} total"
    )
    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure.source.name}: {failure.error}")
    return 0 if not failures else 1


def run(config: CliConfig) -> int:
    if config.target_path.is_file():
        return process_single_target(config)
    if config.target_path.is_dir():
        return process_folder_target(config)

    print(f"Path does not exist: {config.target_path}", file=sys.stderr)
    return 1


def main() -> None:
    try:
        if len(sys.argv) == 1:
            print_logo()
            config = prompt_for_config()
        else:
            config = parse_args()
            print_logo()
    except (EOFError, KeyboardInterrupt):
        print(file=sys.stderr)
        sys.exit(1)

    sys.exit(run(config))


if __name__ == "__main__":
    main()
