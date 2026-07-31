# Profile maintenance

## Self-hosted GitHub Readme Stats (required for two cards)

The **GitHub Stats** and **Top Languages** cards in the README point at a
self-hosted github-readme-stats instance, not the public `github-readme-stats.vercel.app`
(that shared instance is permanently over-quota and returns HTTP 503).

A fork already exists: **https://github.com/D0paX/github-readme-stats**

Deploy it once (the profile's two stats cards stay broken until you do):

1. https://vercel.com/new  →  **Import**  →  select `D0paX/github-readme-stats`.
2. **Name the project exactly `d0pax-readme-stats`** — the README URLs are wired to
   `https://d0pax-readme-stats.vercel.app`. (Different name → update the two
   `d0pax-readme-stats.vercel.app` URLs in `README.md` to match.)
3. Framework preset: **Other**. Deploy.
4. Optional but recommended — higher GitHub rate limits: Project → Settings →
   Environment Variables → add `PAT_1` = a GitHub classic PAT (scope: `repo` or just
   public access). Redeploy.

Endpoints after deploy:
- `https://d0pax-readme-stats.vercel.app/api?username=D0paX&...`  (stats)
- `https://d0pax-readme-stats.vercel.app/api/top-langs/?username=D0paX&...`  (languages)

Redeploy = push to the fork (Vercel auto-builds) or hit **Redeploy** in the dashboard.
Update the upstream: `gh repo sync D0paX/github-readme-stats` or the fork's Sync button.

---

# Hero banner

`dark.svg` and `light.svg` in the repo root are **generated**. This directory holds the
generator and the cached portrait; edit those, not the SVGs.

```bash
python tools/build_hero.py
```

Both SVGs come from one source file so the two themes can never drift apart. Content
lists (typing phrases, focus items, tech stack) and the colour palette sit at the top of
`build_hero.py`.

---

## The profile photo

The portrait is **inlined into both SVGs as a base64 JPEG** — there are no external
assets, so nothing can 404 and nothing depends on the repo layout.

> It has to be a data URI. A relative path or an `https://` URL will not render:
> GitHub serves this SVG inside an `<img>` tag, and browsers block every external
> fetch from that context. It would look fine in your editor and be invisible to
> everyone else.

To change the photo, drop a new `shrisht.png` in the repo root and re-run the
generator. The crop window lives in `build_hero.py`:

```python
AVATAR_BOX = (130, 333, 695, 898)  # left, top, right, bottom in source pixels
AVATAR_PX  = 500                   # covers the 192px disc at 3x DPR in a README
AVATAR_Q   = 86
```

`AVATAR_BOX` is a square window measured against the source image, picked so the head
fills ~73% of the circle with roughly 52px of headroom above the hair and 103px below
the chin. If you swap in a photo with different framing, adjust it — a centred crop is
*not* used, because on a tall portrait that cuts across the face.

Judge any new window against the **inscribed circle**, not the square. The square is
never painted, and the circle is narrowest exactly where the hair and chin sit, so a
window that looks fine as a rectangle can still clip the top of the head.

`shrisht.png` (the 1.9 MB original) is only needed to regenerate. The encoded result is
cached in `avatar.b64.txt`, so you can move or delete the original and the build will
still reproduce both SVGs byte-for-byte.

---

## Avatar component size

The size of the avatar *component* is separate from the crop, and drives the whole left
column:

```python
AV_R   = 96              # 192px disc = 34.2% of the panel height
AVK    = AV_R / 70.0     # scales ring, glow, reflection, strokes, float travel
AV_TOP = LP["y"] + 30    # headroom above the portrait
```

Change `AV_R` and the ring, glow, reflection, stroke weights, float travel and the
entire name/username/badge/info stack all re-derive from it. An assertion fails the
build if the column would overflow its panel.

Keep `AVATAR_PX` at roughly 2.6x the disc diameter, and **never above 565** — that is
the source crop width, past which you would be upscaling.

---

## Notes

- Pure SMIL, no JavaScript, no external references. Both files are self-contained.
- Reveal animations start at `begin="0s"` with the stagger encoded in `keyTimes`, so
  the static base state is the finished composition. Renderers without SMIL support
  show the full design rather than a blank card.
- GitHub caches images aggressively through its image proxy. After pushing an update,
  a hard refresh (or a cache-busting `?v=2` on the `srcset`) may be needed to see it.
