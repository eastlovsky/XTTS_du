from PyInstaller.__main__ import run

if __name__ == '__main__':
    # opts = ['ta5.py', '-F']
    # opts = ['ta5.py', '-F', '-w']
    opts = ['duMain.py',
            '-F',
            '-w',
            '--icon=ta.ico',

            '--upx-dir',
            'upx391w']
    run(opts)