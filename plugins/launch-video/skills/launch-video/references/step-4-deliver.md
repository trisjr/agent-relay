# Step 4: Validate, render, and deliver

## Validate

```bash
cd <output-dir>/composition
npx hyperframes check   # this skill's single pre-render gate — fix every error it reports
```

Fix all errors. `check` is this skill's single pre-render gate — run it and fix everything it reports, including WCAG contrast failures (they gate as errors, not warnings). Each contrast finding carries a suggested compliant color, so apply it or adjust within the palette family and re-run `check` — most fixes need no screenshot. There is no per-element contrast escape hatch for real text; the only bypass is `check --no-contrast`, which skips the entire WCAG pass (all-or-nothing), not a way to accept one borderline element. For exact contrast thresholds, layout escape hatches, and reporting details, follow the current hyperframes-cli `check` guidance. `check`'s layout pass backstops the "keep all text readable" creative law — fix any reported overflow.

For a visual gut-check before rendering, optionally capture key frames:

```bash
npx hyperframes snapshot   # PNG key frames
```

## Preview

```bash
npx hyperframes preview
```

Tell the user the preview is running and give them the localhost URL. Invite them to check it before rendering.

If the user approves or asks to render:

## Render

Pick the worker count from the machine's specs before rendering. `--workers auto` is conservative for a 15-25s launch video: its contention cap (`cpus / 2.5`, divided further for shader/blur/video-heavy scenes) often lands on 1-2 workers. Each worker is a separate Chrome process, so size by both CPU cores and RAM:

| Machine | `--workers` |
|---|---|
| ≥ 8 cores and ≥ 16 GB RAM | `4` |
| ≥ 4 cores and ≥ 8 GB RAM | `3` |
| Smaller | omit the flag (`auto`) |

```bash
CORES=$(getconf _NPROCESSORS_ONLN)
MEM_GB=$(( $(sysctl -n hw.memsize 2>/dev/null || awk '/MemTotal/ {print $2 * 1024}' /proc/meminfo) / 1073741824 ))
if [ "$CORES" -ge 8 ] && [ "$MEM_GB" -ge 16 ]; then WORKERS="--workers 4"
elif [ "$CORES" -ge 4 ] && [ "$MEM_GB" -ge 8 ]; then WORKERS="--workers 3"
else WORKERS=""; fi
echo "cores=$CORES mem=${MEM_GB}GB -> ${WORKERS:-auto}"

npx hyperframes render $WORKERS --output ../launch-video.mp4
```

This outputs to `<output-dir>/launch-video.mp4` (one level up from the composition directory). Reuse the same `$WORKERS` for the draft and final renders below.

If the render fails with a parallel-capture timeout, a worker exiting early, or Chrome running out of memory, step down one worker at a time (4 → 3 → 2) and re-render; drop to `--workers 1` only if 2 still fails (Hyperframes recommends it for video-heavy compositions).

For a faster iteration render:
```bash
npx hyperframes render $WORKERS --quality draft --output ../launch-video.mp4
```

For final delivery:
```bash
npx hyperframes render $WORKERS --quality high --output ../launch-video.mp4
```

## Pick the poster frame

The poster is the still shown before the video plays — the first thing anyone sees when it's idle or unplayed. Don't leave it to the raw first frame or an arbitrary timestamp; those land on fades, mid-transitions, blank intro backgrounds, or half-rendered text.

You built this composition, so you already know its strongest moment and exactly when it lands — the hook line, the hero reveal, or the final logo. Pick that beat at a **settled** point: text fully animated in, before it exits (the storyboard timings tell you the safe window). Then extract that one frame full-res with ffmpeg. From `<output-dir>/composition`:

```bash
# use the timestamp of your strongest settled beat, e.g. 3.2s
ffmpeg -ss 3.2 -i ../launch-video.mp4 -frames:v 1 -q:v 2 ../launch-video.jpg
```

