import PySimpleGUI as sg
import os
from feb_stats.parser import parse_boxscores
from feb_stats.transforms import compute_league_aggregates

def launch():
    sg.theme('BluePurple')
    # STEP 1 define the layout
    layout = [
                [sg.Text('Introduce la carpeta con las actas (ficheros .html).')],
                [sg.Input('data')],
                [sg.Button('Analizar'),
                 sg.Button('Salir')]
             ]

    #STEP 2 - create the window
    window = sg.Window('Análisis actas FEB',
                       layout,
                       grab_anywhere=True)

    # STEP3 - the event loop
    while True:
        event, values = window.read()   # Read the event that happened and the values dictionary

        if event == sg.WIN_CLOSED or event == 'Salir':     # If user closed window with X or if user clicked "Exit" button then exit
            break
        elif event == 'Analizar':
            folder = values.get(0, '')
            folder = '.' if folder == '' else folder

            league = parse_boxscores(os.path.join('../', folder))
            new_league = compute_league_aggregates(league)
            output_file = new_league.export_to_excel('../')
            sg.popup('Estadísticas guardadas en:', output_file)
            window.close()
            break

    window.close()

if __name__ == '__main__':
    launch()