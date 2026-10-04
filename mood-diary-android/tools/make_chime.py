#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Мягкий вечерний перезвон для плашки «пора спать».

Почему не системный звук уведомления. Стандартный звук — короткий и резкий:
он рассчитан на то, чтобы пробить шум улицы, и ночью будит. Здесь обратная
задача — не разбудить, а мягко подсказать. Поэтому: низкие обертона вместо
верхних, медленная атака, длинный спад и тихая амплитуда.

Файл кладётся в res/raw и подключается каналом уведомлений:
sound: "night_chime" (без расширения).

Запуск: python make_chime.py [путь-к-res/raw]
"""
from __future__ import annotations

import math
import struct
import sys
import wave
from pathlib import Path

RATE = 22050
DURATION = 2.4
PEAK = 0.20  # тихо: это ночной сигнал, а не будильник

# Обертона подобраны так, чтобы не было диссонанса: квинта и октава
# над основным тоном. Никаких тритонов и секунд.
PARTIALS = (
    (261.63, 1.00, 2.10),   # C4
    (392.00, 0.62, 1.75),   # G4
    (587.33, 0.34, 1.40),   # D5
    (783.99, 0.14, 1.10),   # G5
)


def build() -> list[float]:
    n = int(RATE * DURATION)
    out = [0.0] * n
    for freq, amp, decay in PARTIALS:
        # лёгкая расстройка пары обертонов даёт «тёплое» звучание
        detune = 1.0035 if amp > 0.5 else 1.0
        phase = 0.0
        for i in range(n):
            t = i / RATE
            env = (1 - math.exp(-t / 0.075)) * math.exp(-t / decay)
            # очень медленная амплитудная модуляция — «дыхание»
            env *= 1 + 0.06 * math.sin(2 * math.pi * 0.7 * t)
            phase += 2 * math.pi * freq * detune / RATE
            out[i] += amp * env * math.sin(phase)
    # нормализация и мягкий хвост
    top = max(abs(v) for v in out) or 1.0
    k = PEAK / top
    fade = int(RATE * 0.35)
    for i in range(n):
        v = out[i] * k
        if i > n - fade:
            v *= (n - i) / fade
        out[i] = v
    return out


def write(path: Path, samples: list[float]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        frames = b"".join(struct.pack("<h", int(max(-1.0, min(1.0, s)) * 32767)) for s in samples)
        w.writeframes(frames)


def main() -> None:
    out = Path(sys.argv[1]) / "night_chime.wav" if len(sys.argv) > 1 else Path("night_chime.wav")
    samples = build()
    write(out, samples)
    print(f"{out}  {out.stat().st_size // 1024} КБ  {DURATION} с  пик {PEAK}")


if __name__ == "__main__":
    main()