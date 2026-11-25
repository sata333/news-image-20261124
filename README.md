[![make.fun · news-image-20261124](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/sata333/news-image-20261124/rank.svg)](https://make.fun/bounty/news-image-20261124/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/sata333/news-image-20261124/reward.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)

# Tuesday 24 November 2026: 40 sourced stories, a world map, a UTC timeline and a date check

One image that sums up the world's news of Tuesday 24 November 2026, drawn as a
newspaper front page by `main.py` (Python standard library only).

- **Masthead** with the full date, so the day is readable from the image alone.
- **40 sourced stories** across Americas, Europe, Middle East, Asia-Pacific,
  Africa, Business, Tech & Science and Sport, each tagged with its outlet.
- **A drawn world map** (108 x 45 land bitmap) with 10 numbered place markers.
- **A UTC timeline** of the day's key events, and a one-line date check in the footer.

`main.py` reads `worldmap.txt` from its own directory and writes
`entry.png` (1024 x 1024, deterministic: two runs produce byte-identical output).

Run it with:

```
MAKEFUN_OUTPUT_DIR=out python3 main.py
```
