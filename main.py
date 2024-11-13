import zipfile
import json
import io
import sys


# Функция для создания архива виртуальной файловой системы (zip)
def create_sample_vfs(zip_path):
    """Создает архив виртуальной файловой системы (zip) с несколькими файлами и папками."""
    with zipfile.ZipFile(zip_path, "w") as vfs_zip:
        # Создаем структуру директорий и файлов внутри архива
        vfs_zip.writestr("dir1/file1.txt", "This is file1 in dir1")
        vfs_zip.writestr("dir1/file2.txt", "This is file2 in dir1")
        vfs_zip.writestr("dir2/file1.txt", "This is file1 in dir2")
        vfs_zip.writestr("dir2/subdir/file1.txt", "This is file1 in subdir of dir2")
        vfs_zip.writestr("file_in_root.txt", "This is a file in the root")


# Функция для создания конфигурационного файла с указанием пути к архиву и имени пользователя
def create_config(config_path, vfs_zip_path):
    """Создает конфигурационный файл с указанным путем к архиву."""
    config = {
        "username": "user",  # Имя пользователя для вывода в приглашении
        "vfs_zip_path": vfs_zip_path,  # Путь к виртуальной файловой системе (zip)
    }
    with open(config_path, "w") as config_file:
        json.dump(config, config_file, indent=4)


# Основной класс эмулятора оболочки
class ShellEmulator:
    def __init__(self, config_path):
        self.load_config(config_path)
        self.vfs = self.load_vfs(self.vfs_zip_path)
        self.current_dir = "/"
        self.user = self.config["username"]

    def load_config(self, config_path):
        """Загружает конфигурационный файл."""
        with open(config_path, "r") as file:
            self.config = json.load(file)
        self.vfs_zip_path = self.config["vfs_zip_path"]

    def load_vfs(self, zip_path):
        """Загружает архив виртуальной файловой системы в память."""
        with open(zip_path, "rb") as f:
            zip_data = io.BytesIO(f.read())
        return zipfile.ZipFile(zip_data)

    def execute_command(self, command):
        """Выполняет команду."""
        if command.startswith("ls"):
            self.ls()
        elif command.startswith("cd"):
            self.cd(command)
        elif command.startswith("exit"):
            sys.exit(0)
        elif command.startswith("cp"):
            self.cp(command)
        elif command.startswith("tree"):
            self.tree()
        else:
            print(f"Unknown command: {command}")

    def ls(self):
        """Выводит список файлов и директорий в текущей директории."""
        print(f"Listing directory: {self.current_dir}")
        files = self.get_files_in_directory(self.current_dir)
        if files:
            for file in files:
                print(file)
        else:
            print("No files or directories found.")

    def get_files_in_directory(self, path):
        """Получает список файлов и директорий в указанной директории."""
        files = set()
        for file in self.vfs.namelist():
            if f"/{file}".startswith(path):
                files.add(
                    file.split("/")[0]
                    if path == "/"
                    else ("/" + file).replace(path, "", 1).split("/")[0]
                )
            elif path == "/":
                if "/" not in file:
                    files.add(file)
                else:
                    files.add(file.split("/")[0])
        return files

    def cd(self, command):
        try:
            """Изменяет текущую рабочую директорию."""
            new_dir = self.is_directory(command.split(" ")[1])
            if command.split(" ")[1] == "..":
                # Переход к родительской директории
                self.current_dir = "/"
            elif new_dir:
                self.current_dir = new_dir
            else:
                print("It's not valid directory.")
        except Exception as ex:
            print(ex)

    def is_directory(self, path):
        """Проверяет, является ли путь директорией."""
        if path == "/":
            return "/"  # Корневая директория всегда существует
        for files in self.vfs.namelist():
            if self.current_dir + path + "/" in f"/{files}/":
                return self.current_dir + path + "/"
        return False

    def cp(self, command):
        """Копирует файл."""
        parts = command.split(" ")
        if len(parts) != 3:
            print("Usage: cp <source> <destination>")
            return
        source, dest = parts[1], parts[2]
        if source in self.vfs.namelist():
            with open(dest, "wb") as f:
                f.write(self.vfs.read(source))
            print(f"Copied {source} to {dest}")
        else:
            print(f"Source file {source} does not exist.")

    def tree(self):
        """Выводит структуру дерева директорий."""
        print("Directory structure:")
        self.print_tree(self.current_dir)

    def print_tree(self, path, level=0):
        """Рекурсивно выводит дерево файлов и директорий."""
        for file in self.vfs.namelist():
            if file.startswith(path):
                print("  " * level + file.split("/")[-1])
                if file.endswith("/"):
                    self.print_tree(file, level + 1)

    def run(self):
        """Запускает оболочку и выполняет команды в цикле."""
        while True:
            command = input(f"{self.user}@emulator:{self.current_dir} $ ")
            self.execute_command(command)


# Путь для создания файлов
vfs_zip_path = "sample_vfs.zip"
config_path = "config.json"

# Создание виртуальной файловой системы (zip)
create_sample_vfs(vfs_zip_path)

# Создание конфигурационного файла
create_config(config_path, vfs_zip_path)

# Запуск эмулятора
if __name__ == "__main__":
    emulator = ShellEmulator(config_path)
    emulator.run()
