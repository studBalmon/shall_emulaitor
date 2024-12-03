import os
import tarfile
import json
import argparse
import shutil
from pathlib import Path


class ShellEmulator:
    def __init__(self, username, tar_path, log_file, start_script):
        self.username = username
        self.tar_path = tar_path
        self.log_file = log_file
        self.start_script = start_script
        self.current_dir = "/"
        self.virtual_fs_root = "./virtual_fs"
        self.log_data = []

        # Подготовка виртуальной файловой системы
        self._prepare_virtual_fs()

    def _prepare_virtual_fs(self):
        # Очистка и создание новой директории для виртуальной ФС
        if os.path.exists(self.virtual_fs_root):
            shutil.rmtree(self.virtual_fs_root)
        os.mkdir(self.virtual_fs_root)

        # Распаковка tar-архива в виртуальную ФС
        with tarfile.open(self.tar_path, "r") as tar:
            tar.extractall(self.virtual_fs_root)

    def _log_action(self, action, details=None):
        entry = {"user": self.username, "action": action, "details": details}
        self.log_data.append(entry)

    def _write_log(self):
        with open(self.log_file, "w") as log_file:
            json.dump(self.log_data, log_file, indent=4)

    def _get_real_path(self, path):
        if not path.startswith("/"):
            path = os.path.join(self.current_dir, path)
        return os.path.normpath(os.path.join(self.virtual_fs_root, path.strip("/")))

        def clean_up(self):
        if os.path.exists(self.virtual_fs_root):
            shutil.rmtree(self.virtual_fs_root)
            print("Temporary virtual file system removed.")

    def run(self):
        if self.start_script:
            self._execute_script(self.start_script)

        while True:
            try:
                command = input(f"{self.username}:{self.current_dir}$ ").strip()
                if not command:
                    continue

                self._log_action("input", command)
                parts = command.split()
                cmd, args = parts[0], parts[1:]

                if cmd == "exit":
                    print("Exiting shell...")
                    self._write_log()
                    self.clean_up()
                    break
                elif cmd == "ls":
                    self.ls(args)
                elif cmd == "cd":
                    self.cd(args)
                elif cmd == "rmdir":
                    self.rmdir(args)
                elif cmd == "tail":
                    self.tail(args)
                else:
                    print(f"Unknown command: {cmd}")
            except (KeyboardInterrupt, EOFError):
                print("\nExiting shell...")
                self._write_log()
                self.clean_up()
                break


    def _execute_script(self, script_path):
        try:
            with open(script_path, "r") as script_file:
                for line in script_file:
                    line = line.strip()
                    if line:
                        self._log_action("script_command", line)
                        print(f"{self.username}:{self.current_dir}$ {line}")
                        self.run_command(line)
        except FileNotFoundError:
            print(f"Start script not found: {script_path}")

    def run_command(self, command):
        parts = command.split()
        cmd, args = parts[0], parts[1:]

        if cmd == "ls":
            self.ls(args)
        elif cmd == "cd":
            self.cd(args)
        elif cmd == "rmdir":
            self.rmdir(args)
        elif cmd == "tail":
            self.tail(args)
        else:
            print(f"Unknown command: {cmd}")

        def ls(self, args):
        recursive = "-R" in args
        path = self._get_real_path(args[0] if args and args[0] != "-R" else ".")
        
        if not os.path.exists(path):
            print(f"ls: cannot access '{path}': No such file or directory")
            return

        def list_directory(directory, show_header=True):
            relative_path = directory[len(self.virtual_fs_root):] or "/"
            if show_header:
                print(f"{relative_path}:")

            try:
                items = sorted(os.listdir(directory)) 
                output = []
                for item in items:
                    item_path = os.path.join(directory, item)
                    if os.path.isdir(item_path):
                        output.append(f"{item}/")
                    else:
                        output.append(item)
                print("  ".join(output) if output else "")
                return items
            except PermissionError:
                print(f"ls: cannot open directory '{relative_path}': Permission denied")
                return []

        def recursive_list(directory):
            items = list_directory(directory)
            for item in items:
                item_path = os.path.join(directory, item)
                if os.path.isdir(item_path):
                    print() 
                    recursive_list(item_path)

        if recursive:
            recursive_list(path)
        else:
            list_directory(path, show_header=False)



    def rmdir(self, args):
        if not args:
            print("Usage: rmdir <directory>")
            return

        path = self._get_real_path(args[0])
        if os.path.isdir(path):
            try:
                os.rmdir(path)
                print(f"Removed directory: {args[0]}")
            except OSError:
                print(f"Directory not empty or in use: {args[0]}")
        else:
            print(f"No such directory: {args[0]}")

    def tail(self, args):
        if not args:
            print("Usage: tail <file>")
            return

        path = self._get_real_path(args[0])
        if os.path.isfile(path):
            with open(path, "r") as file:
                lines = file.readlines()[-10:]
                print("".join(lines))
        else:
            print(f"No such file: {args[0]}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Shell Emulator")
    parser.add_argument("--username", required=True, help="Username for shell prompt")
    parser.add_argument("--tar_path", required=True, help="Path to tar archive")
    parser.add_argument("--log_file", required=True, help="Path to log file")
    parser.add_argument("--start_script", required=False, help="Path to start script")

    args = parser.parse_args()

    shell = ShellEmulator(args.username, args.tar_path, args.log_file, args.start_script)
    shell.run()
