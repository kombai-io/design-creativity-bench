# Variant `bindery__ia_L1` of the bindery weekly class schedule, converging toward the atrium reference

Reproduce the reference HTML document at the end of this file with the changes below applied,
and with nothing else changed. Every change is specified; there is nothing here for you to
choose. Apply the change sets in the order given.

Return one complete standalone HTML document.

## What must not change

- **The visual language stays bindery's own.** Do not change any colour, custom-property value, font-family, border-radius, shadow, or spacing/padding value anywhere on the page. Keep every `:root` custom property exactly as currently defined, keep the serif headings and the monospace data, keep the global `*{border-radius:0 !important}` reset, keep every border-based separator exactly as it is, and add no `box-shadow` anywhere.
- **Every change must be visible when the page loads.** This page is judged from a
  screenshot of its resting state, so a difference that appears only after a click, a hover, a
  scroll or a keystroke is not a change at all.
- **The content is identical.** The same eighteen classes and three bookings, the same days,
  times, durations, class names, instructors, rooms, spot counts and levels, the same studio name,
  week, summary figures, navigation items and filter options, word for word. Nothing added,
  nothing removed, no copy invented. This is the same page restyled and restructured, not a new
  page.
- **The build is identical.** One standalone HTML document with no external files - the reference
  loads none, and neither may you. Plain CSS in a `<style>` tag and plain JavaScript in a
  `<script>` tag. All three interactions (search filtering, level filtering, the Book toggle) keep
  working after your changes. Desktop width, about 1280px.


## The changes (1 change set)

This variant moves the information architecture toward the atrium reference. Apply every set below, in order.

### IA-1 - Replace the top tab bar with atrium's persistent left sidebar

Remove the horizontal tab bar (the four navigation items in one full-width row across the very
top of the page) entirely. In its place add a persistent LEFT sidebar, always visible, holding,
top to bottom: a studio-switcher control showing a round mark with the letters `LR` and the text
*Lantern Row* above the smaller text *Fremont St*; then the same four navigation items as a
VERTICAL list, each a full-width row with its visible text label, *Schedule* still marked active.

Restructure the page shell from one top-to-bottom column into a sidebar-plus-main layout: the
sidebar is a fixed 248px column on the left running the full page height, and everything else -
masthead, filter strip, schedule, bookings panel - moves into a main region that fills the
remaining width to its right, keeping its current top-to-bottom order.

Take every colour, font, border, radius, shadow and padding value in the new sidebar from what
this variant already uses elsewhere. This set adds no visual value of its own.

