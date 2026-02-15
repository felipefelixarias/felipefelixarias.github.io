#!/usr/bin/env python3
"""Basic static-site checks: internal links + lightweight HTML validation."""

from __future__ import annotations

from dataclasses import dataclass, field
from fnmatch import fnmatch
from html.parser import HTMLParser
from pathlib import Path
from typing import Dict, List, Tuple
from urllib.parse import unquote, urlsplit


REPO_ROOT = Path(__file__).resolve().parent.parent
HTML_GLOB = "**/*.html"
IGNORED_DIR_NAMES = {".git", ".github"}
IGNORED_SCHEMES = {"http", "https", "mailto", "tel", "javascript", "data"}
IGNORED_HTML_FILE_PATTERNS = ("google*.html",)


@dataclass
class LinkRef:
  tag: str
  attr: str
  value: str
  line: int


@dataclass
class HtmlFileData:
  path: Path
  has_doctype: bool = False
  has_lang: bool = False
  title_count: int = 0
  has_viewport: bool = False
  h1_count: int = 0
  duplicate_ids: List[str] = field(default_factory=list)
  ids: set[str] = field(default_factory=set)
  links: List[LinkRef] = field(default_factory=list)
  image_lines_missing_alt: List[int] = field(default_factory=list)


class SiteParser(HTMLParser):
  def __init__(self, file_data: HtmlFileData):
    super().__init__(convert_charrefs=True)
    self.file_data = file_data

  def handle_starttag(self, tag: str, attrs: List[Tuple[str, str | None]]) -> None:
    attr_map: Dict[str, str] = {}
    for key, value in attrs:
      if value is not None:
        attr_map[key.lower()] = value

    tag_lower = tag.lower()

    if tag_lower == "html":
      self.file_data.has_lang = bool(attr_map.get("lang"))
    elif tag_lower == "title":
      self.file_data.title_count += 1
    elif tag_lower == "meta":
      if attr_map.get("name", "").lower() == "viewport":
        self.file_data.has_viewport = True
    elif tag_lower == "h1":
      self.file_data.h1_count += 1

    element_id = attr_map.get("id")
    if element_id:
      if element_id in self.file_data.ids and element_id not in self.file_data.duplicate_ids:
        self.file_data.duplicate_ids.append(element_id)
      self.file_data.ids.add(element_id)

    if tag_lower == "img" and "alt" not in attr_map:
      self.file_data.image_lines_missing_alt.append(self.getpos()[0])

    track_attrs = {
      "a": "href",
      "img": "src",
      "script": "src",
      "link": "href",
      "source": "src",
    }
    tracked_attr = track_attrs.get(tag_lower)
    if tracked_attr and tracked_attr in attr_map:
      self.file_data.links.append(
        LinkRef(tag=tag_lower, attr=tracked_attr, value=attr_map[tracked_attr], line=self.getpos()[0])
      )


def discover_html_files() -> List[Path]:
  html_files: List[Path] = []
  for candidate in REPO_ROOT.glob(HTML_GLOB):
    rel = candidate.relative_to(REPO_ROOT)
    if any(part in IGNORED_DIR_NAMES for part in rel.parts):
      continue
    if any(fnmatch(rel.name.lower(), pattern) for pattern in IGNORED_HTML_FILE_PATTERNS):
      continue
    if candidate.is_file():
      html_files.append(candidate)
  return sorted(html_files)


def parse_html_file(path: Path) -> HtmlFileData:
  text = path.read_text(encoding="utf-8")
  data = HtmlFileData(path=path)
  data.has_doctype = "<!doctype html" in text[:1024].lower()
  parser = SiteParser(data)
  parser.feed(text)
  parser.close()
  return data


def resolve_link_target(current_file: Path, raw_value: str) -> tuple[Path | None, str | None]:
  parsed = urlsplit(raw_value)
  scheme = parsed.scheme.lower()
  if scheme in IGNORED_SCHEMES or parsed.netloc:
    return None, None

  if parsed.path == "":
    target = current_file
  elif parsed.path.startswith("/"):
    target = REPO_ROOT / unquote(parsed.path.lstrip("/"))
  else:
    target = current_file.parent / unquote(parsed.path)

  target = target.resolve()
  if target.is_dir() or parsed.path.endswith("/"):
    target = target / "index.html"

  return target, parsed.fragment


def main() -> int:
  html_files = discover_html_files()
  file_data_map = {path.resolve(): parse_html_file(path) for path in html_files}
  errors: List[str] = []

  for data in file_data_map.values():
    rel_path = data.path.relative_to(REPO_ROOT)
    if not data.has_doctype:
      errors.append(f"{rel_path}:1 missing <!DOCTYPE html>")
    if not data.has_lang:
      errors.append(f"{rel_path}:1 missing lang attribute on <html>")
    if data.title_count != 1:
      errors.append(f"{rel_path}:1 expected exactly 1 <title>, found {data.title_count}")
    if not data.has_viewport:
      errors.append(f"{rel_path}:1 missing viewport meta tag")
    if data.h1_count < 1:
      errors.append(f"{rel_path}:1 expected at least one <h1>")
    for dup_id in data.duplicate_ids:
      errors.append(f"{rel_path}:1 duplicate id \"{dup_id}\"")
    for line in data.image_lines_missing_alt:
      errors.append(f"{rel_path}:{line} <img> is missing alt attribute")

  for data in file_data_map.values():
    current = data.path.resolve()
    rel_current = data.path.relative_to(REPO_ROOT)
    for link in data.links:
      if not link.value or link.value.startswith("#"):
        continue

      target, fragment = resolve_link_target(current, link.value)
      if target is None:
        continue

      if not str(target).startswith(str(REPO_ROOT)):
        errors.append(
          f"{rel_current}:{link.line} {link.tag}[{link.attr}] points outside repo: {link.value}"
        )
        continue

      if not target.exists():
        errors.append(f"{rel_current}:{link.line} broken internal link: {link.value}")
        continue

      if fragment and target.suffix.lower() == ".html":
        target_data = file_data_map.get(target.resolve())
        if target_data and fragment not in target_data.ids:
          errors.append(
            f"{rel_current}:{link.line} missing fragment target \"#{fragment}\" in {target.relative_to(REPO_ROOT)}"
          )

  if errors:
    print("Site checks failed:")
    for issue in sorted(errors):
      print(f" - {issue}")
    return 1

  print(f"Site checks passed for {len(html_files)} HTML files.")
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
