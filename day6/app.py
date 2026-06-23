import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from mysql.connector import Error

# ПОДКЛЮЧЕНИЕ К БД 
def connect_db():
    """Подключение к базе данных MySQL"""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",           
            password="elmira1601dav2008#$$",     
            database="myprojectdb"  
        )
        return connection
    except Error as e:
        messagebox.showerror("Ошибка БД", f"Не удалось подключиться: {e}")
        return None

# ГЛАВНЫЙ КЛАСС ПРИЛОЖЕНИЯ
class DatabaseApp:
    def __init__(self, root, table_name, columns):
        self.root = root
        self.table_name = table_name
        self.columns = columns
        self.root.title(f"Управление таблицей: {table_name}")
        self.root.geometry("900x600")

        self.create_widgets()
        self.refresh_table()

    def create_widgets(self):
        """Создание интерфейса"""
        # Рамка для полей ввода
        input_frame = tk.Frame(self.root)
        input_frame.pack(pady=10)

        self.entries = {}
        col_index = 0
        for col in self.columns:
            if col.get('pk') and col.get('auto_increment'):
                continue

            label = tk.Label(input_frame, text=f"{col['label']}:")
            label.grid(row=0, column=col_index*2, padx=5, pady=5, sticky="e")

            entry = tk.Entry(input_frame, width=30)
            entry.grid(row=0, column=col_index*2+1, padx=5, pady=5)
            self.entries[col['name']] = entry
            col_index += 1

        # Кнопки
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Добавить", command=self.add_record,
                  bg="#90EE90", width=12).grid(row=0, column=0, padx=5)
        tk.Button(button_frame, text="Обновить", command=self.update_record,
                  bg="#FFD700", width=12).grid(row=0, column=1, padx=5)
        tk.Button(button_frame, text="Удалить", command=self.delete_record,
                  bg="#FF6347", width=12).grid(row=0, column=2, padx=5)
        tk.Button(button_frame, text="Очистить", command=self.clear_entries,
                  width=12).grid(row=0, column=3, padx=5)
        tk.Button(button_frame, text="Показать всех", command=self.refresh_table,
                  width=15).grid(row=0, column=4, padx=5)

        # Таблица
        tree_frame = tk.Frame(self.root)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        scroll_y = tk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        columns_display = [col['name'] for col in self.columns]
        self.tree = ttk.Treeview(tree_frame, columns=columns_display, show="headings",
                                 yscrollcommand=scroll_y.set)
        scroll_y.config(command=self.tree.yview)

        for col in self.columns:
            self.tree.heading(col['name'], text=col['label'])
            self.tree.column(col['name'], width=120, anchor="center")

        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    def refresh_table(self):
        """Обновить данные"""
        for row in self.tree.get_children():
            self.tree.delete(row)

        conn = connect_db()
        if not conn:
            return
        cursor = conn.cursor()
        columns_names = [col['name'] for col in self.columns]
        query = f"SELECT {', '.join(columns_names)} FROM {self.table_name}"

        try:
            cursor.execute(query)
            for row in cursor.fetchall():
                self.tree.insert("", tk.END, values=row)
        except Error as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {e}")
        finally:
            cursor.close()
            conn.close()

    def on_select(self, event):
        """Выбор строки"""
        selected = self.tree.selection()
        if not selected:
            return
        values = self.tree.item(selected[0])['values']
        for i, col in enumerate(self.columns):
            col_name = col['name']
            if col_name in self.entries:
                self.entries[col_name].delete(0, tk.END)
                self.entries[col_name].insert(0, str(values[i]) if values[i] is not None else "")

    def get_pk_name(self):
        for col in self.columns:
            if col.get('pk'):
                return col['name']
        return None

    def add_record(self):
        """Добавить запись"""
        values = {}
        for col_name, entry in self.entries.items():
            values[col_name] = entry.get().strip()

        # Проверка обязательных полей
        for col in self.columns:
            col_name = col['name']
            if col.get('required') and col_name in self.entries and not values[col_name]:
                messagebox.showwarning("Ошибка", f"Поле '{col['label']}' обязательно")
                return

        conn = connect_db()
        if not conn:
            return
        cursor = conn.cursor()

        columns_names = list(values.keys())
        placeholders = ", ".join(["%s"] * len(columns_names))
        query = f"INSERT INTO {self.table_name} ({', '.join(columns_names)}) VALUES ({placeholders})"

        try:
            cursor.execute(query, list(values.values()))
            conn.commit()
            messagebox.showinfo("Успех", "Запись добавлена")
            self.clear_entries()
            self.refresh_table()
        except Error as e:
            messagebox.showerror("Ошибка БД", str(e))
        finally:
            cursor.close()
            conn.close()

    def update_record(self):
        """Обновить запись"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите запись для обновления")
            return

        pk_name = self.get_pk_name()
        if not pk_name:
            return

        values_current = self.tree.item(selected[0])['values']
        pk_index = [col['name'] for col in self.columns].index(pk_name)
        pk_value = values_current[pk_index]

        new_values = {}
        for col_name, entry in self.entries.items():
            new_values[col_name] = entry.get().strip()

        conn = connect_db()
        if not conn:
            return
        cursor = conn.cursor()

        set_clause = ", ".join([f"{col} = %s" for col in new_values.keys()])
        query = f"UPDATE {self.table_name} SET {set_clause} WHERE {pk_name} = %s"

        try:
            params = list(new_values.values()) + [pk_value]
            cursor.execute(query, params)
            conn.commit()
            messagebox.showinfo("Успех", "Запись обновлена")
            self.refresh_table()
        except Error as e:
            messagebox.showerror("Ошибка БД", str(e))
        finally:
            cursor.close()
            conn.close()

    def delete_record(self):
        """Удалить запись"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите запись для удаления")
            return

        if not messagebox.askyesno("Подтверждение", "Удалить запись?"):
            return

        pk_name = self.get_pk_name()
        if not pk_name:
            return

        values = self.tree.item(selected[0])['values']
        pk_index = [col['name'] for col in self.columns].index(pk_name)
        pk_value = values[pk_index]

        conn = connect_db()
        if not conn:
            return
        cursor = conn.cursor()

        query = f"DELETE FROM {self.table_name} WHERE {pk_name} = %s"
        try:
            cursor.execute(query, (pk_value,))
            conn.commit()
            messagebox.showinfo("Успех", "Запись удалена")
            self.clear_entries()
            self.refresh_table()
        except Error as e:
            messagebox.showerror("Ошибка БД", str(e))
        finally:
            cursor.close()
            conn.close()

    def clear_entries(self):
        """Очистить поля"""
        for entry in self.entries.values():
            entry.delete(0, tk.END)

# ЗАПУСК 
def main():
    root = tk.Tk()
    
    # Конфигурация для таблицы "Товары" (без поля "остаток")
    columns = [
        {"name": "id_товара", "label": "ID товара", "pk": True, "auto_increment": True},
        {"name": "название", "label": "Название", "required": True},
        {"name": "цена", "label": "Цена", "required": True},
        {"name": "описание", "label": "Описание", "required": False}
    ]
    
    app = DatabaseApp(root, table_name="Товары", columns=columns)
    root.mainloop()

if __name__ == "__main__":
    main()