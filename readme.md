# Erebus

## Abstract

Erebus is a tiny, seed‑driven image scrambler. Given an input image, a random seed, and an iteration count, it applies a deterministic sequence of toroidal row/column rotations: on each step it picks a direction (up/down/left/right), a pivot row or column, and a shift amount, then cyclically rotates those pixels. Colors are never changed—only pixel positions are permuted—so running with the same seed and iterations reproduces the exact result, and the transform is theoretically reversible if you apply the inverse steps.

## Introduction

Erebus is an experiment in pixel permutation using only simple wrap-around shifts. With a seed and a step count, it produces the same shuffled arrangement every run while never altering any color values. Because only positions change, structure can reappear with appropriate parameters, and an exact inverse exists in principle. It is useful for reproducible art, pedagogy around permutations, and lightweight obfuscation—though it is not cryptographic security.

## Iterations

### female.png

| Original               | 1w or 1h                             | 1w + 1h                              | 2w + 1h                              | 2w + 2h                              |
|:----------------------:|:------------------------------------:|:------------------------------------:|:------------------------------------:|:------------------------------------:|
|![](./assets/female.png)|![](./assets/female_1769320125726.png)|![](./assets/female_1769320156351.png)|![](./assets/female_1769320208146.png)|![](./assets/female_1769320262424.png)|

## Performance

Performance depends on CPU, memory bandwidth, and Python/Tk build, so times vary by system; however, concrete numbers help set expectations. Each step rotates a single row or column, so runtime scales approximately with iterations × (width + height). The table below reports average timings from a reference system (specs included) as an indicative baseline; results on other systems may differ.

### 1w or 1h

| Image        | Size      | Iterations | Encryption time | Decryption time |
| ------------ | --------- | ---------- | --------------- | --------------- |
| female.png   | 256x256   | 256        | 0.266100        | TBD             |
| mandrill.png | 512x512   | 512        | 0.633300        | TBD             |
| male.png     | 1024x1024 | 1024       | 2.158500        | TBD             |

### 1w + 1h

| Image        | Size      | Iterations | Encryption time | Decryption time |
| ------------ | --------- | ---------- | --------------- | --------------- |
| female.png   | 256x256   | 512        | 0.384200        | TBD             |
| mandrill.png | 512x512   | 1024       | 1.100400        | TBD             |
| male.png     | 1024x1024 | 2048       | 4.071000        | TBD             |

### 2w + 1h

| Image        | Size      | Iterations | Encryption time | Decryption time |
| ------------ | --------- | ---------- | --------------- | --------------- |
| female.png   | 256x256   | 768        | 0.500800        | TBD             |
| mandrill.png | 512x512   | 1536       | 1.580900        | TBD             |
| male.png     | 1024x1024 | 3072       | 6.010700        | TBD             |

### 2w + 2h

| Image        | Size      | Iterations | Encryption time | Decryption time |
| ------------ | --------- | ---------- | --------------- | --------------- |
| female.png   | 256x256   | 1024       | 0.616300        | TBD             |
| mandrill.png | 512x512   | 2048       | 2.084600        | TBD             |
| male.png     | 1024x1024 | 4096       | 8.044000        | TBD             |

### System specs

```
OS: macOS 15.6.1 24G90 arm64
Host: Mac16,10
Kernel: 24.6.0
CPU: Apple M4
GPU: Apple M4
Memory: 2270MiB / 16384MiB
```

## Vision LLMs test

### mistral-3
### qwen3-vl
### gemma3

## Conclusion

## Usage

- Requirements: Python 3.9+ with Tkinter (PhotoImage). Verify with `python3 -c "import tkinter; print('ok')"`.
- CLI: `python3 src/erebus.py <image_path> <seed> <iterations>`
- Example: `python3 src/erebus.py assets/lenna.png 42 1500`
- Output: writes `<image_stem>_<epoch_ms>.png` next to the input image
- Help: `python3 src/erebus.py -h`

Notes:
- Only pixel positions change; running with the same seed and iterations reproduces the same arrangement for a given image size.
- Tk PhotoImage natively supports PNG/GIF/PPM/PGM; convert other formats to PNG before use.

## References

- https://en.wikipedia.org/wiki/Lenna
- https://sipi.usc.edu/database/
