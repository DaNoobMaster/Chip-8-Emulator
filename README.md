# CHIP-8 Emulator

A CHIP-8 interpreter written in Python with a Pygame. It recreates the classic 64×32 monochrome display, emulates the CHIP-8 CPU and timers, provides keyboard and on-screen input, and lets users change several compatibility quirks.

## Controls

The physical keyboard follows the conventional CHIP-8 keypad mapping:

| CHIP-8 row | CHIP-8 keys | Physical keyboard |
|---|:---:|:---:|
| 1 | `1 2 3 C` | `1 2 3 4` |
| 2 | `4 5 6 D` | `Q W E R` |
| 3 | `7 8 9 E` | `A S D F` |
| 4 | `A 0 B F` | `Z X C V` |

You can also use the on-screen keypad with the mouse. Press **Esc** to exit the emulator.

## Configurable quirks

The Quirks panel exposes the following compatibility settings:

| Setting | Enabled | Disabled |
|---|---|---|
| **VF Reset** | `8XY1`, `8XY2`, and `8XY3` clear `VF`. | These logical operations leave `VF` unchanged. |
| **Memory Increment** | `FX55` and `FX65` increment `I` by `X + 1`. | `I` remains unchanged after the transfer. |
| **Display Wait** | `DXYN` waits for the next display/timer tick before drawing. | Sprites are drawn immediately. |
| **Sprite Clipping** | Sprites are clipped at the right and bottom display edges. | Sprites wrap around the display edges. |
| **Shifting** | `8XY6` and `8XYE` use `VY` as the source register. | The shift instructions use `VX` as the source register. |
| **Jumping** | `BNNN` uses `VX` as the address offset. | `BNNN` uses `V0` as the address offset. |

## Supported instructions

The current implementation includes these CHIP-8 instruction families:

- `00E0`, `00EE`
- `1NNN`, `2NNN`, `3XNN`, `4XNN`, `5XY0`, `6XNN`, `7XNN`
- `8XY0`, `8XY1`, `8XY2`, `8XY3`, `8XY4`, `8XY5`, `8XY6`, `8XY7`, `8XYE`
- `9XY0`, `ANNN`, `BNNN`, `CXNN`, `DXYN`
- `EX9E`, `EXA1`
- `FX07`, `FX0A`, `FX15`, `FX18`, `FX1E`, `FX29`, `FX33`, `FX55`, `FX65`

This project currently targets the original CHIP-8 display and instruction set; Super-CHIP-specific extensions are not listed as implemented.

## Run from source

### Requirements

- Python
- Pygame CE
- Tkinter (used for the ROM file picker)

### Install and run

1. Clone or download this repository.
2. Open a terminal in the project directory.
3. Install Pygame CE:

   ```bash
   python -m pip install pygame-ce
   ```

4. Start the emulator:

   ```bash
   python emulator.py
   ```

5. When the file picker opens, choose a CHIP-8 ROM with the `.ch8` extension.

> **Note:** The file picker appears at startup. Select a valid ROM to start the emulator.

## Build a Windows executable

You can package the emulator with PyInstaller:

```bash
python -m pip install pyinstaller pygame-ce
python -m PyInstaller --clean --noconfirm --onefile --windowed --name Chip8 emulator.py
```

The executable will be created at:

```text
dist/Chip8.exe
```

Build the Windows executable on Windows. Test the generated executable on a separate machine before distributing it.
