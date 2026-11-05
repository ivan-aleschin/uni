#!/usr/bin/env bash
# $1 — исходный docx, $2 — куда положить сжатый
set -euo pipefail
src=$(realpath "$1"); dst=$(realpath -m "$2")
w=$(mktemp -d); cd "$w"; unzip -q "$src"
find . -name '*.png' -exec oxipng -q -o 4 --strip safe {} \;
rm -f "$dst"
zip -q -X -0 "$dst" '[Content_Types].xml' 2>/dev/null || true
zip -q -X -9 -r "$dst" . -x '[Content_Types].xml'
cd /; rm -rf "$w"
