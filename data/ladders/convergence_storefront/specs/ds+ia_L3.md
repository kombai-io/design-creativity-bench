# Variant `ds+ia_L3` of the ledger listing, converging toward the lumen reference

`ledger` and `lumen` are two designs of the same page: the product detail page of a refurbished
camera marketplace. They were built to be as different as two designs of one page can be. This
task moves `ledger` a measured step TOWARD `lumen` along the visual language and information architecture only.

- **Hold the reusable components exactly.** The spec row, condition row, review entry and
  related line keep their current internal markup and layout. They may be moved, but not rebuilt.

- **Every change must be visible when the page loads.** The page is judged from a
  screenshot of its resting state, so nothing may be placed behind a click, a tab, an accordion or
  a hover. No modals, no carousels that hide images.
- **Keep every piece of content.** The same product, the same 5 images, the same 3 conditions, the
  same 8 specifications, the same 3 reviews and the same 4 related products survive every change.
  Content is never added or removed - only how it is built and where it sits.
- **Change nothing this task does not name.** Anything not mentioned stays exactly as the document
  below has it.


## The changes (6 change sets)

Apply every set below, in order.

### DS-1 - Repaint and retype: parchment and serif become near-white and one sans

The page runs on a warm parchment ground, dark warm brown-black text, a muted rust accent, a serif
family for prose and a monospace family for every number. Replace all of it.

- Page background -> `#f7f7f9`. Any inset or alternate surface -> `#ffffff`.
- Primary text -> `#111114`. Secondary/muted text -> `#6b6b76`.
- The rust/brick accent, everywhere it is used (the price, the selected condition, any emphasis)
  -> `#4f46e5`. Any tinted accent wash -> `#eef1fe`.
- Every hairline rule and table border colour -> `#e6e6ec`.
- Replace BOTH font families with this one stack, used for absolutely everything on the page -
  headings, prose, prices, spec values, ratings and dates alike:
  `"Inter","Segoe UI",system-ui,-apple-system,"Helvetica Neue",Arial,sans-serif`. No serif and no
  monospace survives anywhere.
- Small uppercase labels lose their wide letter-spacing and become `letter-spacing:.01em`.
  Headings take `letter-spacing:-.02em`.

Do not move, reorder or rebuild anything. This set changes only what things look like.

### IA-1 - Add the global header bar and widen the page

The document currently opens straight onto its breadcrumb, inside a single column capped at 860px
and centred.