## Reference design (this is `bindery` - transcribe the changes above onto this document)

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Lantern Row Fitness — Weekly Schedule</title>
  <style>
    :root{
      --paper:#f7f1e4; --surface:#fffdf6; --surface-2:#efe6d2; --ink:#1f1a12; --ink-soft:#5c5142;
      --line:#2a2216; --line-soft:#c8b899; --accent:#9c3b18; --accent-tint:#f3ddd0;
      --level1:#2f5d3a; --level1-tint:#dfe9dc; --level2:#8a6510; --level2-tint:#f4e8c4;
      --level3:#7a1b23; --level3-tint:#f2d9d7;
      --serif:"Iowan Old Style","Palatino Linotype",Palatino,Georgia,"Times New Roman",serif;
      --mono:"SFMono-Regular",Consolas,"Liberation Mono",Menlo,monospace;
    }

    *{border-radius:0 !important}
    *,*::before,*::after{box-sizing:border-box}

    html{background:var(--paper)}
    body{
      margin:0;
      background:var(--paper);
      color:var(--ink);
      font-family:var(--serif);
      font-size:11.5px;
      line-height:1.35;
    }
    h1,h2,p{margin:0}
    h1,h2{
      font-family:var(--serif);
      font-weight:700;
      letter-spacing:.08em;
      text-transform:uppercase;
    }
    button,input,select{font:inherit}
    [hidden]{display:none !important}

    .page{
      width:calc(100% - 48px);
      max-width:1280px;
      min-width:1000px;
      margin:24px auto;
      background:var(--surface);
    }

    .tabbar{
      display:flex;
      align-items:stretch;
      height:44px;
      border-bottom:2px solid var(--line);
      background:var(--surface);
    }
    .tab-item{
      display:flex;
      align-items:center;
      padding:0 17px;
      color:var(--ink-soft);
      font-family:var(--serif);
      font-size:11px;
      font-weight:700;
      letter-spacing:.08em;
      line-height:1;
      text-decoration:none;
      text-transform:uppercase;
      white-space:nowrap;
    }
    .tab-item.active{
      color:var(--accent);
      border-bottom:3px solid var(--accent);
      margin-bottom:-2px;
    }

    .masthead{
      display:flex;
      align-items:flex-end;
      justify-content:space-between;
      min-height:78px;
      padding:16px 8px 13px;
      border-bottom:1px solid var(--line-soft);
      background:var(--surface);
    }
    .studio-name{
      font-size:22px;
      line-height:1.05;
    }
    .studio-meta{
      margin-top:5px;
      color:var(--ink-soft);
      font-size:11.5px;
      letter-spacing:.02em;
    }
    .studio-location{font-weight:700;color:var(--ink)}
    .meta-divider{padding:0 5px;color:var(--line-soft)}
    .summary{
      display:flex;
      align-items:baseline;
      white-space:nowrap;
      color:var(--ink-soft);
      font-size:10.5px;
    }
    .metric-label{
      font-weight:700;
      letter-spacing:.08em;
      text-transform:uppercase;
    }
    .metric-value{
      color:var(--ink);
      font-family:var(--mono);
      font-size:11px;
      font-weight:700;
    }
    .summary-separator{
      padding:0 10px;
      color:var(--line);
      font-family:var(--serif);
    }

    .filter-strip{
      display:grid;
      grid-template-columns:2fr 1fr 1fr;
      border-bottom:1px solid var(--line);
      background:var(--surface);
    }
    .filter-cell{
      display:flex;
      align-items:center;
      min-height:52px;
      padding:8px;
      border-right:1px solid var(--line-soft);
      background:var(--surface);
    }
    .filter-label{
      flex:0 0 auto;
      margin-right:10px;
      color:var(--ink-soft);
      font-family:var(--serif);
      font-size:10.5px;
      font-weight:700;
      letter-spacing:.08em;
      text-transform:uppercase;
    }
    .search-input,
    .filter-select{
      min-width:0;
      height:30px;
      border:2px solid var(--line);
      background:var(--surface);
      color:var(--ink);
      font-family:var(--mono);
      font-size:11px;
      line-height:1.2;
      padding:4px 8px;
    }
    .search-input{flex:1 1 auto;width:100%}
    .filter-select{flex:1 1 auto;width:100%;cursor:default}
    .search-input::placeholder{color:var(--ink-soft);opacity:1}

    .schedule-table{
      display:grid;
      grid-template-columns:7% 7.5% 23% 18% 12% 12% 9.5% 11%;
      width:100%;
      background:var(--surface);
    }
    .table-header,
    .class-row{
      grid-column:1 / -1;
      display:grid;
      grid-template-columns:7% 7.5% 23% 18% 12% 12% 9.5% 11%;
    }
    .table-header{
      height:32px;
      padding:0 8px;
      border-bottom:2px solid var(--line);
      background:var(--surface);
      color:var(--ink-soft);
      font-family:var(--serif);
      font-size:10px;
      font-weight:700;
      letter-spacing:.08em;
      text-transform:uppercase;
    }
    .header-cell{
      display:flex;
      align-items:center;
      min-width:0;
      padding:0 8px;
      white-space:nowrap;
    }
    .day-group{
      grid-column:1 / -1;
      height:28px;
      padding:5px 8px 4px;
      border-top:2px solid var(--line);
      border-bottom:1px solid var(--line);
      background:var(--surface);
      color:var(--ink);
      font-family:var(--serif);
      font-size:11.5px;
      font-weight:700;
      letter-spacing:.08em;
      line-height:1.2;
      text-transform:uppercase;
    }
    .class-row{
      height:30px;
      min-height:30px;
      padding:2px 8px;
      border-bottom:1px solid var(--line-soft);
      align-items:center;
      background:var(--surface);
    }
    .class-row.alt{background:var(--surface-2)}
    .cell{
      display:flex;
      align-items:center;
      min-width:0;
      overflow:hidden;
      white-space:nowrap;
      text-overflow:ellipsis;
    }
    .time,.duration,.spots{
      font-family:var(--mono);
      font-size:11px;
    }
    .time,.duration{color:var(--ink)}
    .spots{color:var(--ink-soft)}
    .spots.full{color:var(--level3);font-weight:700}
    .level-badge{
      display:inline-block;
      border:1.5px solid currentColor;
      background:transparent;
      padding:1px 6px;
      font-family:var(--serif);
      font-size:10.5px;
      line-height:1.1;
      text-transform:uppercase;
      white-space:nowrap;
    }
    .level-1{color:var(--level1)}
    .level-2{color:var(--level2)}
    .level-3{color:var(--level3)}
    .book-button{
      width:100%;
      max-width:118px;
      height:23px;
      border:1.5px solid var(--line);
      background:transparent;
      color:var(--ink);
      font-family:var(--serif);
      font-size:10.5px;
      font-weight:700;
      line-height:1;
      padding:2px 6px;
      white-space:nowrap;
      cursor:pointer;
    }

    .bookings-panel{
      border-top:2px solid var(--line);
      background:var(--surface);
    }
    .bookings-title{
      min-height:38px;
      padding:10px 8px 8px;
      border-bottom:1px solid var(--line);
      font-size:14px;
      line-height:1.1;
    }
    .booking-table{
      width:100%;
      border-collapse:collapse;
      border-spacing:0;
      table-layout:fixed;
      background:var(--surface);
    }
    .booking-table col:first-child{width:82%}
    .booking-table col:last-child{width:18%}
    .booking-table tr{height:38px}
    .booking-table tr:nth-child(even){background:var(--surface-2)}
    .booking-table td{
      padding:5px 8px;
      border-bottom:1px solid var(--line-soft);
      vertical-align:middle;
    }
    .booking-class{
      color:var(--ink);
      font-size:11.5px;
      font-weight:700;
    }
    .booking-when{
      margin-top:1px;
      color:var(--ink-soft);
      font-family:var(--mono);
      font-size:10.5px;
    }
    .booking-status{
      font-family:var(--serif);
      font-size:10.5px;
      font-weight:700;
      letter-spacing:.08em;
      text-transform:uppercase;
      white-space:nowrap;
    }
    .status-confirmed{color:var(--level1)}
    .status-waitlist{color:var(--level2)}
  </style>
