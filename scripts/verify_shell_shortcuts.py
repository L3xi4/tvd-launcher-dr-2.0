"""Exercise actual Windows IShellLink migration against the installed release."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from unittest.mock import patch


def read_shortcut(path):
    env = dict(os.environ, TVD_TEST_LINK=str(path))
    command = "$s=(New-Object -ComObject WScript.Shell).CreateShortcut($env:TVD_TEST_LINK); @{target=$s.TargetPath;arguments=$s.Arguments;workdir=$s.WorkingDirectory;icon=$s.IconLocation}|ConvertTo-Json -Compress"
    result = subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-Command',command],env=env,capture_output=True,text=True,check=True)
    return json.loads(result.stdout)


def verify(root):
    sys.path.insert(0,str(root/'app'))
    import tvd_install as t
    with tempfile.TemporaryDirectory() as temporary:
        base=Path(temporary);desktop=base/'Desktop';start=base/'Start';desktop.mkdir();start.mkdir()
        target=root/'TVD Rally.exe';icon=t.shell_icon_path(root)
        assert icon.name=='icon-v2.ico'
        legacy=desktop/'TVD Rally.lnk'
        assert t.make_shortcut(legacy,target,'--preserved-test-argument',root,root/'app/icon.ico','TVD test')
        old=read_shortcut(legacy)
        assert t._set_shortcut_icon(legacy,target,icon)
        updated=read_shortcut(legacy)
        assert updated['target']==old['target'] and updated['arguments']==old['arguments'] and updated['workdir']==old['workdir']
        assert updated['icon'].lower().startswith(str(icon).lower())
        # Use real .lnk parsing and filesystem rename, without touching the runner's own shortcuts.
        def paths(common=False):return [] if common else [desktop/'TVD Rally Launcher.lnk',start/'TVD Rally Launcher.lnk']
        with patch.object(t,'_shortcut_paths',paths):
            assert t.rename_shortcuts(root)==[]
            assert not legacy.exists()
            new=desktop/'TVD Rally Launcher.lnk';assert new.exists()
            assert read_shortcut(new)==updated
            assert t.rename_shortcuts(root)==[]
            assert len(list(desktop.glob('*.lnk')))==1
        assert not t._set_shortcut_icon(new,root/'python.exe',root/'app/icon.ico')
        assert read_shortcut(new)==updated
    # Register the sender on Windows and verify the identity used by the process.
    import ctypes
    import winreg
    import native_window
    native_window._register_shell_identity(icon, print)
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Classes\AppUserModelId\TVDRally.Launcher') as key:
        assert winreg.QueryValueEx(key, 'DisplayName')[0] == 'TVD Rally Launcher'
        assert winreg.QueryValueEx(key, 'IconUri')[0].lower() == str(icon.resolve()).lower()
    current = ctypes.c_void_p()
    get_id = ctypes.windll.shell32.GetCurrentProcessExplicitAppUserModelID
    get_id.argtypes = [ctypes.POINTER(ctypes.c_void_p)]
    get_id.restype = ctypes.c_long
    assert get_id(ctypes.byref(current)) >= 0
    try:
        assert ctypes.wstring_at(current) == 'TVDRally.Launcher'
    finally:
        free = ctypes.windll.ole32.CoTaskMemFree
        free.argtypes = [ctypes.c_void_p]
        free(current)
    print('PASS: Windows COM updates only icon, preserves launch parameters, migrates shortcut name without duplicates, rejects another target')


if __name__=='__main__':verify(Path(sys.argv[1]))
