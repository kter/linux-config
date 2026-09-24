#Requires AutoHotkey v2.0
#SingleInstance Force

; Toshy cursor bindings for a US keyboard.
; Only VK_CAPITAL (0x14) can activate navigation.
; Do NOT match SC03A / VK_F0: Japanese Eisu may never send a key-up event.
InstallKeybdHook()
SetCapsLockState "Off"
capsHeld := false

*vk14:: {
    global capsHeld
    capsHeld := true
}
*vk14 up:: {
    global capsHeld
    capsHeld := false
}

CapsPhysicallyHeld() {
    global capsHeld
    return capsHeld && GetKeyState("vk14", "P")
}

IsTerminal() {
    return WinActive("ahk_exe WindowsTerminal.exe")
        || WinActive("ahk_exe powershell.exe")
        || WinActive("ahk_exe pwsh.exe")
        || WinActive("ahk_exe cmd.exe")
        || WinActive("ahk_exe wezterm-gui.exe")
        || WinActive("ahk_exe Alacritty.exe")
        || WinActive("ahk_exe kitty.exe")
        || WinActive("ahk_exe ghostty.exe")
}

IsIde() {
    return WinActive("ahk_exe Code.exe")
        || WinActive("ahk_exe VSCodium.exe")
}

; Toshy excludes terminals and VS Code from GUI cursor translation.
#HotIf CapsPhysicallyHeld() && !IsTerminal() && !IsIde()
*a::Send "{Home}"
*e::Send "{End}"
*f::Send "{Right}"
*b::Send "{Left}"
*p::Send "{Up}"
*n::Send "{Down}"
*d::Send "{Delete}"
*h::Send "{Backspace}"
#HotIf

; Toshy sends Ctrl combinations in terminals instead of arrow keys.
#HotIf CapsPhysicallyHeld() && IsTerminal()
*a::Send "^a"
*e::Send "^e"
*f::Send "^f"
*b::Send "^b"
*p::Send "^p"
*n::Send "^n"
*d::Send "^d"
*h::Send "^h"
*c::Send "^c"
*z::Send "^z"
*l::Send "^l"
*u::Send "^u"
*w::Send "^w"
*k::Send "^k"
*r::Send "^r"
*v::Send "^v"
#HotIf

; Microsoft Japanese IME on a US keyboard: Alt+backquote toggles IME.
#HotIf CapsPhysicallyHeld()
*Space:: {
    Send "!{vkC0}"
    KeyWait "Space"
}
#HotIf

; Left Alt acts as Command for common application shortcuts.
; Suppress native Alt menu activation; right Alt remains a native Alt key.
LAlt::return
LAlt up::return
; App-specific variants must precede the general variants.
#HotIf !CapsPhysicallyHeld() && WinActive("ahk_exe Notepad.exe")
LAlt & n::Send "^+n"
LAlt & t::Send "^n"
#HotIf !CapsPhysicallyHeld() && IsIde()
LAlt & n::Send "^+n"
#HotIf !CapsPhysicallyHeld()
LAlt & f::Send "^f"
LAlt & a::Send "^a"
LAlt & x::Send "^x"
LAlt & c::Send "^c"
LAlt & v::Send "^v"
LAlt & w::Send "^w"
LAlt & n::Send "^n"
LAlt & t::Send "^t"
LAlt & q::WinClose "A"
LAlt & m::WinMinimize "A"
#HotIf

; Emergency pause/resume works even when suspended.
#SuspendExempt True
^!F12:: {
    global capsHeld
    capsHeld := false
    Suspend -1
}
#SuspendExempt False
