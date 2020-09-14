from configparser import ConfigParser
from contextlib import contextmanager
import csv as csv_
import io
import json as json_
import jsonpath_rw
import os
import pytimeparse
import re
import stat
import time
import urllib.request

def flip_flop(re_on, re_off, include_on, include_off, lines):
    on = False
    for l in lines:
        m_on = re_on.search(l)
        m_off = re_off.search(l)
        if m_on and include_on: on = True
        if m_off and not include_off: on = False
        if on: yield l
        if m_on and not include_on: on = True
        if m_off and include_off: on = False

def resource(local_path, create=None, url=None, headers={}, serialize=None, deserialize=None,
        file_action=None, file_open=None, max_age=None, modify_fetched=None, next_page=None,
        grep=None):
    if create and url:
        raise ValueError('resource has both create function and url')
    if not (create or url):
        raise ValueError('resource has neither create function nor url')
    if deserialize and file_action:
        raise ValueError('resource has both "deserialize" and "file_action" functions')
    serialize = serialize or (lambda x: x)
    deserialize = deserialize or (lambda x: x)
    if not os.path.isfile(local_path) or (max_age and time.time() - os.stat(local_path).st_mtime > pytimeparse.parse(max_age)):
        # Create and cache the resource.
        if url and isinstance(url, str) and not modify_fetched and not grep:
            request = urllib.request.Request(url=url, headers=headers)
            with urllib.request.urlopen(request) as r:
                binary = r.read()
        elif url:
            urls = [url] if isinstance(url, str) else url
            artifact = None
            i = 0
            for u in urls:
                ru = re.sub(r'%p(\d+)', lambda m: str(i+int(m.group(1))), u)
                request = urllib.request.Request(url=ru, headers=headers)
                with urllib.request.urlopen(request) as r:
                    binary_part = r.read()
                part = deserialize(binary_part)
                if part and '%p' in u:
                    urls.append(u)
                    i += 1
                if next_page:
                    np = next_page(part)
                    if np: url.append(np)
                if modify_fetched: part = modify_fetched(part)
                artifact = part if artifact is None else (artifact + part)
            if grep:
                m = re.search(r'=?\.\.=?', grep)
                lines = artifact.split('\n')
                if m:
                    g0 = m.group(0)
                    r0 = re.compile(grep[:m.start()])
                    r1 = re.compile(grep[m.end():])
                    new_lines = list(flip_flop(r0, r1, g0.startswith('='), g0.endswith('='), lines))
                else:
                    r = re.compile(grep)
                    new_lines = [l for l in lines if r.search(l)]
                artifact = '\n'.join(new_lines) + '\n'
            binary = serialize(artifact)
        else:
            artifact = create()
            binary = serialize(artifact)
        with open(local_path, 'wb') as f:
            f.write(binary)
    fd = file_open(local_path) if file_open else open(local_path, mode='rb')
    if file_action:
        return file_action(fd)
    binary = fd.read()
    artifact = deserialize(binary)
    return artifact

#####

@contextmanager
def _csv_reader(f, **kwargs):
    try: yield csv_.reader(f, **kwargs)
    finally: f.close()

@contextmanager
def _csv_DictReader(f, **kwargs):
    try: yield csv_.DictReader(f, **kwargs)
    finally: f.close()

def _serialize_config(config, encoding='utf-8'):
    out = io.StringIO()
    config.write(out)
    return out.getvalue().encode(encoding)

def _deserialize_config(binary, encoding='utf-8'):
    config = ConfigParser()
    config.read_string(binary.decode(encoding))
    return config

def _create_default(default):
    config = ConfigParser()
    config.read_dict(default)
    return config

def _jsonpath_find(path):
    return lambda x: [m.value for m in jsonpath_rw.parse(path).find(x)]

def _jsonpath_pick(path):
    return lambda x: next(m.value for m in jsonpath_rw.parse(path).find(x))

#####

def binary(local_path, create=None, url=None, headers={}, max_age=None):
    return resource(local_path, create=create, url=url, headers=headers, max_age=max_age)

def text(local_path, create=None, url=None, headers={}, encoding='utf-8', max_age=None, grep=None):
    return resource(local_path, create=create, url=url, headers=headers, max_age=max_age, grep=grep,
            serialize=lambda x: x.encode(encoding),
            deserialize=lambda x: x.decode(encoding))

def json(local_path, create=None, url=None, headers={}, encoding='utf-8', max_age=None,
        indent=None, find=None, pick=None, next_page=None):
    return resource(local_path, create=create, url=url, headers=headers, max_age=max_age,
            modify_fetched=_jsonpath_find(find) if find else \
                           _jsonpath_pick(pick) if pick else None,
            next_page=next_page if callable(next_page) else _jsonpath_pick(next_page) if next_page else None,
            serialize=lambda x: json_.dumps(x, indent=indent).encode(encoding),
            deserialize=lambda x: json_.loads(x.decode(encoding)))

def ini(local_path, default=None, create=None, url=None, headers={}, encoding='utf-8', max_age=None):
    return resource(local_path, url=url, headers=headers, max_age=max_age,
            create=create or ((lambda: _create_default(default)) if default else None),
            serialize=lambda c: _serialize_config(c, encoding=encoding),
            deserialize=lambda b: _deserialize_config(b, encoding=encoding))

def csv(local_path, url=None, headers={}, encoding='utf-8', max_age=None, **kwargs):
    return resource(local_path, url=url, headers=headers, max_age=max_age,
            file_action=lambda f: _csv_reader(f, **kwargs),
            file_open=lambda s: open(s, mode='r', encoding=encoding))

def csv_dict(local_path, url=None, headers={}, encoding='utf-8', max_age=None, **kwargs):
    return resource(local_path, url=url, headers=headers, max_age=max_age,
            file_action=lambda f: _csv_DictReader(f, **kwargs),
            file_open=lambda s: open(s, mode='r', encoding=encoding))

