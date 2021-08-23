from asyncio import get_event_loop, AbstractEventLoop, sleep
from collections import deque
from sqlite3 import connect, Cursor
from string import ascii_lowercase, digits
from itertools import product, chain, zip_longest
from traceback import format_exception_only, print_exc
from typing import Iterable, Tuple
from json import JSONDecodeError
from pathlib import Path

from aiohttp import ClientSession, TCPConnector, ClientError


def create_table(c: Cursor, name: str):
    c.execute(
        f'CREATE TABLE {name} (\n'
        f'    abbr  TEXT PRIMARY KEY COLLATE NOCASE\n'
        f'          NOT NULL UNIQUE,    -- 缩写\n'
        f'    trans TEXT DEFAULT(NULL)  -- 释义\n'
        f');'
    )


async def download(
    loop: AbstractEventLoop, client: ClientSession, c: Cursor,
    keys: Iterable[str], count: int, chunk_size: int
):
    keys_null = deque()
    keys_finish_count = chunks_finish_count = 0
    keys_success_count = keys_error_count = 0

    async def download_chunk(chunk: Tuple[str]):
        try:
            nonlocal client, c, keys_null
            nonlocal keys_finish_count, chunks_finish_count
            nonlocal keys_success_count, keys_error_count

            keys_str = ','.join(chunk)
            try:
                r = await client.post(
                    'https://lab.magiconch.com/api/nbnhhsh/guess',
                    data={'text': keys_str}
                )
                r.raise_for_status()
                raw = await r.json()
            except ClientError as e:
                print(
                    '%-80s' % f'** {format_exception_only(type(e), e)} @'
                    f' "{keys_str}"'
                )
                keys_error_count += len(chunk)
            except JSONDecodeError as e:
                print(
                    '%-80s' % f'** {format_exception_only(type(e), e)} @'
                    f' "{keys_str}", {await r.text()}'
                )
                keys_error_count += len(chunk)
            else:
                for item in raw:
                    if item['name'] not in chunk:
                        continue
                    if 'trans' in item:
                        if item['trans'] is None:
                            keys_null.append(item['name'])
                        elif len(item['trans']) > 0:
                            c.execute(
                                'INSERT INTO nbnhhsh (abbr, trans)'
                                ' VALUES (?, ?);',
                                (
                                    item['name'],
                                    ','.join(item['trans'])
                                )
                            )
                            keys_success_count += 1
                    elif 'inputting' in item:
                        if item['inputting'] is None:
                            keys_null.append(item['name'])
                        elif len(item['inputting']) > 0:
                            c.execute(
                                'INSERT INTO nbnhhsh (abbr, trans)'
                                ' VALUES (?, ?);',
                                (
                                    item['name'],
                                    '?' + ','.join(item['inputting'])
                                )
                            )
                            keys_success_count += 1
        except Exception as e:
            print_exc()
            print(
                '%-80s' % f'** {format_exception_only(type(e), e)} @'
                f' "{keys_str}", {await r.text()}'
            )
            keys_error_count += len(chunk)
        finally:
            keys_finish_count += len(chunk)
            chunks_finish_count += 1

    keys_iter = iter(keys)
    print('开始下载...')
    for i, chunk in enumerate(zip_longest(*(keys_iter,)*chunk_size), 1):
        chunk = tuple(filter(lambda x: x is not None, chunk))
        loop.create_task(download_chunk(chunk))
        if i - chunks_finish_count > 40:
            while i - chunks_finish_count > 20:
                print(
                    '%-80s' %
                    f'{chunks_finish_count}/{count//chunk_size}'
                    f' ({chunks_finish_count/(count//chunk_size)*100:.02f}%,'
                    f' i {i},'
                    f' F {keys_finish_count},'
                    f' S {keys_success_count},'
                    f' E {keys_error_count},'
                    f' N {len(keys_null)})',
                    end='\r'
                )
                await sleep(0.1)
    while i - chunks_finish_count > 0:
        print(
            '%-80s' %
            f'{chunks_finish_count}/{count//chunk_size}'
            f' ({chunks_finish_count/(count//chunk_size)*100:.02f}%,'
            f' F {keys_finish_count},'
            f' S {keys_success_count},'
            f' E {keys_error_count},'
            f' N {len(keys_null)})',
            end='\r'
        )
        await sleep(0.1)
    print()
    return keys_null


async def main(loop: AbstractEventLoop):
    async with ClientSession(
        headers={
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0)'
            ' Gecko/20100101 Firefox/91.0'
        },
        connector=TCPConnector(limit_per_host=30)
    ) as client:
        with connect(':memory:', isolation_level=None) as database:
            c = database.cursor()
            create_table(c, 'nbnhhsh')

            keys = map(lambda x: ''.join(x), chain(*map(
                lambda n: product(ascii_lowercase + digits, repeat=n),
                range(2, 4+1)
            )))
            keys_null = await download(
                loop, client, c, keys, 36**2 + 36**3 + 36**4, 200
            )

            # for _ in range(2):  # 再试 2 次
            #     if len(keys_null) == 0:
            #         break
            #     keys_null = await download(
            #         loop, client, c, keys_null, len(keys_null), 200
            #     )

            print('开始写入磁盘...')
            Path('build/').mkdir(exist_ok=True)
            path = Path('build/nbnhhsh.db')
            if path.exists():
                path.unlink()
            c.execute('ATTACH DATABASE "build/nbnhhsh.db" AS disk;')
            create_table(c, 'disk.nbnhhsh')
            c.execute('INSERT INTO disk.nbnhhsh SELECT * FROM nbnhhsh;')

    print('开始写入 null 数据的键...')
    with open('build/keys_null', 'w', encoding='utf8') as f:
        f.write(','.join(sorted(keys_null)))


if __name__ == '__main__':
    loop = get_event_loop()
    loop.run_until_complete(main(loop))
