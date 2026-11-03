"""Download the selected public build and verify its checksum and embedded version."""
import hashlib
import json
import os
import re
import urllib.request
import zipfile
from pathlib import Path
from urllib.parse import urlsplit


def prepare():
    release = json.loads(Path('release.json').read_text(encoding='utf-8'))
    version = release['version']
    if not re.fullmatch(r'3\.\d+\.\d+', version):
        raise ValueError('Неверная версия публичного выпуска')
    if os.environ.get('GITHUB_REF_NAME', 'v' + version) != 'v' + version:
        raise ValueError('Тег не соответствует выбранной публичной версии')
    filename = f'TVD-Rally-{version}.zip'
    parsed = urlsplit(release['url'])
    if parsed.scheme != 'https' or parsed.netloc != 'tvdrally.online' or parsed.path != '/downloads/' + filename or parsed.query or parsed.fragment:
        raise ValueError('Ожидалась официальная ссылка на публичную сборку')
    target = Path(filename)
    with urllib.request.urlopen(release['url'], timeout=120) as response:
        target.write_bytes(response.read())
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    if digest != release['sha256'] or target.stat().st_size != release['size']:
        raise ValueError('Размер или контрольная сумма сборки не совпадают')
    with zipfile.ZipFile(target) as archive:
        if archive.read('TVD Rally/app/VERSION').decode().strip() != version:
            raise ValueError('Внутри архива другая версия')
        if archive.testzip() is not None:
            raise ValueError('Архив повреждён')
    Path('SHA256SUMS.txt').write_text(f'{digest}  {filename}\n', encoding='utf-8')
    print(f'Проверена публичная версия {version}: {target.stat().st_size} байт')


if __name__ == '__main__':
    prepare()
