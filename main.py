#!/usr/bin/env python3

from crontab import CronTab
import argparse
import subprocess, sys, os
from simple_term_menu import TerminalMenu
from datetime import date
import calendar
import re


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


class GetThings:
    def __init__(self):
        self.cron = CronTab(user=os.getenv("USER"))
        self.directory = os.path.dirname(os.path.realpath(__file__))
        self.day_of_week = calendar.day_name[date.today().weekday()]

    @staticmethod
    def job_title_msg(job):
        pattern = r"\"(.*)\".*\"(.*)\""
        texto = re.search(pattern, job.command)
        titulo = texto.groups()[0]
        mensaje = texto.groups()[1]
        return titulo, mensaje


class Commands:
    def __init__(self):
        self.commands = [
            method for method in dir(self) if method.startswith("__") is False
        ]
        self.parser = argparse.ArgumentParser()
        self.sp = self.parser.add_subparsers(dest="opt")
        for opt in self.commands:
            self.sp.add_parser(opt)
        self.args = self.parser.parse_args().opt

    def __run__(self, command):
        """Runs the command chosen"""
        return getattr(self, str(command).lower(), lambda: "Invalid command")()

    ## Methods
    def help(self):
        """shows this message"""
        result = "   Please, type: `btime <option>´ where <option> can be: \n"
        for command in self.commands:
            result += (
                "     {:<20} ".format(command)
                + str(getattr(self, command).__doc__)
                + "\n"
            )
        return result

    @staticmethod
    def none():
        """if its left empty it will show your timetable for today"""
        return print_horario_title() + show_day(
            get.cron, get.day_of_week, one_day=True
        )

    @staticmethod
    def reset():
        """resets your daily tasks"""
        ans = input(
            "\nPlease, confirm that you want to delete all non-fixed events: (y/n)"
        )
        if ans != "y":
            sys.exit()
        get.cron.remove_all(comment="today")
        get.cron.remove_all(comment="today reminder")
        get.cron.write()
        return "\n . . . Removing events from yesterday\n"

    @staticmethod
    def addtoday():
        """to define your daily tasks"""
        intro()
        while True:
            add_new_event(get.cron, "today")
        return ""

    @staticmethod
    def week():
        """to show your timetable for the entire week"""
        show_week(get.cron)
        return ""

    @staticmethod
    def edit():
        """to edit any task"""
        while True:
            print()
            a = input("    Press l to show week, e to edit, and q to exit: ")
            if a == "l":
                show_week(get.cron)
            elif a == "q":
                check_fin(a)
            elif a == "e":
                delete_event(get.cron)
                msg = (
                    " Select if the NEW event should be weekly or for today: "
                )
                options = ["Today", "Weekly"]
                result = multiple_select(msg, options)
                day_of_week = "today"
                if result == "Weekly":
                    day_of_week = get.day_of_week
                abotdd_new_event(get.cron, day_of_week)
        return ""

    @staticmethod
    def addfixed():
        """to define your weekly tasks"""
        intro()
        while True:
            add_new_event(get.cron, get.day_of_week)

    @staticmethod
    def delevent():
        """to delete an event"""
        print("Help")

    @staticmethod
    def resetall():
        """to delete all your cron tasks"""
        print("Help")

    @staticmethod
    def wifion():
        """to enable wifi"""
        print("Help")

    @staticmethod
    def wifioff():
        """to disable wifi"""
        print("Help")

    @staticmethod
    def show():
        """to show BTime message"""
        print("Help")


## Vars and objects
get = GetThings()


def print_horario_hoy(jobs, day_of_week):
    result = (
        bcolors.HEADER
        + "                           "
        + day_of_week.upper()
        + bcolors.ENDC
        + "\n"
        + "    ----------------------------------------------------"
        + "\n"
    )
    for i in jobs:
        hora = str(i.hour)
        minuto = str(i.minute)
        if int(hora) < 10:
            hora = str("0" + hora)
        if int(minuto) < 10:
            minuto = str("0" + minuto)
        titulo, mensaje = get.job_title_msg(i)
        if "today" in str(i.comment):
            result += (
                bcolors.OKGREEN
                + "     "
                + hora
                + ":"
                + minuto
                + "   "
                + titulo.upper()
                + ". "
                + mensaje
                + bcolors.ENDC
                + "\n"
            )
        else:
            result += (
                bcolors.OKBLUE
                + "     "
                + hora
                + ":"
                + minuto
                + "   "
                + titulo.upper()
                + ". "
                + mensaje
                + bcolors.ENDC
                + "\n"
            )

    result += "    ----------------------------------------------------\n\n"
    return result


