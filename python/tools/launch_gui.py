import os
from tkinter import *
from tkinter import filedialog
from openpyxl import load_workbook

from python.feb_stats.transforms import export_boxscores_from_path
from io import BytesIO


class CloseWindow(Tk):
    def __init__(self,
                 text_to_show):
        super(CloseWindow, self).__init__()
        self.title("Análisis actas FEB")
        self.minsize(150, 150)
        # self.wm_iconbitmap('icon.ico')
        self.text_to_show = text_to_show
        self.build()

    def build(self):
        self.build_label(0, 0)
        self.build_close_button(1, 0)

    def build_label(self, row, column):
        self.label = Label(text=self.text_to_show)
        self.label.grid(row=row, column=column, sticky=W)

    def build_close_button(self, row, column):
        self.close_button = Button(text="Cerrar",
                                   command=exit)
        self.close_button.grid(row=row, column=column)


class MainWindow(Tk):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.title("Análisis actas FEB")
        self.minsize(150, 150)
        self.dirname = os.path.abspath(os.path.curdir)
        self.build()

    def build(self):
        self.build_instructions_label(0, 0)
        self.build_directory_entry(0, 1)
        self.build_browse_button(0, 2)
        self.build_output_filename_label(1, 0)
        self.build_output_filename_entry(1, 1)

        self.build_analyze_button(3, 0)
        # self.build_close_button(1, 1)

    def build_instructions_label(self, row, column):
        self.instructions_label = Label(text="Selecciona una carpeta con actas:")
        self.instructions_label.grid(row=row, column=column, sticky=W)

    def build_directory_entry(self, row, column):
        self.directory_entry = Entry()
        self.directory_entry.insert(0, self.dirname)
        self.directory_entry.grid(row=row, column=column, sticky=W)

    def build_browse_button(self, row, column):
        self.browse_button = Button(text="Examinar", command=self.ask_directory)
        self.browse_button.grid(row=row, column=column)


    def build_output_filename_entry(self, row, column):
        self.output_filename_entry = Entry()
        self.output_filename_entry.insert(0, 'analisis.xlsx')
        self.output_filename_entry.grid(row=row, column=column, sticky=W)

    def build_output_filename_label(self, row, column):
        self.instructions_label = Label(text=f"Exportar los resultados en:")
        self.instructions_label.grid(row=row, column=column, sticky=W)

    def ask_directory(self):
        self.dirname = filedialog.askdirectory(initialdir="..",
                                               title="Select folder")
        self.directory_entry.delete(0, END)
        self.directory_entry.insert(0, self.dirname)

    def build_analyze_button(self, row, column):
        self.analyze_button = Button(text="Analizar", command=self.analyze)
        self.analyze_button.grid(row=row, column=column, columnspan=3)

    def analyze(self):
        try:
            boxscores_dir = self.directory_entry.get()
            excel_data = export_boxscores_from_path(boxscores_dir)
            self.output_file = os.path.abspath(os.path.join('../',
                                                            self.output_filename_entry.get()))
            wb = load_workbook(filename=BytesIO(excel_data))
            wb.save(self.output_file)
            text_to_show = f"Análisis guardado en {self.output_file}"
        except ValueError:
            text_to_show = f'No he podido encontrar partidos en esta carpeta ({boxscores_dir}).'
        self.destroy()
        close = CloseWindow(text_to_show)
        close.mainloop()


if __name__ == '__main__':
    root = MainWindow()
    root.mainloop()
