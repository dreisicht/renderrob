# Main executable
codesign --force --timestamp --options runtime \
  --entitlements entitlements.plist \
  --sign "$IDENTITY" "$BIN"

# App bundle (top level)
codesign --force --timestamp --options runtime \
  --entitlements entitlements.plist \
  --sign "$IDENTITY" "$APP"
