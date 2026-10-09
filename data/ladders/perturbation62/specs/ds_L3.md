# Variant `case62__ds_L3` of the Ridgewell staff-access screen

Reproduce the reference HTML document at the end of this file with the changes below applied, and
with nothing else changed. Every change is specified; there is nothing here for you to choose.
Apply the change sets in the order given.

Return one complete standalone HTML document.

## What must not change

- **The reusable components are untouched.** The staff row, the role choice button and
  the permission row each keep the internal layout the reference gives them: the roster stays a
  four-column table with its header row, the role choice stays a centred stack with its radio in
  the corner, and the permission cell stays a 20px circle holding `✓` or `—`. Each shows exactly
  what it shows now and hides exactly what it hides now, all five roles included. The same controls
  behave the same way - a staff row opens the drawer, a role choice sets the pending role, the
  permission cells are read-only, and `Apply role` applies immediately with no confirmation. The
  drawer stays a right-hand overlay panel with its backdrop and slide transition.
- **The information architecture is untouched.** The same regions in the same order:
  sidebar on the left, then main with its header, its page heading block and the staff roster; and
  the drawer holding identity, current role, the comparison grid and a footer. The roster stays a
  flat list of seven, the permissions a flat list of twelve, the roles a flat row of five. Nothing
  moves between regions, no region appears or disappears, and everything visible on load stays
  visible on load.
- **The content is identical.** The same people, employee ids, emails, roles, locations,
  sign-in dates, permission labels, headings and body copy, word for word. No records added or
  removed, no new copy invented. This is the same screen redesigned, not a new screen.
- **The build is identical.** One standalone HTML document loading the same Tailwind browser CDN
  script the reference loads, with the same `<style>` block approach and the same inline
  `<script>`. Do not switch to a stylesheet, a build step or a framework - a change of technique
  would register as a design difference in its own right.
- **The `data-kid` and `data-name` attributes stay on the elements that carry them**, and any
  element you add carries neither. Where an element moves, its attributes move with it.
- **Everything keeps working.** Selecting a role re-renders the detail, the counts stay correct,
  and reassignment still moves a person between roles. Desktop width, about 1280px.


## The changes (3 change sets)

This variant moves the visual language. Apply every set below, in order.

### DS-1 - Re-skin: indigo accent, cool neutrals

The screen is built on a green-tinted neutral family with a teal accent and a rust secondary,
declared as custom properties on `.ridgewell-app`. Replace the values. Keep the property NAMES
exactly as they are - `--teal` and `--rust` stay `--teal` and `--rust` even though they no longer
name their colour, because renaming them means touching every reference for nothing.

1. **Tokens.** In the `<style>` block, replace each custom property value:

   | token | from | to |
   | --- | --- | --- |
   | `--canvas` | `#eef2ee` | `#eeeff4` |
   | `--paper` | `#fcfbf8` | `#fbfbfd` |
   | `--white` | `#fffefa` | `#fdfdff` |
   | `--sidebar` | `#edf3ee` | `#edeef5` |
   | `--ink` | `#24363a` | `#2b2a3c` |
   | `--muted` | `#748287` | `#7a7890` |
   | `--line` | `#dce6df` | `#dedde8` |
   | `--line-soft` | `#e9efea` | `#eaeaf1` |
   | `--teal` | `#1d7472` | `#4a3fa0` |
   | `--teal-deep` | `#155e61` | `#372c85` |
   | `--teal-wash` | `#e4f0eb` | `#e8e6f4` |
   | `--sage-wash` | `#f3f7f2` | `#f4f4f9` |
   | `--rust` | `#c57b4b` | `#b8496b` |
   | `--rust-wash` | `#f8eee7` | `#f9e9ee` |
   | `--overlay` | `rgba(35, 52, 56, .28)` | `rgba(38, 36, 58, .28)` |

2. **Loose neutrals.** Eleven colours are written as literals rather than tokens. Replace each
   wherever it appears, in the `<style>` block and in Tailwind arbitrary values alike:

   | from | to |
   | --- | --- |
   | `#8b9992` | `#8e8d9c` |
   | `#9aa7a0` | `#9d9caa` |
   | `#afbbb4` | `#b2b1be` |
   | `#b1bdb6` | `#b4b3c0` |
   | `#b3c0b8` | `#b6b5c2` |
   | `#b7c6bd` | `#babac6` |
   | `#c5d5cc` | `#c8c7d5` |
   | `#dbe4de` | `#dddce7` |
   | `#dbe6de` | `#dddde8` |
   | `#dcebe1` | `#dedeea` |
   | `#fafcf9` | `#fafafd` |

3. **Shadow tints follow the ink.** `rgba(43,72,59,.06)` becomes `rgba(45,43,66,.06)`;
   `rgba(46,67,57,.03)` becomes `rgba(46,44,64,.03)`; `rgba(45,65,56,.035)` becomes
   `rgba(45,43,63,.035)`; both occurrences of `rgba(29,116,114,.16)` become `rgba(74,63,160,.16)`;
   `rgba(34,54,47,.14)` becomes `rgba(38,36,58,.14)`.

Two sets of colours stay exactly as they are, because they identify people and roles rather than
the product: the six per-person avatar tints and their text colours (`#e1eee8`, `#f2e9dc`,
`#9b663b`, `#ebe5f0`, `#72587e`, `#e8ecef`, `#63747c`, `#f1e8df`, `#9c6841`, `#efe7e5`, `#9c655c`)
and the five role dot colours (`#6aa49a`, `#c58a55`, `#897299`, `#7b8c96`, `#b58b78`).

### DS-2 - Geometry and type: square corners, serif type, flat surfaces

1. **Corners.** `rounded-[18px]`, `rounded-[15px]` and `rounded-[13px]` all become
   `rounded-[4px]`; every `rounded-xl` becomes `rounded-[3px]`. In the `<style>` block,
   `.staff-row::before` changes `border-radius: 0 4px 4px 0` to `border-radius: 0`, and the
   `.drawer-scroll::-webkit-scrollbar-thumb` changes `border-radius: 999px` to `2px`.
   `border-radius: 999px` stays on `.avatar`, `.permission-state` and `.role-radio`, and every
   `rounded-full` in the markup stays, because those are circular tokens rather than corners.
2. **Type.** In `.ridgewell-app`, the font family changes from
   `Arial, Helvetica, sans-serif` to `Georgia, "Times New Roman", serif`. Every negative
   letter-spacing goes: delete `tracking-[-.01em]`, `tracking-[-.03em]`, `tracking-[-.05em]` and
   `tracking-[-.06em]` wherever they appear, and change `letter-spacing: -.02em` on `.avatar` to
   `letter-spacing: 0`. The positive uppercase tracking - `tracking-[.15em]` through
   `tracking-[.2em]`, and `letter-spacing: .08em` on `.role-choice-state` - stays. Every
   `font-bold` becomes `font-semibold`, and `font-weight: 700` in the `<style>` block becomes
   `font-weight: 600`.
