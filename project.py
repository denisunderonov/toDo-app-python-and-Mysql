import mysql.connector
import tkinter
from tkinter import messagebox, simpledialog, Tk, Label, Button, Listbox, END
from tkinter import ttk


class TargetTracer:
    def __init__(self):
        self.root = Tk()
        self.root.title("Задачник")
        self.root.geometry("600x400")
        self.root.config(bg="#FAEBD7")

        self.targets = []

        # Создаем подключение к базе данных MySQL
        self.conn = mysql.connector.connect(
            host="localhost",
            user="root",
            database="doapp"
        )

        self.create_table()
        self.create_widgets()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS targets
                          (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255), description TEXT, date DATE, achieved INT)''')
        self.conn.commit()

        # Добавляем таблицы для каждой из категорий: учеба, работа, личное
        cursor.execute('''CREATE TABLE IF NOT EXISTS education_targets
                          (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255), description TEXT, date DATE, achieved INT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS work_targets
                          (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255), description TEXT, date DATE, achieved INT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS personal_targets
                          (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255), description TEXT, date DATE, achieved INT)''')
        self.conn.commit()

    def add_target(self):
        category = self.category_var.get()  # Получаем выбранную категорию
        name = simpledialog.askstring(
            "Добавить цель", "Введите название цели:")
        if name:
            description = simpledialog.askstring(
                "Добавить цель", "Введите описание цели:")
            date = simpledialog.askstring(
                "Добавить цель", "Введите дату достижения цели:")
            achieved = 0  # Исходно цель не достигнута

            cursor = self.conn.cursor()

            # Определяем, в какую таблицу добавлять цель
            if category == "Учеба":
                cursor.execute("INSERT INTO education_targets (name, description, date, achieved) VALUES (%s, %s, %s, %s)",
                               (name, description, date, achieved))
            elif category == "Работа":
                cursor.execute("INSERT INTO work_targets (name, description, date, achieved) VALUES (%s, %s, %s, %s)",
                               (name, description, date, achieved))
            elif category == "Личное":
                cursor.execute("INSERT INTO personal_targets (name, description, date, achieved) VALUES (%s, %s, %s, %s)",
                               (name, description, date, achieved))

            self.conn.commit()
            self.update_targets_list()

    # Остальные методы остаются, но их нужно изменить в соответствии с категориями

    def mark_achieved(self):
        selected_target = self.targets_listbox.curselection()
        if selected_target:
            target_id = self.targets[selected_target[0]][0]
            cursor = self.conn.cursor()

            category = self.category_var.get()

            # Определяем, в какой таблице обновлять цель
            if category == "Учеба":
                cursor.execute(
                    "UPDATE education_targets SET achieved = 1 WHERE id = %s", (target_id,))
            elif category == "Работа":
                cursor.execute(
                    "UPDATE work_targets SET achieved = 1 WHERE id = %s", (target_id,))
            elif category == "Личное":
                cursor.execute(
                    "UPDATE personal_targets SET achieved = 1 WHERE id = %s", (target_id,))

            self.conn.commit()
            self.update_targets_list()

    def delete_target(self):
        selected_target = self.targets_listbox.curselection()
        if selected_target:
            target_id = self.targets[selected_target[0]][0]
            cursor = self.conn.cursor()

            category = self.category_var.get()

            # Определяем, из какой таблицы удалять цель
            if category == "Учеба":
                cursor.execute(
                    "DELETE FROM education_targets WHERE id = %s", (target_id,))
            elif category == "Работа":
                cursor.execute(
                    "DELETE FROM work_targets WHERE id = %s", (target_id,))
            elif category == "Личное":
                cursor.execute(
                    "DELETE FROM personal_targets WHERE id = %s", (target_id,))

            self.conn.commit()
            self.update_targets_list()

    def show_targets_list(self):
        self.targets_listbox.delete(0, END)
        cursor = self.conn.cursor()

        category = self.category_var.get()

        # Определяем, из какой таблицы загружать цели
        if category == "Учеба":
            cursor.execute(
                "SELECT id, name, description, date, achieved FROM education_targets")
        elif category == "Работа":
            cursor.execute(
                "SELECT id, name, description, date, achieved FROM work_targets")
        elif category == "Личное":
            cursor.execute(
                "SELECT id, name, description, date, achieved FROM personal_targets")

        self.targets = cursor.fetchall()
        for target in self.targets:
            status = "Достигнуто" if target[4] else "Не достигнуто"
            self.targets_listbox.insert(
                END, f"{target[1]} - {target[2]} ({target[3]}) - {status}")

    def update_targets_list(self):
        self.show_targets_list()

    def create_widgets(self):
        label = Label(self.root, text="Задачник", font=(
            "Arial", 24), bg="#FAEBD7", fg="black")
        label.pack(pady=10)

        style = ttk.Style()
        style.configure("TButton", padding=6, relief="flat",
                        background="#008080", foreground="black")
        style.map("TButton", background=[("active", "#006666")])

        self.category_var = tkinter.StringVar()

        # Выпадающий список с категориями
        category_combobox = ttk.Combobox(
            self.root, textvariable=self.category_var, values=["Учеба", "Работа", "Личное"])
        category_combobox.set("Учеба")  # Устанавливаем значение по умолчанию
        category_combobox.pack(pady=5)

        add_button = ttk.Button(
            self.root, text="Добавить цель", command=self.add_target, style="TButton")
        add_button.pack(pady=5)

        mark_achieved_button = ttk.Button(
            self.root, text="Отметить достигнутой", command=self.mark_achieved, style="TButton")
        mark_achieved_button.pack(pady=5)

        delete_button = ttk.Button(
            self.root, text="Удалить цель", command=self.delete_target, style="TButton")
        delete_button.pack(pady=5)

        show_list_button = ttk.Button(
            self.root, text="Показать список целей", command=self.show_targets_list, style="TButton")
        show_list_button.pack(pady=5)

        self.targets_listbox = Listbox(
            self.root, selectmode="SINGLE", width=50, height=10, font=("Arial", 12))
        self.targets_listbox.pack(pady=10)

        self.show_targets_list()  # Инициализация списка целей

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = TargetTracer()
    app.run()
