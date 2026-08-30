# AGENTSELF-style UI spec

Everything needed to rebuild the look from the video. Colors are sampled directly from the frames.

---

## 1. The three things that actually make this look

Strip everything else away and the identity comes from exactly three decisions. If you only copy these, you get 80% of the look.

1. **Framed page.** The whole site sits inside a rounded rectangle with a ~20px margin on all sides. Outside that frame is a dark grey backdrop, and the hero's orange glow bleeds *outside* the frame onto that backdrop. This is why it looks like a product shot instead of a webpage.
2. **One display face for everything, cream on near-black.** Heavy condensed grotesque, all caps, tight tracking. No serif, no second display font.
3. **A single warm amber light source** behind a dark object, with everything else desaturated. There is no second accent color. The green status dot is the only exception and it is 8px wide.

Everything below is detail on those three.

---

## 2. Color tokens

```css
:root {
  /* surfaces */
  --bg-page:        #0B0B0B;  /* inside the frame, near black */
  --bg-backdrop:    #1A1A1A;  /* outside the frame */
  --bg-section:     #050505;  /* section 2, deeper than hero */
  --surface-card:   rgba(255, 255, 255, 0.045);
  --border-hair:    rgba(255, 255, 255, 0.08);

  /* type */
  --cream:          #F8F1BD;  /* headlines, wordmark, CTA fill */
  --cream-dim:      #D4C7B7;  /* subheadings */
  --text-muted:     #96957A;  /* card body copy, ~60% */
  --text-faint:     #6B6B5E;  /* micro labels */

  /* glow */
  --amber-core:     #E8A34D;
  --amber-mid:      #C97B2A;
  --amber-deep:     #392407;

  /* status */
  --green:          #35EF46;
}
```

Note the frame backdrop (`--bg-backdrop`) is *lighter* than the page. That inversion is deliberate and it's what sells the framed effect. Most people get this backwards.

**Contrast check:** cream on near-black is about 15:1, fine. `--text-muted` on `--bg-section` is around 4.9:1, which passes AA for normal text but only just. Do not go dimmer.

---

## 3. Typography

The original is almost certainly Druk (commercial, ~$200). Free stand-ins, in order of closeness:

| Role | Font | Fallback |
|---|---|---|
| Display | **Anton** | Archivo Black, Impact |
| Display alt (wider) | **Archivo Expanded 800** | variable font, gives you width control |
| Body / UI | **Inter** | system-ui |
| Micro labels | **Inter** at 500 | same family, different treatment |

```css
--font-display: 'Anton', 'Archivo Black', Impact, sans-serif;
--font-body:    'Inter', system-ui, sans-serif;
```

### Scale

```css
/* hero H1 */
font-family: var(--font-display);
font-size: clamp(3rem, 9vw, 7.5rem);
line-height: 0.88;          /* tight, lines almost touch */
letter-spacing: -0.02em;
text-transform: uppercase;

/* section H2 */
font-size: clamp(2.5rem, 6vw, 5rem);
line-height: 0.92;

/* hero subhead */
font-family: var(--font-body);
font-size: 0.95rem;
font-weight: 500;
letter-spacing: 0.06em;
text-transform: uppercase;
color: var(--cream-dim);

/* micro label ("AGENT AVAILABLE NOW", "BUSINESS GROWTH") */
font-size: 0.6rem;
font-weight: 600;
letter-spacing: 0.14em;
text-transform: uppercase;
color: var(--text-faint);

/* card body */
font-size: 0.7rem;
line-height: 1.5;
letter-spacing: 0.03em;
text-transform: uppercase;
color: var(--text-muted);
```

`line-height: 0.88` on the H1 is the single most important number here. Default 1.2 kills the look instantly.

**Where the original went wrong:** it used the display face for a 5-line body paragraph in section 2. Don't. Set body copy in Inter regular, 18-20px, max-width 60ch. You keep the aesthetic and gain readability.

---

## 4. The frame

```css
body {
  background: var(--bg-backdrop);
  padding: 20px;
}

.frame {
  border-radius: 20px;
  overflow: hidden;
  border: 1px solid rgba(255,255,255,0.06);
  background: var(--bg-page);
  min-height: calc(100vh - 40px);
  position: relative;
}
```

The glow that appears outside the frame is a separate fixed layer sitting *behind* the frame on the body:

```css
body::before {
  content: '';
  position: fixed;
  inset: -10%;
  background: radial-gradient(
    ellipse 60% 50% at 50% 60%,
    var(--amber-mid) 0%,
    var(--amber-deep) 35%,
    transparent 70%
  );
  filter: blur(80px);
  opacity: 0.55;
  z-index: 0;
}
.frame { position: relative; z-index: 1; }
```

---

## 5. Hero layer stack

Bottom to top:

```
0. body glow (fixed, blurred, bleeds outside frame)
1. hero image  - the planet + hands render, object-fit: cover
2. scrim       - radial dark vignette so text stays legible
3. glow bloom  - a second, sharper radial behind the planet
4. content     - badge, H1, subhead, CTA
5. float cards - absolutely positioned, low z, behind nothing
```

The scrim is what makes cream text readable over a bright image:

```css
.hero-scrim {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(ellipse at 50% 55%, transparent 30%, rgba(0,0,0,0.55) 75%),
    linear-gradient(to bottom, rgba(0,0,0,0.6), transparent 40%);
}
```

---

## 6. Float cards

