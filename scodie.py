import os
from datetime import datetime
from shutil import copy2
from sys import platform
from webbrowser import open as wb_open

from PIL import Image
from humanize import naturalsize
from tabulate import tabulate
from vlc import MediaPlayer

TEXT_FILES = ["txt", "log", "py", "md"]
IMAGE_FILES = ["jpg", "png", "jpeg", "webp"]
BROWSER_FILES = ["mp4", "mkv", "html"]
SOUND_FILES = ["mp3", "wav", "ogg"]
BAD_NAMES = ["#", "%", "&", "{", "}", "\\", "<", ">", "*", "?", "/",
             "", "$", "!", "'", "\"", ":", "@", "+", "`", "|", "="]


class FileTree:
    def __init__(self):
        self.files_list = []
        self.clear_command = get_clear()
        show_cur_dir()
        self.reload_files()
        self.show_files()
        self.run = True
        while self.run:
            self.dialogue()

    def reload_files(self):
        self.files_list = [".", "..", *sorted(os.listdir())]

    def show_files(self):
        print(tabulate([[file, self.files_list[file]] for file in range(len(self.files_list))], tablefmt="plain"))

    def dialogue(self):
        dialogue_choice = str(input(">")).split()
        if dialogue_choice:
            command, *args = dialogue_choice
            if args:
                files_list = args[0].split(";")
                del args[0]
                if len(files_list) > 1:
                    for file in files_list:
                        self.dialogue_choice(command, file, args)
                else:
                    self.dialogue_choice(command, files_list[0], args)
            else:
                self.dialogue_choice(command, "", [])

    def dialogue_choice(self, command, file, args):
        try:
            if command == "s":
                self.reload_files()
                self.show_files()
            elif command == "c" or command == "o" or command == "d" or command == "i" or command == "e":
                if len(args) == 1 and args[0] == "-f" and command == "d":
                    command += "f"
                file_name = self.file_handle(file) if command != "c" else file
                FileHandler(file_name, command) if file_name else get_directory_error("file name error", os.getcwd())
                self.reload_files()
            elif command == "cd":
                if change_dir(self.file_handle(file)):
                    self.reload_files()
                    self.show_files()
                else:
                    get_directory_error("no such directory", os.getcwd())
            elif command == "cp" or command == "mv":
                file_name = self.file_handle(file)
                FileMover(file_name, self.file_handle(args[0]), command) if file_name else get_directory_error(
                    "no such file", os.getcwd())
            elif command == "scd":
                show_cur_dir()
            elif command == "cc":
                os.system(self.clear_command)
            elif command == "q":
                self.run = False
            else:
                print("unknown command")
        except IndexError:
            print("pass normal arguments pls")

    def file_handle(self, file_type):
        try:
            if os.path.exists(file_type):
                return os.path.abspath(file_type)
            elif int(file_type) <= len(self.files_list):
                return self.files_list[int(file_type)]
        except ValueError:
            pass
        return False


class FileHandler:
    def __init__(self, file, mode):
        global TEXT_FILES, IMAGE_FILES, BROWSER_FILES, SOUND_FILES, BAD_NAMES
        self.file = file
        self.ext = os.path.splitext(file)[1][1:]
        if mode == "c":
            self.file_create()
        elif mode == "o":
            self.file_open()
        elif mode == "d" or mode == "df":
            if mode == "df" or input(f"deleting {self.file}, you sure? (y if yes): ") == "y":
                self.file_delete()
        elif mode == "i":
            self.file_info()
        elif mode == "e":
            self.file_edit()

    def file_create(self):
        if check_file_name(self.file):
            if self.ext:
                with open(self.file, "w"):
                    pass
            else:
                os.mkdir(self.file)
        else:
            print("illegal file name")

    def file_open(self):
        if self.ext in TEXT_FILES:
            with open(self.file, "r") as f:
                contents = f.read()
                print(contents)
                if self.ext.endswith("py") and input("execute? (y if yes): ") == "y":
                    try:
                        exec(contents)
                    except Exception as e:
                        print(f"exception occurred! {e}")
        elif self.ext in IMAGE_FILES:
            Image.open(self.file).show()
        elif self.ext in BROWSER_FILES:
            wb_open(f"file://{os.getcwd()}/{self.file}")
        elif self.ext in SOUND_FILES:
            p = MediaPlayer(f"file://{os.getcwd()}/{self.file}")
            p.play()
            input("press enter to stop")
            p.stop()
        else:
            get_directory_error("could not open file or directory", os.getcwd())

    def file_delete(self):
        if self.ext:
            os.remove(self.file)
        else:
            [os.remove(f"{self.file}/{file}") for file in os.listdir(self.file)]
            os.rmdir(self.file)

    def file_info(self):
        time_format = "%d-%m-%Y %H:%M:%S"
        print(f"Size: {naturalsize(os.path.getsize(self.file), binary=True, gnu=True)}\n"
              f"Creation time: {datetime.fromtimestamp(os.path.getctime(self.file)).strftime(time_format)}\n"
              f"Modification time: {datetime.fromtimestamp(os.path.getmtime(self.file)).strftime(time_format)}\n"
              f"Last access time: {datetime.fromtimestamp(os.path.getatime(self.file)).strftime(time_format)}")

    def file_edit(self):
        os.system(f"{os.environ['EDITOR']} {self.file}") if self.ext in TEXT_FILES else print("only text files support")


class FileMover:
    def __init__(self, file, path, mode):
        self.file = file
        self.path = path
        if os.path.exists(self.path):
            if mode == "cp":
                self.copy_file()
            elif mode == "mv":
                self.move_file()
        else:
            print("wrong path")

    def copy_file(self):
        if self.file not in os.listdir(self.path):
            copy2(self.file, self.path)

    def move_file(self):
        os.rename(os.path.abspath(self.file), f"{self.path}/{self.file}")


def change_dir(file):
    if os.path.isdir(file):
        os.chdir(file)
        return True
    return False


def get_clear():
    if platform.startswith("win"):
        return "cls"
    elif platform.startswith("darwin"):
        return "printf '\33c\e[3J'"
    else:
        return "clear"


def get_directory_error(error, directory):
    print(f"{error} in\n{directory}")


def show_cur_dir():
    print(os.getcwd())


def check_file_name(file):
    return all([letter not in BAD_NAMES for letter in file])


if __name__ == "__main__":
    FileTree()
