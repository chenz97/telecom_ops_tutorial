#!/usr/bin/env python3
"""Create a portable course package from the current source."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from build import build
from check import check

ROOT = Path(__file__).resolve().parents[1]
if __name__ == '__main__':
    build()
    check()
    destination = ROOT / 'dist' / 'telecom-network-operations-course.zip'
    destination.parent.mkdir(exist_ok=True)
    # The course package contains reader-facing material; maintenance files stay in the repository.
    readme = (ROOT / 'README.md').read_text().split('## 源码维护')[0].rstrip() + '\n'
    with ZipFile(destination, 'w', ZIP_DEFLATED) as package:
        package.writestr('telecom-network-operations-course/README.md', readme)
        for name in ['index.html', 'assets/style.css', 'assets/app.js', 'assets/annotations.js', 'course/tutorial.md']:
            package.write(ROOT / name, 'telecom-network-operations-course/' + name)
    with ZipFile(destination) as package:
        assert package.testzip() is None
        assert len(package.namelist()) == 6
    print(f'教程包：{destination}（{destination.stat().st_size:,} bytes）')