Aim for a frame that's postable on its own (the "show the thing" law — any frozen frame should be shareable). If the pulled frame lands on a transition or mid-animation, nudge the timestamp a few tenths of a second and re-extract.

### Bake the poster as frame 0

A bare `.mp4` has no `poster` attribute — every player and platform picks its own idle thumbnail, and almost all of them grab **frame 0**. Slack, Twitter/X, and Discord regenerate thumbnails server-side and ignore embedded cover-art metadata, so the *only* reliable way to control the idle image everywhere is to make frame 0 *be* the poster.

Replace **only** the first frame's pixels with `launch-video.jpg`, leaving every other frame and all timing untouched — same duration, same frame count, audio copied through. At 30fps the poster shows for 1/30s before the intro rolls, so it's imperceptible on playback but it's what every thumbnail grabber sees. From `<output-dir>`:

```bash
ffmpeg -y -i launch-video.mp4 -i launch-video.jpg \
  -filter_complex "[0:v][1:v]overlay=0:0:enable='eq(n,0)'[v]" \
  -map "[v]" -map 0:a? -c:v libx264 -crf 18 -preset slow -pix_fmt yuv420p \
  -c:a copy -movflags +faststart launch-video.poster.mp4 \
  && mv launch-video.poster.mp4 launch-video.mp4
```

The poster (`launch-video.jpg`) matches the video's dimensions because it was pulled from the same render, so the overlay lines up exactly. Keep `launch-video.jpg` alongside — it's the custom-thumbnail asset for platforms that accept an upload (Instagram, TikTok, YouTube, Facebook, and the LinkedIn post editor) and the `poster="launch-video.jpg"` image for any `<video>` that embeds the launch video (a gallery card, the user's site).

## Write share copy

Write `<output-dir>/share-copy.txt`.

The share copy should be:
- One to three sentences max
- Postable as-is to Twitter/X, LinkedIn, or Discord
- Specific to the project — no generic "excited to share" language
- Tone-matched to the launch video

`share-copy.txt` is the canonical single caption. Do not put multi-platform variants, long launch notes, or Product Hunt copy in this file.

If variants are useful, write them to a separate optional file:

```text
<output-dir>/share-copy-variants.md
```

### Share copy by tone

**`default`:**
```
Made [App Name]. It's [what it does, in the project's own absurd terms].
[The best line from the product.]
```

**`polished`:**
```
Introducing [App Name]: [clean one-liner from the site].
Built with [stack if notable].
```

**`yc-parody`:**
```
We built [App Name] to solve [problem stated completely seriously].
[Deadpan feature or stat.]
```

**`chaotic`:**
```
[ALL CAPS CLAIM].
[App Name] is [wildly overstated description].
Link below.
```

**`deadpan`:**
```
I made [App Name].
It [what it does].
```

**`cinematic`:**
```
[App Name].
[Tagline from the site, verbatim or lightly adapted.]
```

**`app-store`:**
```
[App Name] is now live.
[Feature 1], [Feature 2], and [Feature 3] — all in one place.
```

### Example: Taxi for Taxis

```
Every day, taxis carry us. But who carries the taxis?
Taxi for Taxis: the ride-hailing app for ride-hailing assets.
Available in 12 metros.
```

## Final output structure

After this step, `<output-dir>/` should contain:

```
<output-dir>/
  launch-video.mp4        — the rendered video
  launch-video.jpg        — the poster (best frame, for <video poster>)
  launch-video-plan.md    — the plan and storyboard
  composition-brief.md    — the Hyperframes handoff brief
  share-copy.txt          — the share caption
  composition/            — the Hyperframes project
    index.html
    ...
```

## Telling the user

After everything is done, tell the user:
- Where the video is (`<output-dir>/launch-video.mp4`)
- Where the share copy is
- One sentence on what the video does creatively
- Optionally: offer to re-roll a scene, change tone, or try a different angle
