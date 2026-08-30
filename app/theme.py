"""Shared visual design system.

Framed page, one warm light source, one display face. Both Streamlit entry
points import this so the palette lives in exactly one place.

Tokens are sampled per agentself-ui-spec.md; see that file before changing any
of them. The three decisions that carry the whole look:

  1. The page sits inside a rounded frame and the backdrop OUTSIDE it is
     lighter than the page inside. That inversion is the effect.
  2. One display face (Anton), all caps, cream on near-black.
  3. A single warm amber light source. No second accent — the green status
     dot is the only exception and it is 8px wide.
"""

import streamlit as st

_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Anton&family=Inter:wght@400;500;600&display=swap');

:root {
    /* surfaces */
    --bg-page:      #0B0B0B;
    --bg-backdrop:  #1A1A1A;
    --bg-section:   #050505;
    --surface-card: rgba(255, 255, 255, 0.045);
    --border-hair:  rgba(255, 255, 255, 0.08);

    /* type */
    --cream:      #F8F1BD;
    --cream-dim:  #D4C7B7;
    --text-muted: #96957A;
    --text-faint: #6B6B5E;

    /* glow — the single light source */
    --amber-core: #E8A34D;
    --amber-mid:  #C97B2A;
    --amber-deep: #392407;


    --font-display: 'Anton', 'Archivo Black', Impact, sans-serif;
    --font-body:    'Inter', system-ui, sans-serif;

    --frame-gap:    20px;
    --frame-radius: 20px;
}

/* ---------- 1. The frame. Backdrop is LIGHTER than the page — this inversion
      is what sells it. Get this right before anything else. ---------- */

.stApp {
    background: var(--bg-backdrop);
    font-family: var(--font-body);
}

/* body glow: fixed, blurred, sits BEHIND the frame so it bleeds onto the backdrop */
.stApp::before {
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
    pointer-events: none;
}

[data-testid="stAppViewContainer"] {
    position: absolute;
    inset: var(--frame-gap);
    border-radius: var(--frame-radius);
    border: 1px solid rgba(255, 255, 255, 0.06);
    background: var(--bg-page);
    overflow: hidden;
    z-index: 1;
}

[data-testid="stHeader"] {
    background: linear-gradient(to bottom,
        var(--bg-page) 30%,
        rgba(11, 11, 11, 0.72) 70%,
        transparent 100%);
    backdrop-filter: blur(6px);
    -webkit-backdrop-filter: blur(6px);
    z-index: 3;
}

[data-testid="stMainBlockContainer"] {
    padding: 3.5rem 3rem 5rem;
    max-width: 1400px;
}

/* ---------- 2. Type ---------- */

html, body, [data-testid="stAppViewContainer"] * {
    font-family: var(--font-body);
}

/* Streamlit's icons are ligature fonts — the rule above turned them back into
   literal text like "keyboard_double_arrow_left". Hand them their font back. */
[data-testid="stIconMaterial"],
[class*="material-symbols"],
[class*="material-icons"] {
    font-family: 'Material Symbols Rounded', 'Material Symbols Outlined',
                 'Material Icons' !important;
}

[data-testid="stAppViewContainer"] h1,
[data-testid="stAppViewContainer"] h1 *,
[data-testid="stAppViewContainer"] h2,
[data-testid="stAppViewContainer"] h2 *,
[data-testid="stAppViewContainer"] h3,
[data-testid="stAppViewContainer"] h3 * {
    font-family: var(--font-display);
    text-transform: uppercase;
    letter-spacing: -0.02em;
    color: var(--cream);
    font-weight: 400;
}

[data-testid="stAppViewContainer"] h1 {
    font-size: clamp(3rem, 9vw, 7.5rem);
    line-height: 0.88;
    margin: 0 0 1rem;
}

[data-testid="stAppViewContainer"] h2 {
    font-size: clamp(2.5rem, 6vw, 5rem);
    line-height: 0.92;
    margin: 0 0 1rem;
}

[data-testid="stAppViewContainer"] h3 {
    font-size: clamp(1.75rem, 3.5vw, 2.75rem);
    line-height: 0.95;
    margin: 2.5rem 0 1.25rem;
}

/* h4 stays in the body face — display face on small headings turns to mush */
[data-testid="stAppViewContainer"] h4,
[data-testid="stAppViewContainer"] h4 * {
    font-family: var(--font-body);
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--text-faint);
    margin: 1.75rem 0 0.75rem;
}

