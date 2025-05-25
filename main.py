import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog as filedialog
import tkinter.messagebox as messagebox
import random
import string
import os
import re
from datetime import datetime

class MatemykorApp:
    def __init__(self):
        self.program_path = self.initialize_program_files()
        self.root = None
        self.current_text_top = None
        self.current_text_bottom = None
        self.selected_student_number = None
        self.current_list_name = None
        self.editable_list = None
        self.add_point_button = None
        self.subtract_point_button = None
        self.alphabet_letters = [chr(i) for i in range(ord('A'), ord('Z') + 1)]
        
    def initialize_program_files(self):
        """Inicjalizuje pliki programu w folderze AppData/Local"""
        appdata_path = os.getenv('LOCALAPPDATA')
        if not appdata_path:
            appdata_path = os.path.expanduser('~')
        
        matematykor_path = os.path.join(appdata_path, 'Matematykor')
        
        try:
            if not os.path.exists(matematykor_path):
                os.makedirs(matematykor_path)
            
            logs_path = os.path.join(matematykor_path, 'logs.txt')
            list_path = os.path.join(matematykor_path, 'list.txt')
            
            if not os.path.exists(logs_path):
                with open(logs_path, 'w', encoding='utf-8'):
                    pass
            
            if not os.path.exists(list_path):
                with open(list_path, 'w', encoding='utf-8') as f:
                    f.write("1. Jan Kowalski\n")
                    f.write("2. Anna Nowak\n")
                    f.write("3. Piotr Wiśniewski\n\n")
                    f.write("Tutaj możesz edytować listę uczniów...")
            
            return matematykor_path
            
        except Exception as e:
            print(f"Błąd podczas inicjalizacji plików programu: {e}")
            return None

    def save_log(self, log_text):
        """Zapisuje wpis do pliku logów"""
        try:
            logs_path = os.path.join(self.program_path, 'logs.txt') if self.program_path else "logs.txt"
            with open(logs_path, "a", encoding="utf-8") as log_file:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                log_file.write(f"[{timestamp}] {log_text}\n")
        except Exception as e:
            print(f"Błąd podczas zapisywania logu: {e}")

    def show_logs(self):
        """Wyświetla plik logów"""
        try:
            logs_path = os.path.join(self.program_path, 'logs.txt') if self.program_path else "logs.txt"
            if os.path.exists(logs_path):
                os.startfile(logs_path)
            else:
                messagebox.showinfo("Logi", "Plik logs.txt nie istnieje. Zostanie utworzony przy pierwszym losowaniu.")
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie można otworzyć pliku logów:\n{str(e)}")

    def save_list_to_file(self):
        """Zapisuje listę uczniów do pliku"""
        try:
            initial_dir = self.program_path if self.program_path else os.getcwd()
            file_path = filedialog.asksaveasfilename(
                title="Zapisz listę jako",
                filetypes=[("Pliki tekstowe", "*.txt"), ("Wszystkie pliki", "*.*")],
                defaultextension=".txt",
                initialdir=initial_dir
            )
            
            if file_path:
                content = self.editable_list.get(1.0, tk.END).rstrip('\n')
                
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(content)
                
                self.current_list_name.set(f"Zapisano: {os.path.basename(file_path)}")
                messagebox.showinfo("Sukces", f"Lista została zapisana jako:\n{os.path.basename(file_path)}")
                self.save_log(f"Zapisano listę uczniów do pliku: {os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror("Błąd", f"Wystąpił błąd podczas zapisywania pliku:\n{str(e)}")

    def load_list_from_file(self):
        """Wczytuje listę uczniów z pliku"""
        try:
            initial_dir = self.program_path if self.program_path else os.getcwd()
            file_path = filedialog.askopenfilename(
                title="Wybierz plik z listą",
                filetypes=[("Pliki tekstowe", "*.txt"), ("Wszystkie pliki", "*.*")],
                initialdir=initial_dir
            )
            
            if file_path:
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        content = file.read()
                except UnicodeDecodeError:
                    with open(file_path, 'r', encoding='windows-1250') as file:
                        content = file.read()
                
                self.editable_list.delete(1.0, tk.END)
                self.editable_list.insert(1.0, content)
                
                self.current_list_name.set(f"Wczytano: {os.path.basename(file_path)}")
                messagebox.showinfo("Sukces", f"Lista została wczytana z pliku:\n{os.path.basename(file_path)}")
                self.save_log(f"Wczytano listę uczniów z pliku: {os.path.basename(file_path)}")
                
        except Exception as e:
            messagebox.showerror("Błąd", f"Wystąpił błąd podczas wczytywania pliku:\n{str(e)}")

    def get_student_info(self, student_number):
        """Zwraca informacje o uczniu na podstawie numeru"""
        content = self.editable_list.get(1.0, tk.END)
        lines = content.split('\n')
        
        for line in lines:
            if line.strip().startswith(f"{student_number}."):
                # Wyciągnij nazwę ucznia
                name_match = re.search(r'^\d+\.\s*([^(]+)', line.strip())
                student_name = name_match.group(1).strip() if name_match else "Nieznany"
                
                # Sprawdź obecne punkty
                points_match = re.search(r'\((\d+) pkt\)', line)
                current_points = int(points_match.group(1)) if points_match else 0
                
                return student_name, current_points, line
        
        return None, 0, None

    def update_student_points(self, student_number, points_change):
        """Aktualizuje punkty ucznia o podaną wartość"""
        if self.selected_student_number.get() == 0:
            messagebox.showwarning("Uwaga", "Najpierw wylosuj ucznia!")
            return
        
        try:
            content = self.editable_list.get(1.0, tk.END)
            lines = content.split('\n')
            
            student_name, current_points, original_line = self.get_student_info(student_number)
            
            if original_line is None:
                messagebox.showwarning("Uwaga", f"Nie znaleziono ucznia z numerem {student_number} na liście")
                return
            
            new_points = max(0, current_points + points_change)  # Nie pozwalaj na ujemne punkty
            
            # Aktualizuj linię z punktami
            for i, line in enumerate(lines):
                if line.strip().startswith(f"{student_number}."):
                    if current_points > 0:
                        # Zastąp istniejące punkty
                        if new_points > 0:
                            lines[i] = re.sub(r'\(\d+ pkt\)', f'({new_points} pkt)', line)
                        else:
                            # Usuń punkty jeśli są równe 0
                            lines[i] = re.sub(r'\s*\(\d+ pkt\)', '', line)
                    else:
                        # Dodaj nowe punkty
                        if new_points > 0:
                            lines[i] = line.rstrip() + f' ({new_points} pkt)'
                    break
            
            # Zaktualizuj zawartość listy
            self.update_list_content(lines)
            self.highlight_student(student_number)
            
            # Zapisz log
            action = "Dodano" if points_change > 0 else "Odjęto"
            self.save_log(f"{action} {abs(points_change)} pkt uczniowi nr {student_number} ({student_name}). Aktualne punkty: {new_points}")
            
        except Exception as e:
            messagebox.showerror("Błąd", f"Wystąpił błąd podczas aktualizacji punktów:\n{str(e)}")

    def add_point(self):
        """Dodaje punkt wybranemu uczniowi"""
        self.update_student_points(self.selected_student_number.get(), 1)

    def subtract_point(self):
        """Odejmuje punkt wybranemu uczniowi"""
        self.update_student_points(self.selected_student_number.get(), -1)

    def update_list_content(self, lines):
        """Aktualizuje zawartość listy zachowując pozycję kursora i widok"""
        current_position = self.editable_list.index(tk.INSERT)
        current_view = self.editable_list.yview()
        
        self.editable_list.delete(1.0, tk.END)
        content_to_insert = '\n'.join(lines).rstrip('\n')
        self.editable_list.insert(1.0, content_to_insert)
        
        # Przywróć pozycję kursora i widok
        try:
            self.editable_list.mark_set(tk.INSERT, current_position)
            self.editable_list.yview_moveto(current_view[0])
        except:
            pass

    def highlight_student(self, student_number):
        """Podświetla wylosowanego ucznia na liście"""
        self.editable_list.tag_remove("highlight", "1.0", tk.END)
        
        content = self.editable_list.get("1.0", tk.END)
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            if line.strip().startswith(f"{student_number}."):
                start_pos = f"{i+1}.0"
                end_pos = f"{i+1}.end"
                
                self.editable_list.tag_add("highlight", start_pos, end_pos)
                self.editable_list.see(start_pos)
                break

    def generate_random_number(self):
        """Generuje losowy numer ucznia"""
        try:
            min_val = int(self.min_entry.get().strip())
            max_val = int(self.max_entry.get().strip())
            
            if min_val >= max_val:
                raise ValueError("Minimalna wartość musi być mniejsza niż maksymalna")
            
            random_num = random.randint(min_val, max_val)
            self.current_text_top.set(f"Wylosowano ucznia z numerem: {random_num}")
            self.selected_student_number.set(random_num)
            
            # Odblokuj przyciski operacji na punktach
            self.add_point_button.config(state='normal')
            self.subtract_point_button.config(state='normal')
            
            self.save_log(f"Wylosowano ucznia z numerem: {random_num} (zakres: {min_val}-{max_val})")
            self.highlight_student(random_num)
            
        except ValueError as e:
            if "invalid literal" in str(e).lower():
                self.current_text_top.set("Błąd: Wprowadź prawidłowe liczby")
            else:
                self.current_text_top.set(f"Błąd: {str(e)}")

    def generate_random_char_or_num(self):
        """Generuje losową literę lub liczbę dla zadania"""
        choice = self.mode_combobox.get()
        
        if choice == "Litery":
            try:
                start = self.start_char_combobox.get()
                end = self.end_char_combobox.get()
                
                start_ord = ord(start)
                end_ord = ord(end)
                
                if start_ord >= end_ord:
                    raise ValueError("Pierwsza litera musi być wcześniejsza w alfabecie niż druga")
                
                random_char = chr(random.randint(start_ord, end_ord))
                self.current_text_bottom.set(f"Wylosowano zadanie: {random_char}")
                self.save_log(f"Wylosowano zadanie: {random_char} (zakres: {start}-{end})")
                
            except ValueError as e:
                self.current_text_bottom.set(f"Błąd: {str(e)}")
        else:  # Liczby
            try:
                min_val = int(self.min_num_entry.get().strip())
                max_val = int(self.max_num_entry.get().strip())
                
                if min_val >= max_val:
                    raise ValueError("Minimalna wartość musi być mniejsza niż maksymalna")
                
                random_num = random.randint(min_val, max_val)
                self.current_text_bottom.set(f"Wylosowano zadanie: {random_num}")
                self.save_log(f"Wylosowano zadanie: {random_num} (zakres: {min_val}-{max_val})")
                
            except ValueError as e:
                if "invalid literal" in str(e).lower():
                    self.current_text_bottom.set("Błąd: Wprowadź prawidłowe liczby")
                else:
                    self.current_text_bottom.set(f"Błąd: {str(e)}")

    def update_mode_display(self, event=None):
        """Aktualizuje widoczność pól w zależności od wybranego trybu"""
        self.char_frame.pack_forget()
        self.num_frame.pack_forget()
        
        if self.mode_combobox.get() == "Litery":
            self.char_frame.pack(anchor=tk.W, fill=tk.X)
        else:
            self.num_frame.pack(anchor=tk.W, fill=tk.X)

    def on_enter_top(self, event):
        """Obsługa klawisza Enter w sekcji uczniów"""
        self.generate_random_number()

    def on_enter_bottom(self, event):
        """Obsługa klawisza Enter w sekcji zadań"""
        self.generate_random_char_or_num()

    def create_gui(self):
        """Tworzy główny interfejs graficzny"""
        self.root = tk.Tk()
        self.root.title("Matematykor")
        self.root.geometry("520x680")
        self.root.resizable(True, True)
        
        # Konfiguracja stylu
        style = ttk.Style()
        style.theme_use('clam')
        
        # Zmienne przechowujące dane
        self.current_text_top = tk.StringVar(value="Losuj ucznia")
        self.current_text_bottom = tk.StringVar(value="Losuj zadanie")
        self.selected_student_number = tk.IntVar(value=0)
        self.current_list_name = tk.StringVar(value="Lista domyślna")
        
        self.create_widgets()
        self.center_window()
        
        self.root.mainloop()

    def create_widgets(self):
        """Tworzy wszystkie widgety interfejsu"""
        # Główna ramka
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.create_student_section(main_frame)
        self.create_task_section(main_frame)
        self.create_list_section(main_frame)
        self.create_footer(main_frame)

    def create_student_section(self, parent):
        """Tworzy sekcję losowania uczniów"""
        top_frame = ttk.LabelFrame(parent, text=" Uczeń ", padding=(15, 10))
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Etykieta z wynikiem
        result_label_top = ttk.Label(top_frame, textvariable=self.current_text_top, 
                                    font=('Arial', 11, 'bold'), foreground='#2c3e50')
        result_label_top.pack(anchor=tk.W, pady=(0, 10))
        
        # Ustawienia zakresu
        range_frame = ttk.Frame(top_frame)
        range_frame.pack(anchor=tk.W, pady=(0, 10))
        
        ttk.Label(range_frame, text="Od numeru:", font=('Arial', 9)).pack(side=tk.LEFT)
        self.min_entry = ttk.Entry(range_frame, width=6, font=('Arial', 9))
        self.min_entry.pack(side=tk.LEFT, padx=(5, 15))
        self.min_entry.insert(0, "1")
        
        ttk.Label(range_frame, text="Do numeru:", font=('Arial', 9)).pack(side=tk.LEFT)
        self.max_entry = ttk.Entry(range_frame, width=6, font=('Arial', 9))
        self.max_entry.pack(side=tk.LEFT, padx=(5, 0))
        self.max_entry.insert(0, "30")
        
        # Przyciski
        student_buttons_frame = ttk.Frame(top_frame)
        student_buttons_frame.pack(anchor=tk.W)
        
        button_generate_num = ttk.Button(student_buttons_frame, text="🎲 Losuj ucznia", 
                                       command=self.generate_random_number)
        button_generate_num.pack(side=tk.LEFT, anchor=tk.W)
        
        self.add_point_button = ttk.Button(student_buttons_frame, text="➕ Dodaj punkt", 
                                          command=self.add_point, state='disabled')
        self.add_point_button.pack(side=tk.LEFT, anchor=tk.W, padx=(10, 0))
        
        self.subtract_point_button = ttk.Button(student_buttons_frame, text="➖ Odejmij punkt", 
                                               command=self.subtract_point, state='disabled')
        self.subtract_point_button.pack(side=tk.LEFT, anchor=tk.W, padx=(5, 0))
        
        # Obsługa klawisza Enter
        self.min_entry.bind('<Return>', self.on_enter_top)
        self.max_entry.bind('<Return>', self.on_enter_top)

    def create_task_section(self, parent):
        """Tworzy sekcję losowania zadań"""
        bottom_frame = ttk.LabelFrame(parent, text=" Zadanie ", padding=(15, 10))
        bottom_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Etykieta z wynikiem
        result_frame = ttk.Frame(bottom_frame)
        result_frame.pack(fill=tk.X, pady=(0, 10))
        
        result_label_bottom = ttk.Label(result_frame, textvariable=self.current_text_bottom, 
                                       font=('Arial', 11, 'bold'), foreground='#2c3e50')
        result_label_bottom.pack(anchor=tk.W)
        
        # Wybór trybu
        mode_frame = ttk.Frame(bottom_frame)
        mode_frame.pack(anchor=tk.W, pady=(0, 10))
        
        ttk.Label(mode_frame, text="Tryb:", font=('Arial', 9)).pack(side=tk.LEFT)
        self.mode_combobox = ttk.Combobox(mode_frame, values=["Litery", "Liczby"], 
                                         state="readonly", width=10, font=('Arial', 9))
        self.mode_combobox.pack(side=tk.LEFT, padx=(10, 0))
        self.mode_combobox.set("Litery")
        
        # Ramka dla ustawień
        settings_frame = ttk.Frame(bottom_frame)
        settings_frame.pack(anchor=tk.W, pady=(0, 10), fill=tk.X)
        settings_frame.configure(height=35)
        
        # Ustawienia dla liter
        self.char_frame = ttk.Frame(settings_frame)
        
        ttk.Label(self.char_frame, text="Od litery:", font=('Arial', 9)).pack(side=tk.LEFT)
        self.start_char_combobox = ttk.Combobox(self.char_frame, values=self.alphabet_letters, 
                                               state="readonly", width=4, font=('Arial', 9))
        self.start_char_combobox.pack(side=tk.LEFT, padx=(5, 15))
        self.start_char_combobox.set("A")
        
        ttk.Label(self.char_frame, text="Do litery:", font=('Arial', 9)).pack(side=tk.LEFT)
        self.end_char_combobox = ttk.Combobox(self.char_frame, values=self.alphabet_letters, 
                                             state="readonly", width=4, font=('Arial', 9))
        self.end_char_combobox.pack(side=tk.LEFT, padx=(5, 0))
        self.end_char_combobox.set("Z")
        
        # Ustawienia dla liczb
        self.num_frame = ttk.Frame(settings_frame)
        
        ttk.Label(self.num_frame, text="Od liczby:", font=('Arial', 9)).pack(side=tk.LEFT)
        self.min_num_entry = ttk.Entry(self.num_frame, width=6, font=('Arial', 9))
        self.min_num_entry.pack(side=tk.LEFT, padx=(5, 15))
        self.min_num_entry.insert(0, "1")
        
        ttk.Label(self.num_frame, text="Do liczby:", font=('Arial', 9)).pack(side=tk.LEFT)
        self.max_num_entry = ttk.Entry(self.num_frame, width=6, font=('Arial', 9))
        self.max_num_entry.pack(side=tk.LEFT, padx=(5, 0))
        self.max_num_entry.insert(0, "10")
        
        # Przycisk losowania zadania
        button_frame = ttk.Frame(bottom_frame)
        button_frame.pack(fill=tk.X, pady=(5, 0))
        
        button_generate_char = ttk.Button(button_frame, text="🎯 Losuj zadanie", 
                                        command=self.generate_random_char_or_num)
        button_generate_char.pack(anchor=tk.W)
        
        # Obsługa zmiany trybu i klawisza Enter
        self.mode_combobox.bind("<<ComboboxSelected>>", self.update_mode_display)
        self.min_num_entry.bind('<Return>', self.on_enter_bottom)
        self.max_num_entry.bind('<Return>', self.on_enter_bottom)
        
        self.update_mode_display()

    def create_list_section(self, parent):
        """Tworzy sekcję listy uczniów"""
        list_frame = ttk.LabelFrame(parent, text=" Lista uczniów ", padding=(15, 10))
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 15))
        
        # Obszar tekstowy z listą
        text_frame = ttk.Frame(list_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.editable_list = tk.Text(text_frame, wrap=tk.WORD, yscrollcommand=scrollbar.set, 
                                    height=6, font=('Arial', 9), bg='#f8f9fa', 
                                    relief='solid', borderwidth=1, padx=5, pady=5)
        self.editable_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.editable_list.yview)
        
        # Konfiguracja podświetlenia
        self.editable_list.tag_config("highlight", background="yellow", foreground="black")
        
        # Tekst domyślny
        placeholder_text = """1. Jan Kowalski
2. Anna Nowak
3. Piotr Wiśniewski

Tutaj możesz edytować listę uczniów..."""
        self.editable_list.insert(tk.END, placeholder_text)
        
        # Nazwa aktualnej listy
        list_name_label = ttk.Label(list_frame, textvariable=self.current_list_name, 
                                   font=('Arial', 9, 'italic'), foreground='#666666')
        list_name_label.pack(anchor=tk.W, pady=(5, 5))
        
        # Przyciski zarządzania listą
        load_button_frame = ttk.Frame(list_frame)
        load_button_frame.pack(fill=tk.X, pady=(1, 0))
        
        load_button = ttk.Button(load_button_frame, text="📁 Wczytaj listę", 
                               command=self.load_list_from_file)
        load_button.pack(side=tk.LEFT, anchor=tk.W)
        
        save_button = ttk.Button(load_button_frame, text="💾 Zapisz listę", 
                               command=self.save_list_to_file)
        save_button.pack(side=tk.LEFT, anchor=tk.W, padx=(5, 0))
        
        log_button = ttk.Button(load_button_frame, text="📋 Historia", 
                              command=self.show_logs)
        log_button.pack(side=tk.LEFT, anchor=tk.W, padx=(5, 0))

    def create_footer(self, parent):
        """Tworzy stopkę aplikacji"""
        footer_label = ttk.Label(parent, text="Matematykor | Wersja 0.1", 
                                font=('Arial', 10), foreground='gray')
        footer_label.pack(side=tk.BOTTOM, pady=(0, 5))

    def center_window(self):
        """Centruje okno na ekranie"""
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (self.root.winfo_width() // 2)
        y = (self.root.winfo_screenheight() // 2) - (self.root.winfo_height() // 2)
        self.root.geometry(f"+{x}+{y}")

    def run(self):
        """Uruchamia aplikację"""
        self.create_gui()

def main():
    app = MatemykorApp()
    app.run()

if __name__ == "__main__":
    main()