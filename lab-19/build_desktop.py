"""Build a separate macOS launcher and original geometric icon. Run with Lab 19 Python."""
from pathlib import Path
import plistlib
import shlex
import subprocess
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
build = HERE / 'desktop-build'
build.mkdir(exist_ok=True)
app = Path.home() / 'Desktop/Legend Panel · Lab 19 (AI Finance).app'
if app.exists():
    raise SystemExit(f'Preserving existing launcher: {app}')
command = shlex.join([str(HERE / '.venv/bin/python'), str(HERE / 'launch.py')])
source = build / 'launcher.applescript'
source.write_text('do shell script ' + __import__('json').dumps(command + ' >/dev/null 2>&1 &') + '\n')
subprocess.run(['osacompile', '-o', str(app), str(source)], check=True)
# Three ascending columns represent three investor lenses, on a navy rounded tile.
icon = Image.new('RGBA', (1024, 1024))
draw = ImageDraw.Draw(icon)
draw.rounded_rectangle((36, 36, 988, 988), radius=210, fill='#111e35')
draw.rounded_rectangle((135, 145, 889, 879), radius=130, outline='#344563', width=5)
for x, top, color in [(235, 470, '#7aa7ed'), (437, 340, '#e4bc70'), (639, 220, '#58c9ad')]:
    draw.rounded_rectangle((x, top, x+150, 735), radius=35, fill=color)
draw.rounded_rectangle((235, 790, 789, 809), radius=9, fill='#dde7f4')
iconset = build / 'LegendPanel.iconset'
iconset.mkdir(exist_ok=True)
for size in (16, 32, 128, 256, 512):
    for scale in (1, 2):
        icon.resize((size*scale, size*scale), Image.Resampling.LANCZOS).save(iconset / f'icon_{size}x{size}{"@2x" if scale == 2 else ""}.png')
resources = app / 'Contents/Resources'
subprocess.run(['iconutil', '-c', 'icns', str(iconset), '-o', str(resources / 'LegendPanel.icns')], check=True)
info = app / 'Contents/Info.plist'
with info.open('rb') as stream:
    metadata = plistlib.load(stream)
metadata.update(CFBundleIconFile='LegendPanel', CFBundleIdentifier='edu.purdue.aidanklebenow.lab19', CFBundleName='Legend Panel · Lab 19')
with info.open('wb') as stream:
    plistlib.dump(metadata, stream)
print(app)
