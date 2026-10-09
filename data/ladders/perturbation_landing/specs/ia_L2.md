# Variant `meridian__ia_L2` of the Meridian Field Notes landing page

Reproduce the reference HTML document at the end of this file with the changes below applied, and
with nothing else changed. Every change is specified; there is nothing here for you to choose.
Apply the change sets in the order given.

Return one complete standalone HTML document.

## What must not change

- **The visual language is untouched.** Every custom property in `:root` keeps its value,
  and so does every literal colour and every `rgba(...)` in the `<style>` block. Every
  `border-radius` keeps its value. Georgia stays on the headings and Arial on the body. Every
  `box-shadow` stays, including the concentric rings on the artwork. Font sizes, weights and
  letter-spacing stay, and so do the padding, margin and gap values on everything you do not
  otherwise have to touch.
- **The reusable components are untouched.** The coffee card, the step card, the plan
  card, the quote card and the FAQ row each keep the internal layout the reference gives them: the
  same fields in the same order and the same arrangement, four coffee cards across and three plans
  across. Each shows exactly what it shows now and hides exactly what it hides now - the FAQ opens
  one answer at a time, the tasting notes are visible, every plan lists all its features. The same
  controls behave the same way: the profile buttons update the status text immediately, choosing a
  plan marks its card and flashes the toast, and the coffee cards are not clickable. Nothing moves
  onto a different surface - no panel, drawer or modal appears.
- **Every change must be visible when the page loads.** This page is judged from
  a screenshot of its resting state, so a difference that appears only after a click, a hover or a
  scroll-triggered animation is not a change at all. Where a step involves a control, its effect has
  to be on screen before anything is clicked: a default selection shown, a state marked, a value
  stated. Anything you add starts visible.
- **Every section moves.** The step has to reach the hero, this month's coffees, how it works, the
  plans, the voices, the FAQ, the closing band and the footer - not one region while the rest sit
  untouched.
- **The content is identical.** The same coffees, origins, farms, tasting notes and altitudes; the
  same three plans with the same sizes and prices; the same three subscribers with their cities and
  their quotes; the same four questions and answers; the same headings and body copy, word for word.
  No items added or removed, no new copy invented. This is the same page redesigned, not a new page.
- **The build is identical.** One standalone HTML document with no external files at all - the
  reference loads none, and neither may you. Plain CSS in a `<style>` tag and plain JavaScript in a
  `<script>` tag, exactly as the reference does. Do not introduce Tailwind, any other framework, or
  a build step: a change of technique would register as a design difference in its own right.
  Imagery stays CSS and inline SVG.
- **Everything keeps working.** The roast profile switch, the plan buttons and the FAQ still
  respond to a click, and any behaviour a step gives them works. Desktop width, about 1280px.


## The changes (2 change sets)

This variant moves the information architecture. Apply every set below, in order.

### IA-1 - Reorder the regions

Nothing is added, removed or restyled. Four things sit somewhere else, one of them in the hero.

1. **The hero leads with its actions.** The two hero actions move above the lead paragraph, so the
   order inside the hero becomes eyebrow, headline, actions, lead paragraph, price line.
2. **Plans move above the coffees.** In `<main>` the plans section moves to sit directly after the
   hero, so the order becomes hero, plans, this month's coffees, how it works, voices, FAQ,
   closing. Each section keeps its own background and padding.
3. **The FAQ column order flips.** `.faq-inner` changes `grid-template-columns: .72fr 1.28fr` to
   `1.28fr .72fr`, and its two children swap in the DOM so the questions sit left and the heading
   sits right, right-aligned.
4. **The utility bar moves to the foot.** It leaves the top of the document and sits directly above
   the footer's inner content, inside `.site-footer`, keeping its text and background. The sticky
   header becomes the first thing on the page.

### IA-2 - Regroup

1. **The hero's opening merges into one line.** The eyebrow and the price line join into a single
   line above the headline, reading the eyebrow text, a middot, then the price text. The separate
   price line beneath the headline is gone.
2. **The coffees gain a grouping level.** The four cards are grouped under two subheads, in this
   order: `Africa` holding Kiamugumo AA and Yirgacheffe Konga, then `Latin America` holding Finca
   La Ilusión and Nueva Esperanza. Each subhead is a full-width row above its pair, styled like
   `.section-kicker`, with a count of the coffees beneath it.
3. **The plans gain a grouping level.** The three cards are grouped under two subheads, `For one`
   holding Solo and `For a household` holding Pair and Table, each full width above its group.
4. **The FAQ folds into the closing section.** The FAQ section stops being a region of its own. Its
   heading, its four questions and their answers move inside the closing section beneath the
   closing headline and action, keeping their order and text. `<main>` is one section shorter.

