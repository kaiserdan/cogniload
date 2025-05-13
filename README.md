# CogniLoad - Code
*(Elixir & Python version)*

This repository provides the implementation for the CogniLoad benchmark.

Originally written in **Elixir** for speed and efficiency, we ported the generator to **Python** so that anyone can reproduce the datasets without an Elixir tool-chain.

The Elixir version is roughly 30% faster than the python version and generates the 14'000 thousand  puzzle instances we evaluate in the paper in about 20 seconds on a Apple M4 Max processor.

## Quick start

Running CogniLoad without CLI parameters generates the puzzles in the default grid configuration that is reported in the paper.

### Running the Python version

Ensure Python ≥ 3,8 is on PATH (no additional packages needed).

```bash
python cogniload.py
```

Execution time is roughly 30% slower than Elixir.


### Running the Elixir version

Install the latest version of Elixir using the [official guide](https://elixir-lang.org/install.html).

```bash
elixir cogniload.exs
```

---

## Command-line arguments

The two scripts expose the CLI parameters for the puzzle generation. The defaults are identical and set to the parameters evaluated in the paper.

| Flag Elixir | Flag Elixir short | Flag Python | Type | Default | Description |
|:---|:---|:---|:---|:---|:---|
| `--nums` | `-n` | `--num_grid` | comma-sep ints | 20,50,100,250 | Numbers of **statements** per puzzle |
| `--ratios` | `-r` | `--ratio_grid` | comma-sep ints | 5,10,25,50,75,90,95 | Percentage of **needles** (POI statements) |
| `--diffs` | `-d` | `--difficulty_grid` | comma-sep ints | 1,3,5,7,10 | Puzzle **difficulty** |
| `--puzzles` | `-p` | `--number_of_puzzles` | int | 100 | Puzzles **per (num × ratio × diff)** combo |
| `--seed` | `-s` | `--original_seed` | int | 42 | Global RNG **seed** |

### Examples

Generate 10 puzzles with 50 statements, 10 % needles, difficulty 5, and seed 42:

```bash
# Elixir
elixir cogniload.exs --nums 50 --ratios 10 --diffs 5 --puzzles 10 --seed 42
# Python
python cogniload.py --num_grid 50 --ratio_grid 10 --difficulty_grid 5 --number_of_puzzles 10 --original_seed 42
```

---

## Output structure

| Path | Contents |
|:---|:---|
| `exp/cogniload/…/*.txt` | Generated puzzle instances |
| `meta/cogniload/…/*_state.json` | Full state metadata |
 

The filename of the generated puzzle instances includes the puzzle parameters, a puzzle id, and the solution. 

Example: A puzzle with the name `20_5_10_102133_yellow.txt` consists of 20 statements, has difficulty 5, contains 10 needles, has the random puzzle id 102133, and the solution is the word "yellow".

---
## Dataset on Huggingface

The original dataset with the puzzles evaluated in the paper is provided at [https://huggingface.co/datasets/dkfo/cogniload](https://huggingface.co/datasets/dkfo/cogniload).

The data is enriched with Croissant metadata and includes the puzzle text, the parameter configuration of the puzzle, and the generated metadata in a jsonl format.

---

## Contributing

Bug reports and PRs are very welcome! For substantial changes please open an issue first.

---

## License

This code and the dataset are provided under a [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) license.


