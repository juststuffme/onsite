# Voxelab Aquila X2 (N32 chip) — MRiscoC ProUI firmware

This folder contains ready-to-flash firmware that **fixes the DWIN display
ghosting** (menus/icons not clearing when you make a selection) and replaces the
old 4‑icon menus with **clean, scrollable list menus** that redraw properly.

It is the community **MRiscoC ProUI** firmware, release **`2.1.3h-7`**
(July 2026), built for the **N32** mainboard — the exact chip in your printer.

> **Why not a "no menu at all" build?** The menu is program code compiled into
> the mainboard firmware, and a truly menu‑less custom build would have to be
> compiled and could not be tested before you flash it (real risk of a
> boot‑loop/brick). This pre‑built firmware is tested by thousands of Aquila
> owners, needs no compiling, and its scrollable lists solve the ghosting that
> was the actual problem.

---

## What's in here

| File | Flashes to | Purpose |
|------|-----------|---------|
| `Aquila_N32_Default-07-13.bin` | **Printer mainboard** (printer's SD slot) | The firmware (menus, motion, temps) |
| `DWIN_SET/` | **Display unit** (SD slot *behind the screen*) | The matching icons/graphics |

You flash **both**, in **two separate steps**, using the **two different SD
slots**. The mainboard `.bin` goes in the printer's normal SD slot; the
`DWIN_SET` folder goes in the little SD slot on the **back of the screen**.

`Default` = stock hardware: manual bed leveling, no BLTouch/CR‑Touch probe,
standard PID heating. If you have *added* a BLTouch/CR‑Touch, do **not** use this
file — tell me and I'll get you the matching `BLT` build.

---

## Before you start — you need

- A **microSD card 8 GB or smaller**, formatted **FAT32** with a **4096‑byte
  (4K) allocation unit size**. (Bigger/older cards often fail to flash these
  boards — this is the #1 cause of "it won't flash".)
- Your **stock files as a safety net** — they're already in this repo:
  - `../AquilaX2_V4.0.5_20221121.bin` (stock mainboard firmware)
  - `../DWIN_SET/` (stock display assets)
  Keep a copy. If anything goes wrong, you flash these back the same way to
  return to 100% stock. **Nothing here is permanent.**

---

## Step 1 — Flash the mainboard firmware

1. Copy **`Aquila_N32_Default-07-13.bin`** to the **root** of the SD card
   (nothing else needs to be on it).
2. Power **off** the printer.
3. Insert the SD card into the **printer's** SD slot (the normal one you print
   from).
4. Power **on**. Wait ~10–20 seconds without touching anything. The board
   detects the new `.bin`, flashes it, and boots.
5. When you see the new UI, power off and remove the card.

**Important:**
- Do **not** cut power while it's flashing.
- The bootloader only flashes a `.bin` whose **filename is different** from the
  last one it flashed. To flash again later, **rename the file** (e.g. add a
  letter) or it will be ignored.

## Step 2 — Flash the display (DWIN_SET)

The new firmware uses updated icons, so the screen needs its matching graphics
or icons will look wrong.

1. Put **only** the `DWIN_SET` folder in the **root** of the SD card (delete the
   `.bin` from Step 1 first). The folder must be named exactly `DWIN_SET`.
2. Power **off** the printer.
3. Remove the **back cover of the screen** and insert the SD card into the small
   slot **on the back of the display's circuit board**.
4. Power **on**. The screen goes **blue**, then turns **orange/red** when done
   (a few seconds).
5. Power **off**, remove the SD card from the screen, reassemble.
6. Power **on** to confirm the new graphics.

*If the blue screen only flashes for a second before going orange, the flash
didn't take — reformat the card (FAT32, 4K allocation, ≤8 GB) and try again.*

## Step 3 — Reset settings (do this once)

After both flashes, load the new defaults so old stored values don't cause odd
behavior:

- On the printer: **Control → Advanced → (or Configuration) → Reset / Initialize
  EEPROM**, then **Store Settings**.
- Re‑run your **bed leveling** afterward (your Z‑offset / mesh is reset).

---

## How to revert to 100% stock

1. **Mainboard:** flash `../AquilaX2_V4.0.5_20221121.bin` using **Step 1**
   (rename it if needed so the bootloader picks it up).
2. **Display:** copy the stock `../DWIN_SET/` folder to the card and flash using
   **Step 2**.

That returns the printer exactly to how it shipped.

---

## Other display themes (optional)

The screen graphics come in several color themes — this folder uses **"Original"**
(the standard ProUI look). Others available (Voxelab Original Light, Voxelab Red,
Gotcha, Custom) live in the source repo under
`display assets/Aquila Display Firmware/Firmware Sets/`. They differ only in the
`9.ICO` icon file; flashing a different one is just a repeat of **Step 2**.

## Source & credits

- Firmware: [classicrocker883/MRiscoCProUI](https://github.com/classicrocker883/MRiscoCProUI),
  release `2.1.3h-7`, file `Aquila_N32_Default-07-13.bin`.
- Icons/display: MRiscoC ProUI display assets ("Original" set), credits to
  Voxelab, alexqzd, and ClassicRocker883.

### File checksums (SHA‑256)

```
Aquila_N32_Default-07-13.bin                cd9a0ea1a5940d766f3832ad0bbd30c31a4d02a5f7f40bdfc41be727b8ea0ec6
DWIN_SET/9.ICO                              22c79da31f42b897fba19dae0dd4eb72d25bd91bc69ccc24c4e4bfcf9ce8f530
DWIN_SET/T5UIC1.CFG                         e1c573639bfa2b3a06c2fa7ad3cab483653dd3dc383217ff653fab3145458095
DWIN_SET/T5UIC1_V20_4页面_191022.BIN        f8f9a3075ae5516328044acb79ca522753133b66f1ecbd108e7b5db2f3ff2fe5
```