def intro():
    print(
        "------------------------------------------------------\n" + "Hey, ",
        os.getenv("USER"),
        ". Let's organize the day! 🕑 \n"
        + "------------------------------------------------------\n\n",
    )


def check_fin(char):
    if char == "q":
        print()
        print(
            "   ************************************************************************"
        )
        print(
            "    Felicidades tio, ya esta todo programado. Eres un grande. Lo petas hoy"
        )
        print(
            "   ************************************************************************"
        )
        print()
        sys.exit(0)


def multiple_select(msg, list):
    print("\n" + msg + "\n")
    try:
        d = TerminalMenu(list).show()
        return list[d]
    except:
        error_msg()
        sys.exit()


def choose_time(day_of_week):
    if day_of_week != "today":
        days = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
            "Exit",
        ]
        msg = "Please select a day of the week"
        day = multiple_select(msg, days)
        print(" DAY: ", day)
        if day == "Exit":
            check_fin("q")
    else:
        day = None
    hora = input("Enter an hour [HH] (0-23) (q to exit): ")
    check_fin(hora)
    while not (hora.isdigit() and int(hora) >= 0 and int(hora) < 24):
        hora = input("Please, enter an hour between 0-23: ")
    print(" HOURS: ", hora)
    min = input("Enter an minute [MM] (0-59): ")
    while not (min.isdigit() and int(min) >= 0 and int(min) < 60):
        min = input("Please, enter a minute between 0-60: ")
    print(" MINUTES: ", min)
    return day, str(hora), str(min)


def title_and_text(comment):
    if comment == None:
        comment = "today"
    title = input("Enter title of " + comment.upper() + " notification: ")
    print("Title: ", title)
    msg_text = input("Enter text of notification: ")
    print("Text: ", msg_text)
    command = input("Enter a custom command to run (empty for no command): ")
    print("Command: ", command)
    return str('"' + title.upper() + '"'), str('"' + msg_text + '"'), command


def notification_description(title, msg_text, hour, minute):
    if int(hour) < 10:
        hour = str("0" + str(hour))
    if int(minute) < 10:
        minute = str("0" + str(minute))
    print()
    print("---------------------------------")
    print("|----NOTIFICATION-DETAILS-------|")
    print("| Time: ", hour, ":", minute, "               |")
    print("| Message: ", title.upper(), ": ", msg_text)
    print("---------------------------------")
    print()


def add_notification(cron, title, msg_text, cmd, day, hour, minute, comment):
    get.cron.env["DISPLAY"] = os.getenv("DISPLAY")
    cron.env["XAUTHORITY"] = os.getenv("XAUTHORITY")
    notification = str("notify-send -i " + get.directory + "/clock.svg ")
    beep = str("; play -q " + get.directory + "/swiftly.mp3 -t alsa; ")

    final_command = str(notification + title + " " + msg_text + beep + cmd)

    job = cron.new(command=final_command, comment=comment)
    job.hour.on(int(hour))
    job.minute.on(int(minute))
    if day != "today":
        job.dow.on(day[0:3])

    notification_description(title, msg_text, hour, minute)

    # Reminder
    final_command = str(notification + title + " " + msg_text)
    job2 = cron.new(command=final_command, comment=(comment + " reminder"))
    if int(minute) > 5:
        job2.minute.on(int(minute) - 5)
    else:
        diff = 5 - int(minute)
        job2.minute.on(60 - diff)
        if int(hour) > 0:
            hour = int(hour) - 1
    job2.hour.on(int(hour))
    if day != "today":
        job2.dow.on(day[0:3])

    cron.write()
    print(" STATUS: ", comment.upper(), " notification added 😊 ")
    print("--------------------------------------------------")
    print()


def show_week(cron):
    days = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    today = get.day_of_week
    for i in days:
        print()
        if today == i:
            print(show_day(cron, i, one_day=True))
        else:
            print(show_day(cron, i, one_day=False))


