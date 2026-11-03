"""Verify every installed file against the checked public ZIP, then checksum setup."""
import configparser
import hashlib
import json
import sys
import zipfile
from pathlib import Path


def verify(destination):
    version = json.loads(Path('release.json').read_text(encoding='utf-8'))['version']
    root = Path(destination)
    if (root / 'app/VERSION').read_text().strip() != version:
        raise ValueError('Установлена другая версия')
    settings = configparser.ConfigParser()
    settings.read(root / 'installed.ini', encoding='utf-8-sig')
    if settings.get('TVD Rally', 'version') != version:
        raise ValueError('Неверный признак установленной копии')
    checked = 0
    with zipfile.ZipFile(f'TVD-Rally-{version}.zip') as archive:
        for item in archive.infolist():
            if item.is_dir():
                continue
            relative = Path(item.filename).relative_to('TVD Rally')
            actual = root / relative
            if not actual.is_file() or actual.read_bytes() != archive.read(item):
                raise ValueError(f'Установлен неверный файл: {relative}')
            checked += 1
    setup = Path(f'Output/TVD-Rally-Setup-{version}.exe')
    if setup.read_bytes()[:2] != b'MZ':
        raise ValueError('Установщик не является Windows exe')
    digest = hashlib.sha256(setup.read_bytes()).hexdigest()
    checksum = Path('SHA256SUMS.txt')
    lines = [line for line in checksum.read_text().splitlines() if not line.endswith('  ' + setup.name)]
    checksum.write_text('\n'.join(lines + [f'{digest}  {setup.name}']) + '\n', encoding='utf-8')
    print(f'PASS: установлен TVD Rally {version}, проверено {checked} файлов, контрольная сумма установщика {digest}')


if __name__ == '__main__':
    verify(sys.argv[1])
