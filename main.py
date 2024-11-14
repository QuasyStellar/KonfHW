import os
import zipfile
import json


class VirtualFileSystem:
    def __init__(self, zip_path):
        self.zip_path = zip_path
        self.zip_file = None
        self.current_directory = "/"

    def open(self):
        """Открыть VFS (ZIP-архив)."""
        self.zip_file = zipfile.ZipFile(self.zip_path, "r")

    def list_dir(self, path):
        """Показать содержимое директории."""
        files = set()
        path = path if path == "/" else f"{path}/"
        print(self.zip_file.namelist())
        self.zip_file.namelist().append("1")
        print(self.zip_file.namelist())
        for file in self.zip_file.namelist():
            if f"/{file}".startswith(path):
                # Убираем префикс пути для отображения относительных путей
                rel_path = f"/{file}"[len(path) :]
                if "/" not in rel_path:  # файл
                    files.add(rel_path)
                else:
                    files.add(rel_path.split("/")[0])
        return "\n".join(files)

    def change_dir(self, path):
        """Изменить текущую директорию."""
        if path == "/":
            self.current_directory = "/"
        elif path.startswith("/"):
            self.current_directory = path
        else:
            self.current_directory = os.path.join(self.current_directory, path)

    def copy_file(self, source, dest):
        """Копирование файла."""
        with self.zip_file.open(source, "r") as src_file:
            file_data = src_file.read()

        dest_file_path = os.path.join(self.current_directory, dest)
        with open(dest_file_path, "wb") as dest_file:
            dest_file.write(file_data)

    def close(self):
        """Закрытие ZIP-архива."""
        self.zip_file.close()


class Shell:
    def __init__(self, config_path):
        self.config = self.load_config(config_path)
        self.vfs = VirtualFileSystem(self.config["vfs_path"])
        self.username = self.config["username"]
        self.vfs.open()

    def load_config(self, config_path):
        """Загрузить конфигурацию из файла."""
        with open(config_path, "r") as f:
            return json.load(f)

    def run_command(self, command):
        """Обработка команды."""
        args = command.strip().split()
        if not args:
            return

        cmd = args[0]
        if cmd == "exit":
            self.vfs.close()
            exit()
        elif cmd == "ls":
            print(self.vfs.list_dir(self.vfs.current_directory))
        elif cmd == "cd":
            if len(args) > 1:
                self.vfs.change_dir(args[1])
        elif cmd == "cp":
            if len(args) > 2:
                self.vfs.copy_file(args[1], args[2])
        elif cmd == "tree":
            self.tree(self.vfs.current_directory, 0)
        else:
            print(f"Unknown command: {cmd}")

    def tree(self, path, indent):
        """Вывод структуры каталогов."""
        print("".join(f"{x}\n" for x in self.vfs.zip_file.namelist()))

    def run(self):
        """Главный цикл оболочки."""
        while True:
            current_path = self.vfs.current_directory
            command = input(f"{self.username}@{current_path}$ ")
            self.run_command(command)


if __name__ == "__main__":
    shell = Shell("config.json")
    shell.run()
