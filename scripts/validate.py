#!/usr/bin/env python3
"""Validate the static release without third-party dependencies (Python 3.10+)."""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
CONCEPTS = ('A', 'B', 'C', 'D')
SIZES = ((300, 250), (336, 280), (160, 600), (300, 600), (1080, 1080), (1200, 628))
EXPECTED = {f'ads/Lenker_{c}_{w}x{h}.html': (c, w, h) for c in CONCEPTS for w, h in SIZES}
REPOSITORY = 'cesar-acosta551/LCL-AD-04'
errors: list[str] = []
missing_assets: set[str] = set()
invalid_paths: set[str] = set()


class Document(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.elements: list[tuple[str, dict[str, str]]] = []

    def handle_starttag(self, tag, attrs):
        self.elements.append((tag, dict(attrs)))

    handle_startendtag = handle_starttag


def fail(message):
    errors.append(message)


def reference(path, url, resource=False, ids=None):
    """Check navigational URLs and all local HTML/CSS resources."""
    url = unquote(url.strip())
    if not url:
        if resource:
            fail(f'{path.relative_to(ROOT)}: empty resource URL')
        return
    parsed = urlsplit(url)
    if parsed.scheme == 'data':
        return
    if parsed.scheme or parsed.netloc:
        if resource or parsed.scheme not in ('http', 'https', 'mailto', 'tel'):
            invalid_paths.add(f'{path.relative_to(ROOT)}: {url}')
        if parsed.hostname in ('localhost', '127.0.0.1', '0.0.0.0'):
            invalid_paths.add(f'{path.relative_to(ROOT)}: {url}')
        return
    if url.startswith('/') or '\\' in url:
        invalid_paths.add(f'{path.relative_to(ROOT)}: {url}')
        return
    if not parsed.path:
        if parsed.fragment and ids is not None and parsed.fragment not in ids:
            fail(f'{path.relative_to(ROOT)}: missing anchor #{parsed.fragment}')
        return
    target = (path.parent / parsed.path).resolve()
    if not target.is_relative_to(ROOT):
        invalid_paths.add(f'{path.relative_to(ROOT)}: {url}')
    elif not target.is_file():
        missing_assets.add(f'{path.relative_to(ROOT)}: {url}')


def inspect(path):
    content = path.read_text(encoding='utf-8')
    decoded = unquote(content)
    forbidden = r'file://|/Users/|/mnt/data|blob:|https?://(?:localhost|127\.0\.0\.1|0\.0\.0\.0)(?=[:/\s\'"])'
    if re.search(forbidden, decoded, re.I):
        invalid_paths.add(str(path.relative_to(ROOT)))
    if path.suffix == '.html':
        document = Document()
        document.feed(content)
        ids = {a['id'] for _, a in document.elements if a.get('id')}
        for tag, attrs in document.elements:
            for attr in ('src', 'href', 'poster', 'data'):
                if attr in attrs and (attr != 'data' or tag == 'object'):
                    reference(path, attrs[attr], resource=(attr != 'href' or tag == 'link'), ids=ids)
            if 'srcset' in attrs:
                for candidate in attrs['srcset'].split(','):
                    reference(path, candidate.strip().split()[0], resource=True)
        for url in re.findall(r'url\(\s*[\'"]?([^\)\'"]+)', content):
            reference(path, url, resource=True)
        return content, document
    if path.suffix == '.css':
        for url in re.findall(r'url\(\s*[\'"]?([^\)\'"]+)', content):
            reference(path, url, resource=True)
        for url in re.findall(r'@import\s+[\'"]([^\'"]+)', content):
            reference(path, url, resource=True)
    return content, None


def main():
    for rel in ('index.html', 'README.md', 'manifest.json', 'NOTICE.md', '.github/workflows/pages.yml', '.nojekyll'):
        if not (ROOT / rel).is_file():
            fail(f'missing required file: {rel}')
    # Documentation examples may contain localhost/file URLs, but release URLs
    # and repository names must identify this release consistently.
    for rel in ('README.md', 'index.html', 'manifest.json', '.github/workflows/pages.yml'):
        path = ROOT / rel
        if not path.is_file():
            continue
        content = path.read_text(encoding='utf-8')
        if re.search(r'lenker-display-ads|Lenker-ads2|LCL-ads-3', content, re.I):
            fail(f'{rel}: stale repository reference')
        for url in re.findall(r'https://(?:github\.com/cesar-acosta551|cesar-acosta551\.github\.io)/[^\s<>\)\x22]+', content):
            parsed = urlsplit(url)
            release_name = parsed.path.strip('/').split('/')[1 if parsed.hostname == 'github.com' else 0]
            if release_name != 'LCL-AD-04':
                fail(f'{rel}: unexpected release URL')
        if rel == 'README.md':
            if '# LCL-AD-04 — Lenker Display Ads' not in content:
                fail('README.md: missing release title')
            for url in (f'https://github.com/{REPOSITORY}', 'https://cesar-acosta551.github.io/LCL-AD-04/'):
                if url not in content:
                    fail('README.md: missing canonical release URL')
    actual = {p.relative_to(ROOT).as_posix() for p in (ROOT / 'ads').rglob('*.html')}
    for rel in sorted(set(EXPECTED) - actual):
        fail(f'missing ad: {rel}')
    for rel in sorted(actual - set(EXPECTED)):
        fail(f'unexpected ad: {rel}')
    documents = {}
    for directory in (ROOT / 'ads', ROOT / 'assets'):
        for path in sorted(directory.rglob('*')):
            if path.is_file() and path.suffix in ('.html', '.css', '.js'):
                documents[path.relative_to(ROOT).as_posix()] = inspect(path)
    if (ROOT / 'index.html').is_file():
        documents['index.html'] = inspect(ROOT / 'index.html')
    for rel, (concept, width, height) in EXPECTED.items():
        if rel not in documents:
            continue
        content, doc = documents[rel]
        meta = [a.get('content') for tag, a in doc.elements if tag == 'meta' and a.get('name') == 'ad.size']
        if meta != [f'width={width},height={height}']:
            fail(f'{rel}: incorrect ad.size metadata')
        for selector in (r'html\s*,\s*body', r'a\.ad'):
            rule = re.search(selector + r'\s*\{([^}]+)\}', content)
            if not rule:
                fail(f'{rel}: missing native canvas rule {selector}')
                continue
            declarations = dict(re.findall(r'([\w-]+)\s*:\s*([^;]+)', rule[1]))
            if declarations.get('width') != f'{width}px' or declarations.get('height') != f'{height}px':
                fail(f'{rel}: canvas dimensions must be {width}x{height}')
            if declarations.get('overflow') != 'hidden':
                fail(f'{rel}: native canvas must hide overflow')
        images = [a.get('src') for tag, a in doc.elements if tag == 'img']
        expected_image = f'../assets/{concept}.{"png" if concept == "D" else "jpeg"}'
        if images != [expected_image]:
            fail(f'{rel}: incorrect approved image assignment')
    if 'index.html' in documents:
        _, gallery = documents['index.html']
        frames = [a for tag, a in gallery.elements if tag == 'iframe']
        if Counter(a.get('src') for a in frames) != Counter(EXPECTED.keys()):
            fail('gallery must embed each of the 24 ads exactly once')
        links = {a.get('href') for tag, a in gallery.elements if tag == 'a'}
        if not set(EXPECTED).issubset(links):
            fail('gallery is missing direct ad links')
        for frame in frames:
            if not frame.get('title'):
                fail('gallery iframe is missing an accessible title')
            if frame.get('src') in EXPECTED:
                _, w, h = EXPECTED[frame['src']]
                if (frame.get('width'), frame.get('height')) != (str(w), str(h)):
                    fail(f'gallery iframe has incorrect native dimensions: {frame["src"]}')
        ids = {a.get('id') for _, a in gallery.elements}
        if not {f'concept-{c}' for c in CONCEPTS}.issubset(ids):
            fail('gallery is missing concept sections')
    try:
        manifest = json.loads((ROOT / 'manifest.json').read_text(encoding='utf-8'))
        assert isinstance(manifest, dict), 'manifest must be an object'
        for key, expected in {'project': 'LCL-AD-04 — Lenker Display Ads', 'repository': REPOSITORY,
                              'repository_url': f'https://github.com/{REPOSITORY}',
                              'gallery_url': 'https://cesar-acosta551.github.io/LCL-AD-04/',
                              'pages_url': 'https://cesar-acosta551.github.io/LCL-AD-04/',
                              'ads_path': 'ads/', 'assets_path': 'assets/',
                              'concept_count': 4, 'format_count': 6, 'ad_count': 24, 'execution_count': 24}.items():
            if manifest.get(key) != expected:
                fail(f'manifest: incorrect {key}')
        ads = manifest.get('ads', [])
        if Counter(a['file'] for a in ads) != Counter(EXPECTED.keys()):
            fail('manifest ad inventory must match all 24 files with no duplicates')
        for ad in ads:
            if ad['file'] in EXPECTED and (ad['concept'], ad['width'], ad['height']) != EXPECTED[ad['file']]:
                fail(f'manifest: incorrect concept or dimensions for {ad["file"]}')
        concepts = manifest.get('concepts', [])
        if Counter(c['id'] for c in concepts) != Counter(CONCEPTS):
            fail('manifest: incorrect concept list')
        for concept in concepts:
            reference(ROOT / 'manifest.json', concept['image'], resource=True)
        if Counter((f['width'], f['height']) for f in manifest.get('formats', [])) != Counter(SIZES):
            fail('manifest: incorrect format list')
        for rel in manifest.get('paths', {}).values():
            target = (ROOT / rel).resolve()
            if not target.is_relative_to(ROOT) or not target.exists():
                fail(f'manifest: invalid release path {rel}')
    except (OSError, ValueError, KeyError, TypeError, AssertionError) as exc:
        fail(f'invalid manifest: {exc}')
    for problem in sorted(missing_assets):
        fail(f'missing local asset: {problem}')
    for problem in sorted(invalid_paths):
        fail(f'invalid production path: {problem}')
    print('FAIL' if errors else 'PASS')
    present = set(EXPECTED).intersection(actual)
    concept_count = len({EXPECTED[rel][0] for rel in present})
    format_count = len({EXPECTED[rel][1:] for rel in present})
    dimension_errors = sum('ad.size metadata' in e or 'canvas dimensions' in e or 'native dimensions' in e for e in errors)
    print(f'Project: LCL-AD-04\nConcepts: {concept_count}\nFormats: {format_count}\nPrimary executions: {len(present)}')
    print(f'Missing ads: {len(set(EXPECTED) - actual)}\nMissing assets: {len(missing_assets)}\nInvalid local paths: {len(invalid_paths)}\nDimension errors: {dimension_errors}')
    for error in errors:
        print(f'- {error}')
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
