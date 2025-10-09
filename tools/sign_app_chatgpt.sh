#!/usr/bin/env bash
set -euo pipefail

IDENTITY="${1:?codesign identity}"

APP="renderob.app"
ENT="tools/entitlements.plist"

BIN="$APP/Contents/MacOS/$(/usr/libexec/PlistBuddy -c 'Print :CFBundleExecutable' "$APP/Contents/Info.plist")"

# --- helpers ---------------------------------------------------------------

plist_read() {
  # plist_read <plist_path> <key>  -> prints value or empty string
  local plist="$1" key="$2"
  [ -f "$plist" ] || { echo ""; return 0; }
  /usr/libexec/PlistBuddy -c "Print :$key" "$plist" 2>/dev/null || echo ""
}

main_executable() {
  # read CFBundleExecutable, else try to infer from Contents/MacOS
  local inf="$APP/Contents/Info.plist"
  local exe
  exe="$(plist_read "$inf" "CFBundleExecutable")"
  if [ -z "${exe}" ]; then
    # fall back: pick the only file in Contents/MacOS, or the largest one
    if [ -d "$APP/Contents/MacOS" ]; then
      # prefer non-symlink regular files
      mapfile -t files < <(find "$APP/Contents/MacOS" -type f ! -name ".*" -maxdepth 1)
      if [ "${#files[@]}" -eq 1 ]; then
        exe="$(basename "${files[0]}")"
      elif [ "${#files[@]}" -gt 1 ]; then
        exe="$(ls -lS "$APP/Contents/MacOS" | awk '/^-/{print $9; exit}')"
      fi
    fi
  fi
  printf "%s" "$exe"
}

framework_executable() {
  # framework_executable <framework_dir> -> prints path to binary or empty
  local fw="$1"
  local base; base="$(basename "$fw" .framework)"
  local inf1="$fw/Versions/Current/Resources/Info.plist"
  local inf2="$fw/Resources/Info.plist"
  local exe; exe="$(plist_read "$inf1" "CFBundleExecutable")"
  [ -n "$exe" ] || exe="$(plist_read "$inf2" "CFBundleExecutable")"
  [ -n "$exe" ] || exe="$base"
  # common binary locations:
  for p in \
    "$fw/Versions/Current/$exe" \
    "$fw/$exe"
  do
    [ -f "$p" ] && { printf "%s" "$p"; return 0; }
  done
  echo ""
}

sign_file() {
  local path="$1"
  [ -e "$path" ] || return 0
  codesign --force --timestamp --options runtime --entitlements "$ENT" --sign "$IDENTITY" "$path"
}

# --- start -----------------------------------------------------------------

# 0) Clean extended attributes/quarantine
xattr -cr "$APP" || true

# 1) Sign all native libs first (.dylib/.so)
#    Use -perm -111 (POSIX) and sign the target of symlinks (codesign follows).
while IFS= read -r -d '' f; do
  sign_file "$f"
done < <(find "$APP" -type f \( -name "*.dylib" -o -name "*.so" \) -print0)

# 2) Sign framework binaries first, then the framework bundle
if [ -d "$APP/Contents/Frameworks" ]; then
  while IFS= read -r -d '' fw; do
    bin="$(framework_executable "$fw")"
    [ -n "$bin" ] && sign_file "$bin"
    sign_file "$fw"
  done < <(find "$APP/Contents/Frameworks" -type d -name "*.framework" -print0)
fi

# 3) Sign plugins/XPC/appex bundles (if any)
while IFS= read -r -d '' d; do
  sign_file "$d"
done < <(find "$APP" -type d \( -name "*.plugin" -o -name "*.xpc" -o -name "*.appex" \) -print0 2>/dev/null || true)

# 4) Sign helper executables (but not the main one yet)
MAIN_EXE_NAME="$(main_executable)"
MAIN_BIN="$APP/Contents/MacOS/$MAIN_EXE_NAME"
while IFS= read -r -d '' exe; do
  [ "$exe" = "$MAIN_BIN" ] && continue
  sign_file "$exe"
done < <(find "$APP/Contents/MacOS" -type f -perm -111 -print0 2>/dev/null || true)

# 5) Sign the main binary and then the .app itself
sign_file "$MAIN_BIN"
sign_file "$APP"

# 6) Verify
codesign --verify --strict --verbose=2 "$APP"
spctl --assess --type execute --verbose "$APP"
echo "✅ Signed and locally verified."
