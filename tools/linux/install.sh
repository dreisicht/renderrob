#!/bin/sh
# Registers this Render Rob bundle with the desktop: a launcher entry and the icon.
#
# Wayland compositors and most launchers ignore the icon a window sets on itself. They match the
# window's app ID ("renderrob", set in main.py) to renderrob.desktop and take the icon from there,
# so without this the app runs with a generic icon. Installs per user, into ~/.local/share; run
# it again after moving the bundle, or with --uninstall to remove the entry and the icons.
set -eu

bundle_dir="$(cd "$(dirname "$0")" && pwd)"
data_home="${XDG_DATA_HOME:-$HOME/.local/share}"
applications="$data_home/applications"
icons="$data_home/icons/hicolor"
# Sizes the hicolor theme declares; the bundle's 20 and 40 px icons have no directory there.
sizes="16 24 32 48 64 256"

refresh_caches() {
  # Both are optional: most desktops rescan these directories on their own.
  if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -f -t "$icons" >/dev/null 2>&1 || true
  fi
  if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "$applications" >/dev/null 2>&1 || true
  fi
}

if [ "${1:-}" = "--uninstall" ]; then
  rm -f "$applications/renderrob.desktop"
  for size in $sizes; do
    rm -f "$icons/${size}x${size}/apps/renderrob.png"
  done
  refresh_caches
  echo "Removed Render Rob from the desktop."
  exit 0
fi

executable="$bundle_dir/renderrob"
if [ ! -x "$executable" ]; then
  echo "No renderrob executable next to this script ($bundle_dir)." >&2
  exit 1
fi

for size in $sizes; do
  mkdir -p "$icons/${size}x${size}/apps"
  cp "$bundle_dir/_internal/icon/icon-$size.png" "$icons/${size}x${size}/apps/renderrob.png"
done

# Exec takes a quoted path: escape the characters the desktop entry spec reserves inside quotes,
# then double any % so it is not read as a field code.
quoted_exec="$(printf '%s' "$executable" | sed -e 's/[\\"`$]/\\&/g' -e 's/%/%%/g')"

mkdir -p "$applications"
sed -e "s|^Exec=.*|Exec=\"$(printf '%s' "$quoted_exec" | sed 's/[|&\\]/\\&/g')\"|" \
  "$bundle_dir/renderrob.desktop" >"$applications/renderrob.desktop"
chmod 644 "$applications/renderrob.desktop"

refresh_caches
echo "Render Rob is now in your application launcher."
