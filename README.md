# Nexora — Personal Technology Ecosystem

A dark, atmospheric portfolio and project-catalog site: hero with animated gradient
wordmark, ecosystem cards, category navigation, an updates feed, a filterable project
catalog, a resume page, and a contacts page.

Static HTML/CSS/JS — no build step required to view it, no runtime dependencies.

## Structure

```
index.html        Home: hero, stats, ecosystems, categories, latest updates
projects.html     Filterable project catalog (chips + live text search)
blog.html         Updates feed (articles, releases, changelog, video)
resume.html       Experience, education, skills, tech stack
contacts.html     Contact channels + client-side message form
404.html          Not-found page

assets/css/style.css   Design tokens + all components (single stylesheet)
assets/js/main.js      Theme toggle, nav, scroll reveal, counters, filters, search palette
tools/build.py         Regenerates every page from shared partials + content data
```

## Regenerating the pages

The HTML files are generated. Edit content or templates in `tools/build.py`, then:

```bash
python3 tools/build.py
```

## Viewing locally

```bash
python3 -m http.server 8000
# then open http://localhost:8000/
```

## Design notes

- Colour is driven by HSL custom properties on `:root`, so the whole site re-themes by
  flipping `data-theme` on `<html>` (dark is the default; light is supported).
- Typography: Sora (display), Manrope (body), JetBrains Mono (labels/keys).
- Motion respects `prefers-reduced-motion`; scroll reveals use `IntersectionObserver`.
- The search palette opens with `Ctrl`/`Cmd` + `K`.

## Notes

- The contact form is client-side only. Point it at a backend or form service to
  actually deliver messages.
- Project, ecosystem, and update data in `tools/build.py` is sample content — replace it
  with your own.
