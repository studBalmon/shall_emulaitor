import unittest
import os
import shutil
import json
import tarfile
from main import ShellEmulator  # Импорт вашего эмулятора

class TestShellEmulator(unittest.TestCase):
    def setUp(self):
        """Настройка тестового окружения перед каждым тестом"""
        self.username = "testuser"
        self.virtual_fs_tar = "test_virtual_fs.tar"
        self.virtual_fs_dir = "./virtual_fs"
        self.log_file = "test_log.json"
        self.start_script = None

        # Создаем тестовую файловую систему
        os.mkdir("test_fs")
        with open("test_fs/file1.txt", "w") as f:
            f.write("Line 1\nLine 2\nLine 3\n")
        os.mkdir("test_fs/empty_dir")
        os.mkdir("test_fs/non_empty_dir")
        with open("test_fs/non_empty_dir/file2.txt", "w") as f:
            f.write("Another file")

        # Упаковываем её в tar
        with tarfile.open(self.virtual_fs_tar, "w") as tar:
            tar.add("test_fs", arcname=".")

        # Инициализируем ShellEmulator
        self.shell = ShellEmulator(self.username, self.virtual_fs_tar, self.log_file, self.start_script)

    def tearDown(self):
        """Очистка после каждого теста"""
        if os.path.exists(self.virtual_fs_tar):
            os.remove(self.virtual_fs_tar)
        if os.path.exists("test_fs"):
            shutil.rmtree("test_fs")
        if os.path.exists(self.virtual_fs_dir):
            shutil.rmtree(self.virtual_fs_dir)
        if os.path.exists(self.log_file):
            os.remove(self.log_file)

    def test_ls(self):
        """Тест команды ls"""
        self.shell.ls([])
        self.shell.ls(["non_existent_dir"])  # Ожидается сообщение об ошибке
        self.shell.ls(["-R"])  # Рекурсивный вывод

    def test_cd(self):
        """Тест команды cd"""
        self.shell.cd(["empty_dir"])
        self.assertEqual(self.shell.current_dir, "empty_dir")
        self.shell.cd([".."])
        self.assertEqual(self.shell.current_dir, ".")
        self.shell.cd(["non_existent_dir"])  # Ожидается сообщение об ошибке

    def test_rmdir(self):
        """Тест команды rmdir"""
        self.shell.rmdir(["empty_dir"])  # Успешное удаление пустого каталога
        self.assertFalse(os.path.exists(self.shell._get_real_path("empty_dir")))

        self.shell.rmdir(["non_empty_dir"])  # Ожидается сообщение об ошибке
        self.assertTrue(os.path.exists(self.shell._get_real_path("non_empty_dir")))

        self.shell.rmdir(["-p", "empty_dir"])  # Удаление с родителями

    def test_tail(self):
        """Тест команды tail"""
        self.shell.tail(["test_fs/file1.txt"])  # Успешный вывод последних 10 строк
        self.shell.tail(["-n", "2", "test_fs/file1.txt"])  # Вывод последних 2 строк
        self.shell.tail(["non_existent_file.txt"])  # Ожидается сообщение об ошибке

    def test_exit(self):
        """Тест команды exit"""
        self.shell.clean_up()
        self.assertFalse(os.path.exists(self.virtual_fs_dir))

    def test_logging(self):
        """Проверка логирования действий"""
        self.shell.ls([])
        self.shell._log_action("input", f"{self.username}:{self.shell.current_dir}$ ")
        self.shell._write_log()
        self.shell.cd(["empty_dir"])
        self.shell._log_action("input", f"{self.username}:{self.shell.current_dir}$ ")
        self.shell._write_log()
        self.shell.rmdir(["empty_dir"])
        self.shell._log_action("input", f"{self.username}:{self.shell.current_dir}$ ")
        self.shell._write_log()
        self.shell.tail(["test_fs/file1.txt"])
        self.shell._log_action("input", f"{self.username}:{self.shell.current_dir}$ ")
        self.shell._write_log()

        # Чтение логов из файла
        with open(self.log_file, "r") as log:
            log_data = json.load(log)

        # Проверка длины и содержания логов
        self.assertEqual(len(log_data), 4)  # Ожидается 4 записи
        self.assertEqual(log_data[0]["action"], "input")
        self.assertEqual(log_data[1]["action"], "input")
        self.assertEqual(log_data[2]["action"], "input")
        self.assertEqual(log_data[3]["action"], "input")


if __name__ == "__main__":
    unittest.main()