[data-testid="stAppViewContainer"] p,
[data-testid="stAppViewContainer"] li {
    color: var(--cream-dim);
    font-size: 1rem;
    line-height: 1.6;
}

.subhead {
    font-family: var(--font-body);
    font-size: 0.95rem;
    font-weight: 500;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: var(--cream-dim);
    max-width: 46ch;
}

.micro {
    font-size: 0.6rem;
    font-weight: 600;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--text-faint);
}

/* Streamlit hangs a deep-link anchor off every heading. Navigation here is
   the drawer, not URL fragments, so the icon is only clutter on hover. */
[data-testid="stHeaderActionElements"] { display: none !important; }

/* ---------- 3. Hero ---------- */

.hero {
    position: relative;
    padding: 4.5rem 0 3.5rem;
    margin-bottom: 1rem;
    isolation: isolate;
}

/* sharper bloom behind the headline, inside the frame */
.hero::before {
    content: '';
    position: absolute;
    inset: -30% -25%;
    background: radial-gradient(
        ellipse 42% 45% at 46% 42%,
        rgba(232, 163, 77, 0.26) 0%,
        rgba(201, 123, 42, 0.10) 38%,
        transparent 66%
    );
    filter: blur(56px);
    z-index: -2;
    pointer-events: none;
}

/* scrim — keeps cream legible over the bloom */
.hero::after {
    content: '';
    position: absolute;
    inset: 0;
    background:
        radial-gradient(ellipse at 46% 45%, transparent 42%, rgba(0,0,0,0.42) 100%);
    mask-image: radial-gradient(ellipse 80% 80% at 50% 50%, #000 55%, transparent 100%);
    -webkit-mask-image: radial-gradient(ellipse 80% 80% at 50% 50%, #000 55%, transparent 100%);
    z-index: -1;
    pointer-events: none;
}

.hero h1 { max-width: 14ch; }

/* A plain kicker above the headline. This replaced a pill with a glowing
   green dot reading "live feed connected", which was never wired to the
   fetch and so claimed a connection even when Celestrak was unreachable. */
.kicker {
    font-size: 0.6rem;
    font-weight: 600;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--text-faint);
    margin-bottom: 1.5rem;
}

/* ---------- 4. Cards. Two, not six. ---------- */

.stat-card {
    background: var(--surface-card);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid var(--border-hair);
    border-radius: 10px;
    padding: 14px 18px;
    min-width: 175px;
}

.stat-card .label {
    display: flex;
    justify-content: space-between;
    gap: 12px;
    font-size: 0.6rem;
    font-weight: 600;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--text-faint);
}

.stat-card .value {
    font-family: var(--font-body);
    font-weight: 600;
    font-size: 1.5rem;
    line-height: 1.2;
    color: var(--cream);
    margin: 6px 0 4px;
}

.stat-card .note {
    font-size: 0.7rem;
    line-height: 1.5;
    letter-spacing: 0.03em;
    text-transform: uppercase;
    color: var(--text-muted);
}

.feature-card {
    background: var(--surface-card);
    border: 1px solid var(--border-hair);
    border-radius: 12px;
    padding: 22px;
    min-height: 148px;
    transition: border-color 0.25s ease, transform 0.25s ease;
}

.feature-card:hover {
    border-color: rgba(232, 163, 77, 0.35);
    transform: translateY(-3px);
}

.feature-card .title {
    font-family: var(--font-display);
    text-transform: uppercase;
    letter-spacing: -0.01em;
    font-size: 1.5rem;
    line-height: 0.95;
    color: var(--cream);
    margin-bottom: 10px;
}

.feature-card .body {
    font-size: 0.7rem;
    line-height: 1.5;
    letter-spacing: 0.03em;
    text-transform: uppercase;
    color: var(--text-muted);
}

/* descending diagonal — spec §8. transform reserves no space, so the row
   below carries the offset as padding or the next heading collides with it. */
.offset-1 { transform: translateY(40px); }
.offset-2 { transform: translateY(80px); }
[data-testid="stHorizontalBlock"]:has(.offset-2) { padding-bottom: 96px; }

[data-testid="stAlert"] {
    background: var(--bg-section) !important;
    border: 1px solid var(--border-hair);
    border-left: 2px solid var(--amber-core);
    border-radius: 10px;
    color: var(--cream-dim);
}

[data-testid="stAlert"] * { color: var(--cream-dim) !important; }

