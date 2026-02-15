#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
WEBSITE_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
WORKSPACE_ROOT="$(cd -- "${WEBSITE_ROOT}/../.." && pwd)"

RESUME_DIR="${WORKSPACE_ROOT}/02-career/resume"
RESUME_TEX="${RESUME_DIR}/felipefelixariasresume.tex"
RESUME_PDF="${RESUME_DIR}/FFA_resume.pdf"
SITE_PDF="${WEBSITE_ROOT}/data/FFA_resume.pdf"

if [[ ! -d "${RESUME_DIR}" ]]; then
  echo "Expected resume directory at ${RESUME_DIR}, but it was not found."
  exit 1
fi

# Prefer rebuilding from TeX when a compiler is available.
if [[ -f "${RESUME_TEX}" ]]; then
  if command -v latexmk >/dev/null 2>&1; then
    latexmk -pdf -interaction=nonstopmode -halt-on-error -output-directory="${RESUME_DIR}" "${RESUME_TEX}"
    GENERATED_PDF="${RESUME_DIR}/$(basename "${RESUME_TEX%.tex}.pdf")"
    if [[ -f "${GENERATED_PDF}" ]]; then
      cp "${GENERATED_PDF}" "${RESUME_PDF}"
    fi
  elif command -v tectonic >/dev/null 2>&1; then
    tectonic -o "${RESUME_DIR}" "${RESUME_TEX}"
    GENERATED_PDF="${RESUME_DIR}/$(basename "${RESUME_TEX%.tex}.pdf")"
    if [[ -f "${GENERATED_PDF}" ]]; then
      cp "${GENERATED_PDF}" "${RESUME_PDF}"
    fi
  elif [[ ! -f "${RESUME_PDF}" ]]; then
    echo "No LaTeX compiler found (latexmk/tectonic) and ${RESUME_PDF} does not exist."
    exit 1
  fi
fi

if [[ ! -f "${RESUME_PDF}" ]]; then
  echo "Missing source PDF: ${RESUME_PDF}"
  exit 1
fi

cp "${RESUME_PDF}" "${SITE_PDF}"
echo "Synced resume to ${SITE_PDF}"