def print_horario_title():
    return (
        bcolors.BOLD
        + r"               _   _                      _       "
        + bcolors.ENDC
        + "\n"
        + bcolors.BOLD
        + r"              | | | | ___  _ __ __ _ _ __(_) ___  "
        + bcolors.ENDC
        + "\n"
        + bcolors.BOLD
        + r"              | |_| |/ _ \| '__/ _` | '__| |/ _ \ "
        + bcolors.ENDC
        + "\n"
        + bcolors.BOLD
        + r"              |  _  | (_) | | | (_| | |  | | (_) |"
        + bcolors.ENDC
        + "\n"
        + bcolors.BOLD
        + r"              |_| |_|\___/|_|  \__,_|_|  |_|\___/ "
        + bcolors.ENDC
        + "\n"
        + bcolors.BOLD
        + r"                                                  "
        + bcolors.ENDC
        + "\n"
    )


def print_logo():
    print()
    print(
        bcolors.BOLD
        + r"       -----------------------------------------------------"
        + bcolors.ENDC
    )
    print(
        bcolors.BOLD
        + r"                                                            "
        + bcolors.ENDC
    )
    print(
        bcolors.BOLD
        + r"              =  =           ____ _____ _                   "
        + bcolors.ENDC
    )
    print(
        bcolors.BOLD
        + r"           =    |   =       | __ )_   _(_)_ __ ___   ___    "
        + bcolors.ENDC
    )
    print(
        bcolors.BOLD
        + r"          =     |    =      |  _ \ | | | | '_ ` _ \ / _ \   "
        + bcolors.ENDC
    )
    print(
        bcolors.BOLD
        + r"          =      \   =      | |_) || | | | | | | | |  __/   "
        + bcolors.ENDC
    )
    print(
        bcolors.BOLD
        + r"           =      \ =       |____/ |_| |_|_| |_| |_|\___|   "
        + bcolors.ENDC
    )
    print(
        bcolors.BOLD
        + r"              =  =                                          "
        + bcolors.ENDC
    )
    print(
        bcolors.BOLD
        + r"                                                            "
        + bcolors.ENDC
    )
    print(
        bcolors.BOLD
        + r"                         N e v e r   b e   l a t e   🕑     "
        + bcolors.ENDC
    )
    print(
        bcolors.BOLD
        + r"                                                            "
        + bcolors.ENDC
    )
    print(
        bcolors.BOLD
        + r"       -----------------------------------------------------"
        + bcolors.ENDC
    )
    print(
        bcolors.BOLD
        + r"                                                            "
        + bcolors.ENDC
    )
    print(
        bcolors.BOLD
        + r"                  Maintained by: Miquel Espinosa            "
        + bcolors.ENDC
    )
    print(
        bcolors.BOLD
        + r"                                                            "
        + bcolors.ENDC
    )


def error_msg():
    print()
    print()
    print()
    print("          Exiting BTime")
    print()
    print("     . . . but remember . . . ")
    print()
    print("     N e v e r   b e   l a t e   🕑")
    print()
    print()


def show_day(cron, day_of_week, one_day):
    jobs = []
    for job in cron:
        if one_day:
            if job.comment == "today" or job.comment == get.day_of_week:
                jobs.append(job)
        else:
            if job.comment == day_of_week:
                jobs.append(job)
    jobs.sort(key=lambda x: (int(str(x.hour)), int(str(x.minute))))
    return print_horario_hoy(jobs, day_of_week)


def delete_event(cron):
    ans = input("    Type the title or message of the event: ")
    print()
    jobs_titles = []
    jobs = []
    jobs_reminders = []
    for job in cron:
        title, messaje = get.job_title_msg(job)
        if (ans.lower() in str(title.lower())) or (
            ans in str(messaje.lower())
        ):
            if not ("reminder" in str(job.comment)):
                jobs_titles.append(
                    str("(" + str(job.comment) + ") " + title + ": " + messaje)
                )
                jobs.append(job)
            elif "reminder" in str(job.comment):
                jobs_reminders.append(job)
    if not jobs_titles:
        print("    There is no event with such title or comment ☹")
        print()
        sys.exit()
    else:
        msg = " Select the event to be deleted: "
        selected = multiple_select(msg, jobs_titles)
        print(" EVENT DELETED: ", selected)
        index = jobs_titles.index(selected)
        cron.remove(jobs[index])
        cron.remove(jobs_reminders[index])
        cron.write()


