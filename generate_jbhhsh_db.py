from sqlite3 import connect, Cursor
from pathlib import Path
from collections import deque


def create_table(c: Cursor, name: str):
    c.execute(
        f'CREATE TABLE {name} (\n'
        f'    trans TEXT PRIMARY KEY COLLATE NOCASE\n'
        f'          NOT NULL UNIQUE,    -- 释义\n'
        f'    abbr  TEXT DEFAULT(NULL)  -- 缩写\n'
        f');'
    )


def main():
    with connect('build/nbnhhsh.db', isolation_level=None) as database_in:
        c_in = database_in.cursor()

        print('开始转换...')
        data = {}
        for abbr, trans in c_in.execute('SELECT abbr, trans FROM nbnhhsh;'):
            if trans.startswith('?'):
                trans = trans[1:]
            for item in trans.split(','):
                item = item.lower()
                if item not in data:
                    data[item] = deque()
                data[item].append(abbr)

        with connect(':memory:', isolation_level=None) as database_out:
            c_out = database_out.cursor()
            create_table(c_out, 'jbhhsh')

            print('开始写入内存...')
            for k, v in data.items():
                c_out.execute(
                    'INSERT INTO jbhhsh (trans, abbr)'
                    ' VALUES (?, ?);',
                    (k, ','.join(v))
                )

            print('开始写入磁盘...')
            Path('build/').mkdir(exist_ok=True)
            path = Path('build/jbhhsh.db')
            if path.exists():
                path.unlink()
            c_out.execute('ATTACH DATABASE "build/jbhhsh.db" AS disk;')
            create_table(c_out, 'disk.jbhhsh')
            c_out.execute('INSERT INTO disk.jbhhsh SELECT * FROM jbhhsh;')


if __name__ == '__main__':
    main()
