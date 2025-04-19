import subprocess, threading
import PySimpleGUI as sg

sg.theme('DarkBlue')

layout = [
    [sg.Text('Boot.img:'), sg.Input(key='-BOOT-'), sg.FileBrowse(file_types=(('IMG Files','*.img'),))],
    [sg.Text('Relock.img:'), sg.Input(key='-RELOCK-'), sg.FileBrowse(file_types=(('IMG Files','*.img'),))],
    [sg.Button('Flash Boot'), sg.Button('Flash Relock')],
    [sg.ProgressBar(100, orientation='h', size=(40,20), key='-PROG-')],
    [sg.Multiline(size=(60,10), key='-OUT-')]
]

window = sg.Window('MTK Flash Tool', layout)

def log(msg):
    window['-OUT-'].print(msg)

def run_fastboot(cmd_list, start, end):
    log(f'>> {" ".join(cmd_list)}')
    try:
        proc = subprocess.Popen(cmd_list, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in proc.stdout:
            log(line.strip())
        proc.wait()
        window['-PROG-'].update(end if proc.returncode==0 else start)
    except Exception as e:
        log(f'Error: {e}')

def flash_boot(path):
    window['-PROG-'].update(5); log('– وضع Fastboot...')
    run_fastboot(['fastboot','flashing','unlock'],5,20)
    run_fastboot(['fastboot','flash','boot', path],20,80)
    run_fastboot(['fastboot','reboot'],80,100)

def flash_relock(path):
    window['-PROG-'].update(5); log('– وضع Fastboot...')
    run_fastboot(['fastboot','flash','boot', path],5,80)
    run_fastboot(['fastboot','flashing','lock'],80,95)
    run_fastboot(['fastboot','reboot'],95,100)

while True:
    event, values = window.read()
    if event==sg.WIN_CLOSED: break
    if event=='Flash Boot' and values['-BOOT-']:
        threading.Thread(target=flash_boot, args=(values['-BOOT-'],), daemon=True).start()
    if event=='Flash Relock' and values['-RELOCK-']:
        threading.Thread(target=flash_relock, args=(values['-RELOCK-'],), daemon=True).start()

window.close()