</head>
<body>
  <main class="page">
    <nav class="tabbar" aria-label="Primary navigation">
      <span class="tab-item active" aria-current="page">Schedule</span>
      <span class="tab-item">Bookings</span>
      <span class="tab-item">Instructors</span>
      <span class="tab-item">Membership</span>
    </nav>

    <header class="masthead">
      <div class="studio-block">
        <h1 class="studio-name">Lantern Row Fitness</h1>
        <p class="studio-meta"><span class="studio-location">Fremont St</span><span class="meta-divider">·</span><span>2-8 March 2026</span></p>
      </div>
      <div class="summary" aria-label="Weekly summary">
        <span class="metric"><span class="metric-label">Classes this week:</span> <span class="metric-value">18</span></span>
        <span class="summary-separator" aria-hidden="true">·</span>
        <span class="metric"><span class="metric-label">Your bookings:</span> <span class="metric-value">3</span></span>
        <span class="summary-separator" aria-hidden="true">·</span>
        <span class="metric"><span class="metric-label">Spots remaining:</span> <span class="metric-value">142</span></span>
      </div>
    </header>

    <form class="filter-strip" aria-label="Class filters" onsubmit="return false">
      <div class="filter-cell">
        <label class="filter-label" for="class-search">Search</label>
        <input class="search-input" id="class-search" type="search" placeholder="Search classes or instructors" autocomplete="off">
      </div>
      <div class="filter-cell">
        <label class="filter-label" for="studio-select">Studio</label>
        <select class="filter-select" id="studio-select">
          <option selected>Fremont St</option>
          <option>Alder Way</option>
          <option>Quay North</option>
        </select>
      </div>
      <div class="filter-cell">
        <label class="filter-label" for="level-select">Level</label>
        <select class="filter-select" id="level-select">
          <option value="all" selected>All levels</option>
          <option value="Level 1">Level 1</option>
          <option value="Level 2">Level 2</option>
          <option value="Level 3">Level 3</option>
        </select>
      </div>
    </form>

    <section class="schedule-table" role="table" aria-label="Weekly class schedule">
      <div class="table-header" role="row">
        <div class="header-cell" role="columnheader">Time</div>
        <div class="header-cell" role="columnheader">Duration</div>
        <div class="header-cell" role="columnheader">Class</div>
        <div class="header-cell" role="columnheader">Instructor</div>
        <div class="header-cell" role="columnheader">Room</div>
        <div class="header-cell" role="columnheader">Spots</div>
        <div class="header-cell" role="columnheader">Level</div>
        <div class="header-cell" role="columnheader">Book</div>
      </div>

      <div class="day-group" data-day-group="mon-2" role="row">Mon 2 Mar</div>
      <div class="class-row" data-day="mon-2" data-class-name="Sunrise Conditioning" data-instructor="Nadia Okonjo" data-level="Level 3" role="row">
        <div class="cell time" role="cell">06:30</div>
        <div class="cell duration" role="cell">45 min</div>
        <div class="cell" role="cell">Sunrise Conditioning</div>
        <div class="cell" role="cell">Nadia Okonjo</div>
        <div class="cell" role="cell">Studio A</div>
        <div class="cell spots" role="cell">4 spots left</div>
        <div class="cell" role="cell"><span class="level-badge level-3">Level 3</span></div>
        <div class="cell" role="cell"><button class="book-button" type="button" data-full="false" data-selected="false">Book</button></div>
      </div>
      <div class="class-row alt" data-day="mon-2" data-class-name="Express Core" data-instructor="Tomas Reiner" data-level="Level 2" role="row">
        <div class="cell time" role="cell">12:15</div>
        <div class="cell duration" role="cell">30 min</div>
        <div class="cell" role="cell">Express Core</div>
        <div class="cell" role="cell">Tomas Reiner</div>
        <div class="cell" role="cell">Studio B</div>
        <div class="cell spots" role="cell">9 spots left</div>
        <div class="cell" role="cell"><span class="level-badge level-2">Level 2</span></div>
        <div class="cell" role="cell"><button class="book-button" type="button" data-full="false" data-selected="false">Book</button></div>
      </div>
      <div class="class-row" data-day="mon-2" data-class-name="Barbell Foundations" data-instructor="Priya Raman" data-level="Level 2" role="row">
        <div class="cell time" role="cell">18:00</div>
        <div class="cell duration" role="cell">60 min</div>
        <div class="cell" role="cell">Barbell Foundations</div>
        <div class="cell" role="cell">Priya Raman</div>
        <div class="cell" role="cell">Platform</div>
        <div class="cell spots" role="cell">2 spots left</div>
        <div class="cell" role="cell"><span class="level-badge level-2">Level 2</span></div>
        <div class="cell" role="cell"><button class="book-button" type="button" data-full="false" data-selected="false">Book</button></div>
      </div>

      <div class="day-group" data-day-group="tue-3" role="row">Tue 3 Mar</div>
      <div class="class-row alt" data-day="tue-3" data-class-name="Vinyasa Flow" data-instructor="Marta Lindqvist" data-level="Level 1" role="row">
        <div class="cell time" role="cell">07:00</div>
        <div class="cell duration" role="cell">60 min</div>
        <div class="cell" role="cell">Vinyasa Flow</div>
        <div class="cell" role="cell">Marta Lindqvist</div>
        <div class="cell" role="cell">Studio C</div>
        <div class="cell spots" role="cell">11 spots left</div>
        <div class="cell" role="cell"><span class="level-badge level-1">Level 1</span></div>
        <div class="cell" role="cell"><button class="book-button" type="button" data-full="false" data-selected="false">Book</button></div>
      </div>
      <div class="class-row" data-day="tue-3" data-class-name="Kettlebell Circuit" data-instructor="Dmitri Kovac" data-level="Level 3" role="row">
        <div class="cell time" role="cell">17:30</div>
        <div class="cell duration" role="cell">45 min</div>
        <div class="cell" role="cell">Kettlebell Circuit</div>
        <div class="cell" role="cell">Dmitri Kovac</div>
        <div class="cell" role="cell">Platform</div>
        <div class="cell spots full" role="cell">Full</div>
        <div class="cell" role="cell"><span class="level-badge level-3">Level 3</span></div>
        <div class="cell" role="cell"><button class="book-button" type="button" data-full="true" data-selected="false">Join waitlist</button></div>
      </div>
      <div class="class-row alt" data-day="tue-3" data-class-name="Restorative Yin" data-instructor="Marta Lindqvist" data-level="Level 1" role="row">
        <div class="cell time" role="cell">19:00</div>
        <div class="cell duration" role="cell">75 min</div>
        <div class="cell" role="cell">Restorative Yin</div>
        <div class="cell" role="cell">Marta Lindqvist</div>
        <div class="cell" role="cell">Studio C</div>
        <div class="cell spots" role="cell">8 spots left</div>
        <div class="cell" role="cell"><span class="level-badge level-1">Level 1</span></div>
        <div class="cell" role="cell"><button class="book-button" type="button" data-full="false" data-selected="false">Book</button></div>
      </div>

      <div class="day-group" data-day-group="wed-4" role="row">Wed 4 Mar</div>
      <div class="class-row" data-day="wed-4" data-class-name="Sunrise Conditioning" data-instructor="Nadia Okonjo" data-level="Level 3" role="row">
        <div class="cell time" role="cell">06:30</div>
        <div class="cell duration" role="cell">45 min</div>
        <div class="cell" role="cell">Sunrise Conditioning</div>
        <div class="cell" role="cell">Nadia Okonjo</div>
        <div class="cell" role="cell">Studio A</div>
        <div class="cell spots" role="cell">6 spots left</div>
        <div class="cell" role="cell"><span class="level-badge level-3">Level 3</span></div>
        <div class="cell" role="cell"><button class="book-button" type="button" data-full="false" data-selected="false">Book</button></div>
      </div>
      <div class="class-row alt" data-day="wed-4" data-class-name="Mobility Lab" data-instructor="Tomas Reiner" data-level="Level 1" role="row">
        <div class="cell time" role="cell">12:15</div>
        <div class="cell duration" role="cell">45 min</div>
        <div class="cell" role="cell">Mobility Lab</div>
        <div class="cell" role="cell">Tomas Reiner</div>
        <div class="cell" role="cell">Studio B</div>
        <div class="cell spots" role="cell">14 spots left</div>
        <div class="cell" role="cell"><span class="level-badge level-1">Level 1</span></div>
        <div class="cell" role="cell"><button class="book-button" type="button" data-full="false" data-selected="false">Book</button></div>
      </div>
      <div class="class-row" data-day="wed-4" data-class-name="Sprint Intervals" data-instructor="Dmitri Kovac" data-level="Level 3" role="row">
        <div class="cell time" role="cell">18:15</div>
        <div class="cell duration" role="cell">60 min</div>
        <div class="cell" role="cell">Sprint Intervals</div>
        <div class="cell" role="cell">Dmitri Kovac</div>
        <div class="cell" role="cell">Track</div>
        <div class="cell spots" role="cell">3 spots left</div>
        <div class="cell" role="cell"><span class="level-badge level-3">Level 3</span></div>
        <div class="cell" role="cell"><button class="book-button" type="button" data-full="false" data-selected="false">Book</button></div>
      </div>

      <div class="day-group" data-day-group="thu-5" role="row">Thu 5 Mar</div>
      <div class="class-row alt" data-day="thu-5" data-class-name="Power Pilates" data-instructor="Chidi Balogun" data-level="Level 2" role="row">
        <div class="cell time" role="cell">07:00</div>
        <div class="cell duration" role="cell">60 min</div>
        <div class="cell" role="cell">Power Pilates</div>
        <div class="cell" role="cell">Chidi Balogun</div>
        <div class="cell" role="cell">Studio B</div>
        <div class="cell spots" role="cell">5 spots left</div>
        <div class="cell" role="cell"><span class="level-badge level-2">Level 2</span></div>
        <div class="cell" role="cell"><button class="book-button" type="button" data-full="false" data-selected="false">Book</button></div>
      </div>
      <div class="class-row" data-day="thu-5" data-class-name="Barbell Foundations" data-instructor="Priya Raman" data-level="Level 2" role="row">
        <div class="cell time" role="cell">17:30</div>
        <div class="cell duration" role="cell">60 min</div>
        <div class="cell" role="cell">Barbell Foundations</div>
        <div class="cell" role="cell">Priya Raman</div>
        <div class="cell" role="cell">Platform</div>
        <div class="cell spots" role="cell">7 spots left</div>
        <div class="cell" role="cell"><span class="level-badge level-2">Level 2</span></div>
        <div class="cell" role="cell"><button class="book-button" type="button" data-full="false" data-selected="false">Book</button></div>
      </div>
      <div class="class-row alt" data-day="thu-5" data-class-name="Evening Stretch" data-instructor="Marta Lindqvist" data-level="Level 1" role="row">
        <div class="cell time" role="cell">20:00</div>
        <div class="cell duration" role="cell">30 min</div>
        <div class="cell" role="cell">Evening Stretch</div>
        <div class="cell" role="cell">Marta Lindqvist</div>
        <div class="cell" role="cell">Studio C</div>
        <div class="cell spots" role="cell">16 spots left</div>
        <div class="cell" role="cell"><span class="level-badge level-1">Level 1</span></div>
        <div class="cell" role="cell"><button class="book-button" type="button" data-full="false" data-selected="false">Book</button></div>
      </div>

      <div class="day-group" data-day-group="fri-6" role="row">Fri 6 Mar</div>
      <div class="class-row" data-day="fri-6" data-class-name="Sunrise Conditioning" data-instructor="Nadia Okonjo" data-level="Level 3" role="row">
        <div class="cell time" role="cell">06:30</div>
        <div class="cell duration" role="cell">45 min</div>
        <div class="cell" role="cell">Sunrise Conditioning</div>
        <div class="cell" role="cell">Nadia Okonjo</div>
        <div class="cell" role="cell">Studio A</div>
        <div class="cell spots full" role="cell">Full</div>
        <div class="cell" role="cell"><span class="level-badge level-3">Level 3</span></div>
        <div class="cell" role="cell"><button class="book-button" type="button" data-full="true" data-selected="false">Join waitlist</button></div>
      </div>
      <div class="class-row alt" data-day="fri-6" data-class-name="Express Core" data-instructor="Tomas Reiner" data-level="Level 2" role="row">
        <div class="cell time" role="cell">12:15</div>
        <div class="cell duration" role="cell">30 min</div>
        <div class="cell" role="cell">Express Core</div>
        <div class="cell" role="cell">Tomas Reiner</div>
        <div class="cell" role="cell">Studio B</div>
        <div class="cell spots" role="cell">12 spots left</div>
        <div class="cell" role="cell"><span class="level-badge level-2">Level 2</span></div>
        <div class="cell" role="cell"><button class="book-button" type="button" data-full="false" data-selected="false">Book</button></div>
      </div>
      <div class="class-row" data-day="fri-6" data-class-name="Kettlebell Circuit" data-instructor="Dmitri Kovac" data-level="Level 3" role="row">
        <div class="cell time" role="cell">18:00</div>
        <div class="cell duration" role="cell">45 min</div>
        <div class="cell" role="cell">Kettlebell Circuit</div>
        <div class="cell" role="cell">Dmitri Kovac</div>
        <div class="cell" role="cell">Platform</div>
        <div class="cell spots" role="cell">6 spots left</div>
        <div class="cell" role="cell"><span class="level-badge level-3">Level 3</span></div>
        <div class="cell" role="cell"><button class="book-button" type="button" data-full="false" data-selected="false">Book</button></div>
      </div>

      <div class="day-group" data-day-group="sat-7" role="row">Sat 7 Mar</div>
      <div class="class-row alt" data-day="sat-7" data-class-name="Long Ride" data-instructor="Priya Raman" data-level="Level 2" role="row">
        <div class="cell time" role="cell">08:00</div>
        <div class="cell duration" role="cell">90 min</div>
        <div class="cell" role="cell">Long Ride</div>
        <div class="cell" role="cell">Priya Raman</div>
        <div class="cell" role="cell">Cycle Room</div>
        <div class="cell spots" role="cell">4 spots left</div>
        <div class="cell" role="cell"><span class="level-badge level-2">Level 2</span></div>
        <div class="cell" role="cell"><button class="book-button" type="button" data-full="false" data-selected="false">Book</button></div>
      </div>
      <div class="class-row" data-day="sat-7" data-class-name="Vinyasa Flow" data-instructor="Marta Lindqvist" data-level="Level 1" role="row">
        <div class="cell time" role="cell">10:30</div>
        <div class="cell duration" role="cell">60 min</div>
        <div class="cell" role="cell">Vinyasa Flow</div>
        <div class="cell" role="cell">Marta Lindqvist</div>
        <div class="cell" role="cell">Studio C</div>
        <div class="cell spots" role="cell">9 spots left</div>
        <div class="cell" role="cell"><span class="level-badge level-1">Level 1</span></div>
        <div class="cell" role="cell"><button class="book-button" type="button" data-full="false" data-selected="false">Book</button></div>
      </div>

      <div class="day-group" data-day-group="sun-8" role="row">Sun 8 Mar</div>
      <div class="class-row alt" data-day="sun-8" data-class-name="Recovery Mobility" data-instructor="Chidi Balogun" data-level="Level 1" role="row">
        <div class="cell time" role="cell">09:30</div>
        <div class="cell duration" role="cell">60 min</div>
        <div class="cell" role="cell">Recovery Mobility</div>
        <div class="cell" role="cell">Chidi Balogun</div>
        <div class="cell" role="cell">Studio A</div>
        <div class="cell spots" role="cell">13 spots left</div>
        <div class="cell" role="cell"><span class="level-badge level-1">Level 1</span></div>
        <div class="cell" role="cell"><button class="book-button" type="button" data-full="false" data-selected="false">Book</button></div>
      </div>
    </section>

    <section class="bookings-panel" aria-labelledby="your-bookings-title">
      <h2 class="bookings-title" id="your-bookings-title">Your bookings</h2>
      <table class="booking-table" aria-label="Your bookings">
        <colgroup><col><col></colgroup>
        <tbody>
          <tr>
            <td><div class="booking-class">Barbell Foundations</div><div class="booking-when">Mon 2 Mar, 18:00</div></td>
            <td class="booking-status status-confirmed">Confirmed</td>
          </tr>
          <tr>
            <td><div class="booking-class">Mobility Lab</div><div class="booking-when">Wed 4 Mar, 12:15</div></td>
            <td class="booking-status status-confirmed">Confirmed</td>
          </tr>
          <tr>
            <td><div class="booking-class">Long Ride</div><div class="booking-when">Sat 7 Mar, 08:00</div></td>
            <td class="booking-status status-waitlist">Waitlist #2</td>
          </tr>
        </tbody>
      </table>
    </section>
  </main>

  <script>
    (function(){
      var searchInput = document.getElementById('class-search');
      var levelSelect = document.getElementById('level-select');
      var rows = Array.prototype.slice.call(document.querySelectorAll('.class-row'));
      var groups = Array.prototype.slice.call(document.querySelectorAll('.day-group'));

      function applyFilters(){
        var term = searchInput.value.trim().toLowerCase();
        var selectedLevel = levelSelect.value;
        rows.forEach(function(row){
          var classMatch = row.dataset.className.toLowerCase().indexOf(term) !== -1;
          var instructorMatch = row.dataset.instructor.toLowerCase().indexOf(term) !== -1;
          var levelMatch = selectedLevel === 'all' || row.dataset.level === selectedLevel;
          row.hidden = !(levelMatch && (term === '' || classMatch || instructorMatch));
        });
        groups.forEach(function(group){
          var dayRows = rows.filter(function(row){ return row.dataset.day === group.dataset.dayGroup; });
          group.hidden = !dayRows.some(function(row){ return !row.hidden; });
        });
      }

      searchInput.addEventListener('input', applyFilters);
      levelSelect.addEventListener('change', applyFilters);

      document.querySelectorAll('.book-button').forEach(function(button){
        button.addEventListener('click', function(){
          var full = button.dataset.full === 'true';
          var selected = button.dataset.selected === 'true';
          button.dataset.selected = selected ? 'false' : 'true';
          button.textContent = selected ? (full ? 'Join waitlist' : 'Book') : (full ? 'Waitlisted' : 'Booked');
        });
      });
    }());
  </script>
</body>
</html>
```
