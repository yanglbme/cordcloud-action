import sys
from datetime import timedelta, timezone, datetime

from actions_toolkit import core

# 本地 Windows 控制台默认 GBK 编码，无法输出 emoji 等字符，强制使用 UTF-8 输出
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')


def now():
    tz = timezone(timedelta(hours=+8))
    return datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')


def info(s: str = ''):
    core.info(f'[{now()}] {s}')


def warning(s: str = ''):
    core.warning(f'[{now()}] {s}')


def error(s: str = ''):
    core.info(f'[{now()}] {s}')


def set_failed(s: str = ''):
    core.set_failed(f'[{now()}] {s}')
