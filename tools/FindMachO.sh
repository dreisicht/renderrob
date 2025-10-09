% cat FindMachO.sh
#! /bin/sh

# Passing `-0` to `find` causes it to emit a NUL delimited after the
# file name and the `:`. Sadly, macOS `cut` doesn’t support a nul
# delimiter so we use `tr` to convert that to a DLE (0x01) and `cut` on
# that.
#
# Weirdly, `find` only inserts the NUL on the primary line, not the
# per-architecture Mach-O lines. We use that to our advantage, filtering
# out the per-architecture noise by only passing through lines
# containing a DLE.

find "$@" -type f -print0 \
    | xargs -0 file -0 \
    | grep -a Mach-O \
    | tr '\0' '\1' \
    | grep -a $(printf '\1') \
    | cut -d $(printf '\1') -f 1
