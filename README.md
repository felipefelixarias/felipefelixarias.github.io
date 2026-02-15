# felipefelixarias.github.io

## Resume Workflow

- Canonical resume source lives in `../../02-career/resume`.
- Website copy is `data/FFA_resume.pdf`.

To sync the resume into this website repo:

```bash
make sync-resume
```

The sync script:
- Rebuilds from `felipefelixariasresume.tex` if `latexmk` or `tectonic` is installed.
- Falls back to `../../02-career/resume/FFA_resume.pdf` when no LaTeX compiler is available.
- Copies the final PDF to `data/FFA_resume.pdf`.

## Site Checks

Run local HTML + internal-link validation:

```bash
make check-site
```

GitHub Actions runs the same check on pushes to `master` and pull requests.