- Insert a NEW full-width header bar as the first element of the page, above the breadcrumb: a
  wordmark on the left, three navigation links in the middle ("Cameras", "Lenses", "Sell your
  gear"), and a cart control on the right showing an item count. It spans the full window width,
  not the content column.
- Widen the content column from 860px to 1200px, still centred. Every block below inherits the new
  width.

Build the header from the visual vocabulary the document already uses - take its colours, fonts,
rules and spacing from the existing page. Add no new colour, font or radius. This is the first
thing in the document, so it is unavoidably in the first viewport.

### DS-2 - Separate surfaces with shadow instead of rules

The page currently separates everything with 1px hairlines: rules under the breadcrumb and each
section label, cell borders throughout the specifications table, rules between reviews and between
related lines.

Remove every one of those separator rules and borders. In their place, give each block that was
previously fenced by rules - the specifications table, each plate's caption block, the purchase
block, each review, each related line - a raised surface instead: `background:#ffffff` (or whatever
DS-1 set the surface colour to) with `box-shadow:0 1px 2px rgba(17,17,20,.05), 0 4px 12px
rgba(17,17,20,.06)`. The specifications table keeps its rows but loses every cell border and
gridline, becoming a plain block on that surface.

No border may remain as a separator anywhere on the page. Do not move, reorder or rebuild anything.

### IA-2 - Split the top of the page into gallery and buy box columns

Everything is currently stacked in one column, in the order: identity, specifications, plates,
purchase, reviews, related.

Restructure the TOP of the page into two side-by-side columns sitting directly beneath the
breadcrumb:
- LEFT column, about 58% of the width: the gallery - whatever the plates/images block currently is,
  moved here whole and unchanged internally.
- RIGHT column, about 42% of the width: a buy box holding, stacked in this order, the product name,
  the subtitle, the rating line, and then the entire purchase block (price, condition choices,
  stock line and the two actions) moved up from its current position lower down the page.

The specifications, reviews and related blocks stay in one full-width column below those two,
keeping their current relative order. Nothing about any component's internals changes, and no
colour, font, radius or spacing value is introduced. This rebuilds the first viewport completely.

### DS-3 - Round every corner and open the page up

- **Shape.** Every corner on the page becomes `border-radius:16px` - every surface, image, plate,
  button, control and input. Nothing square remains.
- **Type scale.** The page currently runs a small, tight scale. Raise it: body text -> `15px`, the
  product name -> `40px` with `font-weight:700`, section labels -> `13px`, and every value or
  price that is currently 12px or smaller -> `13px`.
- **Density.** Open the spacing out. Padding inside any surface -> `24px`. The gap between the six
  page blocks -> `48px`. The gap between rows inside a block -> `16px`. Line-height on body prose
  -> `1.6`.

Do not move, reorder or rebuild anything. This set changes only shape, scale and spacing.

### IA-3 - Re-lay the lower sections into grids and fix their order

Below the two columns, the remaining blocks are still full-width and stacked one item per line.

- Order them exactly: specifications, then reviews, then related products.
- The specifications block becomes a TWO-column grid, its pairs filling left-to-right across two
  columns instead of running one per line down the page.
- The reviews block becomes a TWO-up grid: two reviews on the first row, the third on the second.
- The related products block becomes a single row of four across.
- Give each of the three a section heading line above it, in whatever style the document already
  uses for its section labels.

Nothing about any component's internals changes, and no colour, font, radius or spacing value is
introduced. By this level the page above is compact enough that the top of the specifications grid
sits within the first viewport.

## The document to change (this is `ledger`)

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=1280">
<title>Fujinon X-T3 Body (Refurbished) — Ledger Optics</title>
<style>
  :root{
    --paper:#f3ece0;
    --inset:#e9e0cf;
    --ink:#221b14;
    --muted:#7b6b58;
    --rule:#cdbfa7;
    --rule-strong:#b6a488;
    --accent:#9d4a2c;
    --serif:"Iowan Old Style","Palatino Linotype",Palatino,"Book Antiqua",Georgia,"Times New Roman",serif;
    --mono:"SFMono-Regular",Menlo,Consolas,"DejaVu Sans Mono","Liberation Mono",monospace;
  }
  *{box-sizing:border-box;border-radius:0 !important;}
  html{background:var(--paper);}
  body{
    margin:0;
    background:var(--paper);
    color:var(--ink);
    font-family:var(--serif);
    font-size:14px;
    line-height:1.5;
    -webkit-font-smoothing:antialiased;
  }
  .sheet{
    width:860px;
    max-width:860px;
    margin:0 auto;
    padding:28px 0 60px;
  }
  /* ---------- generic bits ---------- */
  .mono{font-family:var(--mono);}
  .num{font-family:var(--mono);font-variant-numeric:tabular-nums;}
  .label{
    font-family:var(--mono);
    font-size:10px;
    text-transform:uppercase;
    letter-spacing:.18em;
    color:var(--muted);
  }
  hr.rule{
    border:0;
    border-top:1px solid var(--rule);
    margin:10px 0;
  }
  hr.rule-strong{
    border:0;
    border-top:1px solid var(--rule-strong);
    margin:10px 0;
  }
  .section{
    margin-top:26px;
  }
  .section-head{
    display:block;
    border-bottom:1px solid var(--rule-strong);
    padding-bottom:5px;
    margin:0 0 10px;
  }
  h2.section-title{
    margin:0;
    font-family:var(--mono);
    font-size:10px;
    font-weight:700;
    text-transform:uppercase;
    letter-spacing:.20em;
    color:var(--muted);
  }
  /* ---------- 1. masthead / identity ---------- */
  .breadcrumb{
    font-family:var(--mono);
    font-size:10.5px;
    letter-spacing:.10em;
    text-transform:uppercase;
    color:var(--muted);
    margin:0 0 8px;
  }
  .breadcrumb span{padding:0 6px;}
  .breadcrumb span:first-child{padding-left:0;}
  h1.product-name{
    font-family:var(--serif);
    font-size:23px;
    font-weight:600;
    letter-spacing:.005em;
    line-height:1.25;
    margin:12px 0 4px;
  }
  .subtitle{
    margin:0 0 8px;
    font-size:14px;
    font-style:italic;
    color:var(--muted);
  }
  .rating-line{
    font-family:var(--mono);
    font-size:12px;
    letter-spacing:.04em;
    margin:0;
    color:var(--ink);
  }
  .rating-line .sep{color:var(--rule-strong);padding:0 8px;}
  .rating-line .meta{color:var(--muted);}
  /* ---------- 2. specifications table ---------- */
  table.specs{
    width:100%;
    border-collapse:collapse;
    border:1px solid var(--rule-strong);
    background:var(--inset);
  }
  table.specs caption{
    caption-side:top;
    text-align:left;
    font-family:var(--mono);
    font-size:10px;
    letter-spacing:.16em;
    text-transform:uppercase;
    color:var(--muted);
    padding-bottom:5px;
  }
  table.specs th,
  table.specs td{
    border:1px solid var(--rule);
    padding:5px 9px;
    text-align:left;
    vertical-align:top;
  }
  table.specs thead th{
    background:#ded2bd;
    border-color:var(--rule-strong);
    font-family:var(--mono);
    font-size:9.5px;
    font-weight:700;
    text-transform:uppercase;
    letter-spacing:.18em;
    color:#5f5140;
    padding:6px 9px;
  }
  table.specs thead th.c-idx{width:38px;}
  table.specs th.spec-label{
    width:210px;
    font-family:var(--serif);
    font-size:13.5px;
    font-weight:600;
  }
  table.specs td.spec-idx{
    font-family:var(--mono);
    font-size:10.5px;
    color:var(--muted);
    text-align:right;
    width:38px;
  }
  table.specs td.spec-value{
    font-family:var(--mono);
    font-size:12px;
    letter-spacing:.01em;
    color:var(--ink);
  }
  /* ---------- 3. gallery ---------- */
  .plate{
    display:block;
    width:100%;
    border:1px solid var(--rule-strong);
    margin:0;
  }
  .plate svg{display:block;width:100%;height:300px;}
  .plate-caption{
    font-family:var(--mono);
    font-size:10.5px;
    letter-spacing:.08em;
    color:var(--muted);
    padding:5px 0 0;
    border-bottom:1px solid var(--rule);
    margin:0 0 14px;
    padding-bottom:9px;
  }
  .plate-caption b{
    color:var(--ink);
    font-weight:700;
    letter-spacing:.14em;
    text-transform:uppercase;
    margin-right:8px;
  }
  figure.gallery-item{margin:0 0 0;}
  /* ---------- 4. purchase block ---------- */
  .purchase{
    border:1px solid var(--rule-strong);
    background:var(--inset);
    padding:12px 14px 14px;
  }
  .price-line{
    display:flex;
    align-items:baseline;
    gap:10px;
    padding-bottom:9px;
    border-bottom:1px solid var(--rule);
  }
  .price-now{
    font-family:var(--mono);
    font-size:22px;
    font-weight:700;
    letter-spacing:-.01em;
    color:var(--accent);
  }
  .price-was{
    font-family:var(--mono);
    font-size:13px;
    color:var(--muted);
    text-decoration:line-through;
  }
  .price-save{
    font-family:var(--mono);
    font-size:10px;
    letter-spacing:.14em;
    text-transform:uppercase;
    color:var(--muted);
    margin-left:auto;
  }
  .condition-head{
    padding:9px 0 6px;
  }
  .condition-list{
    border-top:1px solid var(--rule);
    border-left:1px solid var(--rule);
    border-right:1px solid var(--rule);
    background:var(--paper);
  }
  /* condition row */
  .condition-row{
    display:flex;
    align-items:flex-start;
    gap:9px;
    width:100%;
    padding:8px 10px;
    border-bottom:1px solid var(--rule);
    cursor:pointer;
  }
  .condition-row input{
    -webkit-appearance:none;appearance:none;
    width:11px;height:11px;
    margin:4px 0 0;
    border:1px solid var(--muted);
    background:var(--paper);
    flex:0 0 auto;
  }
  .condition-row input:checked{
    background:var(--accent);
    border-color:var(--accent);
    box-shadow:inset 0 0 0 2px var(--paper);
  }
  .condition-body{flex:1 1 auto;min-width:0;}
  .condition-grade{
    font-family:var(--serif);
    font-size:13.5px;
    font-weight:600;
    line-height:1.2;
  }
  .condition-desc{
    font-size:12.5px;
    color:var(--muted);
    line-height:1.35;
    margin-top:2px;
  }
  .condition-price{
    font-family:var(--mono);
    font-size:13px;
    font-variant-numeric:tabular-nums;
    white-space:nowrap;
    padding-left:12px;
    text-align:right;
  }
  .condition-row input:checked ~ .condition-body .condition-grade{color:var(--accent);}
  .condition-row input:checked ~ .condition-price{color:var(--accent);font-weight:700;}
  .condition-row:has(input:checked){
    background:var(--inset);
    box-shadow:inset 3px 0 0 0 var(--accent);
  }
  .condition-tag{
    font-family:var(--mono);
    font-size:9px;
    letter-spacing:.16em;
    text-transform:uppercase;
    color:var(--accent);
    margin-left:8px;
    vertical-align:1px;
  }
  .stock-line{
    font-family:var(--mono);
    font-size:11.5px;
    letter-spacing:.04em;
    color:var(--ink);
    padding:10px 0 11px;
    border-bottom:1px solid var(--rule);
  }
  .stock-line .dot{
    display:inline-block;width:7px;height:7px;
    background:var(--accent);margin-right:7px;vertical-align:1px;
  }
  .stock-line em{color:var(--muted);font-style:italic;font-family:var(--serif);font-size:12.5px;}
  .actions{
    display:flex;
    gap:10px;
    padding-top:12px;
  }
  .btn{
    font-family:var(--mono);
    font-size:11px;
    letter-spacing:.20em;
    text-transform:uppercase;
    padding:10px 16px;
    border:1px solid var(--accent);
    background:var(--accent);
    color:#f5efe3;
    cursor:pointer;
    flex:1 1 auto;
  }
  .btn.secondary{
    background:transparent;
    color:var(--ink);
    border:1px solid var(--rule-strong);
    flex:0 0 190px;
  }
  /* ---------- 5. reviews ---------- */
  .reviews{
    border-top:1px solid var(--rule-strong);
  }
  /* review entry */
  .review-entry{
    padding:11px 0 12px;
    border-bottom:1px solid var(--rule);
  }
  .review-meta{
    display:flex;
    align-items:baseline;
    gap:10px;
    font-family:var(--mono);
    font-size:10.5px;
    letter-spacing:.08em;
    color:var(--muted);
    text-transform:uppercase;
  }
  .review-score{
    color:var(--ink);
    font-weight:700;
    border:1px solid var(--rule-strong);
    padding:1px 5px;
    letter-spacing:.04em;
  }
  .review-name{
    font-family:var(--serif);
    font-size:13px;
    font-style:normal;
    text-transform:none;
    letter-spacing:0;
    color:var(--ink);
    font-weight:600;
  }
  .review-date{margin-left:auto;}
  .review-title{
    font-family:var(--serif);
    font-size:14px;
    font-weight:600;
    margin:5px 0 2px;
  }
  .review-body{
    margin:0;
    font-size:13.5px;
    line-height:1.45;
    color:#3a2f24;
  }
  /* ---------- 6. related ---------- */
  .related-list{
    list-style:none;
    margin:0;
    padding:0;
    border-top:1px solid var(--rule-strong);
  }
  /* related line */
  .related-line{
    display:flex;
    align-items:baseline;
    gap:10px;
    padding:7px 0;
    border-bottom:1px solid var(--rule);
  }
  .related-idx{
    font-family:var(--mono);
    font-size:10px;
    color:var(--muted);
    width:26px;
    flex:0 0 26px;
  }
  .related-name{
    font-family:var(--serif);
    font-size:13.5px;
  }
  .related-dots{
    flex:1 1 auto;
    border-bottom:1px dotted var(--rule-strong);
    transform:translateY(-3px);
  }
  .related-price{
    font-family:var(--mono);
    font-size:12.5px;
    font-variant-numeric:tabular-nums;
  }
  .colophon{
    margin-top:26px;
    padding-top:8px;
    border-top:1px solid var(--rule-strong);
    font-family:var(--mono);
    font-size:9.5px;
    letter-spacing:.14em;
    text-transform:uppercase;
    color:var(--muted);
  }
</style>
</head>
<body>
<div class="sheet">

  <!-- 1. IDENTITY -->
  <p class="breadcrumb"><span>Ledger Optics</span>/<span>Cameras</span>/<span>Mirrorless bodies</span>/<span>Refurbished</span>/<span>Item 44-1180</span></p>
  <hr class="rule-strong">
  <h1 class="product-name">Aperion X-T3 Mirrorless Camera Body — Refurbished</h1>
  <p class="subtitle">26.1 MP APS-C body, factory-inspected and re-certified, single owner stock.</p>
  <p class="rating-line"><span class="num">4.6 / 5</span> from <span class="num">128</span> reviews<span class="sep">|</span><span class="meta">Stock no. <span class="num">44-1180</span> · listed <span class="num">2024-03-04</span></span></p>

  <!-- 2. SPECIFICATIONS -->
  <section class="section">
    <div class="section-head"><h2 class="section-title">Specifications</h2></div>
    <table class="specs">
      <caption>Table 1 — Verified at intake by bench technician (ref. TB-90).</caption>
      <thead>
        <tr>
          <th scope="col" class="c-idx">No.</th>
          <th scope="col">Specification</th>
          <th scope="col">Recorded value</th>
        </tr>
      </thead>
      <tbody>
        <!-- spec row -->
        <tr class="spec-row"><td class="spec-idx">01</td><th scope="row" class="spec-label">Sensor</th><td class="spec-value">APS-C X-Trans CMOS 4, 23.5 × 15.6 mm</td></tr>
        <!-- spec row -->
        <tr class="spec-row"><td class="spec-idx">02</td><th scope="row" class="spec-label">Lens mount</th><td class="spec-value">Aperion X-mount, metal, 17.7 mm flange</td></tr>
        <!-- spec row -->
        <tr class="spec-row"><td class="spec-idx">03</td><th scope="row" class="spec-label">Resolution</th><td class="spec-value">26.1 MP — 6240 × 4160 px</td></tr>
        <!-- spec row -->
        <tr class="spec-row"><td class="spec-idx">04</td><th scope="row" class="spec-label">ISO range</th><td class="spec-value">160 – 12800 (ext. 80 – 51200)</td></tr>
        <!-- spec row -->
        <tr class="spec-row"><td class="spec-idx">05</td><th scope="row" class="spec-label">Weight</th><td class="spec-value">539 g with battery and card</td></tr>
        <!-- spec row -->
        <tr class="spec-row"><td class="spec-idx">06</td><th scope="row" class="spec-label">Shutter count</th><td class="spec-value">18,420 actuations (rated 300,000)</td></tr>
        <!-- spec row -->
        <tr class="spec-row"><td class="spec-idx">07</td><th scope="row" class="spec-label">Included accessories</th><td class="spec-value">Body cap, NP-W126S battery, charger, strap</td></tr>
        <!-- spec row -->
        <tr class="spec-row"><td class="spec-idx">08</td><th scope="row" class="spec-label">Warranty</th><td class="spec-value">12 months, parts and labour, transferable</td></tr>
      </tbody>
    </table>
  </section>

  <!-- 3. GALLERY -->
  <section class="section">
    <div class="section-head"><h2 class="section-title">Plates — five views, as received</h2></div>

    <figure class="gallery-item">
      <div class="plate">
        <svg viewBox="0 0 860 300" preserveAspectRatio="none" role="img" aria-label="Front view of camera body">
          <rect width="860" height="300" fill="#6f6656"/>
          <rect x="300" y="80" width="260" height="150" fill="#3d3830"/>
          <circle cx="430" cy="155" r="52" fill="#2a2622"/>
          <circle cx="430" cy="155" r="30" fill="#585044"/>
          <rect x="300" y="60" width="90" height="24" fill="#4c4638"/>
        </svg>
      </div>
      <p class="plate-caption"><b>Plate 1</b> Front elevation, lens mount with body cap fitted.</p>
    </figure>

    <figure class="gallery-item">
      <div class="plate">
        <svg viewBox="0 0 860 300" preserveAspectRatio="none" role="img" aria-label="Rear view with screen">
          <rect width="860" height="300" fill="#8a7b63"/>
          <rect x="270" y="70" width="320" height="170" fill="#4a4235"/>
          <rect x="292" y="92" width="180" height="126" fill="#c9c0ab"/>
          <rect x="500" y="92" width="70" height="70" fill="#332e28"/>
          <rect x="500" y="176" width="70" height="42" fill="#332e28"/>
        </svg>
      </div>
      <p class="plate-caption"><b>Plate 2</b> Rear elevation, 3.0 in. tilting monitor, no delamination.</p>
    </figure>

    <figure class="gallery-item">
      <div class="plate">
        <svg viewBox="0 0 860 300" preserveAspectRatio="none" role="img" aria-label="Top plate with dials">
          <rect width="860" height="300" fill="#5c5b52"/>
          <rect x="180" y="120" width="500" height="70" fill="#37362f"/>
          <circle cx="270" cy="120" r="42" fill="#8d8471"/>
          <circle cx="430" cy="120" r="42" fill="#8d8471"/>
          <circle cx="590" cy="120" r="42" fill="#8d8471"/>
          <rect x="180" y="188" width="500" height="8" fill="#26251f"/>
        </svg>
      </div>
      <p class="plate-caption"><b>Plate 3</b> Top plate, three machined dials, engraving unworn.</p>
    </figure>

    <figure class="gallery-item">
      <div class="plate">
        <svg viewBox="0 0 860 300" preserveAspectRatio="none" role="img" aria-label="Port side detail">
          <rect width="860" height="300" fill="#9a8768"/>
          <rect x="0" y="150" width="860" height="150" fill="#7d6c52"/>
          <rect x="330" y="70" width="200" height="160" fill="#413a2d"/>
          <rect x="356" y="104" width="60" height="18" fill="#a49madd"/>
          <rect x="356" y="104" width="60" height="18" fill="#b3a68c"/>
          <rect x="356" y="138" width="60" height="18" fill="#b3a68c"/>
          <rect x="356" y="172" width="148" height="18" fill="#b3a68c"/>
        </svg>
      </div>
      <p class="plate-caption"><b>Plate 4</b> Port side, USB-C / micro-HDMI / mic, covers intact.</p>
    </figure>

    <figure class="gallery-item">
      <div class="plate">
        <svg viewBox="0 0 860 300" preserveAspectRatio="none" role="img" aria-label="Base plate and battery door">
          <rect width="860" height="300" fill="#43443f"/>
          <rect x="240" y="60" width="380" height="180" fill="#6b6c62"/>
          <rect x="270" y="90" width="120" height="120" fill="#2f302c"/>
          <circle cx="500" cy="150" r="26" fill="#2f302c"/>
          <rect x="240" y="232" width="380" height="8" fill="#8f9086"/>
        </svg>
      </div>
      <p class="plate-caption"><b>Plate 5</b> Base plate, tripod thread true, battery door latch firm.</p>
    </figure>
  </section>

  <!-- 4. PURCHASE -->
  <section class="section">
    <div class="section-head"><h2 class="section-title">Purchase</h2></div>
    <div class="purchase">
      <div class="price-line">
        <span class="price-now">£849.00</span>
        <span class="price-was">£1,199.00</span>
        <span class="price-save">You save £350.00 · 29% off list</span>
      </div>

      <div class="condition-head"><span class="label">Choose condition grade</span></div>

      <div class="condition-list">
        <!-- condition row -->
        <label class="condition-row">
          <input type="radio" name="condition" value="like-new">
          <span class="condition-body">
            <span class="condition-grade">Like new</span>
            <span class="condition-desc">No visible wear; original box, seals and full accessory kit present.</span>
          </span>
          <span class="condition-price">£929.00</span>
        </label>

        <!-- condition row -->
        <label class="condition-row">
          <input type="radio" name="condition" value="very-good" checked>
          <span class="condition-body">
            <span class="condition-grade">Very good<span class="condition-tag">Selected</span></span>
            <span class="condition-desc">Light marks on the base plate only; glass, screen and controls flawless.</span>
          </span>
          <span class="condition-price">£849.00</span>
        </label>

        <!-- condition row -->
        <label class="condition-row">
          <input type="radio" name="condition" value="good">
          <span class="condition-body">
            <span class="condition-grade">Good</span>
            <span class="condition-desc">Honest working wear on edges and grip; fully functional, generic accessories.</span>
          </span>
          <span class="condition-price">£769.00</span>
        </label>
      </div>

      <p class="stock-line"><span class="dot"></span>In stock — 3 units at this grade. <em>Dispatched from the Leeds workshop within one working day.</em></p>

      <div class="actions">
        <button type="button" class="btn">Add to basket</button>
        <button type="button" class="btn secondary">Save</button>
      </div>
    </div>
  </section>

  <!-- 5. REVIEWS -->
  <section class="section">
    <div class="section-head"><h2 class="section-title">Customer reviews — 3 of 128 shown</h2></div>
    <div class="reviews">

      <!-- review entry -->
      <article class="review-entry">
        <div class="review-meta">
          <span class="review-score num">4.5 / 5</span>
          <span class="review-name">Marianne Ostler</span>
          <span>Verified purchase</span>
          <span class="review-date num">2024-02-18</span>
        </div>
        <h3 class="review-title">Indistinguishable from new at half the outlay</h3>
        <p class="review-body">The body arrived with a shutter count under twenty thousand and not a single mark on the top plate. I have shot two weddings on it since and the metering has been faultless throughout.</p>
      </article>

      <!-- review entry -->
      <article class="review-entry">
        <div class="review-meta">
          <span class="review-score num">5.0 / 5</span>
          <span class="review-name">Devan Roy</span>
          <span>Verified purchase</span>
          <span class="review-date num">2024-01-29</span>
        </div>
        <h3 class="review-title">Packing and paperwork were exemplary</h3>
        <p class="review-body">Every accessory was itemised on the inspection sheet in the box, which made checking the contents a two-minute job. The grade description matched the item exactly, which is rarer than it should be.</p>
      </article>

      <!-- review entry -->
      <article class="review-entry">
        <div class="review-meta">
          <span class="review-score num">4.0 / 5</span>
          <span class="review-name">Priya Nandakumar</span>
          <span>Verified purchase</span>
          <span class="review-date num">2023-12-11</span>
        </div>
        <h3 class="review-title">Good value, though the battery is tired</h3>
        <p class="review-body">Optically and mechanically the camera is perfect and the sensor was spotless under a loupe. The supplied battery only holds around three hundred frames, so budget for a spare cell.</p>
      </article>

    </div>
  </section>

  <!-- 6. RELATED -->
  <section class="section">
    <div class="section-head"><h2 class="section-title">Related stock</h2></div>
    <ul class="related-list">
      <!-- related line -->
      <li class="related-line"><span class="related-idx num">01</span><span class="related-name">Aperion XF 35 mm f/1.4 R — refurbished</span><span class="related-dots"></span><span class="related-price">£379.00</span></li>
      <!-- related line -->
      <li class="related-line"><span class="related-idx num">02</span><span class="related-name">Aperion X-T2 body — very good grade</span><span class="related-dots"></span><span class="related-price">£549.00</span></li>
      <!-- related line -->
      <li class="related-line"><span class="related-idx num">03</span><span class="related-name">VG-XT3 vertical battery grip</span><span class="related-dots"></span><span class="related-price">£129.00</span></li>
      <!-- related line -->
      <li class="related-line"><span class="related-idx num">04</span><span class="related-name">Aperion XF 18–55 mm f/2.8–4 OIS kit lens</span><span class="related-dots"></span><span class="related-price">£249.00</span></li>
    </ul>
  </section>

  <p class="colophon">Ledger Optics · Workshop-inspected equipment · Prices include VAT · Sheet 44-1180 rev. C</p>

</div>
</body>
</html>
```
