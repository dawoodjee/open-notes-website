#!/usr/bin/env python3
"""Serve the open-notes web app at https://<domain>/web from a production bench.

    sudo python3 apply_web_nginx.py --domain example.com --web-parent /home/frappe/notes-web --bench /home/frappe/frappe-bench

`--web-parent` is the folder that CONTAINS `web/` (the built app). The script:

1. writes /etc/nginx/snippets/open-notes-web.conf from open-notes-web.conf;
2. adds one `include` line to each server block for the domain in bench's
   config/nginx.conf (skipping the http->https redirect block);
3. checks the result with `nginx -t`, restores the old config if it fails, and
   reloads nginx if it passes.

Safe to re-run: steps it finds already done are left alone. Re-run it after
anything that regenerates bench's nginx config (`bench setup nginx`,
`bench setup production`, `bench setup lets-encrypt`, adding a domain), which
drops the include line.
"""

import argparse
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MARK = "# open-notes web app (apps/open_notes_website/deploy/apply_web_nginx.py)"


def server_blocks(text):
	"""(start, end) of every top-level `server { ... }` block."""
	blocks, depth, i = [], 0, 0
	for match in re.finditer(r"[{}]", text):
		if match.group() == "{":
			if depth == 0:
				header = text[text.rfind("\n", 0, match.start()) + 1 : match.start()].strip()
				i = match.start() if header == "server" else -1
			depth += 1
		else:
			depth -= 1
			if depth == 0 and i >= 0:
				blocks.append((i, match.end()))
	return blocks


def add_includes(text, domain, include_line):
	added = found = 0
	for start, end in reversed(server_blocks(text)):
		block = text[start:end]
		names = re.search(r"server_name\s+([^;]*);", block)
		if not names or domain not in names.group(1).split():
			continue
		if "location" not in block:  # the http->https redirect block
			continue
		found += 1
		if include_line in block:
			continue
		root = re.search(r"\n([ \t]*)root\s+[^;]+;", block)
		if not root:
			sys.exit(f"no `root` line in the server block for {domain}; is this bench's nginx.conf?")
		indent = root.group(1)
		at = start + root.end()
		text = text[:at] + f"\n\n{indent}{MARK}\n{indent}{include_line}" + text[at:]
		added += 1
	return text, found, added


def main():
	parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
	parser.add_argument("--domain", required=True)
	parser.add_argument("--web-parent", required=True, help="folder containing web/index.html")
	parser.add_argument("--bench", required=True, help="the bench folder, e.g. /home/frappe/frappe-bench")
	parser.add_argument("--snippet", default="/etc/nginx/snippets/open-notes-web.conf")
	parser.add_argument("--no-reload", action="store_true", help="write and test, but don't reload nginx")
	args = parser.parse_args()

	web_parent = os.path.abspath(args.web_parent)
	if not os.path.isfile(os.path.join(web_parent, "web", "index.html")):
		sys.exit(f"{web_parent}/web/index.html not found: unpack the built app there first")
	conf = os.path.join(args.bench, "config", "nginx.conf")
	if not os.path.isfile(conf):
		sys.exit(f"{conf} not found: run `bench setup production` first")

	original = open(conf).read()
	updated, found, added = add_includes(original, args.domain, f"include {args.snippet};")
	if not found:
		sys.exit(f"no server block for {args.domain} in {conf}: is the site's domain set up in bench?")

	snippet = open(os.path.join(HERE, "open-notes-web.conf")).read().replace("__WEB_PARENT__", web_parent)
	os.makedirs(os.path.dirname(args.snippet), exist_ok=True)
	old_snippet = open(args.snippet).read() if os.path.exists(args.snippet) else None
	with open(args.snippet, "w") as f:
		f.write(snippet)
	if updated != original:
		shutil.copy2(conf, conf + ".before-open-notes")
		with open(conf, "w") as f:
			f.write(updated)

	test = subprocess.run(["nginx", "-t"], capture_output=True, text=True)
	if test.returncode != 0:
		if updated != original:
			shutil.copy2(conf + ".before-open-notes", conf)
		if old_snippet is None:
			os.remove(args.snippet)
		else:
			with open(args.snippet, "w") as f:
				f.write(old_snippet)
		sys.exit("nginx -t failed; nothing changed:\n" + test.stderr)

	print(f"server blocks for {args.domain}: {found}, include added to {added}")
	print(f"/web serves {web_parent}/web")
	if args.no_reload:
		print("nginx config OK (not reloaded)")
	else:
		subprocess.run(["systemctl", "reload", "nginx"], check=True)
		print("nginx reloaded")


if __name__ == "__main__":
	main()