[data-testid="stAlertContainer"] {
    background: var(--bg-section) !important;
    border: 1px solid var(--border-hair);
    border-left: 2px solid var(--amber-core);
    border-radius: 10px;
}

[data-testid="stAlert"]:has([data-testid="stAlertContentError"]) [data-testid="stAlertContainer"] {
    border-left-color: #E0674F;
}

.satellite-card {
    background: var(--surface-card);
    border: 1px solid var(--border-hair);
    border-left: 2px solid var(--amber-core);
    border-radius: 10px;
    padding: 1.25rem 1.5rem;
    margin: 1rem 0;
}

.real-time-display {
    background: var(--bg-section);
    color: var(--amber-core);
    font-family: ui-monospace, 'SF Mono', 'JetBrains Mono', Menlo, monospace;
    font-size: 0.8rem;
    letter-spacing: 0.02em;
    padding: 1rem 1.25rem;
    border-radius: 10px;
    border: 1px solid var(--border-hair);
}

/* ---------- 5. Streamlit widgets ---------- */

[data-testid="stSidebar"] {
    background: var(--bg-section);
    border-right: 1px solid var(--border-hair);
}

[data-testid="stSidebar"] * { color: var(--cream-dim); }

/* The sidebar is too narrow to split into columns — side-by-side number
   inputs clip their own values. Stack them at every width. */
[data-testid="stSidebar"] [data-testid="stHorizontalBlock"] {
    flex-wrap: wrap;
    gap: 0;
}

[data-testid="stSidebar"] [data-testid="stColumn"] {
    min-width: 100% !important;
    flex: 1 1 100% !important;
}

[data-testid="stHeader"] button:not([data-testid="stExpandSidebarButton"]),
[data-testid="stBaseButton-headerNoPadding"]:not([data-testid="stExpandSidebarButton"]),
[data-testid="stBaseButton-header"] {
    border: 0 !important;
    background: transparent !important;
    border-radius: 8px !important;
    letter-spacing: normal !important;
    text-transform: none !important;
    padding: 4px !important;
}

[data-testid^="stBaseButton"],
.stButton > button,
.stDownloadButton > button {
    font-family: var(--font-body);
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    border-radius: 100px;
    padding: 0.7rem 1.5rem;
    border: 1px solid var(--border-hair);
    background: transparent;
    color: var(--cream-dim);
    transition: background 0.2s ease, color 0.2s ease, border-color 0.2s ease;
}

[data-testid^="stBaseButton"]:hover,
.stButton > button:hover,
.stDownloadButton > button:hover {
    border-color: var(--cream);
    color: var(--cream);
    background: rgba(248, 241, 189, 0.06);
}

/* Primary: cream fill, dark label. The nested label element carries its own
   color, so it has to be forced too or you get cream on cream. */
[data-testid="stBaseButton-primary"],
[data-testid="stBaseButton-primaryFormSubmit"],
[data-testid="stBaseButton-secondaryFormSubmit"] {
    background: var(--cream) !important;
    border-color: var(--cream) !important;
}

[data-testid="stBaseButton-primary"],
[data-testid="stBaseButton-primary"] *,
[data-testid="stBaseButton-primaryFormSubmit"],
[data-testid="stBaseButton-primaryFormSubmit"] *,
[data-testid="stBaseButton-secondaryFormSubmit"],
[data-testid="stBaseButton-secondaryFormSubmit"] * {
    color: #0B0B0B !important;
}

[data-testid="stBaseButton-primary"]:hover,
[data-testid="stBaseButton-primaryFormSubmit"]:hover {
    background: #FFF8D2 !important;
    border-color: #FFF8D2 !important;
}

[data-testid="stMetric"] {
    background: var(--surface-card);
    border: 1px solid var(--border-hair);
    border-radius: 10px;
    padding: 14px 18px;
}

[data-testid="stMetricLabel"] {
    font-size: 0.6rem !important;
    font-weight: 600;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--text-faint) !important;
}

[data-testid="stMetricValue"] {
    font-size: 1.5rem !important;
    font-weight: 600;
    color: var(--cream) !important;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    border-bottom: 1px solid var(--border-hair);
    background: transparent;
}

.stTabs [data-baseweb="tab"] {
    background: transparent;
    border-radius: 8px 8px 0 0;
    padding: 10px 18px;
    font-size: 0.62rem;
    font-weight: 600;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--text-faint);
}

.stTabs [aria-selected="true"] {
    color: var(--cream) !important;
    background: var(--surface-card) !important;
}

