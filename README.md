# euclids-elements.org

The static content site at [euclids-elements.org](https://www.euclids-elements.org/):
Dr. David E. Joyce's online edition of Euclid's *Elements*, with the
diagrams now rendered live by the
[`geomlib`](https://github.com/brownnrl/euclid) TypeScript library
instead of the original (defunct) Java applet.

## Repository layout

```
.
├── index.html              site landing page
├── elements/               Books I-XIII (~1,099 files)
├── geomlib/
│   ├── index.html          "what is geomlib" + Clark attribution
│   ├── usingGeomlib.html   guide to interactive diagrams
│   ├── eulerline.html      Euler line demo
│   ├── compass/            Compass Geometry tutorial (7 pages)
│   ├── round/              Spherical geometry tutorials
│   ├── coverage/           c8 coverage report for geomlib (manually synced)
│   └── snapshots/          visual-regression snapshots (manually synced)
├── css/style.css           styling (Joyce's original elements.css)
├── js/header-footer.js     navigation + header/footer injection
├── migrate.py              path-rewrite script (re-runnable)
├── CNAME                   GitHub Pages domain mapping
├── COPYRIGHT.md            content copyright (Dr. Joyce)
├── LICENSE                 MIT (for repo plumbing only)
└── README.md               this file
```

## Local preview

```sh
python3 -m http.server 8000
# open http://localhost:8000/
```

Click into any proposition. The `geomlib` bundle is loaded from
`https://unpkg.com/@brownnrl/geomlib@0.2.0/dist/bundle.js`. Drag a free
point (red) and the rest of the construction follows.

## Updating the geomlib bundle version

When `@brownnrl/geomlib` ships a new version, edit `GEOMLIB_VERSION`
at the top of [`migrate.py`](migrate.py) and re-run it. The script is
idempotent — re-running on already-rewritten files is a no-op.

```sh
python3 migrate.py
```

## Refreshing the coverage + snapshots reports

These artifacts come from the geomlib source repo. To regenerate:

```sh
# In a checkout of github.com/brownnrl/euclid:
cd /path/to/euclid
npm install
npm run coverage              # populates ./coverage/
npm run snapshots:clean
npm test                      # regenerates ./tests/snapshots/ + report.html

# Then sync to this repo:
cp -a ./coverage/ /path/to/euclids-elements.org/geomlib/coverage/
cp -a ./tests/snapshots/ /path/to/euclids-elements.org/geomlib/snapshots/
```

Note: `tests/snapshots/` is ~41 MB of PNGs. The snapshot tree
dominates this repo's size.

## Deployment

GitHub Pages serves the `main` branch root directory. The
[`CNAME`](CNAME) file maps the apex domain `euclids-elements.org` to
the Pages site. DNS for the apex needs A records pointing at GitHub
Pages' four IPs (185.199.108.153, 185.199.109.153, 185.199.110.153,
185.199.111.153) and/or an `AAAA` set for IPv6.

## Mobile testing

A Cloudflare Workers Static Assets project also builds this repo on
every push to `main` and serves it at
[`euclids-elements-org.brownnrl.workers.dev`](https://euclids-elements-org.brownnrl.workers.dev/).
That URL is the one to load on a phone when iterating on
responsive-layout changes — `localhost:8000` isn't reachable from a
mobile device, and pushing untested CSS to the canonical
`euclids-elements.org` would interrupt readers.

[`.assetsignore`](.assetsignore) (same syntax as `.gitignore`)
controls what the CF build skips when uploading assets. The 25 MiB
per-file limit is the main constraint; add patterns there if more
excludable files appear.

Production canonical URL remains `https://www.euclids-elements.org/`.
The `workers.dev` URL is a parallel mirror, not a replacement.

## Licensing

- **Content** (everything under `elements/`, `geomlib/compass/`,
  `geomlib/round/`, `geomlib/eulerline.html`) is &copy; David E.
  Joyce, republished here with his permission. See
  [COPYRIGHT.md](COPYRIGHT.md).
- **Repo plumbing** authored for this site (the new landing pages,
  `migrate.py`, README, CNAME, etc.) is MIT-licensed; see
  [LICENSE](LICENSE).
- **`geomlib` itself** is MIT, with joint copyright. Source at
  [github.com/brownnrl/euclid](https://github.com/brownnrl/euclid).
