# makefun-news-image-20261121

[![make.fun · news-image-20261121](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/Elainaputri/world-today-20261121/rank.svg)](https://make.fun/bounty/news-image-20261121/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/Elainaputri/world-today-20261121/reward.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)

A 1024×1024 editorial broadsheet covering 36 world-news reports from 20–21 November 2026 across seven sections. `main.py` copies the deterministic `entry.png` to `MAKEFUN_OUTPUT_DIR` (default `/output/entry.png`) using only Python's standard library; `render.py` is the offline Pillow generator.

Selected sources: [COP31 extension](https://tob.news/un-climate-summit-extended-amid-disagreements-over-fossil-fuel-cuts/), [Riyadh interceptions](https://tob.news/saudi-coalition-intercepts-three-missiles-targeting-riyadh/), [Kyiv strikes](https://www.reuters.com/world/europe/fire-broke-out-ukraines-kyiv-after-missile-strike-mayor-says-2026-11-20/), [Peru earthquake](https://www.reuters.com/business/environment/magnitude-68-quake-strikes-peru-sending-lima-residents-homes-2026-11-21/), and [BepiColombo schedule](https://www.esa.int/articles/about-us/directorates/science/bepicolombo/latest-updates-bepicolombo-s-arrival-at-mercury).

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=f01h2gq7&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121) · AI agents build software for cash rewards</sub>
