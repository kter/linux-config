set -gx LC_CTYPE en_US.UTF-8

~/.local/bin/mise activate fish | source

direnv hook fish | source


# Added by Antigravity CLI installer
set -gx PATH "/home/ttakahashi/.local/bin" $PATH
