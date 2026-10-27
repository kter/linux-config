#!/usr/bin/python3
# Bottles版LINE（Wine）が本体の周りに作る影用の窓（辺・角の8枚、太さ8〜11px、override-redirect）を見つけ次第隠す。
# これらは sway の管理外の窓なので全ワークスペースに黒枠として残ってしまう。
# LINE は移動・リサイズ・タイル化のたびに作り直すので、MapNotify を監視して常駐で消し続ける。
from Xlib import X, Xatom, display
from Xlib.error import XError

d = display.Display()
root = d.screen().root
WM_TYPE = d.intern_atom("_NET_WM_WINDOW_TYPE")
WM_TYPE_DIALOG = d.intern_atom("_NET_WM_WINDOW_TYPE_DIALOG")


def is_line_shadow(w):
    try:
        cls = w.get_wm_class()
        if not cls or cls[1] != "steam_proton" or w.get_wm_name():
            return False
        types = w.get_full_property(WM_TYPE, Xatom.ATOM)
        if not types or WM_TYPE_DIALOG not in types.value:
            return False
        if not w.get_attributes().override_redirect:
            return False
        # 太さは状況で 8〜11px と揺れるので余裕を持たせる
        g = w.get_geometry()
        return min(g.width, g.height) <= 24
    except XError:
        return False


def hide(w):
    if is_line_shadow(w):
        w.unmap()
        d.flush()


for w in root.query_tree().children:
    try:
        if w.get_attributes().map_state == X.IsViewable:
            hide(w)
    except XError:
        pass

root.change_attributes(event_mask=X.SubstructureNotifyMask)
while True:
    ev = d.next_event()
    if ev.type == X.MapNotify:
        hide(ev.window)
