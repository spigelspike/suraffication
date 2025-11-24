@echo off
echo Running Sand Preset...
python -m py_surrafication --src examples/demo_source.jpg --tgt examples/sura.jpg --out demo_sand.mp4 --preset sand --verbose

echo Running Blocks Preset...
python -m py_surrafication --src examples/demo_source.jpg --tgt examples/sura.jpg --out demo_blocks.mp4 --preset blocks --verbose

echo Running Bubbles Preset...
python -m py_surrafication --src examples/demo_source.jpg --tgt examples/sura.jpg --out demo_bubbles.mp4 --preset bubbles --verbose

echo Done! Check demo_sand.mp4, demo_blocks.mp4, and demo_bubbles.mp4
pause