.stTabs [data-baseweb="tab-highlight"] { background: var(--amber-core); }

[data-baseweb="select"] > div,
.stTextInput input,
.stNumberInput input,
.stDateInput input {
    background: var(--bg-section) !important;
    border-color: var(--border-hair) !important;
    color: var(--cream-dim) !important;
    border-radius: 8px !important;
}

.stSlider [data-baseweb="slider"] [role="slider"] { background: var(--amber-core); }

[data-testid="stExpander"] {
    border: 1px solid var(--border-hair);
    border-radius: 10px;
    background: var(--surface-card);
}

[data-testid="stDataFrame"] {
    border: 1px solid var(--border-hair);
    border-radius: 10px;
}

hr { border-color: var(--border-hair); }

[data-testid="stAppViewContainer"] a,
[data-testid="stAppViewContainer"] a:visited,
[data-testid="stMarkdownContainer"] a {
    color: var(--amber-core) !important;
    text-decoration-color: rgba(232, 163, 77, 0.4);
}

.monogram {
    display: grid;
    place-items: center;
    width: 160px;
    aspect-ratio: 1;
    border-radius: 14px;
    border: 1px solid var(--border-hair);
    background:
        radial-gradient(ellipse at 50% 120%, rgba(232, 163, 77, 0.35), transparent 70%),
        var(--bg-section);
    font-family: var(--font-display);
    font-size: 5rem;
    line-height: 1;
    color: var(--cream);
}

.byline .name {
    font-family: var(--font-display);
    text-transform: uppercase;
    font-size: 2.5rem;
    line-height: 0.92;
    color: var(--cream);
}

.byline .role {
    font-size: 0.6rem;
    font-weight: 600;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--text-faint);
    margin: 8px 0 14px;
}

.byline p {
    max-width: 52ch;
    margin-bottom: 12px;
}

@media (max-width: 768px) {
    .monogram { width: 108px; font-size: 3.25rem; margin-bottom: 1rem; }
    .byline .name { font-size: 2rem; }
}

/* ---------- 6. Mobile. Frame tightens, diagonal collapses, cards unmount. ---------- */

@media (max-width: 1024px) {
    [data-testid="stMainBlockContainer"] { padding: 3rem 2rem 4rem; }
    .offset-1, .offset-2 { transform: none; }
    [data-testid="stHorizontalBlock"]:has(.offset-2) { padding-bottom: 0; }
}

@media (max-width: 768px) {
    :root { --frame-gap: 10px; --frame-radius: 14px; }

    [data-testid="stMainBlockContainer"] { padding: 2.5rem 1.25rem 3.5rem; }

    .hero { padding: 2.5rem 0 3rem; }
    .hero h1 { max-width: 100%; }

    [data-testid="stAppViewContainer"] h3 { margin: 2rem 0 1rem; }

    /* spec §11: float cards unmount below 768px rather than stacking */
    .float-only { display: none; }

    .feature-card { padding: 18px; }

    .stApp::before { filter: blur(60px); opacity: 0.45; }

    /* stop Streamlit's horizontal columns from squeezing on narrow screens */
    [data-testid="stHorizontalBlock"] {
        flex-wrap: wrap;
        gap: 0.75rem;
    }
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
        min-width: 100% !important;
        flex: 1 1 100% !important;
    }

    [data-testid="stSidebar"] {
        box-shadow: 0 0 40px rgba(0, 0, 0, 0.6);
    }

    [data-testid="stMain"],
    [data-testid="stMainBlockContainer"] {
        min-width: 0;
        width: 100%;
    }

    .stTabs [data-baseweb="tab-list"] {
        overflow-x: auto;
        scrollbar-width: none;
    }
    .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar { display: none; }
    .stTabs [data-baseweb="tab"] { padding: 9px 12px; white-space: nowrap; }
}

@media (max-width: 420px) {
    [data-testid="stMainBlockContainer"] { padding: 2rem 1rem 3rem; }
    [data-testid="stAppViewContainer"] h1 { font-size: clamp(2.25rem, 12vw, 3rem); }
    .subhead { font-size: 0.8rem; }
    .stat-card { min-width: 0; }
    .stButton > button { padding: 0.65rem 1rem; font-size: 0.6rem; }
}

/* nothing on the page may push the frame sideways */
[data-testid="stAppViewContainer"] { max-width: 100vw; }

