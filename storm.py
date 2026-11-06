"""ASCII thunderstorm reconstructed from the supplied video.
Clipped source portions are reconstructed; see README.md.
Original video credit visible on screen: @leonario23 (2026).
"""
import argparse
import os
import shutil
import sys
import time
import numpy as np

W, H = 120, 76
FPS = 30
RAMP = " .`^,:;Il!i><~+_-?][}{1)(|/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"
rng = np.random.default_rng(23)


def hash3(x, y, z):
    h = np.sin(x * 127.1 + y * 311.7 + z * 74.7) * 43758.5453
    return h - np.floor(h)


def noise(x, y, z):
    xi, yi, zi = np.floor(x), np.floor(y), np.floor(z)
    u, v, w = [(f - i) ** 2 * (3 - 2 * (f - i))
               for f, i in ((x, xi), (y, yi), (z, zi))]
    def c(a, b, d):
        return hash3(xi + a, yi + b, zi + d)
    lo = ((c(0, 0, 0) * (1-u) + c(1, 0, 0) * u) * (1-v)
          + (c(0, 1, 0) * (1-u) + c(1, 1, 0) * u) * v)
    hi = ((c(0, 0, 1) * (1-u) + c(1, 0, 1) * u) * (1-v)
          + (c(0, 1, 1) * (1-u) + c(1, 1, 1) * u) * v)
    return lo * (1-w) + hi * w


def fbm(x, y, z, octaves=5):
    total, amp = 0.0, 0.5
    for _ in range(octaves):
        total += amp * noise(x, y, z)
        x, y, z, amp = x*2.03, y*2.01, z*1.7, amp*0.5
    return total


# Tuples cut off by the video's right edge are approximations.
PUFFS = [(.12, .41, .07, 1.5), (.30, .42, .085, 1.2),
         (.48, .41, .10, 1.0), (.66, .41, .095, 1.3),
         (.84, .42, .075, 1.4), (.25, .36, .11, 2.0),
         (.43, .34, .12, 2.1), (.61, .34, .115, 2.0),
         (.79, .37, .10, 2.2), (.17, .30, .10, 2.8),
         (.33, .27, .105, 2.6), (.52, .26, .12, 2.8),
         (.72, .23, .125, 3.0), (.86, .31, .095, 2.7),
         (.45, .15, .115, 3.3), (.26, .15, .065, 4.0),
         (.80, .17, .06, 4.1)]


def cloud(t):
    X, Y = np.meshgrid(np.linspace(0, 1, W), np.linspace(0, 1, H))
    depth, light = np.zeros(X.shape), np.zeros(X.shape)
    turbulence = fbm(X*10, Y*10, t*.15) - .5  # clipped expression reconstructed
    for x, y, r, born in sorted(PUFFS, key=lambda p: p[1]):
        grow = 1 - (1 - np.clip(t-born, 0, 1)) ** 3
        if grow <= 0:
            continue
        nx, ny = (X-x)/(r*grow), (Y-y)/(r*grow)
        inside = nx**2 + ny**2 < 1 + .28*turbulence
        nz = np.sqrt(np.clip(1 - nx**2 - ny**2, 0, 1))
        depth = np.where(inside, nz, depth)
        light = np.where(inside, np.clip(-.35*nx - .75*ny + .55*nz, 0, 1), light)
    rim = np.clip(depth/.45, 0, 1)
    return light**1.4 * (.25 + .75*rim) * (Y < .445)


class Rain:
    def __init__(self, n=900):
        self.x = rng.uniform(0, W, n)
        self.y = rng.uniform(0, H, n)
        self.v = rng.uniform(26, 42, n)
        self.wind = -.28

    def step(self, dt, intensity):
        self.y += self.v*dt
        self.x += self.v*self.wind*dt
        gone = self.y > H-4
        self.y[gone] = rng.uniform(33, 36, gone.sum())
        self.x[gone] = rng.uniform(12, W-8, gone.sum())
        return np.flatnonzero(rng.random(len(self.v)) < intensity)


def bolt(x0, y0, ground, depth=0):
    pts, x, y, forks = [(x0, y0)], x0, y0, []
    while y < ground:
        y += rng.uniform(.6, 1.4)
        x += rng.normal(0, .9)
        pts.append((x, y))
        if depth < 2 and rng.random() < .12/(depth+1):
            end = min(ground, y + rng.uniform(6, 18))
            forks.append(bolt(x, y, end, depth+1))
    return {'path': pts, 'forks': forks, 'power': .55**depth}


