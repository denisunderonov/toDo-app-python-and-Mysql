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

        self.create_tables()
        self.create_widgets()

    def create_tables(self):
        cursor = self.conn.cursor()

        # Создаем таблицу категорий
        cursor.execute('''CREATE TABLE IF NOT EXISTS categories
                          (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(20) UNIQUE)''')

        # Создаем таблицу целей
        cursor.execute('''CREATE TABLE IF NOT EXISTS targets
                          (id INT AUTO_INCREMENT PRIMARY KEY, category_id INT, name VARCHAR(255), description TEXT, date DATE, achieved INT,
                          FOREIGN KEY (category_id) REFERENCES categories(id))''')

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

            try:
                # Пытаемся добавить категорию, если ее нет
                cursor.execute("INSERT INTO categories (name) VALUES (%s) ON DUPLICATE KEY UPDATE id=LAST_INSERT_ID(id)",
                               (category,))
                self.conn.commit()

                # Получаем ID категории
                cursor.execute(
                    "SELECT id FROM categories WHERE name = %s", (category,))
                category_id = cursor.fetchone()[0]

                # Добавляем цель
                cursor.execute("INSERT INTO targets (category_id, name, description, date, achieved) VALUES (%s, %s, %s, %s, %s)",
                               (category_id, name, description, date, achieved))

                self.conn.commit()
                self.update_targets_list()

            except mysql.connector.IntegrityError as e:
                messagebox.showerror(
                    "Ошибка", "Ошибка добавления категории: {}".format(str(e)))

    def mark_achieved(self):
        selected_target = self.targets_listbox.curselection()
        if selected_target:
            target_id = self.targets[selected_target[0]][0]
            cursor = self.conn.cursor()

            try:
                # Отмечаем цель как достигнутую
                cursor.execute(
                    "UPDATE targets SET achieved = 1 WHERE id = %s", (target_id,))

                self.conn.commit()
                self.update_targets_list()

            except mysql.connector.Error as e:
                messagebox.showerror(
                    "Ошибка", "Ошибка при отметке цели: {}".format(str(e)))

    def delete_target(self):
        selected_target = self.targets_listbox.curselection()
        if selected_target:
            target_id = self.targets[selected_target[0]][0]
            cursor = self.conn.cursor()

            try:
                # Удаляем цель
                cursor.execute(
                    "DELETE FROM targets WHERE id = %s", (target_id,))

                self.conn.commit()
                self.update_targets_list()

            except mysql.connector.Error as e:
                messagebox.showerror(
                    "Ошибка", "Ошибка при удалении цели: {}".format(str(e)))

    def show_targets_list(self):
        self.targets_listbox.delete(0, END)
        cursor = self.conn.cursor()

        try:
            # Загружаем цели из общей таблицы
            cursor.execute('''SELECT t.id, c.name, t.name, t.description, t.date, t.achieved
                              FROM targets t
                              JOIN categories c ON t.category_id = c.id''')

            self.targets = cursor.fetchall()
            for target in self.targets:
                status = "Достигнуто" if target[5] else "Не достигнуто"
                self.targets_listbox.insert(
                    END, f"{target[1]} - {target[2]} ({target[3]}) - {status}")

        except mysql.connector.Error as e:
            messagebox.showerror(
                "Ошибка", "Ошибка при загрузке целей: {}".format(str(e)))

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

        self.targets_listbox = Listbox(
            self.root, selectmode="SINGLE", width=50, height=10, font=("Arial", 12))
        self.targets_listbox.pack(pady=10)

        self.show_targets_list()  # Инициализация списка целей

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = TargetTracer()
    app.run()
