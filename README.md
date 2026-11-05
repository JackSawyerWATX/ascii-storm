# ASCII Thunderstorm

A terminal-based ASCII thunderstorm animation reconstructed from a 20-second
video recording. Run it in a Windows terminal to see animated clouds, rain, and
lightning.

## Table of Contents

- [About](#about)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [Security](#security)
- [How to Contribute?](#how-to-contribute)
- [What's Next?](#whats-next)
- [License](#license)
- [Acknowledgements](#acknowledgements)
- [Author](#author)

## About

ASCII Thunderstorm recreates the central storm effect visible in the source
recording as a text animation. It is a reconstruction, not a verbatim extraction:
parts of the original source were cropped out of the recording and had to be
approximated. The animation aims to resemble the visible effect; pixel-for-pixel
fidelity is not guaranteed.

The recording's status counters, ground decorations and splashes, timer, and
code editor are not part of this reconstruction.

## Features

- Animated cloud, rain, and lightning effects rendered as terminal characters.
- Real-time playback at 30 frames per second for 20 seconds by default.
- Optional loop playback and fitting to a smaller terminal.
- Still-frame output for saving or inspecting a chosen point in the animation.
- Windows ANSI terminal support and restoration of the cursor and terminal
  screen when playback ends.
- A default-resolution terminal size check to help prevent wrapped output.

## Tech Stack

- Python 3.10 or newer
- NumPy 2.x
- Windows Command Prompt, PowerShell, or Windows Terminal for the provided
  launcher and interactive playback

## Architecture

The animation is generated locally by `storm.py`:

1. NumPy arrays represent the terminal grid and calculate cloud density and
   lighting using layered noise.
2. A rain simulation advances raindrop positions each frame.
3. Lightning strikes are generated from seeded paths and composited over the
   scene at the configured strike times.
4. A character brightness ramp converts the scene into a grid of text.
5. The playback loop writes each frame to the terminal at the target frame rate.

The random-number generator is seeded, and the storm uses a fixed resolution of
120 columns by 76 rows unless `--fit` is selected.

## Project Structure

```text
ascii-storm/
├── README.md
├── requirements.txt
├── run.cmd
└── storm.py
```

- `storm.py` — storm simulation, frame rendering, playback, and command-line
  options.
- `requirements.txt` — NumPy dependency.
- `run.cmd` — Windows launcher that creates a local virtual environment,
  installs dependencies, runs the animation, and pauses afterward.

## Getting Started

### Prerequisites

- Python 3.10 or newer.
- Internet access for the initial NumPy installation.
- For the default animation size, a terminal with at least 121 columns and
  77 rows. Maximize the terminal or reduce its font size if needed.

A dark terminal background and a monospaced font such as Consolas are
recommended.

### Run on Windows

Open a terminal in the project folder and run:

```powershell
.\run.cmd
```

The launcher creates `.venv`, installs the requirements, and starts playback.
Press `Ctrl+C` to stop.

To fit the animation to a smaller terminal:

```powershell
.\run.cmd --fit
```

To repeat the animation:

```powershell
.\run.cmd --loop
```

### Manual setup

If you prefer not to use the launcher:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe storm.py
```

If the `py` launcher is unavailable but `python` is installed, use
`python -m venv .venv` for the first command.

Save a still frame at 10 seconds:

```powershell
.\.venv\Scripts\python.exe storm.py --snapshot 10 > frame.txt
```

## Configuration

Command-line options are available through `storm.py` and are passed through by
`run.cmd`:

| Option | Description |
| --- | --- |
| `--seconds SECONDS` | Set playback duration in seconds (default: `20`). |
| `--loop` | Repeat playback until interrupted. |
| `--fit` | Fit the animation to a smaller terminal; this changes its proportions. |
| `--snapshot SECONDS` | Print one still frame at the specified time without ANSI playback controls. |

For example, run a 12-second animation:

```powershell
.\.venv\Scripts\python.exe storm.py --seconds 12
```

## Security

The application does not require credentials or contact a service during
playback. Internet access is needed to install NumPy when setting up the
environment. Install dependencies from the included `requirements.txt` and
review the source before running it if you need to verify its behavior.

## How to Contribute?

Contributions can improve the reconstruction, documentation, or playback
experience. Before proposing a change:

1. Keep changes focused and explain any intentional change to the animation.
2. Run the program or use `--snapshot` to check the affected behavior.
3. Update this README if commands, options, or requirements change.
4. Share your change through the project's hosting platform, if applicable.

## What's Next?

Possible future improvements include adding automated checks for frame
dimensions and command-line validation, and documenting or refining the
approximated details of the source reconstruction.

## License

No license is specified in the files included with this project. Contact the
project owner for permission before redistributing or reusing the code.

## Acknowledgements

The source recording displays the credit `@leonario23` (2026). This
reconstruction uses that recording as its visual reference; portions obscured by
the editor crop are approximations.

## Author

The author of this reconstruction is not identified in the project files.
