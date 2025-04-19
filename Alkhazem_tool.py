#!/usr/bin/env python3
import subprocess
import threading
import time
import PySimpleGUI as sg

# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# 1) ثيم الواجهة مع دعم الإصدارات القديمة من PySimpleGUI
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
try:
    sg.theme('DarkBlue')
except AttributeError:
    sg.ChangeLookAndFeel('DarkBlue')

# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# 2) واجهة المستخدم
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
layout = [
    [sg.Text('Boot.img:'), sg.Input(key='-BOOT-'), sg.FileBrowse(file_types=(('IMG Files','*.img'),))],
    [sg.Text('Relock Boot.img:'), sg.Input(key='-RELOCK-'), sg.FileBrowse(file_types=(('IMG Files','*.img'),))],
    [sg.Button('Flash Boot'), sg.Button('Flash Relock')],
    [sg.ProgressBar(100, orientation='h', size=(40, 20), key='-PROG-')],
    [sg.Multiline(size=(60,10), key='-OUT-')]
]
window = sg.Window('MTK Flash Tool', layout)

# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# 3) دوال مساعدة
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
def log(msg):
    window['-OUT-'].print(msg)

def run_fastboot(cmd_list, start, end):
    log(f'>> {" ".join(cmd_list)}')
    window['-PROG-'].update(start)
    proc = subprocess.Popen(cmd_list, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    for line in proc.stdout:
        log(line.strip())
    proc.wait()
    if proc.returncode == 0:
        window['-PROG-'].update(end)
        log('✔ نجاح')
    else:
        log('✖ فشل')

def wait_brom():
    """ينتظر حتى يظهر الجهاز في وضع BROM عبر mtkclient"""
    log('– انتظر وضع BROM (وصل الجهاز + اضغط Power+Volume Up)...')
    window['-PROG-'].update(5)
    while True:
        res = subprocess.run(
            ['mtkclient', 'detect'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if res.returncode == 0:
            log(res.stdout.strip())
            window['-PROG-'].update(20)
            break
        time.sleep(1)

# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# 4) إجراءات الفلاش
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
def flash_boot(path):
    wait_brom()
    run_fastboot(['fastboot', 'flashing', 'unlock'], 20, 30)
    run_fastboot(['fastboot', 'flash', 'boot', path], 30, 90)
    run_fastboot(['fastboot', 'reboot'], 90, 100)

def flash_relock(path):
    wait_brom()
    run_fastboot(['fastboot', 'flash', 'boot', path], 20, 90)
    run_fastboot(['fastboot', 'flashing', 'lock'], 90, 95)
    run_fastboot(['fastboot', 'reboot'], 95, 100)

# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# 5) حلقة الأحداث
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED:
        break

    if event == 'Flash Boot':
        p = values['-BOOT-']
        if not p:
            log('❗ اختر ملف boot.img أولاً')
        else:
            window['-PROG-'].update(0)
            threading.Thread(target=flash_boot, args=(p,), daemon=True).start()

    if event == 'Flash Relock':
        p = values['-RELOCK-']
        if not p:
            log('❗ اختر ملف boot.img أولاً')
        else:
            window['-PROG-'].update(0)
            threading.Thread(target=flash_relock, args=(p,), daemon=True).start()

window.close()
