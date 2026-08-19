# Option キーが Meta として送られない端末向けのフォールバック（macOS 限定）。
# macOS の US/ABC 配列で Option+B / F / D が生む文字そのものをバインドする。
# iTerm2 側で Option Key Sends = Esc+ にしてあるマシンではこれらの文字は届かないので、
# 二重設定にはならない（衝突しない）。
# Linux では Option キー自体が存在せず、これらの文字が入力される経路もないため何もしない。
if status is-interactive; and test (uname) = Darwin
    bind ∫ backward-word   # Option+B
    bind ƒ forward-word    # Option+F
    bind ∂ kill-word       # Option+D
end
