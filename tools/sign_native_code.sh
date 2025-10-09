ENTITLEMENTS="tools/entitlements.plist"

# Sign .dylib and .so (inside Frameworks, Resources, site-packages, etc.)
find "$APP" -type f \( -name "*.dylib" -o -name "*.so" \) -print0 | while IFS= read -r -d '' f; do
  codesign --force --timestamp --options runtime \
    --entitlements $ENTITLEMENTS \
    -s "Peter Baintner" --keychain "dev" "$f"
done

# Sign actual framework binaries
find "$APP/Contents/Frameworks" -type d -name "*.framework" -print0 2>/dev/null | \
while IFS= read -r -d '' fw; do
  BINPATH="$(/usr/libexec/PlistBuddy -c 'Print :CFBundleExecutable' "$fw/Resources/Info.plist" 2>/dev/null || basename "$fw" .framework)"
  CODEBIN="$fw/Versions/Current/$BINPATH"
  if [ -f "$CODEBIN" ]; then
    codesign --force --timestamp --options runtime \
      --entitlements $ENTITLEMENTS \
      -s "Peter Baintner" --keychain "dev" "$CODEBIN"
  fi
  # (Optional) sign the framework bundle for completeness
  codesign --force --timestamp --options runtime \
    --entitlements $ENTITLEMENTS \
    -s "Peter Baintner" --keychain "dev" "$fw"
done

# Sign plugins/XPCs if any
find "$APP" -type d \( -name "*.plugin" -o -name "*.xpc" -o -name "*.appex" \) -print0 2>/dev/null | \
while IFS= read -r -d '' plug; do
  codesign --force --timestamp --options runtime \
    --entitlements $ENTITLEMENTS \
    -s "Peter Baintner" --keychain "dev" "$plug"
done

