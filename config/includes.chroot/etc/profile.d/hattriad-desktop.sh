if [ -z "$WAYLAND_DISPLAY" ] && [ "$(tty)" = "/dev/tty1" ] && [ "$USER" = "user" ]; then
  if systemd-detect-virt -q; then
    export WLR_RENDERER=pixman
    export WLR_NO_HARDWARE_CURSORS=1
  fi
  labwc
fi
