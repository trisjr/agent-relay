# ElevenLabs voiceover

Used when `voice.provider = elevenlabs` (see "Parsing the invocation" in `SKILL.md`). Kokoro has no Vietnamese voice and few non-English ones, so this is the path for Vietnamese and any other language Kokoro can't speak. It replaces the `npx hyperframes tts` step in `step-3-compose.md`; wiring, ducking and the 15-25s window rules stay the same.

## Preflight

- `elevenlabs auth status` must report a logged-in session. If the `elevenlabs` CLI is missing or not logged in, stop and tell the user; installing a CLI globally or logging in is the user's call (ask first, never run `brew`/`npm -g` unprompted). Offer to fall back to Kokoro only when the narration language is English.
- Only the narration lines are sent to ElevenLabs. Never send plan text, source code, secrets, emails or user data.

## Voice and model

| Setting | Default | Override |
|---|---|---|
| Voice | Vietnamese: `f5q6kePPoQAjCPYG6moa` ("Giang - Northern female Narrator"). Other languages: ask the user for a voice ID | `--voice-id <id>` |
| Language | the on-screen language of the video; Vietnamese is `vi` | `--lang <code>` |
| Model | try `eleven_v4` on one line first; if it errors or the voice doesn't render, use `eleven_turbo_v2_5` | `--voice-model <id>` |

Always pass `--language-code`. Report the voice and model actually used when delivering.

## Generate

One file per sentence, not one file for the whole script, so each line can be timed to a scene:

```bash
mkdir -p <output-dir>/work/vo <output-dir>/composition/assets/vo
elevenlabs text-to-speech convert \
  --voice-id <voice-id> --model-id <model> --language-code <lang> \
  --text "<one sentence>" -o <output-dir>/work/vo/vo1.mp3
```

Convert to 44.1 kHz mono wav and trim leading/trailing silence (enable `set -o pipefail` when the command has pipes):

```bash
ffmpeg -y -i <output-dir>/work/vo/vo1.mp3 -ar 44100 -ac 1 \
  -af "silenceremove=start_periods=1:start_threshold=-50dB,areverse,silenceremove=start_periods=1:start_threshold=-50dB,areverse" \
  <output-dir>/composition/assets/vo/vo1.wav
```

Measure each wav with `ffprobe -v error -show_entries format=duration -of csv=p=0 <wav>`.

## Script rules

- Write the lines into `launch-video-plan.md` under `## Voiceover script`, in the video's language.
- Short sentences (about 3s or less) for a 15-25s clip; each line complements the visual and does not read the on-screen text back.
- Keep product names, numbers and currency exactly as in the source (e.g. "€5/month" stays "€5").
- A line that runs too long gets rewritten shorter. Never speed the voice up.
- Check that the on-screen font renders the language's diacritics (Vietnamese needs a font with full dấu support).

## Wire into the composition

One `<audio>` per sentence, each on its own track-index above the music and SFX tracks (never share a track-index between overlapping audio). Set `data-start` and `data-duration` from the measured wav so every line sits inside its scene and lines never overlap:

```html
<audio id="vo-1" data-start="0.4" data-duration="2.6" data-track-index="20" data-volume="1" src="assets/vo/vo1.wav"></audio>
<audio id="vo-2" data-start="3.4" data-duration="2.2" data-track-index="21" data-volume="1" src="assets/vo/vo2.wav"></audio>
```

Duck the music bed to about 0.12-0.16 while lines play (0.16 is the ceiling for a Vietnamese run), then restore it. Narration does not extend the video past the 25s window; scene durations flex to the measured audio, and the script gets cut if it overruns.

## Verify before delivering

- `ffmpeg -i <video> -af volumedetect -f null -` over a voiced section: speech clearly louder than the music bed, no clipping.
- You cannot hear the result. Say so in the delivery note, along with the voice, model and language used.