def stroke(path):
    cells = {}
    for (xa, ya), (xb, yb) in zip(path, path[1:]):
        dx, dy = xb-xa, yb-ya
        ch = '|' if abs(dx) < .35*dy else ('\\' if dx > 0 else '/')
        cells[int(yb), int(xb)] = ch
    return cells


def flash(t, strikes):
    f = 0.0
    for s in strikes:
        for k, dt in enumerate((0, .12, .27)):
            if t >= s+dt:
                f += .9*k*np.exp(-(t-s-dt)/.06)
    return min(f, 1.5)


def shade(d, light):
    i = np.clip(d*(.6+light), 0, .999)
    return np.take(np.array(list(RAMP)), (i*len(RAMP)).astype(int))


STRIKES = [8.30, 12.05, 15.55]
BOLTS = {s: bolt(W*(.32+.18*k), 35, H-4) for k, s in enumerate(STRIKES)}


def frame(t, rain):
    d = cloud(t)
    canvas = shade(d, .4*flash(t, STRIKES))
    for i in rain.step(1/FPS, np.clip((t-5.2)/3.8, 0, 1)):
        x, y = int(rain.x[i]), int(rain.y[i])
        if 0 <= x < W and 0 <= y < H and d[y, x] == 0:
            canvas[y, x] = '/'
    for s, b in BOLTS.items():
        if s-.35 < t < s+.6:
            for (y, x), ch in stroke(b['path']).items():
                if 0 <= x < W and 0 <= y < H:
                    canvas[y, x] = ch
    return '\n'.join(''.join(row) for row in canvas)


def enable_ansi():
    if os.name == 'nt':
        import ctypes
        kernel = ctypes.windll.kernel32
        handle = kernel.GetStdHandle(-11)
        mode = ctypes.c_ulong()
        if kernel.GetConsoleMode(handle, ctypes.byref(mode)):
            kernel.SetConsoleMode(handle, mode.value | 4)


def run(seconds=20, loop=False, fit=False):
    global W, H, BOLTS
    if not sys.stdout.isatty():
        raise SystemExit('Run in a terminal, or use --snapshot SECONDS to save one frame.')
    cols, rows = shutil.get_terminal_size((121, 78))
    if fit:
        W, H = min(W, max(20, cols-1)), min(H, max(12, rows-1))
        BOLTS = {s: bolt(W*(.32+.18*k), H*35/76, H-4)
                 for k, s in enumerate(STRIKES)}
    elif cols < W+1 or rows < H+1:
        raise SystemExit(f'Use at least {W+1} columns and {H+1} rows. Maximize the terminal and reduce font size, or run with --fit.')
    enable_ansi()
    sys.stdout.write('\x1b[?1049h\x1b[2J\x1b[H\x1b[?25l')
    try:
        while True:
            rain = Rain()
            start = time.perf_counter()
            for n in range(round(seconds*FPS)):
                sys.stdout.write('\x1b[H' + frame(n/FPS, rain))
                sys.stdout.flush()
                time.sleep(max(0, start+(n+1)/FPS-time.perf_counter()))
            if not loop:
                break
    except KeyboardInterrupt:
        pass
    finally:
        sys.stdout.write('\x1b[?25h\x1b[?1049l')
        sys.stdout.flush()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seconds', type=float, default=20)
    parser.add_argument('--loop', action='store_true')
    parser.add_argument('--fit', action='store_true', help='Fit a smaller terminal (changes proportions)')
    parser.add_argument('--snapshot', type=float, metavar='SECONDS', help='Print a still frame without ANSI codes')
    args = parser.parse_args()
    if args.seconds <= 0 or not np.isfinite(args.seconds):
        parser.error('--seconds must be positive and finite')
    if args.snapshot is not None:
        if args.snapshot < 0 or not np.isfinite(args.snapshot):
            parser.error('--snapshot must be nonnegative and finite')
        rain = Rain()
        for n in range(round(args.snapshot*FPS)+1):
            result = frame(n/FPS, rain)
        print(result)
    else:
        run(args.seconds, args.loop, args.fit)
