# davidjwoodbury.com (GitHub Pages)

Static site for **David J Woodbury** with affiliate links preserved and a simple mailto contact button.

## Quick start

1. Create a repository named `davidjwoodbury.github.io` on GitHub.
2. Add these files to the repo (root). Commit to the `main` branch.
3. In **Settings → Pages**, choose **Deploy from branch** (main / root).

## Custom domain

Add a file named **CNAME** with exactly:

```
davidjwoodbury.com
```

Then configure DNS (GitHub Pages IPs for apex + CNAME for www).

## Contact

The Contact section uses a `mailto:` button to open the visitor's email client to **[email protected]** with a preset subject. No backend is required.

## SEO

- Titles & meta description included.
- Open Graph + Twitter cards use `assets/share-1200x630.png` (replace with your image).
- JSON‑LD `Person` schema is included.
- `robots.txt` and `sitemap.xml` are present.
- External affiliate links use `rel="nofollow sponsored"`.