def add_new_event(cron, day_of_week):
    if day_of_week == "today":
        show_day(cron, day_of_week, one_day=True)
    day, hour, min = choose_time(day_of_week)
    title, text, cmd = title_and_text(day)
    if day_of_week == "today":
        day = "today"
    add_notification(cron, title, text, cmd, day, hour, min, day)


def print_wifioff():
    print(
        bcolors.BOLD
        + r"                                           "
        + bcolors.ENDC
    )
    print(
        bcolors.BOLD
        + r"         ====                              "
        + bcolors.ENDC
    )
    print(
        bcolors.BOLD
        + r"      =======                              "
        + bcolors.ENDC
    )
    print(
        bcolors.BOLD
        + r"    ==    ==                               "
        + bcolors.ENDC
    )
    print(
        bcolors.BOLD
        + r"  ===    ==              ____        ____  "
        + bcolors.ENDC
    )
    print(
        bcolors.BOLD
        + r"  ==     ===            |  _ \ _ __ |  _ \ "
        + bcolors.ENDC
    )
    print(
        bcolors.BOLD
        + r"  ==      ===           | | | | '_ \| | | |"
        + bcolors.ENDC
    )
    print(
        bcolors.BOLD
        + r"  ===       ====        | |_| | | | | |_| |"
        + bcolors.ENDC
    )
    print(
        bcolors.BOLD
        + r"    ==          ====    |____/|_| |_|____/ "
        + bcolors.ENDC
    )
    print(
        bcolors.BOLD
        + r"      ====   =====                         "
        + bcolors.ENDC
    )
    print(
        bcolors.BOLD
        + r"         ======                            "
        + bcolors.ENDC
    )
    print(
        bcolors.BOLD
        + r"                                           "
        + bcolors.ENDC
    )


def print_wifion():
    print(
        bcolors.BOLD
        + r"                                                                         "
        + bcolors.ENDC
    )
    print(
        bcolors.BOLD
        + r"             ==========                                                  "
        + bcolors.ENDC
    )
    print(
        bcolors.BOLD
        + r"        ====================                                             "
        + bcolors.ENDC
    )
    print(
        bcolors.BOLD
        + r"     ==========================                                          "
        + bcolors.ENDC
    )
    print(
        bcolors.BOLD
        + r"   ========              ========    __        ___  __ _    ___          "
        + bcolors.ENDC
    )
    print(
        bcolors.BOLD
        + r"   =====      ========      =====    \ \      / (_)/ _(_)  / _ \ _ __    "
        + bcolors.ENDC
    )
    print(
        bcolors.BOLD
        + r"           ==============             \ \ /\ / /| | |_| | | | | | '_ \   "
        + bcolors.ENDC
    )
    print(
        bcolors.BOLD
        + r"         ==================            \ V  V / | |  _| | | |_| | | | |  "
        + bcolors.ENDC
    )
    print(
        bcolors.BOLD
        + r"          ====        ====              \_/\_/  |_|_| |_|  \___/|_| |_|  "
        + bcolors.ENDC
    )
    print(
        bcolors.BOLD
        + r"                ====                                                     "
        + bcolors.ENDC
    )
    print(
        bcolors.BOLD
        + r"               ======                                                    "
        + bcolors.ENDC
    )
    print(
        bcolors.BOLD
        + r"                ====                                                     "
        + bcolors.ENDC
    )
    print(
        bcolors.BOLD
        + r"                                                                         "
        + bcolors.ENDC
    )


def main():

    try:

        command = Commands()
        print(command.__run__(command.args))

#        if flag == "resetall":
#            print()
#            print("-------   ¡¡¡ CAUTION !!!   -------")
#            print()
#            ans = input(
#                "Please, confirm that you want to delete ALL cron tasks from your profile: (y/n)"
#            )
#            if ans != "y":
#                sys.exit()
#            get.cron.remove_all()
#            get.cron.write()
#            print()
#            print(" . . . Removing ALL tasks")
#            print()
#
#        elif flag == "wifioff":
#            os.system("nmcli networking off")
#            print_wifioff()
#
#        elif flag == "wifion":
#            os.system("nmcli networking on")
#            print_wifion()
#
#        elif flag == "show":
#            print_logo()
#
#        elif flag == "delevent":
#            print()
#            print("   --------- ¡¡¡ CAUTION !!! ---------")
#            print("    You are going to delete an event")
#            print("   -------------------------------------")
#            print()
#            delete_event(get.cron)

    except KeyboardInterrupt:
        error_msg()


main()