3. **Elevation.** Delete all six `shadow-[...]` utilities. In their place the four elements that
   used them for lift take a border instead: the staff roster container, the clinic selector
   button and the active staff nav item each gain `border border-[var(--line)]` (the roster and
   selector already have one - make theirs `border-2`), and the apply button gains
   `border border-[var(--teal-deep)]`. The drawer panel keeps its existing `border-l` and gains
   nothing. The `box-shadow: inset ...` rules on `.role-choice` stay: they mark state, not height.

### DS-3 - Density and surface: tighter rhythm, inverted surfaces

1. **Spacing.** Apply each swap everywhere the class appears, in the markup and in the `<script>`
   templates: `px-8` to `px-5`; `px-7` to `px-4`; `px-5` to `px-3.5`; `pt-8` to `pt-5`; `pb-8` to
   `pb-5`; `pt-7` to `pt-4`; `pb-7` to `pb-4`; `py-5` to `py-3`; `py-3` to `py-2`; `gap-3` to
   `gap-2`; `mt-8` to `mt-5`; `mt-7` to `mt-4`; `mt-5` to `mt-3`; `space-y-1.5` to `space-y-1`;
   `h-[76px]` to `h-[56px]`; `min-h-[72px]` to `min-h-[52px]`; `min-h-[34px]` to `min-h-[26px]`;
   `w-[228px]` to `w-[196px]`; `w-[600px]` to `w-[520px]`. In the `<style>` block, `.role-choice`
   changes `min-height: 72px` to `52px` and `padding: 10px 6px 9px` to `6px 4px 5px`. Leave
   `min-h-[760px]` alone.
2. **Type scale.** Every `text-[Npx]` drops by one pixel for N of 10 or more - `text-[13px]`
   becomes `text-[12px]`, and so on - except the two headings, which drop further: `text-[34px]`
   becomes `text-[26px]` and `text-[23px]` becomes `text-[18px]`. `text-[9px]` is unchanged. In
   the `<style>` block, `font-size: 13px` becomes `12px`, `11px` becomes `10px`, `10px` becomes
   `9px`, and `8px` is unchanged. Work from the original sizes, not from the results, so no size
   is reduced twice.
3. **Surface inversion.** The page ground and the card ground trade places: in the `<style>`
   block, swap the values of `--canvas` and `--white` as they stand after DS-1, so the app
   background takes the near-white value and the roster, the drawer, the clinic selector and the
   active nav item take the darker one. No other token changes, and no element changes which
   token it references.

## Reference design