```css
.stat-card {
  background: rgba(255,255,255,0.045);
  backdrop-filter: blur(12px);
  border: 1px solid var(--border-hair);
  border-radius: 10px;
  padding: 14px 18px;
  min-width: 175px;
}
```

Structure inside is always the same 3 rows: micro label (+ optional right-aligned meta), a big value in display or Inter 600 at ~1.5rem, then a faint one-liner.

Positioning: absolute, roughly at `left: 12% / top: 58%` and `right: 10% / top: 62%`. Keep them **above** the fold. In the video every card gets clipped, which means they carry zero information.

**Cut from six cards to two.** Six is noise.

---

## 7. Motion

The smooth momentum feel in the video is Lenis, not native scroll. That's a real part of the identity.

```bash
npm i lenis framer-motion
```

```js
import Lenis from 'lenis'

useEffect(() => {
  const lenis = new Lenis({ duration: 1.1, smoothWheel: true })
  const raf = (t) => { lenis.raf(t); requestAnimationFrame(raf) }
  requestAnimationFrame(raf)
  return () => lenis.destroy()
}, [])
```

### Parallax pattern

```jsx
const ref = useRef(null)
const { scrollYProgress } = useScroll({
  target: ref,
  offset: ['start start', 'end start']
})

const headlineY = useTransform(scrollYProgress, [0, 1], [0, -180])
const cardsY    = useTransform(scrollYProgress, [0, 1], [0, -60])
const imageY    = useTransform(scrollYProgress, [0, 1], [0, 90])
const fade      = useTransform(scrollYProgress, [0, 0.6], [1, 0])

<motion.h1 style={{ y: headlineY, opacity: fade }}>...</motion.h1>
```

### Rules that fix the video's bug

- **Translate on Y only.** The broken frames in your video are elements moving on X at different rates, so the headline crosses the subhead. Vertical-only parallax can't collide.
- **Move the hero text block as one unit.** Headline, subhead and CTA share a single wrapper with one `y` transform. Do not animate them independently.
- **Foreground moves faster than background.** `headlineY: -180` vs `imageY: +90`. Opposite directions, and the bigger magnitude goes to the thing nearest the viewer.
- **Fade out before overlap is possible.** Hero opacity hits 0 by 60% scroll progress, so anything weird after that is invisible anyway.

### Footer wordmark reveal

Giant `AGENTSELF` clipped at the bottom edge, revealed by a gradient mask:

```css
.wordmark {
  font-family: var(--font-display);
  font-size: 22vw;
  line-height: 0.8;
  background: linear-gradient(to bottom, #504434 0%, #C9C095 100%);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  white-space: nowrap;
  transform: translateY(18%);
}
```

Set the container to `overflow: hidden` so the bottom clips cleanly. Size it so it hits the frame's left and right edges exactly, not past them, otherwise it reads as broken rather than as bleed.

### Non-negotiable

```css
@media (prefers-reduced-motion: reduce) {
  * { animation: none !important; transition: none !important; }
}
```
And skip Lenis init entirely when that query matches.

---

## 8. Section 2 (feature cards)

Three cards on a descending diagonal, each `translateY` offset progressively: 0, +80px, +160px. Each is image on top, title, then uppercase micro body.

The video uses blue holographic AI stock photos here and it clashes hard with the amber palette. Two fixes, pick one:

```css
/* option A: force them into the palette */
.feature-img {
  filter: sepia(0.5) saturate(1.3) hue-rotate(-15deg) brightness(0.85);
  mix-blend-mode: luminosity;
}
```

Option B: drop photos entirely, use flat amber-on-black line illustrations. Cleaner, and it dodges the AI-stock look that makes a portfolio piece read as generated.

---

## 9. Stack

```
Next.js 14 (app router)
Tailwind CSS      - tokens go in tailwind.config as theme.extend.colors
Framer Motion     - useScroll / useTransform only, no layout animations
Lenis             - smooth scroll
next/font/google  - Anton + Inter, self-hosted, avoids FOUT
```

Tailwind config:

```js
theme: {
  extend: {
    colors: {
      cream: '#F8F1BD',
      'cream-dim': '#D4C7B7',
      amber: { core: '#E8A34D', mid: '#C97B2A', deep: '#392407' },
      page: '#0B0B0B',
      backdrop: '#1A1A1A',
    },
    fontFamily: {
      display: ['var(--font-anton)'],
      body: ['var(--font-inter)'],
    },
  },
}
```

---

## 10. Build order

1. Frame + backdrop + body glow. Get the inversion right before anything else.
2. Fonts loaded, H1 at `line-height: 0.88`. Check it against the video.
3. Hero image + scrim. Verify cream text is readable at every scroll position.
4. Two float cards only.
5. Lenis, then parallax, Y-axis only.
6. Section 2 and the wordmark last.

Steps 1-3 give you the whole identity. If those don't look right, no amount of animation saves it.

---

## 11. Things to change, not copy

- **The fake metrics.** 99.8% uptime, +38.4%, 12 tasks. Unsourced precise numbers read as filler to anyone technical. Either back them or replace with something real.
- **Two verbs for one action.** Nav says TRY FREE, hero says LAUNCH YOUR AGENT. Pick one and use it everywhere, including the confirmation state.
- **Display face for body copy.** Covered in section 3.
- **X-axis parallax.** Covered in section 7.
- **No mobile story.** At 22vw the wordmark and a `clamp(3rem, 9vw, 7.5rem)` H1 need testing at 375px. The float cards should just unmount below 768px, not stack.