/* ---------- 7. Navigation ----------

   The sidebar starts closed and is opened by a hamburger. Streamlit ships a
   chevron ligature for both controls; the glyph is hidden and the bars are
   drawn in CSS so the button reads as a menu control at a glance. */

[data-testid="stExpandSidebarButton"],
[data-testid="stSidebarCollapseButton"] > button[data-testid] {
    position: relative;
    width: 40px !important;
    height: 40px !important;
    padding: 0 !important;
    border: 1px solid var(--border-hair) !important;
    border-radius: 11px !important;
    background: rgba(11, 11, 11, 0.72) !important;
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    transition: border-color 0.2s ease, background 0.2s ease;
}

[data-testid="stExpandSidebarButton"]:hover,
[data-testid="stSidebarCollapseButton"] > button[data-testid]:hover {
    border-color: rgba(232, 163, 77, 0.55) !important;
    background: rgba(232, 163, 77, 0.08) !important;
}

/* hide the chevron ligature Streamlit puts inside */
[data-testid="stExpandSidebarButton"] span,
[data-testid="stSidebarCollapseButton"] > button[data-testid] span {
    display: none !important;
}

/* three bars: the element is the middle bar, the shadows are the outer two */
[data-testid="stExpandSidebarButton"]::before,
[data-testid="stSidebarCollapseButton"] > button[data-testid]::before {
    content: '';
    position: absolute;
    left: 11px;
    right: 11px;
    top: 19px;
    height: 1.5px;
    border-radius: 2px;
    background: var(--cream);
    box-shadow: 0 -6px 0 var(--cream), 0 6px 0 var(--cream);
}

/* open state closes the menu, so the same control becomes a cross */
[data-testid="stSidebarCollapseButton"] > button[data-testid]::before {
    box-shadow: none;
    transform: rotate(45deg);
}

[data-testid="stSidebarCollapseButton"] > button[data-testid]::after {
    content: '';
    position: absolute;
    left: 11px;
    right: 11px;
    top: 19px;
    height: 1.5px;
    border-radius: 2px;
    background: var(--cream);
    transform: rotate(-45deg);
}

/* keep the hamburger clear of the page content when the sidebar is closed */
[data-testid="stExpandSidebarButton"] {
    margin-left: 4px;
}

/* ---------- the menu itself ---------- */

[data-testid="stSidebarUserContent"] {
    padding-top: 0.5rem;
}

.nav-brand {
    font-family: var(--font-display);
    text-transform: uppercase;
    font-size: 1.35rem;
    line-height: 0.9;
    letter-spacing: -0.01em;
    color: var(--cream);
    margin-bottom: 2px;
}

.nav-brand-sub {
    font-size: 0.55rem;
    font-weight: 600;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: var(--text-faint);
    margin-bottom: 1.75rem;
}

/* radio group rendered as a menu list rather than radio buttons */
[data-testid="stSidebar"] [role="radiogroup"] {
    gap: 2px;
}

[data-testid="stSidebar"] [role="radiogroup"] label {
    display: flex;
    align-items: center;
    width: 100%;
    padding: 10px 12px;
    border-radius: 9px;
    border: 1px solid transparent;
    cursor: pointer;
    transition: background 0.18s ease, border-color 0.18s ease;
}

[data-testid="stSidebar"] [role="radiogroup"] label:hover {
    background: rgba(255, 255, 255, 0.04);
}

/* Hide the radio dot without removing it: selection is shown by the row.
   display:none here also hides the <input> and the row stops responding. */
[data-testid="stSidebar"] [role="radiogroup"] label > div:first-child {
    width: 0 !important;
    height: 0 !important;
    min-width: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
    opacity: 0;
    overflow: hidden;
}

[data-testid="stSidebar"] [role="radiogroup"] label p {
    font-size: 0.68rem !important;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--text-muted) !important;
    margin: 0 !important;
}

[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {
    background: rgba(232, 163, 77, 0.10);
    border-color: rgba(232, 163, 77, 0.30);
}

[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) p {
    color: var(--cream) !important;
}

@media (max-width: 768px) {
    [data-testid="stExpandSidebarButton"],
    [data-testid="stSidebarCollapseButton"] > button[data-testid] {
        width: 38px !important;
        height: 38px !important;
    }
}

@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation: none !important;
        transition: none !important;
    }
}
</style>
"""


def apply_theme() -> None:
    """Inject the design system. Call once, immediately after set_page_config."""
    st.markdown(_CSS, unsafe_allow_html=True)