```html
<!DOCTYPE html><html><head><meta charset='utf-8'><script src='https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4'></script><style> *,*::before,*::after{box-sizing:border-box;} body{margin:0;padding:0;}</style></head><body><style>
    .ridgewell-app {
    --canvas: #eef2ee;
    --paper: #fcfbf8;
    --white: #fffefa;
    --sidebar: #edf3ee;
    --ink: #24363a;
    --muted: #748287;
    --line: #dce6df;
    --line-soft: #e9efea;
    --teal: #1d7472;
    --teal-deep: #155e61;
    --teal-wash: #e4f0eb;
    --sage-wash: #f3f7f2;
    --rust: #c57b4b;
    --rust-wash: #f8eee7;
    --overlay: rgba(35, 52, 56, .28);
    font-family: Arial, Helvetica, sans-serif;
  }

  .ridgewell-app button {
    font-family: inherit;
  }

  .ridgewell-app .staff-row {
    position: relative;
    width: 100%;
    border-bottom: 1px solid var(--line-soft);
    text-align: left;
    cursor: pointer;
  }

  .ridgewell-app .staff-row:last-child {
    border-bottom: 0;
  }

  .ridgewell-app .staff-row::before {
    position: absolute;
    inset-block: 14px;
    left: 0;
    width: 3px;
    border-radius: 0 4px 4px 0;
    background: var(--teal);
    content: "";
    opacity: 0;
  }

  .ridgewell-app .staff-row:hover {
    background: var(--sage-wash);
  }

  .ridgewell-app .staff-row.is-selected {
    background: var(--teal-wash);
  }

  .ridgewell-app .staff-row.is-selected::before {
    opacity: 1;
  }

  .ridgewell-app .staff-row:focus-visible,
  .ridgewell-app .role-choice:focus-visible,
  .ridgewell-app .close-drawer:focus-visible,
  .ridgewell-app .apply-role:focus-visible,
  .ridgewell-app .clinic-switcher:focus-visible {
    outline: 2px solid var(--rust);
    outline-offset: -2px;
  }

  .ridgewell-app .drawer-panel {
    transform: translateX(100%);
    transition: transform 240ms cubic-bezier(.22, .8, .24, 1);
  }

  .ridgewell-app #drawerOverlay.is-open .drawer-panel {
    transform: translateX(0);
  }

  .ridgewell-app .drawer-scroll {
    scrollbar-color: #c5d5cc transparent;
    scrollbar-width: thin;
  }

  .ridgewell-app .drawer-scroll::-webkit-scrollbar {
    width: 6px;
  }

  .ridgewell-app .drawer-scroll::-webkit-scrollbar-thumb {
    border-radius: 999px;
    background: #c5d5cc;
  }

  .ridgewell-app .role-grid {
    grid-template-columns: minmax(176px, 1fr) repeat(5, minmax(0, 1fr));
  }

  .ridgewell-app .role-choice {
    position: relative;
    min-height: 72px;
    border-left: 1px solid var(--line-soft);
    background: var(--paper);
    padding: 10px 6px 9px;
    color: var(--muted);
    text-align: center;
  }

  .ridgewell-app .role-choice:hover {
    background: var(--sage-wash);
    color: var(--ink);
  }

  .ridgewell-app .role-choice.is-current {
    background: var(--teal-wash);
    color: var(--teal-deep);
    box-shadow: inset 0 2px 0 var(--teal);
  }

  .ridgewell-app .role-choice.is-picked {
    box-shadow: inset 0 -3px 0 var(--rust);
  }

  .ridgewell-app .role-choice.is-current.is-picked {
    box-shadow: inset 0 2px 0 var(--teal), inset 0 -3px 0 var(--teal);
  }

  .ridgewell-app .role-choice-name {
    display: block;
    min-height: 27px;
    font-size: 10px;
    font-weight: 700;
    line-height: 1.2;
  }

  .ridgewell-app .role-choice-state {
    display: block;
    min-height: 13px;
    margin-top: 2px;
    color: var(--teal);
    font-size: 8px;
    font-weight: 700;
    letter-spacing: .08em;
    line-height: 1.1;
    text-transform: uppercase;
  }

  .ridgewell-app .role-radio {
    position: absolute;
    right: 7px;
    top: 7px;
    display: block;
    width: 10px;
    height: 10px;
    border: 1px solid #b7c6bd;
    border-radius: 999px;
    background: var(--white);
  }

  .ridgewell-app .role-choice.is-picked .role-radio {
    border: 3px solid var(--teal);
  }

  .ridgewell-app .permission-row:nth-child(even) {
    background: #fafcf9;
  }

  .ridgewell-app .permission-state {
    display: inline-grid;
    width: 20px;
    height: 20px;
    place-items: center;
    border-radius: 999px;
    font-size: 11px;
    font-weight: 700;
  }

  .ridgewell-app .permission-state.is-granted {
    background: var(--teal-wash);
    color: var(--teal-deep);
  }

  .ridgewell-app .permission-state.is-denied {
    color: #b1bdb6;
    font-size: 13px;
    font-weight: 400;
  }

  .ridgewell-app .apply-role:disabled {
    cursor: default;
    background: #dbe4de;
    color: #8b9992;
  }

  .ridgewell-app .apply-role:not(:disabled):hover {
    background: var(--teal-deep);
  }

  .ridgewell-app .avatar {
    display: inline-grid;
    flex-shrink: 0;
    place-items: center;
    border-radius: 999px;
    font-weight: 700;
    letter-spacing: -.02em;
  }
</style>
<div class="ridgewell-app min-h-screen overflow-x-clip bg-[var(--canvas)] text-[var(--ink)] antialiased" data-kid="1" data-name="application root container">
    <div class="relative flex min-h-[760px] w-full overflow-hidden bg-[var(--paper)]" data-kid="1-1" data-name="layout wrapper">
        <aside class="flex w-[228px] shrink-0 flex-col border-r border-[var(--line)] bg-[var(--sidebar)] px-5 pb-6 pt-6" data-kid="1-1-1" data-name="sidebar navigation column">
            <div class="flex items-center gap-3 border-b border-[#dbe6de] pb-7" data-kid="1-1-1-1" data-name="branding header area">
                <div class="grid h-10 w-10 shrink-0 place-items-center rounded-[13px] bg-[var(--teal)] text-[15px] font-bold text-white shadow-[0_5px_14px_rgba(29,116,114,.16)]" data-kid="1-1-1-1-1" data-name="app logo placeholder icon">
                    R
                </div>
                <div class="min-w-0" data-kid="1-1-1-1-2" data-name="brand name and subtitle group">
                    <div class="text-[15px] font-bold tracking-[-.03em] text-[var(--ink)]" data-kid="1-1-1-1-2-1" data-name="app title text">
                        Ridgewell
                    </div>
                    <div class="mt-1 text-[10px] font-semibold uppercase tracking-[.2em] text-[var(--muted)]" data-kid="1-1-1-1-2-2" data-name="app subtitle text">
                        Clinics
                    </div>
                </div>
            </div>
            <nav aria-label="Primary" class="mt-8 space-y-1.5" data-kid="1-1-1-2" data-name="main navigation list">
                <div class="flex items-center gap-3 rounded-xl px-3 py-3 text-[13px] font-semibold text-[var(--muted)]" data-kid="1-1-1-2-1" data-name="navigation schedule link">
                    <svg aria-hidden="true" class="h-[17px] w-[17px]" data-kid="1-1-1-2-1-1" data-name="schedule icon" fill="none" stroke="currentColor" stroke-width="1.7" viewbox="0 0 24 24">
                        <rect height="15" rx="2" width="16" x="4" y="5">
                        </rect>
                        <path d="M8 3v4M16 3v4M4 10h16">
                        </path>
                    </svg>
                    <span data-kid="1-1-1-2-1-2" data-name="schedule link text">
                        Schedule
                    </span>
                </div>
                <div class="flex items-center gap-3 rounded-xl px-3 py-3 text-[13px] font-semibold text-[var(--muted)]" data-kid="1-1-1-2-2" data-name="navigation patients link">
                    <svg aria-hidden="true" class="h-[17px] w-[17px]" data-kid="1-1-1-2-2-1" data-name="patients icon" fill="none" stroke="currentColor" stroke-width="1.7" viewbox="0 0 24 24">
                        <circle cx="9" cy="8" r="3">
                        </circle>
                        <path d="M3.5 19c.7-3 2.5-4.5 5.5-4.5s4.8 1.5 5.5 4.5M16 11a3 3 0 1 0 0-6M16 14.5c2.4 0 4 1.5 4.6 4.5">
                        </path>
                    </svg>
                    <span data-kid="1-1-1-2-2-2" data-name="patients link text">
                        Patients
                    </span>
                </div>
                <div class="flex items-center gap-3 rounded-xl px-3 py-3 text-[13px] font-semibold text-[var(--muted)]" data-kid="1-1-1-2-3" data-name="navigation billing link">
                    <svg aria-hidden="true" class="h-[17px] w-[17px]" data-kid="1-1-1-2-3-1" data-name="billing icon" fill="none" stroke="currentColor" stroke-width="1.7" viewbox="0 0 24 24">
                        <path d="M5 4.5h14v15H5z">
                        </path>
                        <path d="M8 8h8M8 12h5M8 16h8">
                        </path>
                    </svg>
                    <span data-kid="1-1-1-2-3-2" data-name="billing link text">
                        Billing
                    </span>
                </div>
                <div class="flex items-center gap-3 rounded-xl bg-[var(--white)] px-3 py-3 text-[13px] font-bold text-[var(--teal)] shadow-[0_6px_18px_rgba(43,72,59,.06)]" data-kid="1-1-1-2-4" data-name="navigation staff link active">
                    <svg aria-hidden="true" class="h-[17px] w-[17px]" data-kid="1-1-1-2-4-1" data-name="staff icon" fill="none" stroke="currentColor" stroke-width="1.7" viewbox="0 0 24 24">
                        <circle cx="9" cy="8" r="3">
                        </circle>
                        <circle cx="17" cy="9" r="2.2">
                        </circle>
                        <path d="M3.5 19c.7-3 2.5-4.5 5.5-4.5s4.8 1.5 5.5 4.5M14.5 18c.4-2 1.5-3 3.5-3s3.1 1 3.5 3">
                        </path>
                    </svg>
                    <span data-kid="1-1-1-2-4-2" data-name="staff link text">
                        Staff
                    </span>
                    <span class="ml-auto h-1.5 w-1.5 rounded-full bg-[var(--rust)]" data-kid="1-1-1-2-4-3" data-name="active navigation indicator">
                    </span>
                </div>
            </nav>
        </aside>
        <main class="min-w-0 flex-1" data-kid="1-1-2" data-name="main content area">
            <header class="flex h-[76px] items-center justify-between border-b border-[var(--line)] px-8" data-kid="1-1-2-1" data-name="page top header">
                <button class="clinic-switcher flex items-center gap-3 rounded-xl border border-[var(--line)] bg-[var(--white)] px-3.5 py-2.5 text-left shadow-[0_2px_8px_rgba(46,67,57,.03)]" data-kid="1-1-2-1-1" data-name="clinic selector button" type="button">
                    <span class="text-[10px] font-bold uppercase tracking-[.18em] text-[var(--muted)]" data-kid="1-1-2-1-1-1" data-name="clinic label">
                        Clinic
                    </span>
                    <span class="h-2 w-2 rounded-full bg-[var(--teal)]" data-kid="1-1-2-1-1-2" data-name="clinic status indicator">
                    </span>
                    <span class="text-[13px] font-bold text-[var(--ink)]" data-kid="1-1-2-1-1-3" data-name="clinic current name">
                        Lakeside / Central
                    </span>
                    <svg aria-hidden="true" class="ml-1 h-3.5 w-3.5 text-[var(--muted)]" data-kid="1-1-2-1-1-4" data-name="clinic selector dropdown icon" fill="none" stroke="currentColor" stroke-width="1.8" viewbox="0 0 20 20">
                        <path d="m5 7 5 5 5-5">
                        </path>
                    </svg>
                </button>
                <div class="flex items-center gap-3" data-kid="1-1-2-1-2" data-name="user profile section">
                    <div class="avatar h-9 w-9 bg-[var(--teal-wash)] text-[11px] text-[var(--teal-deep)]" data-kid="1-1-2-1-2-1" data-name="user avatar initials">
                        AC
                    </div>
                    <div class="text-right" data-kid="1-1-2-1-2-2" data-name="user profile name and role group">
                        <div class="text-[13px] font-bold tracking-[-.01em]" data-kid="1-1-2-1-2-2-1" data-name="user display name">
                            Amira Cole
                        </div>
                        <div class="mt-1 text-[10px] font-medium text-[var(--muted)]" data-kid="1-1-2-1-2-2-2" data-name="user role description">
                            Clinic admin
                        </div>
                    </div>
                </div>
            </header>
            <section class="px-8 pb-8 pt-8" data-kid="1-1-2-2" data-name="staff access management section">
                <div class="flex items-end justify-between" data-kid="1-1-2-2-1" data-name="page heading and separator group">
                    <div data-kid="1-1-2-2-1-1" data-name="page breadcrumb section">
                        <div class="text-[10px] font-bold uppercase tracking-[.2em] text-[var(--teal)]" data-kid="1-1-2-2-1-1-1" data-name="breadcrumb label">
                            Staff
                        </div>
                        <h1 class="mt-3 text-[34px] font-bold tracking-[-.06em] text-[var(--ink)]" data-kid="1-1-2-2-1-1-2" data-name="page title">
                            Access
                        </h1>
                    </div>
                    <div class="mb-1 h-px w-[180px] bg-[var(--line)]" data-kid="1-1-2-2-1-2" data-name="horizontal decorative separator">
                    </div>
                </div>
                <div class="mt-7 overflow-hidden rounded-[18px] border border-[var(--line)] bg-[var(--white)] shadow-[0_10px_28px_rgba(45,65,56,.035)]" data-kid="1-1-2-2-2" data-name="staff roster table container">
                    <div class="grid grid-cols-[1.75fr_1fr_1.05fr_1.35fr] border-b border-[var(--line)] bg-[var(--sage-wash)] px-5 py-3 text-[10px] font-bold uppercase tracking-[.17em] text-[var(--muted)]" data-kid="1-1-2-2-2-1" data-name="staff roster table header row">
                        <div data-kid="1-1-2-2-2-1-1" data-name="header name">
                            Name
                        </div>
                        <div data-kid="1-1-2-2-2-1-2" data-name="header role">
                            Role
                        </div>
                        <div data-kid="1-1-2-2-2-1-3" data-name="header location">
                            Location
                        </div>
                        <div data-kid="1-1-2-2-2-1-4" data-name="header last sign-in">
                            Last sign-in
                        </div>
                    </div>
                    <div data-dynamic="true" data-kid="1-1-2-2-2-2" data-name="staff list container" data-reason="children rows injected/managed by script" id="staffRoster">
                        <button class="staff-row grid min-h-[72px] grid-cols-[1.75fr_1fr_1.05fr_1.35fr] items-center gap-3 px-5 py-3" data-kid="1-1-2-2-2-2-1" data-name="staff row button" data-person-id="EMP-1041" type="button">
                            <span class="flex min-w-0 items-center gap-3" data-kid="1-1-2-2-2-2-1-1" data-name="staff person info container">
                                <span class="avatar h-10 w-10 bg-[#e1eee8] text-[11px] text-[var(--teal-deep)]" data-kid="1-1-2-2-2-2-1-1-1" data-name="staff avatar initials">
                                    PS
                                </span>
                                <span class="min-w-0" data-kid="1-1-2-2-2-2-1-1-2" data-name="staff identity details">
                                    <span class="block truncate text-[13px] font-bold" data-kid="1-1-2-2-2-2-1-1-2-1" data-name="staff name">
                                        Priya Shah
                                    </span>
                                    <span class="mt-1 block truncate text-[11px] text-[var(--muted)]" data-kid="1-1-2-2-2-2-1-1-2-2" data-name="staff employee ID and email">
                                        EMP-1041
                                        <span class="px-1 text-[#afbbb4]" data-kid="1-1-2-2-2-2-1-1-2-2-1" data-name="email separator">
                                            ·
                                        </span>
                                        priya.shah@ridgewell.example
                                    </span>
                                </span>
                            </span>
                            <span class="flex items-center gap-2 text-[12px] font-bold" data-kid="1-1-2-2-2-2-1-2" data-name="staff role badge container">
                                <span class="h-2 w-2 rounded-full bg-[#6aa49a]" data-dynamic="true" data-kid="1-1-2-2-2-2-1-2-1" data-name="staff role status dot" data-reason="class reinitialized on role change" data-role-dot="">
                                </span>
                                <span data-dynamic="true" data-kid="1-1-2-2-2-2-1-2-2" data-name="staff role name" data-reason="text reinitialized on role change" data-role-label="">
                                    Front desk
                                </span>
                            </span>
                            <span class="text-[12px] font-medium text-[var(--muted)]" data-kid="1-1-2-2-2-2-1-3" data-name="staff location">
                                Lakeside
                            </span>
                            <span class="flex items-center justify-between gap-3 text-[12px] font-medium text-[var(--muted)]" data-kid="1-1-2-2-2-2-1-4" data-name="staff sign-in status container">
                                <span data-kid="1-1-2-2-2-2-1-4-1" data-name="last sign-in date">
                                    24 Aug 2026
                                </span>
                                <svg aria-hidden="true" class="h-4 w-4 text-[#b3c0b8]" data-kid="1-1-2-2-2-2-1-4-2" data-name="chevron icon" fill="none" stroke="currentColor" stroke-width="1.8" viewbox="0 0 20 20">
                                    <path d="m7 4 5 6-5 6">
                                    </path>
                                </svg>
                            </span>
                        </button>
                        <button class="staff-row grid min-h-[72px] grid-cols-[1.75fr_1fr_1.05fr_1.35fr] items-center gap-3 px-5 py-3" data-kid="1-1-2-2-2-2-2" data-person-id="EMP-1108" type="button">
                            <span class="flex min-w-0 items-center gap-3" data-kid="1-1-2-2-2-2-2-1">
                                <span class="avatar h-10 w-10 bg-[#f2e9dc] text-[11px] text-[#9b663b]" data-kid="1-1-2-2-2-2-2-1-1">
                                    MB
                                </span>
                                <span class="min-w-0" data-kid="1-1-2-2-2-2-2-1-2">
                                    <span class="block truncate text-[13px] font-bold" data-kid="1-1-2-2-2-2-2-1-2-1">
                                        Marcus Bell
                                    </span>
                                    <span class="mt-1 block truncate text-[11px] text-[var(--muted)]" data-kid="1-1-2-2-2-2-2-1-2-2">
                                        EMP-1108
                                        <span class="px-1 text-[#afbbb4]" data-kid="1-1-2-2-2-2-2-1-2-2-1">
                                            ·
                                        </span>
                                        marcus.bell@ridgewell.example
                                    </span>
                                </span>
                            </span>
                            <span class="flex items-center gap-2 text-[12px] font-bold" data-kid="1-1-2-2-2-2-2-2">
                                <span class="h-2 w-2 rounded-full bg-[#c58a55]" data-kid="1-1-2-2-2-2-2-2-1" data-role-dot="">
                                </span>
                                <span data-kid="1-1-2-2-2-2-2-2-2" data-role-label="">
                                    Nurse
                                </span>
                            </span>
                            <span class="text-[12px] font-medium text-[var(--muted)]" data-kid="1-1-2-2-2-2-2-3">
                                Lakeside
                            </span>
                            <span class="flex items-center justify-between gap-3 text-[12px] font-medium text-[var(--muted)]" data-kid="1-1-2-2-2-2-2-4">
                                <span data-kid="1-1-2-2-2-2-2-4-1">
                                    23 Aug 2026
                                </span>
                                <svg aria-hidden="true" class="h-4 w-4 text-[#b3c0b8]" data-kid="1-1-2-2-2-2-2-4-2" fill="none" stroke="currentColor" stroke-width="1.8" viewbox="0 0 20 20">
                                    <path d="m7 4 5 6-5 6">
                                    </path>
                                </svg>
                            </span>
                        </button>
                        <button class="staff-row grid min-h-[72px] grid-cols-[1.75fr_1fr_1.05fr_1.35fr] items-center gap-3 px-5 py-3" data-kid="1-1-2-2-2-2-3" data-person-id="EMP-0902" type="button">
                            <span class="flex min-w-0 items-center gap-3" data-kid="1-1-2-2-2-2-3-1">
                                <span class="avatar h-10 w-10 bg-[#ebe5f0] text-[11px] text-[#72587e]" data-kid="1-1-2-2-2-2-3-1-1">
                                    EV
                                </span>
                                <span class="min-w-0" data-kid="1-1-2-2-2-2-3-1-2">
                                    <span class="block truncate text-[13px] font-bold" data-kid="1-1-2-2-2-2-3-1-2-1">
                                        Dr. Elena Voss
                                    </span>
                                    <span class="mt-1 block truncate text-[11px] text-[var(--muted)]" data-kid="1-1-2-2-2-2-3-1-2-2">
                                        EMP-0902
                                        <span class="px-1 text-[#afbbb4]" data-kid="1-1-2-2-2-2-3-1-2-2-1">
                                            ·
                                        </span>
                                        elena.voss@ridgewell.example
                                    </span>
                                </span>
                            </span>
                            <span class="flex items-center gap-2 text-[12px] font-bold" data-kid="1-1-2-2-2-2-3-2">
                                <span class="h-2 w-2 rounded-full bg-[#897299]" data-kid="1-1-2-2-2-2-3-2-1" data-role-dot="">
                                </span>
                                <span data-kid="1-1-2-2-2-2-3-2-2" data-role-label="">
                                    Physician
                                </span>
                            </span>
                            <span class="text-[12px] font-medium text-[var(--muted)]" data-kid="1-1-2-2-2-2-3-3">
                                Lakeside · Central
                            </span>
                            <span class="flex items-center justify-between gap-3 text-[12px] font-medium text-[var(--muted)]" data-kid="1-1-2-2-2-2-3-4">
                                <span data-kid="1-1-2-2-2-2-3-4-1">
                                    24 Aug 2026
                                </span>
                                <svg aria-hidden="true" class="h-4 w-4 text-[#b3c0b8]" data-kid="1-1-2-2-2-2-3-4-2" fill="none" stroke="currentColor" stroke-width="1.8" viewbox="0 0 20 20">
                                    <path d="m7 4 5 6-5 6">
                                    </path>
                                </svg>
                            </span>
                        </button>
                        <button class="staff-row grid min-h-[72px] grid-cols-[1.75fr_1fr_1.05fr_1.35fr] items-center gap-3 px-5 py-3" data-kid="1-1-2-2-2-2-4" data-person-id="EMP-1214" type="button">
                            <span class="flex min-w-0 items-center gap-3" data-kid="1-1-2-2-2-2-4-1">
                                <span class="avatar h-10 w-10 bg-[#e8ecef] text-[11px] text-[#63747c]" data-kid="1-1-2-2-2-2-4-1-1">
                                    JR
                                </span>
                                <span class="min-w-0" data-kid="1-1-2-2-2-2-4-1-2">
                                    <span class="block truncate text-[13px] font-bold" data-kid="1-1-2-2-2-2-4-1-2-1">
                                        Jonah Reeve
                                    </span>
                                    <span class="mt-1 block truncate text-[11px] text-[var(--muted)]" data-kid="1-1-2-2-2-2-4-1-2-2">
                                        EMP-1214
                                        <span class="px-1 text-[#afbbb4]" data-kid="1-1-2-2-2-2-4-1-2-2-1">
                                            ·
                                        </span>
                                        jonah.reeve@ridgewell.example
                                    </span>
                                </span>
                            </span>
                            <span class="flex items-center gap-2 text-[12px] font-bold" data-kid="1-1-2-2-2-2-4-2">
                                <span class="h-2 w-2 rounded-full bg-[#7b8c96]" data-kid="1-1-2-2-2-2-4-2-1" data-role-dot="">
                                </span>
                                <span data-kid="1-1-2-2-2-2-4-2-2" data-role-label="">
                                    Billing
                                </span>
                            </span>
                            <span class="text-[12px] font-medium text-[var(--muted)]" data-kid="1-1-2-2-2-2-4-3">
                                Central
                            </span>
                            <span class="flex items-center justify-between gap-3 text-[12px] font-medium text-[var(--muted)]" data-kid="1-1-2-2-2-2-4-4">
                                <span data-kid="1-1-2-2-2-2-4-4-1">
                                    19 Aug 2026
                                </span>
                                <svg aria-hidden="true" class="h-4 w-4 text-[#b3c0b8]" data-kid="1-1-2-2-2-2-4-4-2" fill="none" stroke="currentColor" stroke-width="1.8" viewbox="0 0 20 20">
                                    <path d="m7 4 5 6-5 6">
                                    </path>
                                </svg>
                            </span>
                        </button>
                        <button class="staff-row grid min-h-[72px] grid-cols-[1.75fr_1fr_1.05fr_1.35fr] items-center gap-3 px-5 py-3" data-kid="1-1-2-2-2-2-5" data-person-id="EMP-0801" type="button">
                            <span class="flex min-w-0 items-center gap-3" data-kid="1-1-2-2-2-2-5-1">
                                <span class="avatar h-10 w-10 bg-[var(--teal-wash)] text-[11px] text-[var(--teal-deep)]" data-kid="1-1-2-2-2-2-5-1-1">
                                    AC
                                </span>
                                <span class="min-w-0" data-kid="1-1-2-2-2-2-5-1-2">
                                    <span class="block truncate text-[13px] font-bold" data-kid="1-1-2-2-2-2-5-1-2-1">
                                        Amira Cole
                                    </span>
                                    <span class="mt-1 block truncate text-[11px] text-[var(--muted)]" data-kid="1-1-2-2-2-2-5-1-2-2">
                                        EMP-0801
                                        <span class="px-1 text-[#afbbb4]" data-kid="1-1-2-2-2-2-5-1-2-2-1">
                                            ·
                                        </span>
                                        amira.cole@ridgewell.example
                                    </span>
                                </span>
                            </span>
                            <span class="flex items-center gap-2 text-[12px] font-bold" data-kid="1-1-2-2-2-2-5-2">
                                <span class="h-2 w-2 rounded-full bg-[var(--teal)]" data-kid="1-1-2-2-2-2-5-2-1" data-role-dot="">
                                </span>
                                <span data-kid="1-1-2-2-2-2-5-2-2" data-role-label="">
                                    Clinic admin
                                </span>
                            </span>
                            <span class="text-[12px] font-medium text-[var(--muted)]" data-kid="1-1-2-2-2-2-5-3">
                                Central
                            </span>
                            <span class="flex items-center justify-between gap-3 text-[12px] font-medium text-[var(--muted)]" data-kid="1-1-2-2-2-2-5-4">
                                <span data-kid="1-1-2-2-2-2-5-4-1">
                                    24 Aug 2026
                                </span>
                                <svg aria-hidden="true" class="h-4 w-4 text-[#b3c0b8]" data-kid="1-1-2-2-2-2-5-4-2" fill="none" stroke="currentColor" stroke-width="1.8" viewbox="0 0 20 20">
                                    <path d="m7 4 5 6-5 6">
                                    </path>
                                </svg>
                            </span>
                        </button>
                        <button class="staff-row grid min-h-[72px] grid-cols-[1.75fr_1fr_1.05fr_1.35fr] items-center gap-3 px-5 py-3" data-kid="1-1-2-2-2-2-6" data-person-id="EMP-1188" type="button">
                            <span class="flex min-w-0 items-center gap-3" data-kid="1-1-2-2-2-2-6-1">
                                <span class="avatar h-10 w-10 bg-[#f1e8df] text-[11px] text-[#9c6841]" data-kid="1-1-2-2-2-2-6-1-1">
                                    LO
                                </span>
                                <span class="min-w-0" data-kid="1-1-2-2-2-2-6-1-2">
                                    <span class="block truncate text-[13px] font-bold" data-kid="1-1-2-2-2-2-6-1-2-1">
                                        Luis Ortega
                                    </span>
                                    <span class="mt-1 block truncate text-[11px] text-[var(--muted)]" data-kid="1-1-2-2-2-2-6-1-2-2">
                                        EMP-1188
                                        <span class="px-1 text-[#afbbb4]" data-kid="1-1-2-2-2-2-6-1-2-2-1">
                                            ·
                                        </span>
                                        luis.ortega@ridgewell.example
                                    </span>
                                </span>
                            </span>
                            <span class="flex items-center gap-2 text-[12px] font-bold" data-kid="1-1-2-2-2-2-6-2">
                                <span class="h-2 w-2 rounded-full bg-[#c58a55]" data-kid="1-1-2-2-2-2-6-2-1" data-role-dot="">
                                </span>
                                <span data-kid="1-1-2-2-2-2-6-2-2" data-role-label="">
                                    Nurse
                                </span>
                            </span>
                            <span class="text-[12px] font-medium text-[var(--muted)]" data-kid="1-1-2-2-2-2-6-3">
                                Central
                            </span>
                            <span class="flex items-center justify-between gap-3 text-[12px] font-medium text-[var(--muted)]" data-kid="1-1-2-2-2-2-6-4">
                                <span data-kid="1-1-2-2-2-2-6-4-1">
                                    22 Aug 2026
                                </span>
                                <svg aria-hidden="true" class="h-4 w-4 text-[#b3c0b8]" data-kid="1-1-2-2-2-2-6-4-2" fill="none" stroke="currentColor" stroke-width="1.8" viewbox="0 0 20 20">
                                    <path d="m7 4 5 6-5 6">
                                    </path>
                                </svg>
                            </span>
                        </button>
                        <button class="staff-row grid min-h-[72px] grid-cols-[1.75fr_1fr_1.05fr_1.35fr] items-center gap-3 px-5 py-3" data-kid="1-1-2-2-2-2-7" data-person-id="EMP-1303" type="button">
                            <span class="flex min-w-0 items-center gap-3" data-kid="1-1-2-2-2-2-7-1">
                                <span class="avatar h-10 w-10 bg-[#efe7e5] text-[11px] text-[#9c655c]" data-kid="1-1-2-2-2-2-7-1-1">
                                    HC
                                </span>
                                <span class="min-w-0" data-kid="1-1-2-2-2-2-7-1-2">
                                    <span class="block truncate text-[13px] font-bold" data-kid="1-1-2-2-2-2-7-1-2-1">
                                        Hannah Cho
                                    </span>
                                    <span class="mt-1 block truncate text-[11px] text-[var(--muted)]" data-kid="1-1-2-2-2-2-7-1-2-2">
                                        EMP-1303
                                        <span class="px-1 text-[#afbbb4]" data-kid="1-1-2-2-2-2-7-1-2-2-1">
                                            ·
                                        </span>
                                        hannah.cho@ridgewell.example
                                    </span>
                                </span>
                            </span>
                            <span class="flex items-center gap-2 text-[12px] font-bold" data-kid="1-1-2-2-2-2-7-2">
                                <span class="h-2 w-2 rounded-full bg-[#b58b78]" data-kid="1-1-2-2-2-2-7-2-1" data-role-dot="">
                                </span>
                                <span data-kid="1-1-2-2-2-2-7-2-2" data-role-label="">
                                    Front desk
                                </span>
                            </span>
                            <span class="text-[12px] font-medium text-[var(--muted)]" data-kid="1-1-2-2-2-2-7-3">
                                Lakeside
                            </span>
                            <span class="flex flex-col justify-center gap-1 text-[12px] font-medium text-[var(--muted)]" data-kid="1-1-2-2-2-2-7-4">
                                <span data-kid="1-1-2-2-2-2-7-4-1">
                                    Never signed in
                                </span>
                                <span class="text-[10px] text-[#9aa7a0]" data-kid="1-1-2-2-2-2-7-4-2">
                                    Invite sent 2 Mar 2026
                                </span>
                            </span>
                        </button>
                    </div>
                </div>
            </section>
        </main>
        <div class="absolute inset-0 z-20" data-dynamic="true" data-kid="1-1-3" data-name="role comparison drawer overlay" data-reason="hidden state toggled by script" hidden="" id="drawerOverlay">
            <button aria-label="Close role comparison" class="absolute inset-0 h-full w-full bg-[var(--overlay)]" data-kid="1-1-3-1" data-name="drawer backdrop" id="drawerBackdrop" type="button">
            </button>
            <aside aria-labelledby="drawerTitle" aria-modal="true" class="drawer-panel absolute inset-y-0 right-0 flex w-[600px] max-w-[calc(100vw-24px)] flex-col border-l border-[var(--line)] bg-[var(--white)] shadow-[-22px_0_55px_rgba(34,54,47,.14)]" data-kid="1-1-3-2" data-name="drawer panel container" id="roleDrawer" role="dialog" tabindex="-1">
                <div class="flex items-start justify-between border-b border-[var(--line)] px-7 pb-6 pt-7" data-kid="1-1-3-2-1" data-name="drawer header">
                    <div data-kid="1-1-3-2-1-1" data-name="drawer header content">
                        <div class="text-[10px] font-bold uppercase tracking-[.2em] text-[var(--teal)]" data-kid="1-1-3-2-1-1-1" data-name="drawer section label">
                            Role comparison
                        </div>
                        <div class="mt-4 flex items-center gap-3" data-kid="1-1-3-2-1-1-2" data-name="selected user header group">
                            <div class="avatar h-11 w-11 bg-[var(--teal-wash)] text-[12px] text-[var(--teal-deep)]" data-dynamic="true" data-kid="1-1-3-2-1-1-2-1" data-name="drawer user avatar" data-reason="initials and background style replaced by script" id="drawerAvatar">
                            </div>
                            <div class="min-w-0" data-kid="1-1-3-2-1-1-2-2" data-name="drawer user identity container">
                                <h2 class="truncate text-[23px] font-bold tracking-[-.05em] text-[var(--ink)]" data-dynamic="true" data-kid="1-1-3-2-1-1-2-2-1" data-name="drawer user name" data-reason="text replaced by script" id="drawerTitle">
                                </h2>
                                <div class="mt-1.5 truncate text-[11px] text-[var(--muted)]" data-dynamic="true" data-kid="1-1-3-2-1-1-2-2-2" data-name="drawer user email" data-reason="text replaced by script" id="drawerMeta">
                                </div>
                            </div>
                        </div>
                    </div>
                    <button aria-label="Close role comparison" class="close-drawer grid h-9 w-9 shrink-0 place-items-center rounded-full border border-[var(--line)] text-[var(--muted)] hover:bg-[var(--sage-wash)]" data-kid="1-1-3-2-1-2" data-name="close drawer button" id="closeDrawer" type="button">
                        <svg aria-hidden="true" class="h-4 w-4" data-kid="1-1-3-2-1-2-1" data-name="close icon" fill="none" stroke="currentColor" stroke-width="1.7" viewbox="0 0 20 20">
                            <path d="m6 6 8 8M14 6l-8 8">
                            </path>
                        </svg>
                    </button>
                </div>
                <div class="drawer-scroll min-h-0 flex-1 overflow-y-auto px-7 py-5" data-kid="1-1-3-2-2" data-name="drawer scrollable content area">
                    <div class="flex items-center justify-between rounded-xl border border-[#dcebe1] bg-[var(--sage-wash)] px-4 py-3" data-kid="1-1-3-2-2-1" data-name="current role summary card">
                        <div data-kid="1-1-3-2-2-1-1" data-name="current role header">
                            <div class="text-[9px] font-bold uppercase tracking-[.16em] text-[var(--muted)]" data-kid="1-1-3-2-2-1-1-1" data-name="label">
                                Current role
                            </div>
                            <div class="mt-1 text-[13px] font-bold text-[var(--teal-deep)]" data-dynamic="true" data-kid="1-1-3-2-2-1-1-2" data-name="current role display" data-reason="text replaced by script" id="currentRoleLabel">
                            </div>
                        </div>
                        <div class="text-right text-[11px] font-medium text-[var(--muted)]" data-dynamic="true" data-kid="1-1-3-2-2-1-2" data-name="current role location display" data-reason="text replaced by script" id="currentRoleLocation">
                        </div>
                    </div>
                    <div class="mt-5 flex items-end justify-between" data-kid="1-1-3-2-2-2" data-name="permissions header group">
                        <div class="text-[11px] font-bold uppercase tracking-[.16em] text-[var(--muted)]" data-kid="1-1-3-2-2-2-1" data-name="permissions title">
                            Permissions
                        </div>
                        <div class="text-[10px] font-medium text-[#9aa7a0]" data-kid="1-1-3-2-2-2-2" data-name="selection helper text">
                            Select a role
                        </div>
                    </div>
                    <div class="mt-2" data-dynamic="true" data-kid="1-1-3-2-2-3" data-name="role comparison interactive grid" data-reason="content dynamically rendered by script" id="roleComparison">
                    </div>
                </div>
                <div class="flex items-center justify-between border-t border-[var(--line)] px-7 py-5" data-kid="1-1-3-2-3" data-name="drawer footer">
                    <div class="text-[11px] font-medium text-[var(--muted)]" data-kid="1-1-3-2-3-1" data-name="global scope notice">
                        Role applies globally
                    </div>
                    <button class="apply-role rounded-xl bg-[var(--teal)] px-5 py-3 text-[12px] font-bold text-white shadow-[0_7px_16px_rgba(29,116,114,.16)]" data-dynamic="true" data-kid="1-1-3-2-3-2" data-name="apply role button" data-reason="disabled attribute and state toggled by script" disabled="" id="applyRole" type="button">
                        Apply
                    </button>
                </div>
            </aside>
        </div>
    </div>
</div>
<script>
    (() => {
    const roles = ['Front desk', 'Nurse', 'Physician', 'Billing', 'Clinic admin'];
    const permissions = [
      'View patient demographics',
      'View clinical notes',
      'Edit clinical notes',
      'View calendar',
      'Book appointments',
      'Cancel appointments',
      'View invoices',
      'Post payments',
      'Issue refunds',
      'Export patient list',
      'Manage staff access',
      'Edit clinic settings'
    ];
    const roleMap = {
      'Front desk': ['View patient demographics', 'View calendar', 'Book appointments', 'Cancel appointments'],
      'Nurse': ['View patient demographics', 'View clinical notes', 'Edit clinical notes', 'View calendar', 'Book appointments'],
      'Physician': ['View patient demographics', 'View clinical notes', 'Edit clinical notes', 'View calendar', 'Book appointments', 'Cancel appointments'],
      'Billing': ['View patient demographics', 'View calendar', 'View invoices', 'Post payments', 'Issue refunds'],
      'Clinic admin': ['View patient demographics', 'Export patient list', 'View calendar', 'Book appointments', 'Cancel appointments', 'View invoices', 'Manage staff access', 'Edit clinic settings']
    };
    const staff = {
      'EMP-1041': { name: 'Priya Shah', initials: 'PS', email: 'priya.shah@ridgewell.example', role: 'Front desk', location: 'Lakeside', avatar: 'bg-[#e1eee8] text-[var(--teal-deep)]' },
      'EMP-1108': { name: 'Marcus Bell', initials: 'MB', email: 'marcus.bell@ridgewell.example', role: 'Nurse', location: 'Lakeside', avatar: 'bg-[#f2e9dc] text-[#9b663b]' },
      'EMP-0902': { name: 'Dr. Elena Voss', initials: 'EV', email: 'elena.voss@ridgewell.example', role: 'Physician', location: 'Lakeside · Central', avatar: 'bg-[#ebe5f0] text-[#72587e]' },
      'EMP-1214': { name: 'Jonah Reeve', initials: 'JR', email: 'jonah.reeve@ridgewell.example', role: 'Billing', location: 'Central', avatar: 'bg-[#e8ecef] text-[#63747c]' },
      'EMP-0801': { name: 'Amira Cole', initials: 'AC', email: 'amira.cole@ridgewell.example', role: 'Clinic admin', location: 'Central', avatar: 'bg-[var(--teal-wash)] text-[var(--teal-deep)]' },
      'EMP-1188': { name: 'Luis Ortega', initials: 'LO', email: 'luis.ortega@ridgewell.example', role: 'Nurse', location: 'Central', avatar: 'bg-[#f1e8df] text-[#9c6841]' },
      'EMP-1303': { name: 'Hannah Cho', initials: 'HC', email: 'hannah.cho@ridgewell.example', role: 'Front desk', location: 'Lakeside', avatar: 'bg-[#efe7e5] text-[#9c655c]' }
    };

    const overlay = document.getElementById('drawerOverlay');
    const drawer = document.getElementById('roleDrawer');
    const comparison = document.getElementById('roleComparison');
    const applyButton = document.getElementById('applyRole');
    const selectedRows = document.querySelectorAll('[data-person-id]');
    let activePersonId = null;
    let pendingRole = null;

    function renderComparison() {
      const person = staff[activePersonId];
      comparison.innerHTML = `
        <div class="overflow-hidden rounded-[15px] border border-[var(--line)] bg-[var(--paper)]">
          <div class="role-grid grid border-b border-[var(--line)] bg-[var(--sage-wash)]">
            <div class="flex items-end px-3 pb-3 text-[9px] font-bold uppercase tracking-[.15em] text-[var(--muted)]">Permission</div>
            ${roles.map((role) => `
              <button type="button" class="role-choice ${person.role === role ? 'is-current' : ''} ${pendingRole === role ? 'is-picked' : ''}" data-role-choice="${role}" aria-pressed="${pendingRole === role ? 'true' : 'false'}">
                <span class="role-radio" aria-hidden="true"></span>
                <span class="role-choice-name">${role}</span>
                <span class="role-choice-state">${person.role === role ? 'Current' : '&nbsp;'}</span>
              </button>
            `).join('')}
          </div>
          <div>
            ${permissions.map((permission) => `
              <div class="permission-row role-grid grid min-h-[34px] items-center border-b border-[var(--line-soft)] last:border-b-0">
                <div class="px-3 py-2 text-[10px] font-medium leading-[1.15] text-[var(--ink)]">${permission}</div>
                ${roles.map((role) => {
                  const granted = roleMap[role].includes(permission);
                  return `<div class="flex items-center justify-center border-l border-[var(--line-soft)]"><span class="permission-state ${granted ? 'is-granted' : 'is-denied'}" aria-label="${granted ? 'Granted' : 'Not granted'}">${granted ? '✓' : '—'}</span></div>`;
                }).join('')}
              </div>
            `).join('')}
          </div>
        </div>
      `;

      comparison.querySelectorAll('[data-role-choice]').forEach((choice) => {
        choice.addEventListener('click', () => {
          pendingRole = choice.dataset.roleChoice;
          renderComparison();
          updateApplyState();
        });
      });
      updateApplyState();
    }

    function updateApplyState() {
      const person = staff[activePersonId];
      applyButton.disabled = !person || pendingRole === person.role;
    }

    function getRoleDotClass(role) {
      const colors = {
        'Front desk': 'bg-[#6aa49a]',
        'Nurse': 'bg-[#c58a55]',
        'Physician': 'bg-[#897299]',
        'Billing': 'bg-[#7b8c96]',
        'Clinic admin': 'bg-[var(--teal)]'
      };
      return colors[role] || 'bg-[var(--teal)]';
    }

    function updateSelectedRow() {
      selectedRows.forEach((row) => row.classList.toggle('is-selected', row.dataset.personId === activePersonId));
    }

    function openDrawer(personId) {
      activePersonId = personId;
      const person = staff[personId];
      pendingRole = person.role;
      document.getElementById('drawerAvatar').className = `avatar h-11 w-11 ${person.avatar}`;
      document.getElementById('drawerAvatar').textContent = person.initials;
      document.getElementById('drawerTitle').textContent = person.name;
      document.getElementById('drawerMeta').textContent = `${personId} · ${person.email}`;
      document.getElementById('currentRoleLabel').textContent = person.role;
      document.getElementById('currentRoleLocation').textContent = person.location;
      renderComparison();
      updateSelectedRow();
      overlay.hidden = false;
      requestAnimationFrame(() => overlay.classList.add('is-open'));
      drawer.focus({ preventScroll: true });
    }

    function closeDrawer() {
      overlay.classList.remove('is-open');
      window.setTimeout(() => {
        overlay.hidden = true;
        updateSelectedRow();
      }, 240);
    }

    selectedRows.forEach((row) => row.addEventListener('click', () => openDrawer(row.dataset.personId)));
    document.getElementById('closeDrawer').addEventListener('click', closeDrawer);
    document.getElementById('drawerBackdrop').addEventListener('click', closeDrawer);
    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape' && !overlay.hidden) closeDrawer();
    });

    applyButton.addEventListener('click', () => {
      const person = staff[activePersonId];
      if (!person || pendingRole === person.role) return;
      person.role = pendingRole;
      const row = document.querySelector(`[data-person-id="${activePersonId}"]`);
      if (row) {
        row.querySelector('[data-role-label]').textContent = person.role;
        row.querySelector('[data-role-dot]').className = `h-2 w-2 rounded-full ${getRoleDotClass(person.role)}`;
      }
      document.getElementById('currentRoleLabel').textContent = person.role;
      renderComparison();
      updateSelectedRow();
    });
  })();
</script>
</body></html>
```
