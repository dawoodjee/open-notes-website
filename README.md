### Open Notes Website

The marketing page for [open-notes](https://github.com/dawoodjee/open-notes): a
local-first, end-to-end encrypted notes app. One page, built in
[Frappe Builder](https://github.com/frappe/builder) and shipped with this app.

### Requirements

- Frappe **v16**
- Frappe Builder **v1.34.0**, pinned. Builder v1.35.0 (released 2026-09-30)
  imports `@framework/ui/telemetry`, a module Frappe v16 doesn't have, so its
  frontend won't build on v16. Move off the pin once a Builder release builds
  against v16 again.

### Install

```bash
bench get-app --branch v1.34.0 https://github.com/frappe/builder
bench get-app https://github.com/dawoodjee/open-notes-website
bench --site <site> install-app open_notes_website
```

Installing pulls in Builder if the site doesn't have it (`required_apps`), and
Builder's own install hook imports the page from `builder_files/`: the page at
`/open-notes`, its colour tokens, and its data script.

**Restart the bench processes after installing** (`bench restart` in
production, or stop and re-run `bench start` in development). Processes started
before the app existed can't import it; the scheduler crashes on its first run
and, under `bench start`, takes every other process down with it.

**Make it the home page** (optional, and deliberately not automatic, so it can't
take over an existing site's home page): Builder Settings → Home Page →
`open-notes`.

### Settings

Desk → **Open Notes Website Settings**. Both links stay hidden until set, so the
page never ships a dead link, and the "Where it runs today" copy changes with
them:

- **Web App URL**: wherever the hosted web app lives.
- **Android Download URL**: `https://github.com/dawoodjee/open-notes/releases/latest`
  once a release with the APK attached exists.

### Editing the page

Edit it in Builder (`/builder`). On a bench with `developer_mode` on, every save
re-exports the page into this app's `builder_files/`: commit that, and
`bench migrate` or `install-app` carries it to other sites. Edits made on a
production site stay in that site's database only.

Colours are Builder Tokens (`on-bg`, `on-text`, `on-muted`, `on-accent`, …),
each with a light and a dark value, so dark mode follows the visitor's system.

The page's head HTML holds the only CSS blocks can't express: the system font
stack (Builder treats a block's font as a Google Font to download), and the
App Store button's "Coming soon" swap on hover or tap.

### Known Builder behaviour

- Builder renders paragraph blocks as `<div>` (it does this on purpose, because
  a `<p>` inside a `<p>` is invalid HTML). Headings stay real `h1`–`h3`.
- Builder's page template always adds `preconnect` hints to
  `fonts.googleapis.com` and `fonts.gstatic.com`. This page loads nothing from
  them, but a browser may still open a connection.

### License

MIT
