# ---------------------------------------------------------------------------
# macOS / Linux 共通の fish 設定。
# OS 判定ではなく「そのツールが入っているか」で分岐させ、片方にしか無いツールは
# 静かにスキップする。マシン固有の絶対パスは書かない。
# ---------------------------------------------------------------------------

# Linux 側でのみ設定していた既存の挙動を維持する。
# macOS は LANG=ja_JP.UTF-8 で運用しており、ここを触ると挙動が変わるため対象外。
test (uname) = Linux; and set -gx LC_CTYPE en_US.UTF-8

# 存在するものだけ PATH に追加する。
for dir in ~/bin ~/.local/bin
    test -d $dir; and fish_add_path $dir
end

# mise: PATH 上にあればそれを使い、無ければ ~/.local/bin を直接見る。
if command -q mise
    mise activate fish | source
else if test -x ~/.local/bin/mise
    ~/.local/bin/mise activate fish | source
end

# direnv: 入っている環境でのみ有効化する。
if command -q direnv
    direnv hook fish | source
end
