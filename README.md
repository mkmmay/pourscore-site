# pourscoreapp.com

Landing page, features page, support, Privacy Policy and Terms for the Pour Score app, served by GitHub Pages.

- Page copy: `src/home.html` (landing) and `src/features.html`. The Support section and the header live in `build.py`.
- Phone mockups, feature cards and the store badges: `parts.py`. At launch, paste the store links into `APP_STORE_URL` and `PLAY_URL` there.
- Styles: `style.css` (all pages) and `landing.css` (landing and features). Behaviour: `site.js`.
- The legal pages are generated from `Coffee App/Legal Docs/extracted/*.md`.

After any change:

    python3 build.py   # needs: pip3 install markdown
    git add -A && git commit -m "..." && git push

The email-confirmed page (`/confirmed/`) has its own build script so it can be rebuilt on its own:

    python3 build_confirmed.py

It hands people back into the app (`pourscore://auth/confirmed`) after the sign-up email link.