## Reference design

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="Meridian Field Notes sends freshly roasted, single-origin coffee to your door every two weeks, from £11 per fortnight.">
  <title>Meridian Field Notes — Coffee, marked by place</title>
  <style>
    :root {
      --paper: #fbf8f1;
      --cream: #f2ede3;
      --sand: #e8dfd1;
      --ink: #20332e;
      --forest: #183f35;
      --forest-deep: #12332d;
      --muted: #6d766f;
      --rust: #b86145;
      --rust-dark: #9f4d37;
      --gold: #e4b961;
      --sage: #b4c7bb;
      --line: #d8d0c4;
      --white: #fffdf7;
      --shadow: 0 20px 50px rgba(32, 51, 46, .10);
    }

    * { box-sizing: border-box; }
    html { scroll-behavior: smooth; }
    body {
      margin: 0;
      color: var(--ink);
      background: var(--paper);
      font-family: Arial, Helvetica, sans-serif;
      font-size: 15px;
      line-height: 1.55;
      -webkit-font-smoothing: antialiased;
      text-rendering: optimizeLegibility;
    }
    a { color: inherit; text-decoration: none; }
    button { font: inherit; }
    button, a { -webkit-tap-highlight-color: transparent; }
    button:focus-visible, a:focus-visible {
      outline: 3px solid var(--gold);
      outline-offset: 4px;
    }
    h1, h2, h3, p, figure, blockquote { margin: 0; }
    h1, h2, h3, .serif { font-family: Georgia, 'Times New Roman', serif; font-weight: 400; }
    .shell { width: min(1160px, calc(100% - 56px)); margin: 0 auto; }
    .eyebrow, .section-kicker, .utility-bar, .nav-links, .button, .coffee-card-top,
    .coffee-detail > span, .tasting-label, .plan-overline, .plan-list, .footer-label,
    .art-word, .visual-topline, .visual-note, .profile-button, .step-number {
      letter-spacing: .12em;
      text-transform: uppercase;
    }

    /* Global navigation */
    .utility-bar {
      min-height: 34px;
      display: flex;
      align-items: center;
      color: #e9e1d4;
      background: var(--forest-deep);
      font-size: 10px;
      letter-spacing: .16em;
    }
    .utility-inner {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 24px;
    }
    .utility-left { display: flex; align-items: center; gap: 9px; }
    .utility-dot, .green-dot {
      width: 7px;
      height: 7px;
      display: inline-block;
      border-radius: 50%;
      background: var(--gold);
      flex: none;
    }
    .utility-right { color: #b8c9bd; }
    .site-header {
      position: sticky;
      top: 0;
      z-index: 20;
      background: rgba(251, 248, 241, .94);
      border-bottom: 1px solid rgba(32, 51, 46, .12);
      backdrop-filter: blur(12px);
    }
    .nav-wrap {
      height: 78px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 36px;
    }
    .brand {
      display: inline-flex;
      align-items: center;
      gap: 11px;
      min-width: 220px;
      color: var(--forest);
    }
    .brand svg { width: 35px; height: 35px; flex: none; }
    .brand-word { display: flex; flex-direction: column; line-height: 1; }
    .brand-word strong {
      font-family: Georgia, 'Times New Roman', serif;
      font-size: 17px;
      letter-spacing: .08em;
      font-weight: 400;
    }
    .brand-word small {
      margin-top: 5px;
      color: var(--rust);
      font-size: 8px;
      font-weight: 700;
      letter-spacing: .28em;
    }
    .nav-links { display: flex; align-items: center; gap: 28px; font-size: 10px; font-weight: 700; color: #4d5c54; }
    .nav-links a { transition: color .2s ease; }
    .nav-links a:hover { color: var(--rust); }
    .nav-pill, .button {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 12px;
      border-radius: 999px;
      border: 1px solid transparent;
      font-size: 10px;
      line-height: 1;
      font-weight: 700;
      white-space: nowrap;
      letter-spacing: .13em;
      text-transform: uppercase;
      transition: transform .2s ease, background .2s ease, color .2s ease, border-color .2s ease;
      cursor: pointer;
    }
    .nav-pill {
      padding: 13px 17px;
      color: var(--paper);
      background: var(--rust);
    }
    .nav-pill:hover, .button-primary:hover { transform: translateY(-2px); background: var(--rust-dark); }
    .nav-pill span, .button span { font-size: 16px; line-height: 8px; letter-spacing: 0; }

    /* Hero */
    .hero-section {
      position: relative;
      overflow: hidden;
      border-bottom: 1px solid var(--line);
      background:
        radial-gradient(circle at 86% 20%, rgba(228, 185, 97, .14) 0, rgba(228,185,97,0) 22%),
        var(--paper);
    }
    .hero-section::before {
      content: '';
      position: absolute;
      width: 620px;
      height: 620px;
      right: -280px;
      top: -280px;
      border: 1px solid rgba(32, 51, 46, .09);
      border-radius: 50%;
      box-shadow: 0 0 0 24px rgba(32, 51, 46, .025), 0 0 0 48px rgba(32, 51, 46, .018);
    }
    .hero-grid {
      position: relative;
      min-height: 570px;
      display: grid;
      grid-template-columns: minmax(0, 1fr) minmax(420px, .92fr);
      align-items: center;
      gap: 70px;
      padding-top: 62px;
      padding-bottom: 68px;
    }
    .hero-copy { position: relative; z-index: 1; }
    .eyebrow, .section-kicker {
      display: inline-flex;
      align-items: center;
      gap: 9px;
      color: var(--rust);
      font-size: 10px;
      line-height: 1;
      font-weight: 700;
      letter-spacing: .18em;
    }
    .eyebrow::before {
      content: '';
      width: 24px;
      height: 1px;
      background: var(--rust);
    }
    .hero-copy h1 {
      max-width: 650px;
      margin-top: 23px;
      color: var(--ink);
      font-size: clamp(52px, 5.1vw, 72px);
      line-height: .99;
      letter-spacing: -.055em;
    }
    .hero-copy h1 em { color: var(--rust); font-style: normal; }
    .hero-intro {
      max-width: 545px;
      margin-top: 26px;
      color: #56645d;
      font-size: 17px;
      line-height: 1.65;
    }
    .hero-actions { display: flex; align-items: center; gap: 12px; margin-top: 31px; }
    .button { padding: 16px 21px; }
    .button-primary { color: var(--paper); background: var(--rust); }
    .button-secondary {
      color: var(--ink);
      border-color: rgba(32, 51, 46, .25);
      background: transparent;
    }
    .button-secondary:hover { color: var(--rust); border-color: var(--rust); transform: translateY(-2px); }
    .hero-meta {
      display: flex;
      align-items: stretch;
      gap: 24px;
      margin-top: 42px;
    }
    .starting-price { display: flex; flex-direction: column; gap: 2px; min-width: 132px; }
    .starting-price small, .hero-meta-note small {
      color: var(--muted);
      font-size: 9px;
      font-weight: 700;
      letter-spacing: .16em;
      text-transform: uppercase;
    }
    .starting-price strong {
      font-family: Georgia, 'Times New Roman', serif;
      font-size: 29px;
      line-height: 1;
      font-weight: 400;
    }
    .starting-price strong span { color: var(--muted); font-family: Arial, Helvetica, sans-serif; font-size: 11px; letter-spacing: .02em; }
    .hero-meta-divider { width: 1px; background: var(--line); }
    .hero-meta-note { display: flex; flex-direction: column; justify-content: center; gap: 2px; }
    .hero-meta-note b { font-size: 13px; font-weight: 700; }

    /* CSS / SVG editorial illustration */
    .hero-visual {
      position: relative;
      min-height: 474px;
      overflow: hidden;
      border-radius: 7px;
      background: #c76e4c;
      box-shadow: var(--shadow);
      isolation: isolate;
    }
    .hero-visual::before {
      content: '';
      position: absolute;
      width: 370px;
      height: 370px;
      top: 55px;
      left: 50%;
      transform: translateX(-50%);
      border: 1px solid rgba(255, 250, 239, .34);
      border-radius: 50%;
      box-shadow: 0 0 0 24px rgba(255,250,239,.09), 0 0 0 65px rgba(255,250,239,.06);
    }
    .hero-visual::after {
      content: '';
      position: absolute;
      width: 170px;
      height: 170px;
      right: -55px;
      bottom: -64px;
      border: 1px solid rgba(24, 63, 53, .28);
      border-radius: 50%;
      box-shadow: 0 0 0 17px rgba(24,63,53,.08), 0 0 0 34px rgba(24,63,53,.05);
    }
    .visual-topline {
      position: absolute;
      z-index: 4;
      top: 19px;
      right: 21px;
      left: 21px;
      display: flex;
      justify-content: space-between;
      color: rgba(255, 250, 239, .85);
      font-size: 9px;
      font-weight: 700;
      letter-spacing: .16em;
    }
    .topo-lines { position: absolute; z-index: 1; inset: 0; width: 100%; height: 100%; opacity: .72; }
    .package-shadow {
      position: absolute;
      z-index: 1;
      width: 257px;
      height: 44px;
      left: 50%;
      bottom: 43px;
      transform: translateX(-47%) rotate(-5deg);
      border-radius: 50%;
      background: rgba(52, 39, 26, .24);
      filter: blur(11px);
    }
    .coffee-package {
      position: absolute;
      z-index: 3;
      width: 268px;
      height: 355px;
      top: 66px;
      left: 50%;
      padding: 30px 25px 22px;
      overflow: hidden;
      transform: translateX(-50%) rotate(-5deg);
      border: 1px solid rgba(32, 51, 46, .23);
      border-radius: 5px 5px 14px 14px;
      color: var(--ink);
      background: linear-gradient(135deg, #f9f0dd 0%, #eee1c9 68%, #dbc9a9 100%);
      box-shadow: 17px 21px 0 rgba(67, 46, 31, .12), 0 28px 30px rgba(71, 44, 26, .19);
    }
    .coffee-package::before {
      content: '';
      position: absolute;
      top: 0;
      right: 0;
      left: 0;
      height: 17px;
      background: repeating-linear-gradient(90deg, rgba(32,51,46,.34) 0 2px, transparent 2px 7px);
      opacity: .45;
      border-bottom: 1px solid rgba(32,51,46,.26);
    }
    .coffee-package::after {
      content: '';
      position: absolute;
      width: 160px;
      height: 160px;
      right: -74px;
      bottom: -72px;
      border: 1px solid rgba(32,51,46,.19);
      border-radius: 50%;
      box-shadow: 0 0 0 13px rgba(32,51,46,.05), 0 0 0 26px rgba(32,51,46,.035);
    }
    .package-label {
      position: relative;
      z-index: 1;
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      font-size: 8px;
      line-height: 1.3;
      font-weight: 700;
      letter-spacing: .16em;
    }
    .package-label span:last-child { color: var(--rust); }
    .package-title {
      position: relative;
      z-index: 1;
      margin-top: 63px;
      font-family: Georgia, 'Times New Roman', serif;
      font-size: 34px;
      line-height: .9;
      letter-spacing: -.06em;
    }
    .package-title small {
      display: block;
      margin-top: 9px;
      color: var(--rust);
      font-family: Arial, Helvetica, sans-serif;
      font-size: 9px;
      font-weight: 700;
      letter-spacing: .23em;
    }
    .package-rule { position: relative; z-index: 1; width: 62px; height: 2px; margin-top: 22px; background: var(--rust); }
    .package-copy {
      position: relative;
      z-index: 1;
      max-width: 150px;
      margin-top: 16px;
      color: #5f655c;
      font-size: 10px;
      line-height: 1.45;
    }
    .package-foot {
      position: absolute;
      z-index: 1;
      right: 24px;
      bottom: 21px;
      left: 25px;
      display: flex;
      justify-content: space-between;
      color: #5f655c;
      font-size: 8px;
      font-weight: 700;
      letter-spacing: .15em;
      text-transform: uppercase;
    }
    .package-seal {
      position: absolute;
      z-index: 1;
      top: 87px;
      right: 23px;
      display: grid;
      width: 42px;
      height: 42px;
      place-items: center;
      border: 1px solid var(--rust);
      border-radius: 50%;
      color: var(--rust);
      font-size: 7px;
      font-weight: 700;
      line-height: 1.25;
      text-align: center;
      letter-spacing: .1em;
    }
    .visual-note {
      position: absolute;
      z-index: 4;
      display: flex;
      align-items: center;
      gap: 8px;
      color: rgba(255,250,239,.88);
      font-size: 9px;
      font-weight: 700;
      letter-spacing: .15em;
    }
    .visual-note::before { content: ''; width: 22px; height: 1px; background: currentColor; }
    .note-left { left: 21px; bottom: 64px; transform: rotate(-90deg); transform-origin: left center; }
    .note-bottom { right: 21px; bottom: 20px; }
    .note-bottom::before { width: 9px; height: 9px; border: 1px solid currentColor; border-radius: 50%; background: transparent; }

    /* This month's box */
    .box-section { background: var(--sand); border-bottom: 1px solid var(--line); }
    .section-pad { padding-top: 92px; padding-bottom: 92px; }
    .section-heading-row { display: flex; align-items: flex-end; justify-content: space-between; gap: 40px; margin-bottom: 37px; }
    .section-heading-row h2, .center-heading h2 {
      max-width: 650px;
      margin-top: 15px;
      color: var(--ink);
      font-size: 45px;
      line-height: 1.03;
      letter-spacing: -.045em;
    }
    .heading-aside {
      max-width: 250px;
      padding-bottom: 3px;
      color: #637068;
      font-size: 12px;
      line-height: 1.5;
      text-align: right;
    }
    .heading-aside .green-dot { margin-right: 6px; background: var(--forest); }
    .heading-aside strong { display: block; margin-top: 5px; color: var(--ink); font-size: 13px; }
    .coffee-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }
    .coffee-card {
      min-height: 410px;
      display: flex;
      flex-direction: column;
      padding: 14px 17px 17px;
      overflow: hidden;
      border: 1px solid rgba(32,51,46,.14);
      border-radius: 5px;
      background: var(--paper);
      box-shadow: 0 7px 18px rgba(32,51,46,.035);
    }
    .coffee-card-top { display: flex; align-items: center; justify-content: space-between; min-height: 19px; color: #728077; font-size: 8px; font-weight: 700; }
    .altitude-tag { color: var(--rust); }
    .coffee-art { position: relative; height: 96px; margin: 11px 0 18px; overflow: hidden; border-radius: 3px; }
    .coffee-art::before, .coffee-art::after { content: ''; position: absolute; }
    .coffee-art::before { width: 160px; height: 160px; top: -74px; right: -42px; border: 1px solid currentColor; border-radius: 50%; opacity: .45; box-shadow: 0 0 0 13px rgba(255,255,255,.09), 0 0 0 27px rgba(255,255,255,.06); }
    .coffee-art::after { width: 175px; height: 1px; left: -18px; bottom: 23px; background: currentColor; opacity: .45; transform: rotate(-27deg); transform-origin: left; }
    .art-index, .art-word { position: absolute; z-index: 1; font-size: 9px; font-weight: 700; }
    .art-index { top: 12px; left: 13px; letter-spacing: .15em; }
    .art-word { right: 13px; bottom: 10px; font-size: 18px; font-family: Georgia, 'Times New Roman', serif; letter-spacing: -.02em; opacity: .64; }
    .art-kenya { color: #355146; background: #d9bd8b; }
    .art-colombia { color: #335a54; background: #b9cec0; }
    .art-ethiopia { color: #6a4935; background: #e4c4a9; }
    .art-honduras { color: #3b5448; background: #b4c3a4; }
    .art-colombia::after { transform: rotate(24deg); bottom: 27px; }
    .art-ethiopia::before { right: auto; left: -52px; top: -72px; }
    .art-honduras::after { transform: rotate(-6deg); bottom: 34px; }
    .coffee-card h3 { min-height: 28px; color: var(--ink); font-size: 22px; line-height: 1.08; letter-spacing: -.035em; }
    .coffee-origin { margin-top: 5px; color: var(--rust); font-size: 11px; font-weight: 700; letter-spacing: .03em; }
    .coffee-detail { min-height: 66px; margin-top: 17px; padding-top: 13px; border-top: 1px solid var(--line); }
    .coffee-detail > span, .tasting-label { display: block; color: #808a82; font-size: 8px; font-weight: 700; letter-spacing: .16em; }
    .coffee-detail strong { display: block; margin-top: 4px; color: #43544c; font-size: 12px; line-height: 1.35; font-weight: 700; }
    .tasting { margin-top: auto; padding: 12px 13px 13px; border-radius: 3px; background: #f0e9dd; }
    .tasting p { margin-top: 6px; color: var(--ink); font-family: Georgia, 'Times New Roman', serif; font-size: 14px; line-height: 1.25; }
    .box-tail { display: flex; justify-content: space-between; align-items: center; gap: 20px; margin-top: 22px; padding: 16px 3px 0; border-top: 1px solid rgba(32,51,46,.15); color: #637068; font-size: 12px; }
    .box-tail strong { color: var(--ink); font-weight: 700; }
    .text-link { color: var(--rust); font-size: 11px; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; transition: color .2s ease; }
    .text-link:hover { color: var(--rust-dark); }

    /* How it works */
    .how-section { position: relative; overflow: hidden; color: var(--paper); background: var(--forest); }
    .how-section::before {
      content: '';
      position: absolute;
      width: 650px;
      height: 650px;
      right: -300px;
      top: -220px;
      border: 1px solid rgba(229,219,198,.14);
      border-radius: 50%;
      box-shadow: 0 0 0 28px rgba(229,219,198,.04), 0 0 0 56px rgba(229,219,198,.035);
    }
    .how-section::after {
      content: 'M';
      position: absolute;
      left: -28px;
      bottom: -128px;
      color: rgba(229,219,198,.045);
      font-family: Georgia, 'Times New Roman', serif;
      font-size: 330px;
      line-height: 1;
    }
    .how-inner { position: relative; z-index: 1; padding-top: 94px; padding-bottom: 98px; }
    .how-intro { max-width: 680px; }
    .how-intro .section-kicker { color: var(--gold); }
    .how-intro .section-kicker::before { background: var(--gold); }
    .how-intro h2 { margin-top: 16px; color: var(--paper); font-size: 47px; line-height: 1.02; letter-spacing: -.045em; }
    .how-intro > p:last-child { max-width: 550px; margin-top: 19px; color: #c6d0c6; font-size: 16px; line-height: 1.6; }
    .steps-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-top: 50px; }
    .step-card {
      min-height: 263px;
      padding: 25px 23px 22px;
      border: 1px solid rgba(238,235,223,.22);
      border-radius: 4px;
      background: rgba(255,253,247,.055);
    }
    .step-card:first-child { background: #285246; border-color: rgba(228,185,97,.55); }
    .step-number { display: flex; align-items: center; justify-content: space-between; color: var(--gold); font-size: 10px; font-weight: 700; }
    .step-number::after { content: '↗'; font-family: Arial, Helvetica, sans-serif; font-size: 16px; letter-spacing: 0; }
    .step-card h3 { max-width: 260px; margin-top: 22px; color: var(--paper); font-size: 25px; line-height: 1.08; letter-spacing: -.035em; }
    .step-card p { margin-top: 13px; color: #c7d1c8; font-size: 13px; line-height: 1.55; }
    .profile-switch { display: grid; grid-template-columns: repeat(3, 1fr); gap: 4px; margin-top: 20px; }
    .profile-button {
      padding: 8px 4px;
      border: 1px solid rgba(238,235,223,.25);
      border-radius: 2px;
      color: #d7dfd6;
      background: transparent;
      font-size: 8px;
      font-weight: 700;
      cursor: pointer;
      transition: background .2s ease, color .2s ease, border-color .2s ease;
    }
    .profile-button:hover { border-color: var(--gold); color: var(--gold); }
    .profile-button.active { color: var(--forest); border-color: var(--gold); background: var(--gold); }
    .profile-status { min-height: 31px; margin-top: 10px !important; color: #e9e3d5 !important; font-size: 11px !important; line-height: 1.35 !important; }
    .mini-calendar { display: flex; align-items: center; gap: 7px; margin-top: 22px; color: var(--gold); font-size: 10px; font-weight: 700; letter-spacing: .09em; }
    .calendar-icon { display: grid; width: 28px; height: 26px; place-items: center; border: 1px solid var(--gold); border-radius: 2px; font-family: Georgia, 'Times New Roman', serif; font-size: 13px; letter-spacing: 0; }
    .cutoff-line { display: flex; align-items: center; gap: 9px; margin-top: 22px; color: var(--gold); font-size: 10px; font-weight: 700; letter-spacing: .08em; }
    .cutoff-line::before { content: ''; width: 42px; height: 1px; background: repeating-linear-gradient(90deg, var(--gold) 0 4px, transparent 4px 8px); }

    /* Plans */
    .plans-section { background: var(--paper); }
    .plans-inner { padding-top: 96px; padding-bottom: 100px; }
    .center-heading { text-align: center; }
    .center-heading .section-kicker { justify-content: center; }
    .center-heading h2 { margin-right: auto; margin-left: auto; }
    .center-heading > p:last-child { max-width: 540px; margin: 17px auto 0; color: var(--muted); font-size: 15px; }
    .plans-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; max-width: 1040px; margin: 48px auto 0; align-items: stretch; }
    .plan-card {
      position: relative;
      min-height: 394px;
      display: flex;
      flex-direction: column;
      padding: 29px 27px 25px;
      border: 1px solid var(--line);
      border-radius: 5px;
      background: #f3eee5;
      transition: transform .2s ease, box-shadow .2s ease, border-color .2s ease;
    }
    .plan-card:hover { transform: translateY(-4px); box-shadow: 0 14px 28px rgba(32,51,46,.09); }
    .plan-card.featured { border: 2px solid var(--forest); background: var(--white); transform: translateY(-9px); box-shadow: 0 18px 34px rgba(32,51,46,.12); }
    .plan-card.featured:hover { transform: translateY(-13px); }
    .plan-badge { position: absolute; top: -13px; left: 24px; padding: 7px 11px; color: var(--forest); background: var(--gold); font-size: 9px; line-height: 1; font-weight: 800; letter-spacing: .13em; text-transform: uppercase; }
    .plan-overline { color: var(--rust); font-size: 9px; font-weight: 700; }
    .plan-card h3 { margin-top: 13px; color: var(--ink); font-size: 33px; line-height: 1; letter-spacing: -.05em; }
    .plan-size { margin-top: 8px; color: var(--muted); font-size: 12px; font-weight: 700; }
    .plan-price { display: flex; align-items: baseline; gap: 7px; margin-top: 26px; color: var(--ink); font-family: Georgia, 'Times New Roman', serif; font-size: 50px; line-height: .9; letter-spacing: -.05em; }
    .plan-price small { color: var(--muted); font-family: Arial, Helvetica, sans-serif; font-size: 11px; letter-spacing: 0; }
    .plan-list { display: grid; gap: 9px; margin-top: 28px; padding: 0; color: #596961; font-size: 10px; font-weight: 700; letter-spacing: .08em; list-style: none; }
    .plan-list li { display: flex; align-items: center; gap: 9px; }
    .check { display: inline-grid; width: 16px; height: 16px; place-items: center; border-radius: 50%; color: var(--paper); background: var(--forest); font-size: 11px; letter-spacing: 0; }
    .plan-button { width: 100%; margin-top: auto; }
    .plan-card .button-secondary { border-color: rgba(32,51,46,.28); }
    .plan-card .button-secondary:hover { background: var(--forest); color: var(--paper); border-color: var(--forest); }
    .plan-card .button-primary { background: var(--forest); }
    .plan-card .button-primary:hover { background: var(--forest-deep); }
    .plans-foot { margin-top: 29px; color: var(--muted); font-size: 12px; text-align: center; }
    .plans-foot strong { color: var(--ink); }
    .selection-toast {
      position: fixed;
      z-index: 40;
      right: 24px;
      bottom: 24px;
      max-width: 330px;
      padding: 15px 18px;
      border: 1px solid rgba(228,185,97,.7);
      border-radius: 4px;
      color: var(--paper);
      background: var(--forest-deep);
      box-shadow: var(--shadow);
      font-size: 13px;
      opacity: 0;
      transform: translateY(22px);
      pointer-events: none;
      transition: opacity .25s ease, transform .25s ease;
    }
    .selection-toast.show { opacity: 1; transform: translateY(0); }

    /* Subscriber voices */
    .voices-section { background: #dce5dc; border-top: 1px solid #cbd7cd; border-bottom: 1px solid #cbd7cd; }
    .voices-inner { padding-top: 89px; padding-bottom: 94px; }
    .voices-top { display: flex; align-items: flex-end; justify-content: space-between; gap: 28px; margin-bottom: 36px; }
    .voices-top h2 { margin-top: 15px; color: var(--ink); font-size: 43px; line-height: 1.04; letter-spacing: -.045em; }
    .voices-aside { max-width: 240px; color: #5f7066; font-size: 12px; text-align: right; }
    .quote-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
    .quote-card { min-height: 257px; display: flex; flex-direction: column; padding: 23px 23px 20px; border: 1px solid rgba(32,51,46,.15); border-radius: 4px; background: var(--paper); }
    .quote-mark { height: 31px; color: var(--rust); font-family: Georgia, 'Times New Roman', serif; font-size: 54px; line-height: .8; }
    .quote-card blockquote { max-width: 300px; margin-top: 10px; color: var(--ink); font-family: Georgia, 'Times New Roman', serif; font-size: 19px; line-height: 1.32; letter-spacing: -.015em; }
    .quote-card figcaption { display: flex; align-items: center; gap: 11px; margin-top: auto; padding-top: 18px; border-top: 1px solid var(--line); }
    .initials { display: grid; width: 32px; height: 32px; place-items: center; border-radius: 50%; color: var(--paper); background: var(--forest); font-size: 10px; font-weight: 700; letter-spacing: .04em; }
    .quote-card:nth-child(2) .initials { color: var(--ink); background: var(--gold); }
    .quote-card:nth-child(3) .initials { background: var(--rust); }
    .person { display: flex; flex-direction: column; line-height: 1.3; }
    .person strong { font-size: 12px; font-weight: 700; }
    .person span { margin-top: 2px; color: var(--muted); font-size: 10px; }

    /* FAQ */
    .faq-section { background: var(--cream); }
    .faq-inner { display: grid; grid-template-columns: .72fr 1.28fr; gap: 92px; padding-top: 96px; padding-bottom: 104px; }
    .faq-side h2 { max-width: 400px; margin-top: 16px; color: var(--ink); font-size: 45px; line-height: 1.03; letter-spacing: -.045em; }
    .faq-side > p { max-width: 335px; margin-top: 20px; color: var(--muted); font-size: 14px; line-height: 1.65; }
    .faq-contact { display: flex; align-items: center; gap: 11px; margin-top: 32px; padding-top: 19px; border-top: 1px solid var(--line); color: var(--rust); font-size: 11px; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; }
    .faq-contact::before { content: '↗'; display: grid; width: 26px; height: 26px; place-items: center; border: 1px solid var(--rust); border-radius: 50%; font-size: 15px; letter-spacing: 0; }
    .faq-list { border-top: 1px solid var(--ink); }
    .faq-item { border-bottom: 1px solid #cfc7bb; }
    .faq-question {
      width: 100%;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 24px;
      padding: 21px 0;
      border: 0;
      color: var(--ink);
      background: transparent;
      font-family: Georgia, 'Times New Roman', serif;
      font-size: 20px;
      line-height: 1.2;
      text-align: left;
      cursor: pointer;
    }
    .faq-question:hover { color: var(--rust); }
    .faq-plus { position: relative; flex: none; width: 25px; height: 25px; border: 1px solid currentColor; border-radius: 50%; }
    .faq-plus::before, .faq-plus::after { content: ''; position: absolute; top: 50%; left: 50%; width: 9px; height: 1px; background: currentColor; transform: translate(-50%, -50%); transition: transform .2s ease; }
    .faq-plus::after { transform: translate(-50%, -50%) rotate(90deg); }
    .faq-item.open .faq-question { color: var(--rust); }
    .faq-item.open .faq-plus::after { transform: translate(-50%, -50%) rotate(0deg); }
    .faq-answer { display: none; padding: 0 56px 22px 0; color: #627069; font-size: 14px; line-height: 1.65; }
    .faq-item.open .faq-answer { display: block; }

    /* Closing call to action */
    .closing-section { position: relative; overflow: hidden; color: var(--paper); background: var(--rust); }
    .closing-section::before {
      content: '';
      position: absolute;
      width: 480px;
      height: 480px;
      right: -170px;
      top: -130px;
      border: 1px solid rgba(255,250,239,.28);
      border-radius: 50%;
      box-shadow: 0 0 0 22px rgba(255,250,239,.07), 0 0 0 44px rgba(255,250,239,.045);
    }
    .closing-section::after {
      content: 'MF';
      position: absolute;
      right: 55px;
      bottom: -70px;
      color: rgba(24,63,53,.14);
      font-family: Georgia, 'Times New Roman', serif;
      font-size: 190px;
      line-height: 1;
      letter-spacing: -.14em;
    }
    .closing-inner { position: relative; z-index: 1; min-height: 329px; display: grid; grid-template-columns: 110px 1fr 270px; align-items: center; gap: 35px; }
    .closing-stamp { align-self: start; margin-top: 51px; padding-top: 11px; border-top: 1px solid rgba(255,250,239,.55); color: rgba(255,250,239,.85); font-size: 10px; font-weight: 700; letter-spacing: .18em; }
    .closing-inner .section-kicker { color: #f8e7bf; }
    .closing-inner h2 { margin-top: 16px; color: var(--paper); font-size: 52px; line-height: .98; letter-spacing: -.055em; }
    .closing-inner h2 em { color: #f8d98d; font-style: normal; }
    .closing-copy { position: relative; z-index: 2; max-width: 235px; }
    .closing-copy p { color: #f8e9d2; font-size: 14px; line-height: 1.55; }
    .button-light { color: var(--forest); background: var(--paper); }
    .button-light:hover { color: var(--paper); border-color: var(--forest); background: var(--forest); transform: translateY(-2px); }
    .closing-copy .button { margin-top: 19px; }
    .closing-price { display: block; margin-top: 10px; color: #f7d8c1; font-size: 10px; letter-spacing: .08em; }

    /* Footer */
    .site-footer { color: #dfe8dc; background: var(--forest-deep); }
    .footer-main { display: grid; grid-template-columns: 1.45fr .75fr 1fr; gap: 80px; padding-top: 54px; padding-bottom: 47px; }
    .brand-light { color: var(--paper); }
    .brand-light .brand-word small { color: var(--gold); }
    .footer-brand > p { max-width: 285px; margin-top: 17px; color: #a9bcb0; font-size: 12px; line-height: 1.6; }
    .footer-label { margin-bottom: 15px; color: var(--gold); font-size: 9px; font-weight: 700; }
    .footer-links-col { display: flex; flex-direction: column; align-items: flex-start; gap: 9px; color: #e3e9df; font-size: 12px; }
    .footer-links-col a:hover { color: var(--gold); }
    .footer-address { color: #b8c9bd; font-size: 12px; line-height: 1.65; font-style: normal; }
    .footer-bottom { display: flex; align-items: center; justify-content: space-between; gap: 20px; padding: 18px 0 17px; border-top: 1px solid rgba(223,232,220,.16); color: #91aa9b; font-size: 10px; }
    .footer-bottom-links { display: flex; gap: 21px; color: #c9d7ca; }
    .footer-bottom-links a:hover { color: var(--gold); }
    .footer-policies { display: flex; gap: 26px; padding: 14px 0 25px; border-top: 1px solid rgba(223,232,220,.08); color: #789286; font-size: 10px; line-height: 1.5; }
    .footer-policies span { scroll-margin-top: 100px; }

    @media (max-width: 980px) {
      .nav-links { gap: 15px; }
      .brand { min-width: auto; }
      .hero-grid { grid-template-columns: 1fr 380px; gap: 35px; }
      .hero-copy h1 { font-size: 56px; }
      .coffee-grid { grid-template-columns: repeat(2, 1fr); }
      .coffee-card { min-height: 390px; }
      .faq-inner { gap: 45px; }
    }
    @media (max-width: 740px) {
      .shell { width: min(100% - 36px, 600px); }
      .utility-right, .nav-links { display: none; }
      .nav-wrap { height: 68px; }
      .nav-pill { padding: 12px 13px; font-size: 9px; }
      .hero-grid { grid-template-columns: 1fr; gap: 45px; padding-top: 54px; padding-bottom: 60px; }
      .hero-copy h1 { font-size: 53px; }
      .hero-visual { min-height: 415px; }
      .coffee-package { top: 52px; transform: translateX(-50%) scale(.9) rotate(-5deg); }
      .section-heading-row, .voices-top { display: block; }
      .heading-aside, .voices-aside { max-width: 300px; margin-top: 18px; text-align: left; }
      .section-heading-row h2, .voices-top h2, .faq-side h2 { font-size: 39px; }
      .how-intro h2 { font-size: 40px; }
      .steps-grid, .plans-grid, .quote-grid { grid-template-columns: 1fr; }
      .step-card { min-height: auto; }
      .plan-card.featured, .plan-card.featured:hover { transform: none; }
      .faq-inner { grid-template-columns: 1fr; gap: 42px; }
      .closing-inner { grid-template-columns: 1fr; gap: 20px; padding-top: 47px; padding-bottom: 52px; }
      .closing-stamp { margin-top: 0; }
      .closing-inner h2 { font-size: 47px; }
      .footer-main { grid-template-columns: 1fr 1fr; gap: 40px 25px; }
      .footer-brand { grid-column: 1 / -1; }
      .footer-bottom, .footer-policies { display: block; }
      .footer-bottom-links { margin-top: 11px; }
      .footer-policies span { display: block; margin-top: 7px; }
    }
    @media (prefers-reduced-motion: reduce) {
      html { scroll-behavior: auto; }
      *, *::before, *::after { transition-duration: .01ms !important; animation-duration: .01ms !important; }
    }
  </style>
</head>
<body>
  <div class="utility-bar">
    <div class="shell utility-inner">
      <div class="utility-left"><span class="utility-dot"></span><span>Roasted fresh · posted every second Tuesday</span></div>
      <div class="utility-right">Postage included on every plan</div>
    </div>
  </div>

  <header class="site-header">
    <div class="shell nav-wrap">
      <a class="brand" href="#top" aria-label="Meridian Field Notes home">
        <svg viewBox="0 0 36 36" fill="none" aria-hidden="true">
          <circle cx="18" cy="18" r="15" stroke="currentColor" stroke-width="1.4"></circle>
          <path d="M18 3v30M3 18h30M8.3 8.3c5.2 4.2 14.2 4.2 19.4 0M8.3 27.7c5.2-4.2 14.2-4.2 19.4 0" stroke="currentColor" stroke-width="1.1" opacity=".7"></path>
          <circle cx="18" cy="18" r="3.1" fill="var(--rust)"></circle>
        </svg>
        <span class="brand-word"><strong>MERIDIAN</strong><small>FIELD NOTES</small></span>
      </a>
      <nav class="nav-links" aria-label="Main navigation">
        <a href="#box">This month's box</a>
        <a href="#how">How it works</a>
        <a href="#plans">Plans</a>
        <a href="#faq">FAQ</a>
      </nav>
      <a class="nav-pill" href="#plans">Start a subscription <span>↗</span></a>
    </div>
  </header>

  <main id="top">
    <section class="hero-section" aria-labelledby="hero-title">
      <div class="shell hero-grid">
        <div class="hero-copy">
          <div class="eyebrow">Coffee, marked by place</div>
          <h1 id="hero-title">Single-origin coffee,<br><em>on a better schedule.</em></h1>
          <p class="hero-intro">Meridian Field Notes is a coffee subscription that sends a box of single-origin coffee to your door every two weeks — roasted fresh, sourced with care, and easy to pause.</p>
          <div class="hero-actions">
            <a class="button button-primary" href="#plans">Start a subscription <span>↗</span></a>
            <a class="button button-secondary" href="#box">See this month's box <span>↓</span></a>
          </div>
          <div class="hero-meta">
            <div class="starting-price"><small>Starting at</small><strong>£11 <span>/ fortnight</span></strong></div>
            <div class="hero-meta-divider"></div>
            <div class="hero-meta-note"><small>The little promise</small><b>Fresh coffee. No lock-in.</b></div>
          </div>
        </div>

        <div class="hero-visual" aria-label="A Meridian Field Notes coffee parcel featuring Kiamugumo AA from Kenya">
          <div class="visual-topline"><span>Meridian / field note 07</span><span>Four origins / June</span></div>
          <svg class="topo-lines" viewBox="0 0 500 500" preserveAspectRatio="none" aria-hidden="true">
            <path d="M-30 375C77 288 129 432 241 340s154-100 289-30" stroke="#fff9ee" stroke-width="1" fill="none" opacity=".44"></path>
            <path d="M-40 406c125-91 177 39 282-46 96-78 154-105 298-45" stroke="#fff9ee" stroke-width="1" fill="none" opacity=".38"></path>
            <path d="M-36 440c114-76 171 33 275-48 112-87 172-82 300-30" stroke="#fff9ee" stroke-width="1" fill="none" opacity=".3"></path>
            <path d="M65 0c42 81 19 134 79 188 50 44 98 45 128 112" stroke="#193f35" stroke-width="1" fill="none" opacity=".24"></path>
            <path d="M28 0c56 92 29 145 96 202 52 43 92 47 124 116" stroke="#193f35" stroke-width="1" fill="none" opacity=".18"></path>
          </svg>
          <div class="package-shadow"></div>
          <div class="coffee-package">
            <div class="package-label"><span>Single-origin / 250g</span><span>Roasted in Sheffield</span></div>
            <div class="package-title">KIAMUGUMO<br>AA<small>Kirinyaga · Kenya</small></div>
            <div class="package-rule"></div>
            <p class="package-copy">Blackcurrant, cane sugar, dry finish. A bright note from high ground.</p>
            <div class="package-seal">FIELD<br>NOTE<br>07</div>
            <div class="package-foot"><span>Meridian Field Notes</span><span>1,750m</span></div>
          </div>
          <div class="visual-note note-left">sourced by place</div>
          <div class="visual-note note-bottom">Two-weekly, by post</div>
        </div>
      </div>
    </section>

    <section class="box-section" id="box" aria-labelledby="box-title">
      <div class="shell section-pad">
        <div class="section-heading-row">
          <div>
            <div class="section-kicker">This month's box / 04 origins</div>
            <h2 id="box-title">Four places. One very good post.</h2>
          </div>
          <div class="heading-aside"><span class="green-dot"></span>Roasted to order, then on its way.<strong>Meet the current field notes.</strong></div>
        </div>

        <div class="coffee-grid">
          <article class="coffee-card">
            <div class="coffee-card-top"><span>01 / East Africa</span><span class="altitude-tag">1,750m</span></div>
            <div class="coffee-art art-kenya"><span class="art-index">KEN / 01</span><span class="art-word">Kenya</span></div>
            <h3>Kiamugumo AA</h3>
            <p class="coffee-origin">Kirinyaga, Kenya</p>
            <div class="coffee-detail"><span>Farm / co-operative</span><strong>Kiamugumo Farmers Co-operative</strong></div>
            <div class="tasting"><span class="tasting-label">Tasting note</span><p>Blackcurrant, cane sugar, dry finish</p></div>
          </article>

          <article class="coffee-card">
            <div class="coffee-card-top"><span>02 / South America</span><span class="altitude-tag">1,680m</span></div>
            <div class="coffee-art art-colombia"><span class="art-index">COL / 02</span><span class="art-word">Colombia</span></div>
            <h3>Finca La Ilusión</h3>
            <p class="coffee-origin">Huila, Colombia</p>
            <div class="coffee-detail"><span>Farm / co-operative</span><strong>Finca La Ilusión</strong></div>
            <div class="tasting"><span class="tasting-label">Tasting note</span><p>Red apple, panela, soft cocoa</p></div>
          </article>

          <article class="coffee-card">
            <div class="coffee-card-top"><span>03 / East Africa</span><span class="altitude-tag">2,050m</span></div>
            <div class="coffee-art art-ethiopia"><span class="art-index">ETH / 03</span><span class="art-word">Ethiopia</span></div>
            <h3>Yirgacheffe Konga</h3>
            <p class="coffee-origin">Gedeb, Ethiopia</p>
            <div class="coffee-detail"><span>Farm / co-operative</span><strong>Konga Farmers Co-operative</strong></div>
            <div class="tasting"><span class="tasting-label">Tasting note</span><p>Jasmine, peach, bergamot</p></div>
          </article>

          <article class="coffee-card">
            <div class="coffee-card-top"><span>04 / Central America</span><span class="altitude-tag">1,420m</span></div>
            <div class="coffee-art art-honduras"><span class="art-index">HON / 04</span><span class="art-word">Honduras</span></div>
            <h3>Nueva Esperanza</h3>
            <p class="coffee-origin">Marcala, Honduras</p>
            <div class="coffee-detail"><span>Farm / co-operative</span><strong>Cooperativa Nueva Esperanza</strong></div>
            <div class="tasting"><span class="tasting-label">Tasting note</span><p>Toffee, walnut, dried fig</p></div>
          </article>
        </div>

        <div class="box-tail"><span><strong>In the box:</strong> four origins, tasting cards, and a better Tuesday.</span><a class="text-link" href="#plans">Choose your amount&nbsp; →</a></div>
      </div>
    </section>

    <section class="how-section" id="how" aria-labelledby="how-title">
      <div class="shell how-inner">
        <div class="how-intro">
          <div class="section-kicker">The Meridian method</div>
          <h2 id="how-title">Great coffee, without the homework.</h2>
          <p>We do the wandering and the roasting. You choose the lane, then let good coffee turn up like clockwork.</p>
        </div>
        <div class="steps-grid">
          <article class="step-card">
            <div class="step-number"><span>01 / Choose</span></div>
            <h3>Pick a roast profile</h3>
            <p>Tell us the kind of cup you reach for, and we will keep every delivery in that neighbourhood.</p>
            <div class="profile-switch" role="group" aria-label="Choose a roast profile">
              <button class="profile-button active" type="button" data-profile="light" aria-pressed="true">Light</button>
              <button class="profile-button" type="button" data-profile="balanced" aria-pressed="false">Balanced</button>
              <button class="profile-button" type="button" data-profile="deep" aria-pressed="false">Deep</button>
            </div>
            <p class="profile-status" id="profile-status" aria-live="polite">Light profile: bright, floral and full of lift.</p>
          </article>

          <article class="step-card">
            <div class="step-number"><span>02 / Receive</span></div>
            <h3>We post it every second Tuesday</h3>
            <p>Your coffee is roasted close to dispatch, packed with its field notes, and sent straight to your door.</p>
            <div class="mini-calendar"><span class="calendar-icon">14</span><span>On the way / every fortnight</span></div>
          </article>

          <article class="step-card">
            <div class="step-number"><span>03 / Stay in control</span></div>
            <h3>Pause or swap any time before the Friday cut-off</h3>
            <p>Going away or fancy a change? A couple of clicks is all it takes. No awkward emails, no lock-in.</p>
            <div class="cutoff-line">Friday cut-off</div>
          </article>
        </div>
      </div>
    </section>

    <section class="plans-section" id="plans" aria-labelledby="plans-title">
      <div class="shell plans-inner">
        <div class="center-heading">
          <div class="section-kicker">Set your rhythm</div>
          <h2 id="plans-title">Pick your fortnightly pour.</h2>
          <p>Enough for one, a pair, or the whole table. Every plan arrives with postage included and can be paused.</p>
        </div>
        <div class="plans-grid">
          <article class="plan-card" data-plan-card="Solo">
            <div class="plan-overline">For your mug</div>
            <h3>Solo</h3>
            <p class="plan-size">250g / roughly 15 cups</p>
            <div class="plan-price">£11 <small>/ fortnight</small></div>
            <ul class="plan-list">
              <li><span class="check">✓</span> Single-origin coffee</li>
              <li><span class="check">✓</span> Postage included</li>
              <li><span class="check">✓</span> Pause whenever you need</li>
            </ul>
            <button class="button button-secondary plan-button" type="button" data-plan="Solo">Choose Solo <span>↗</span></button>
          </article>

          <article class="plan-card featured" data-plan-card="Pair">
            <div class="plan-badge">Most people choose</div>
            <div class="plan-overline">For two good cups</div>
            <h3>Pair</h3>
            <p class="plan-size">500g / roughly 30 cups</p>
            <div class="plan-price">£19 <small>/ fortnight</small></div>
            <ul class="plan-list">
              <li><span class="check">✓</span> Single-origin coffee</li>
              <li><span class="check">✓</span> Postage included</li>
              <li><span class="check">✓</span> Pause whenever you need</li>
            </ul>
            <button class="button button-primary plan-button" type="button" data-plan="Pair">Choose Pair <span>↗</span></button>
          </article>

          <article class="plan-card" data-plan-card="Table">
            <div class="plan-overline">For a full table</div>
            <h3>Table</h3>
            <p class="plan-size">1kg / roughly 60 cups</p>
            <div class="plan-price">£34 <small>/ fortnight</small></div>
            <ul class="plan-list">
              <li><span class="check">✓</span> Single-origin coffee</li>
              <li><span class="check">✓</span> Postage included</li>
              <li><span class="check">✓</span> Pause whenever you need</li>
            </ul>
            <button class="button button-secondary plan-button" type="button" data-plan="Table">Choose Table <span>↗</span></button>
          </article>
        </div>
        <p class="plans-foot"><strong>Every plan includes postage.</strong> Change, pause or swap before the Friday cut-off.</p>
      </div>
    </section>

    <section class="voices-section" aria-labelledby="voices-title">
      <div class="shell voices-inner">
        <div class="voices-top">
          <div>
            <div class="section-kicker">Postcards from subscribers</div>
            <h2 id="voices-title">The good word, in their words.</h2>
          </div>
          <div class="voices-aside">No tasting exams. Just people who like having good coffee around.</div>
        </div>
        <div class="quote-grid">
          <figure class="quote-card">
            <div class="quote-mark">“</div>
            <blockquote>The cards make each delivery feel like a tiny holiday. Kiamugumo is the one I still talk about.</blockquote>
            <figcaption><span class="initials">ID</span><span class="person"><strong>Ines Duarte</strong><span>Bristol · subscriber for 2 years</span></span></figcaption>
          </figure>
          <figure class="quote-card">
            <div class="quote-mark">“</div>
            <blockquote>I used to forget to order beans. Now my coffee arrives on Tuesday and tastes like someone cared.</blockquote>
            <figcaption><span class="initials">TO</span><span class="person"><strong>Tom Okonkwo</strong><span>Leeds · subscriber for 8 months</span></span></figcaption>
          </figure>
          <figure class="quote-card">
            <div class="quote-mark">“</div>
            <blockquote>Three years in and I still look forward to the swap email. Never a stale bag, never a hard sell.</blockquote>
            <figcaption><span class="initials">RS</span><span class="person"><strong>Ruth Salinas</strong><span>Glasgow · subscriber for 3 years</span></span></figcaption>
          </figure>
        </div>
      </div>
    </section>

    <section class="faq-section" id="faq" aria-labelledby="faq-title">
      <div class="shell faq-inner">
        <div class="faq-side">
          <div class="section-kicker">The short answers</div>
          <h2 id="faq-title">Questions, answered plainly.</h2>
          <p>Subscriptions should make life easier, not give you another thing to manage. Here is the useful bit.</p>
          <a class="faq-contact" href="mailto:hello@meridianfieldnotes.co.uk">Still curious? Email a human</a>
        </div>
        <div class="faq-list" aria-label="Frequently asked questions">
          <div class="faq-item open">
            <button class="faq-question" type="button" aria-expanded="true" aria-controls="answer-away"><span>What happens if I am away?</span><span class="faq-plus" aria-hidden="true"></span></button>
            <div class="faq-answer" id="answer-away"><p>Pause your next box before the Friday cut-off and it will wait for you. You can also skip one delivery or swap your profile, then pick things back up whenever you are ready.</p></div>
          </div>
          <div class="faq-item">
            <button class="faq-question" type="button" aria-expanded="false" aria-controls="answer-grind"><span>Can I choose the grind?</span><span class="faq-plus" aria-hidden="true"></span></button>
            <div class="faq-answer" id="answer-grind"><p>Yes. Choose whole bean, filter, cafetière or espresso when you start, and change it any time before your next roast. We will print the brew guidance on the field note too.</p></div>
          </div>
          <div class="faq-item">
            <button class="faq-question" type="button" aria-expanded="false" aria-controls="answer-post"><span>Where do you post to?</span><span class="faq-plus" aria-hidden="true"></span></button>
            <div class="faq-answer" id="answer-post"><p>We post across the UK, from Sheffield to the Highlands and islands. Postage is already included in the price you see, so there are no delivery surprises at checkout.</p></div>
          </div>
          <div class="faq-item">
            <button class="faq-question" type="button" aria-expanded="false" aria-controls="answer-cancel"><span>How do I cancel?</span><span class="faq-plus" aria-hidden="true"></span></button>
            <div class="faq-answer" id="answer-cancel"><p>Use the cancellation link in your account before the Friday cut-off. There is no minimum term and no phone call to make — although we would love to know what we could do better.</p></div>
          </div>
        </div>
      </div>
    </section>

    <section class="closing-section" aria-labelledby="closing-title">
      <div class="shell closing-inner">
        <div class="closing-stamp">MF / 07<br>THE NEXT NOTE</div>
        <div>
          <div class="section-kicker">The next note is yours</div>
          <h2 id="closing-title">Make room for<br><em>better coffee.</em></h2>
        </div>
        <div class="closing-copy">
          <p>Choose your amount, tell us how you brew, and we will take care of the rest.</p>
          <a class="button button-light" href="#plans">Start a subscription <span>↗</span></a>
          <small class="closing-price">From £11 / fortnight · postage included</small>
        </div>
      </div>
    </section>
  </main>

  <footer class="site-footer">
    <div class="shell footer-main">
      <div class="footer-brand">
        <a class="brand brand-light" href="#top" aria-label="Meridian Field Notes home">
          <svg viewBox="0 0 36 36" fill="none" aria-hidden="true">
            <circle cx="18" cy="18" r="15" stroke="currentColor" stroke-width="1.4"></circle>
            <path d="M18 3v30M3 18h30M8.3 8.3c5.2 4.2 14.2 4.2 19.4 0M8.3 27.7c5.2-4.2 14.2-4.2 19.4 0" stroke="currentColor" stroke-width="1.1" opacity=".7"></path>
            <circle cx="18" cy="18" r="3.1" fill="var(--gold)"></circle>
          </svg>
          <span class="brand-word"><strong>MERIDIAN</strong><small>FIELD NOTES</small></span>
        </a>
        <p>A considered coffee subscription for curious cups, quiet mornings, and wherever the next good bean comes from.</p>
      </div>
      <div class="footer-links-col">
        <div class="footer-label">Find us</div>
        <a href="mailto:hello@meridianfieldnotes.co.uk">Contact</a>
        <a href="#delivery">Delivery</a>
        <a href="#terms">Terms</a>
      </div>
      <div>
        <div class="footer-label">Write to us</div>
        <address class="footer-address">Meridian Field Notes<br>14 Furnace Lane<br>Sheffield S3 8AA<br>United Kingdom</address>
      </div>
    </div>
    <div class="shell footer-bottom">
      <span>© 2024 Meridian Field Notes</span>
      <div class="footer-bottom-links"><a href="mailto:hello@meridianfieldnotes.co.uk">hello@meridianfieldnotes.co.uk</a><a href="#top">Back to top ↑</a></div>
    </div>
    <div class="shell footer-policies">
      <span id="delivery"><strong>Delivery:</strong> UK-wide, posted every second Tuesday with postage included.</span>
      <span id="terms"><strong>Terms:</strong> Pause, swap or cancel before the Friday cut-off.</span>
    </div>
  </footer>

  <div class="selection-toast" id="selection-toast" role="status" aria-live="polite"></div>

  <script>
    (function () {
      var profiles = {
        light: 'Light profile: bright, floral and full of lift.',
        balanced: 'Balanced profile: sweet, rounded and quietly complex.',
        deep: 'Deep profile: rich, chocolatey and wonderfully full-bodied.'
      };
      var profileButtons = document.querySelectorAll('[data-profile]');
      var profileStatus = document.getElementById('profile-status');

      profileButtons.forEach(function (button) {
        button.addEventListener('click', function () {
          profileButtons.forEach(function (item) {
            item.classList.remove('active');
            item.setAttribute('aria-pressed', 'false');
          });
          button.classList.add('active');
          button.setAttribute('aria-pressed', 'true');
          profileStatus.textContent = profiles[button.getAttribute('data-profile')];
        });
      });

      var faqItems = document.querySelectorAll('.faq-item');
      faqItems.forEach(function (item) {
        var question = item.querySelector('.faq-question');
        question.addEventListener('click', function () {
          var shouldOpen = !item.classList.contains('open');
          faqItems.forEach(function (otherItem) {
            otherItem.classList.remove('open');
            otherItem.querySelector('.faq-question').setAttribute('aria-expanded', 'false');
          });
          if (shouldOpen) {
            item.classList.add('open');
            question.setAttribute('aria-expanded', 'true');
          }
        });
      });

      var toast = document.getElementById('selection-toast');
      var toastTimer;
      document.querySelectorAll('[data-plan]').forEach(function (button) {
        button.addEventListener('click', function () {
          var plan = button.getAttribute('data-plan');
          document.querySelectorAll('[data-plan-card]').forEach(function (card) {
            card.classList.toggle('selected', card.getAttribute('data-plan-card') === plan);
          });
          toast.textContent = plan + ' is ready — choose your grind in the next step.';
          toast.classList.add('show');
          window.clearTimeout(toastTimer);
          toastTimer = window.setTimeout(function () {
            toast.classList.remove('show');
          }, 3600);
        });
      });
    }());
  </script>
</body>
</html>
```
