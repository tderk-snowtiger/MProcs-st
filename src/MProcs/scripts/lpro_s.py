import random
import time
import datetime
import string
import secrets
import threading
import subprocess
import platform
import os
import shutil
import argparse
import math
import struct
import sys
import session
import re
import version_checker


from data_loader import acadlist, bible1, biology1, chemistry1, chi_chars, degrees1, dhammapada1, diction, fcci, hospitals, jamo, katakana, koran1, legal_terms1, medicals1, mims, proverbs, psychology1, science1, strains, tracks, verses1
import deepseek_ai
RED = '\033[91m'
GREEN = '\033[92m'
PURPLE = '\033[35m'
ORANGE = '\033[93m'
BLUE = '\033[94m'
PINK = '\033[95m'
RESET = '\033[0m'

colors = {
    'GREEN': '\033[32m',
    'YELLOW': '\033[33m',
    'PURPLE': '\033[35m',
    'CYAN': '\033[36m',
    'DEFAULT': '\033[0m',
    'BRIGHT_RED': '\033[91m',
    'BRIGHT_GREEN': '\033[92m',
    'BRIGHT_YELLOW': '\033[93m',
    'BRIGHT_BLUE': '\033[94m',
    'BRIGHT_PURPLE': '\033[95m',
    'BRIGHT_CYAN': '\033[96m',
}

def get_random_color():
    return random.choice(list(colors.values()))

_no_color_on = False
_orig_colors = {}

raw_name = session.raw_usr

global usr
usr = f" st ( {GREEN}{raw_name}{RESET} ) {PURPLE}${RESET} "

def set_usr(newUsr):
    session.usr = newUsr

def change_username(provided_name=None):
    global usr
    global raw_usr
    
    if provided_name:
        if isinstance(provided_name, str):
            clean_name = re.sub(r'\x1b\[[0-9;]*m', '', provided_name)
            
            match = re.search(r'st\s*\(([^)]+)\)', clean_name)
            if match:
                new_raw = match.group(1).strip()
            else:
                new_raw = clean_name.strip()
        else:
            new_raw = str(provided_name)
    else:
        new_raw = input("Session username: ").strip()

    if not new_raw:
        new_raw = "zeta"

    session.raw_usr = new_raw
    raw_usr = new_raw
    
    usr = f" st ( {GREEN}{new_raw}{RESET} ) {BLUE}${RESET} "
    
    return usr

omit_result = False
current_ddd = [""]
jot_log = None
jot_active = False
jot_file_path = ""

def jot(path=None):
    import os
    global jot_log, jot_active, jot_file_path
    if not jot_active:
        jot_file_path = path if path else "JOT.txt"
        folder = os.path.dirname(jot_file_path)
        if folder and not os.path.isdir(folder):
            print(f"{ORANGE}[JOT] Folder not found: {folder}{RESET}")
            return
        jot_log = open(jot_file_path, "a", buffering=1)
        jot_active = True
        print(f"{GREEN}[JOT] Recording started -> {jot_file_path}{RESET}")
    else:
        jot_log.close()
        jot_active = False
        print(f"{ORANGE}[JOT] Recording stopped -> {jot_file_path}{RESET}")
        jot_log = None
        jot_file_path = ""

def jot_write(msg):
    global jot_log, jot_active
    if jot_log and jot_active:
        jot_log.write(msg + "\n")
        jot_log.flush()

print_orig = print

class SkipLog:
    pass

skip_log = SkipLog()

def jot_print(*args, **kwargs):
    global jot_log, jot_active
    f = kwargs.get('file')
    if f is skip_log or (hasattr(f, 'name') and 'MProcs' in f.name):
        return print_orig(*args, file=None, **kwargs)
    text = " ".join(str(a) for a in args)
    clean_text = re.sub(r'\x1b\[[0-9;]*m', '', text)
    if jot_active and jot_log:
        jot_log.write(clean_text + "\n")
        jot_log.flush()
    if 'file' not in kwargs and clean_text.strip():
        deepseek_ai.write_output(clean_text)
    print_orig(*args, **kwargs)

print = jot_print

def main():

    alphabeta = ["A", "a", "B", "b", "C", "c", "D", "d", "E", "e", "F", "f", "G", "g", "H", "h", "I", "i", "J", "j", "K", "k", "L", "l", "M", "m", "N", "n", "O", "o", "P", "p", "Q", "q", "R", "r", "S", "s", "T", "t", "U", "u", "V", "v", "W", "w", "X", "x", "Y", "y", "Z", "z", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]

    ruh = ["а", "б", "в", "г", "д", "е", "ё", "ж", "з", "и", "й", "к", "л", "м", "н", "о", "п", "р", "с", "т", "у", "ф", "х", "ц", "ч", "ш", "щ", "ъ", "ы", "ь", "э", "ю", "я"]

    def select_charset(provided_choice=None):
        global current_ddd, omit_result
        
        while True:
            choice = provided_choice if provided_choice else input("Nano EST Charset - 1. Korean 2. Chinese 3. Japanese 4. Alphanumeric 5. Russian 6. None/English  (add 'a' for English toggle): ").strip()
            
            c = choice.lower().replace(" ", "") 

            if c in ['', '1', 'korean', 'k']:
                current_ddd = jamo
            elif c in ['2', 'chinese', 'c']:
                current_ddd = chi_chars
            elif c in ['3', 'japanese', 'j']:
                current_ddd = katakana
            elif c in ['6', 'none']:
                current_ddd, omit_result = [""], False
            elif c in ['1a', '1-a', 'koreana', 'korean-a', 'ka', 'k-a']:
                current_ddd, omit_result = jamo, not omit_result
            elif c in ['2a', '2-a', 'chinesea','chinese-a', 'ca', 'c-a']:
                current_ddd, omit_result = chi_chars, not omit_result
            elif c in ['3a', '3-a', 'japanesea', 'japanese-a', 'ja', 'j-a']:
                current_ddd, omit_result = katakana, not omit_result
            elif c in ["alphanumeric", "an", "4"]:
                current_ddd = alphabeta
            elif c in ['alphanumerica', 'alphanumerica-a', "ana", "an-a", "4a", "4-a"]:
                current_ddd, omit_result = alphabeta, not omit_result
            elif c in ["russian", "ru", "5"]:
                current_ddd = ruh
            elif c in ['russiana', 'russian-a', "rua", "ru-a", "5a", "5-a"]:
                current_ddd, omit_result = ruh, not omit_result
            elif c in ['a']:
                omit_result = not omit_result
            elif c in ['6a', '6-a']:
                current_ddd, omit_result = [""], not omit_result
            else:
                print("Invalid input")
                provided_choice = None
                continue
            break

            session.current_charset = selected  # Persist to session
            return selected
    ###

    def alerts():
        kk = (katakana)
        j = (jamo)
        cc = (chi_chars)
        rr = (ruh)
        def generate_random_letters():
            random1 = random.choice(string.ascii_letters)
            random2 = random.choice(string.ascii_letters)
            random3 = random.choice(string.ascii_letters)
            random4 = random.choice(string.ascii_letters)
            random5 = random.choice(string.ascii_letters)
            letters = [random1, random2, random3, random4, random5]
            random.shuffle(letters)
            return letters
        random_letters = generate_random_letters()
        rrchar = random.choices(rr, k=random.randint(1,8))
        kkchar = random.choices(kk, k=random.randint(1,7))
        hchar = random.choices(j, k=random.randint(1,7))
        cchat = random.choices(cc, k=random.randint(1,5))
        rrchar_str = ''.join(rrchar)
        kkchar_str = ''.join(kkchar)
        hchar_str = ''.join(hchar)
        value = (round(random.random()*9999999999,10))
        ct = datetime.datetime.now()
        alerts = "Alerts:"
        alert = f"{PINK}{alerts}{RESET}"
        print(alert, value, random_letters, kkchar_str, cchat, hchar_str, rrchar_str, ct)

    def version():
        title =  usr + "" + " " + "" + f"snowtiger >>> {ORANGE}I.S. (Incubator Studios) Outbeat Produce:{RESET} {GREEN}MProcs-10.0-s (v{version_checker.PACKAGE_VERSION}){RESET} {ORANGE}by tderk{RESET} - {ORANGE}Established Lpro.py (Life-pro) and Destiny [2024]{RESET}"
        title2 = f"| {BLUE}Indicative: @USVirtualUni && © Medicine, Computable (N_2025) && FNTCCI{RESET} |"
        title3 = f"{ORANGE}All Rights Reserved{RESET} - {BLUE}Medicci.ca{RESET}"
        title4 = f"- {RED}(P0cket Un1-Ver$e){RESET}"
        cdt = datetime.datetime.now()
        time = f"{GREEN}{cdt}{RESET}"
        print(title, time, title3, title4)
        print()
        prvrb = random.sample(proverbs, 1)
        pr = " "
        print(pr, prvrb)
        print()
        print(title2)
        print()
        alerts()

    time.sleep(0)

    def mp():

        deck1 = ["Ace of Hearts", "Two of Hearts", "Three of Hearts", "Four of Hearts", "Five of Hearts", "Six of Hearts", "Seven of Hearts", "Eight of Hearts", "Nine of Hearts", "Ten of Hearts", "Jack of Hearts", "Queen Of Hearts", "King of Hearts", "Ace of Clubs", "Two of Clubs", "Three of Clubs", "Four of Clubs", "Five of Clubs", "Six of Clubs", "Seven of Clubs", "Eight of Clubs", "Nine of Clubs", "Ten of Clubs", "Jack of Clubs", "Queen Of Clubs", "King of Clubs", "Ace of Diamonds", "Two of Diamonds", "Three of Diamonds", "Four of Diamonds", "Five of Diamonds", "Six of Diamonds", "Seven of Diamonds", "Eight of Diamonds", "Nine of Diamonds", "Ten of Diamonds", "Jack of Diamonds", "Queen Of Diamonds", "King of Diamonds", "Ace of Spades", "Two of Spades", "Three of Spades", "Four of Spades", "Five of Spades", "Six of Spades", "Seven of Spades", "Eight of Spades", "Nine of Spades", "Ten of Spades", "Jack of Spades", "Queen Of Spades", "King of Spades", "Joker", "Joker"]

        interpret_active = False

        def dsnan_interpret():
            nonlocal interpret_active
            interpret_active = not interpret_active
            if interpret_active:
                print(f"{GREEN}[DSNAN] ON. Blank Enter = nano+interpret, 'dsnan' toggles off.{RESET}")
            else:
                print(f"{ORANGE}[DSNAN] Off.{RESET}")

        def dsnan_nano():
            import re as _re
            CYAN = '\033[96m'
            dd = (diction)
            ddd = session.current_charset if session.current_charset else current_ddd
            ct = datetime.datetime.now()
            cchar = random.choices(ddd, k=random.randint(1, 8))
            chchars_str = ''.join(cchar)
            nano_words = tuple(random.choice(dd) for _ in range(9))
            result = "  ".join(random.sample(nano_words, random.randint(1, 9)))
            star = "&"
            random_color = random.choice(['\033[32m', '\033[33m', '\033[35m', '\033[36m', '\033[91m', '\033[94m', '\033[95m', '\033[96m'])
            line = f"{star}  {random_color}{chchars_str}  {result}{RESET}  {ct}"
            print(line)
            clean_line = _re.sub(r'\x1b\[[0-9;]*m', '', line)
            prompt = (
                "The following is randomly generated contemplative output from a meditation "
                "terminal called MProcs. It contains random script characters (katakana/jamo/"
                "hanzi/Russian/alphanumeric) combined with random English dictionary words and "
                "a timestamp. Interpret it creatively \u2014 find meaning, symbolism, or poetry in it. "
                "Respond with a short, insightful interpretation (1-2 sentences).\n\n"
                f"Output:\n{clean_line}"
            )
            reply = deepseek_ai.chat_once(prompt, enable_browsing=False)
            meaning = _re.sub(r'\x1b\[[0-9;]*m', '', reply).strip()
            line_i = f"{CYAN}***{RESET} {meaning}"
            print(line_i)
            print()

        def nano():
            global omit_result
            dd = (diction)
            ddd = session.current_charset if session.current_charset else current_ddd
            ct = datetime.datetime.now()
            cchar = random.choices(ddd, k=random.randint(1,8))
            chchars_str = ''.join(cchar)
            if omit_result:
                result = ""
            else:
                nano = (random.choice(dd), random.choice(dd), random.choice(dd), random.choice(dd), random.choice(dd), random.choice(dd), random.choice(dd), random.choice(dd), random.choice(dd))
                result = "  ".join(random.sample(nano, random.randint(1, 9)))
            star = "&"
            dash = ""
            random_color = get_random_color()
            print(f"{star} {dash} {random_color}{chchars_str} {dash} {result}{RESET} {dash} {ct}")

        def morn():
            try:
                result = subprocess.run(['clear'], capture_output=True, text=True, check=True)
                print(result.stdout)
            except subprocess.CalledProcessError as e:
                print(f"Error executing command: {e}")
                print(f"Stderr: {e.stderr}")
            print()
            print()
            print()
            global omit_result
            dd = (diction)
            ddd = session.current_charset if session.current_charset else current_ddd
            ct = datetime.datetime.now()
            cchar = random.choices(ddd, k=random.randint(1,8))
            chchars_str = ''.join(cchar)
            if omit_result:
                result = ""
            else:
                nano = (random.choice(dd), random.choice(dd), random.choice(dd), random.choice(dd), random.choice(dd), random.choice(dd), random.choice(dd), random.choice(dd), random.choice(dd))
                result = "  ".join(random.sample(nano, random.randint(1, 9)))
            star = "&"
            dash = ""
            random_color = get_random_color()
            print(f"{star} {dash} {random_color}{chchars_str} {dash} {result}{RESET} {dash} {ct}")

        if getattr(sys.modules.get(__name__), '_SWAP_NANO_MORN', False):
            nano, morn = morn, nano

        def n1():
            global omit_result
            dd = (diction)
            ddd = session.current_charset if session.current_charset else current_ddd
            ct = datetime.datetime.now()
            cchar = random.choices(ddd, k=random.randint(1,7))
            chchars_str = ''.join(cchar)
            if omit_result:
                result = ""
            else:
                result = "".join(random.choice(dd))
            star = "&"
            dash = ""
            print(star, dash, chchars_str, dash, result, dash, ct)

        def kata():
            dd = (diction)
            kk = (katakana)
            ct = datetime.datetime.now()
            kkchar = random.choices(kk, k=random.randint(1,12))
            kkchar_str = ''.join(kkchar)
            nano = (random.choice(dd), random.choice(dd), random.choice(dd), random.choice(dd), random.choice(dd), random.choice(dd), random.choice(dd), random.choice(dd), random.choice(dd))
            result = "  ".join(random.sample(nano, random.randint(1, 9)))
            tars = "~~"
            print(tars, kkchar_str, result, ct)

        def hangu():
            dd = (diction)
            hang = (jamo)
            ct = datetime.datetime.now()
            hangchar = random.choices(hang, k=random.randint(1,14))
            hangchar_str = ''.join(hangchar)
            nano = (random.choice(dd), random.choice(dd), random.choice(dd), random.choice(dd), random.choice(dd), random.choice(dd), random.choice(dd), random.choice(dd), random.choice(dd))
            result = "  ".join(random.sample(dd, random.randint(1, 9)))
            arts = "^^"
            print(arts, hangchar_str, result, ct)

        def manton():
            dd = (diction)
            mac = (chi_chars)
            ct = datetime.datetime.now()
            macchar = random.choices(mac, k=random.randint(1,16))
            macchar_str = ''.join(macchar)
            nano = (random.choice(dd), random.choice(dd), random.choice(dd), random.choice(dd), random.choice(dd), random.choice(dd), random.choice(dd), random.choice(dd), random.choice(dd))
            result = "  ".join(random.sample(dd, random.randint(1, 9)))
            marts = "+++"
            print(marts, macchar_str, result, ct)

        def aans():
            dd = (diction)
            ans = (alphabeta)
            ct = datetime.datetime.now()
            anschar = random.choices(ans, k=random.randint(1,9))
            anschar_str = ''.join(anschar)
            nano = (random.choice(dd), random.choice(dd), random.choice(dd), random.choice(dd), random.choice(dd), random.choice(dd), random.choice(dd), random.choice(dd), random.choice(dd))
            result = "  ".join(random.sample(dd, random.randint(1, 9)))
            ansarts = "@@@"
            print(ansarts, anschar_str, result, ct)

        def ruuh():
            dd = (diction)
            ru = (ruh)
            ct = datetime.datetime.now()
            ruchar = random.choices(ru, k=random.randint(1,10))
            ruchar_str = ''.join(ruchar)
            nano = (random.choice(dd), random.choice(dd), random.choice(dd), random.choice(dd), random.choice(dd), random.choice(dd), random.choice(dd), random.choice(dd), random.choice(dd))
            result = "  ".join(random.sample(dd, random.randint(1, 9)))
            rarts = "%%%"
            print(rarts, ruchar_str, result, ct)

        def tinie_N():
            an = (fcci)
            acad = (acadlist)
            ct = datetime.datetime.now()
            cci = random.choices(an, k=random.randint(1,10))
            acadl = random.sample(acad, random.randint(1,5))
            wonyao_str = ''.join(cci)
            ha_sh = "#"
            print(ha_sh, wonyao_str, acadl, ct)

        _no_color_on = False
        _orig_colors = {}

        def no_color():
            global _no_color_on, _orig_colors, RED, GREEN, PURPLE, ORANGE, BLUE, PINK, RESET, colors
            _no_color_on = not _no_color_on
            if _no_color_on:
                _orig_colors = {k: v for k, v in globals().items() if k in ('RED','GREEN','PURPLE','ORANGE','BLUE','PINK','RESET')}
                _orig_colors['colors'] = dict(colors)
                RED = GREEN = PURPLE = ORANGE = BLUE = PINK = RESET = ''
                colors = {k: '' for k in colors}
            else:
                for k, v in _orig_colors.items():
                    globals()[k] = v
                _orig_colors.clear()
            print(f"ANSI colors {'disabled' if _no_color_on else 'enabled'}")

        def commands():
            print()
            print(" version | no_color [nc] | switch/lpro [lx] | [blank input] for nano / 1-nano [n1/3 spaces] | morn [m] | nano characters [nanochars/nnc] | katakana [kata/b] | jamo [hangu/n] | chi [++] | ans [@@] | ruh [%%] | profile | pwd / ls / cd / clear [cl] / mkdir / rm | type-text | Term-Search [tsearch] | fsearch | scmpy / scm [social media] | jot [JOT] (record terminal to file) | update | restart | Deepseek AI [DS/ds] | DS change-api | dsnan interpret [interpret on/off] | ai_image [local AI image generation]")
            print()
            print(" FNTCCI: tinien [single space/**], ntag, fcci-monitor [fstart/fcci] | synthesis: xcbmp, xcbmpc, xhbmp, xhbmpc, xjbmp, xjbmpc, xfbmp")
            print()
            print(" | Medicines (MIMS/mim), Medicals (M), equips, rpg, Bible [bb/BB], random hospital [rhosp/ghosthunt], jburner/jtburner, cburner/ctburner, ruh-time-call [RTC], ruh-monitor [rmonitor], insta ghost write [IGW], sound stream [sst], ghost write/code [GW], proverbs [ps], c-characters [cchar/cc], ch-monitor [CHM], kata-monitor [KM], jamo-monitor [JM], speak [spk], map, threads, zuz [pp], call, time-call [TC], message [lh], [echo], [fuzz], alerts, light incense, prayer, dhammapada, message-scan [scan], ascii [double space], archery, value, tag / atag, monitor-start [mstart], acad-monitor (astart), weapon start [wstart], oscillator/time-oscillator [oscill/toscill], MedProc AI [MAI], MedProcCont [MAIc/MPC], burner-start/time-burner [burn/tburn], burner-search [b-search], Earth Science (SCI), psychology (psyc), Patient Simu, biology (B), chemistry (ch), legal terms (Law), change username [username/user], print time, (ai) auto-mat [AAM], [ID / IDC], the heart sutra, herbs/herbals, maryjane [mj], degree/major, frames [fps], police (prad), CAI Environments (CAI/GES), time-monitor [tmonitor], speech-time-monitor [stmonitor], guard, Programs [PROGR], generate string [gstring]")
            print()
            print(" | pray, sleep, eat, meditate, draw card, slot, find coins, search for items, fly, drink coffee, drink tea, surf, skate, art, give alms, radio, hack, brawl, souls, hipster tarot, mp3, spar, train, rest, psalms, haiku, karate, koans, color key, doodling, BUMP, MA, Magic, zen melody, monopoly, stats, progress, collections, football, c, entry, posting, koran, heBrews, Clearance, MiCasa, stuff, worship, License, climb, teletubby, {[muslim prayer] fajr (before dawn) / dhuhr (noon) / asr (late afternoon) / maghrib (at sunset) / isha (nighttime)}")

        def ls():
            try:
                result = subprocess.run(['ls'], capture_output=True, text=True, check=True)
                print(result.stdout)
            except subprocess.CalledProcessError as e:
                print(f"Error executing command: {e}")
                print(f"Stderr: {e.stderr}")

        def pwd():
            print(f"Current directory: {os.getcwd()}")

        def cd():
            path = input("$ ")
            try:
                os.chdir(path)
            except FileNotFoundError:
                print(f"Error: Folder '{path}' does not exist.")
            except NotADirectoryError:
                print(f"Error: '{path}' is not a directory.")
            except PermissionError:
                print(f"Error: Permission denied to access '{path}'.")
            except Exception as e:
                print(f"An unexpected error occurred: {e}")

        def mkdir():
            path = input("$ ")
            try:
                os.mkdir(path)
            except FileExistsError:
                print(f"Directory already exists at: {path}")

        def clear():
            try:
                result = subprocess.run(['clear'], capture_output=True, text=True, check=True)
                print(result.stdout)
            except subprocess.CalledProcessError as e:
                print(f"Error executing command: {e}")
                print(f"Stderr: {e.stderr}")

        def rm():
            path = input("$ ")
            try:
                os.remove(path)
            except FileNotFoundError:
                print(f"Error: Folder '{path}' does not exist.")
            except NotADirectoryError:
                print(f"Error: '{path}' is not a directory.")
            except PermissionError:
                print(f"Error: Permission denied to access '{path}'.")
            except Exception as e:
                print(f"An unexpected error occurred: {e}")        

        def clear():
            if os.name == 'posix':
                _ = os.system('clear')
            else:
                _ = os.system('cls')

        def text():
            title = input("Title: ")
            j = open("MProcs-text.txt", "a", buffering=1)
            ct = datetime.datetime.now()
            monitor = "text-type:"
            print(usr, monitor, title, ct)
            print(usr, monitor, title, ct, file=j)
            print()
            print("*this saves to MProcs-text.txt*")
            print()
            print(file=j)
            type_text = input("# ")
            print(type_text, file=j)
            print(file=j)

        def GES():
            print()
            print("Crown | ART | Birth Snapshot | YzB | Thailand Hospital | egg | Zen Meditation (USVU) | Shinobi Primer | Hacking 101 @m0nkrpg | Saler | 445 | First Office Salute | Poker Table | chi_a | med_apteu #proc #music")

        def print_time():
            t_time = datetime.datetime.now()
            l_time = "Time: "
            print(l_time, t_time)

        def search():
            zen = input("Search: ")
            print()
            with open(r"MProcs-logs.txt", 'r') as fp:
                for l_no, line in enumerate(fp):
                    # search string
                    if zen in line:
                        print(zen + "" + ' found')
                        print('Line Number:', l_no)
                        print('Line:', line)

        def busearch(file_path="burner-log.txt"):
            zen = input("(burner) search: ")
            if not zen:
                print("Search cancelled.")
                return

            while True:
                try:
                    fps = float(input("Indicate speed in seconds: "))
                    if fps < 0:
                        print("Speed must be non-negative.")
                        continue
                    break
                except ValueError:
                    print("Invalid value. Please enter a number.")
                except KeyboardInterrupt:
                    print("\nInput cancelled.")
                    return

            print()
            print("Ctrl-C to stop")
            print()
            try:
                with open(file_path, 'r') as fp:
                    for line in fp:  # Process line by line to save memory
                        if zen in line:  # Case-sensitive search
                            try:
                                time.sleep(fps)  # Can be interrupted by Ctrl+C
                                print(line.strip())
                            except KeyboardInterrupt:
                                print("\nSearch interrupted by user.")
                                return
            except FileNotFoundError:
                print(f"Error: File '{file_path}' not found.")
            except Exception as e:
                print(f"An error occurred: {e}")

        def search_in_lists(search_term, *lists):
            results = []
            search_str = str(search_term).lower()
            
            for current_list in lists:
                if not isinstance(current_list, (list, tuple)):
                    continue
                for item in current_list:
                    if search_str in str(item).lower():
                        results.append(item)
            
            print("\n" + "="*50)
            print("SEARCH RESULTS")
            print("="*50)
            
            if results:
                print(f"\nFound {len(results)} match(es) for '{search_term}':\n")
                for idx, match in enumerate(results):
                    print(f"  {match}")
                    if idx < len(results) - 1:
                        print()
            else:
                print(f"\nNo matches found for '{search_term}'")
            
            print("\n" + "="*50)
            
            return results

        def tsearch():
            search_term = input("Term-Search: ")
            search_results = search_in_lists(search_term, proverbs, dhammapada1, medicals1, mims, science1, psychology1, biology1, chemistry1, legal_terms1, degrees1, verses1, bible1, koran1, strains)       


        def profile():
            print()
            ID()
            print()
            value()
            print()
            atag()
            print()
            earth_science()
            print()
            draw_card()
            print()
            stats()
            print()
            hack()
            print()
            progress()
            print()
            haiku()
            print()
            rpg()
            print()
            equips()
            print()
            legal_terms()
            print()
            dhammapada()

        def echo():
            echo = input("$ ")
            ct = datetime.datetime.now()
            print()
            ech = "echo:"
            print(ech, usr, echo, ct)

        def worker_thread(thread_id, delay, stop_event):

            def generate_random_letters():
                random1 = random.choice(string.ascii_letters)
                random2 = random.choice(string.ascii_letters)
                random3 = random.choice(string.ascii_letters)
                letters = [random1, random2, random3]
                random.shuffle(letters)
                return letters

            try:
                while not stop_event.is_set():
                    maroon = " st"
                    title = f"Thread-{thread_id}"
                    hangu = jamo
                    cc = chi_chars
                    kk = katakana
                    nano = diction
                    acad = acadlist                 
                    random_letters = generate_random_letters()
                    sitch  = (round(random.random() * 9999, 4))
                    
                    sample_size_hangu = random.randint(1, min(20, len(hangu)))
                    sample_size_cc = random.randint(1, min(12, len(cc)))
                    sample_size_kk = random.randint(1, min(15, len(kk)))
                    sample_size_nano = random.randint(1, min(7, len(nano)))
                    sample_size_acad = random.randint(1, min(7, len(acad)))

                    hchat = random.choices(hangu, k=sample_size_hangu)
                    cchat = random.choices(cc, k=sample_size_cc)
                    kkhat = random.choices(kk, k=sample_size_kk)
                    kchat = random.choices(nano, k=sample_size_nano)
                    kchat2 = random.choices(acad, k=sample_size_acad)
                
                    ctm = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                    print(f"{maroon} {title} {random_letters} {sitch:.4f} {hchat} {cchat} {kkhat} {kchat} {kchat2} {ctm}")
                    print()
                    stop_event.wait(delay)

            except Exception as e:
                print(f"Thread {thread_id} error: {e}")
            finally:
                print(f"\nThread {thread_id} finished")

        def activate_threads(stop_event):
            title = input("thread name: ")
            while True:
                try:
                    num_threads = int(input("Number of threads: "))
                    if num_threads <= 0:
                        print("Enter a positive integer")
                        continue
                    break
                except ValueError:
                    print("Invalid input")

            while True:
                try:
                    delay_seconds = float(input("Time buffer: "))
                    if delay_seconds <= 0:
                        print("Enter a positive value")
                        continue
                    break
                except ValueError:
                    print("Invalid input")

            ct = datetime.datetime.now()
            monitor = "s-threads-start:"
            print()
            print(usr, monitor, title, ct)
            print()
            time.sleep(3)

            print("\nStarting threads...")
            print()
            
            threads = []
            
            for i in range(1, num_threads + 1):
                t = threading.Thread(target=worker_thread, args=(i, delay_seconds, stop_event), daemon=True)
                threads.append(t)
                t.start()
                print(f"Started Thread {i}")

            print("\nThreads started: Ctrl+C to stop\n")
            
            try:
                while True:
                    time.sleep(1) 
            except KeyboardInterrupt:
                print("\nStopping...")
                stop_event.set()
                for t in threads:
                    if t.is_alive():
                        t.join(timeout=1)

        def chichars():
            dd = list(chi_chars)
            while True:
                try:
                    number = int(input("Indicate number of (c-characters) results: "))
                except ValueError:
                    print("Invalid value")
                else:
                    break
            number
            time.sleep(0)
            print()
            chichar = random.choices(dd, k=number)
            ct = datetime.datetime.now()
            chchar = "c-characters:"
            print(chchar, chichar, ct)

        def pray():
            ct = datetime.datetime.now()
            print("You start praying to a God...")
            time.sleep(7)
            print("You finished praying", ct)
            time.sleep(3)

        def climb():
            time.sleep(1)
            climbing = ["you climb", "you climb", "you climb", "you climb", "you climb", "you climb", "you climb", "you climb", "you climb", "you climb", "you climb", "you climb", "you climb", "you climb", "you climb", "you climb", "you climb", "you climb", "you climb", "you climb", "you climb", "you climb", "you climb", "you climb", "you climb", "you climb", "you climb", "you climb", "you climb", "you climb", "you climb", "you climb", "you climb", "you climb", "you climb", "you climb", "you climb", "you climb", "you climb", "you climb", "you climb", "you climb", "you climb", "you climb", "you climb", "you climb", "you climb", "you climb", "you climb", "you hold unto a groove", "you hold unto a groove", "you hold unto a groove", "you hold unto a groove", "you hold unto a groove", "you hold unto a groove", "you reached a level", "you reached a level", "you reached a level", "you reached a level", "you reached a level", "you balance along a plank", "you balance along a plank", "you balance along a plank", "you balance along a plank", "you balance along a plank", "you balance along a plank", "you reach the top", "you reach the top", "you reach the top", "you reach the top", "you reach the top", "you reach the top", "you reach the top", "you fall",  "you fall",  "you fall",  "you fall", "you slide down", "you slide down", "you slide down", "you slide down", "you slide down", "you slide down", "you slide down", "you slip", "you slip", "you slip", "you slip", "you slip", "you walk along a ledge", "you walk along a ledge", "you walk along a ledge", "you walk along a ledge", "you walk along a ledge", "you walk along a ledge", "you walk along a ledge", "you walk along a ledge", "you walk along a ledge", "you find something to hold unto",  "you find something to hold unto",  "you find something to hold unto",  "you find something to hold unto",  "you find something to hold unto",  "you find something to hold unto",  "you find something to hold unto",  "you find something to hold unto",  "you find something to hold unto",  "you find something to hold unto",  "you find something to hold unto", "you hold for your life", "you hold for your life", "you hold for your life", "you hold for your life", "you hold for your life", "you hold for your life", "you hold for your life", "you hold for your life", "you hold for your life", "you got sighted", "you got sighted", "you got sighted", "you got sighted", "you got sighted", "you got sighted", "you got sighted", "you got sighted", "you balance", "you balance", "you balance", "you balance", "you balance", "you balance", "you balance", "you balance", "you balance", "you balance", "you balance", "you balance", "you balance", "you balance", "you balance", "you balance", ]
            climb = random.sample(climbing, 1)
            ct = datetime.datetime.now()
            clim = "climb:"
            print(clim, climb, ct)

        def prayer():
            ct = datetime.datetime.now()
            print("OM MANI PADME HUM", ct)

        def stats():
            stat = "stats:"
            hea = "Health:"
            health = (round(random.random()*120))
            conf = "Confidence:"
            confidence = (round(random.random()*120))
            oxyg = "Oxygen:"
            oxygen  = (round(random.random()*120))
            happ = "Happiness:"
            happiness = (round(random.random()*120))
            luc = "Luck:"
            luck = (round(random.random()*120))
            rele = "Release:"
            release = (round(random.random()*120))
            ener = "Energy:"
            energy = (round(random.random()*120))
            oppo = "Opportunity:"
            opportunity = (round(random.random()*120))
            chem = "Chemicals:"
            chemicals = (round(random.random()*120))
            ct = datetime.datetime.now()
            print(stat, hea, health, conf, confidence, oxyg, oxygen, happ, happiness, luc, luck, rele, release, ener, energy, oppo, opportunity, chem, chemicals, ct)

        def progress():
            ct = datetime.datetime.now()
            time.sleep(2)
            percentage = (round(random.random()*300))
            progress = "progress: "
            print(percentage)
            print("% done with")
            probability = (round(random.random()*4))
            print(probability)
            print("quads", ct)

        def light_incense():
            while True:
                try:
                    number = int(input("Enter incense number: "))
                except ValueError:
                    print("Invalid value")
                else:
                    break
            number
            numberstr = str(number)
            print()
            ct = datetime.datetime.now()
            print("You light" + "" + " " + "" + numberstr + "" + " " + "" + "incense...", ct)
            time.sleep(3)

        def heart_sutra():
            time.sleep(2)
            print()
            print("The Bodhisattva of Compassion, / When he meditated deeply, / Saw the emptiness of all five skandhas / And sundered the bonds that caused him suffering.")
            time.sleep(8)
            print()
            print("Here then, / Form is no other than emptiness, / Emptiness no other than form. / Form is only emptiness, / Emptiness only form.")
            time.sleep(8)
            print()
            print("Feeling, thought, and choice, / Consciousness itself, / Are the same as this.")
            time.sleep(8)
            print()
            print("All things are by nature void / They are not born or destroyed / Nor are they stained or pure / Nor do they wax or wane")
            time.sleep(8)
            print()
            print("So, in emptiness, no form, / No feeling, thought, or choice, / Nor is there consciousness. / No eye, ear, nose, tongue, body, mind; / No colour, sound, smell, taste, touch, / Or what the mind takes hold of, / Nor even act of sensing.")
            time.sleep(10)
            print()
            print("No ignorance or end of it, / Nor all that comes of ignorance; / No withering, no death, / No end of them.")
            time.sleep(7)
            print()
            print("Nor is there pain, or cause of pain, / Or cease in pain, or noble path / To lead from pain; / Not even wisdom to attain! / Attainment too is emptiness.")
            time.sleep(8)
            print()
            print("So know that the Bodhisattva / Holding to nothing whatever, / But dwelling in Prajna wisdom, / Is freed of delusive hindrance, / Rid of the fear bred by it, / And reaches clearest Nirvana.")
            time.sleep(9)
            print()
            print("All Buddhas of past and present, / Buddhas of future time, / Using this Prajna wisdom, / Come to full and perfect vision.")
            time.sleep(8)
            print()
            print("Hear then the great dharani, / The radiant peerless mantra, / The Prajnaparamita / Whose words allay all pain; Hear and believe its truth!")
            time.sleep(8)
            print()
            print("Gate Gate Paragate Parasamgate / Bodhi Svaha / Gate Gate Paragate Parasamgate / Bodhi Svaha / Gate Gate Paragate Parasamgate / Bodhi Svaha")
            time.sleep(10)

        def hebrews():
            time.sleep(2)
            heBrews1 = ['Scroll 1.1 "The Meadows" There isnt compliance, there is only substance.', 'Scroll 1.2 "The Meadows" Nothing is really certain, but we are certain.', 'Scroll 1.3 "The Meadows" Is there a multiverse? Because if there is then the jobs are really done.', 'Scroll 1.4 "The Meadows" I think that there is no certainty to anything, only probability.', 'Scroll 1.5 "The Meadows" Tobacco got me, just a little, right now, what is this chemical?', 'Scroll 1.6 "The Meadows" Extreme climate is too extreme.', 'Scroll 1.7 "The Meadows" High up high, low as lows.', 'Scroll 1.8 "The Meadows" Music playing nothing really matters anymore, is that not the matter?', 'Scroll 1.9 "The Meadows" I come black and blue.', 'Scroll 1.10 "The Meadows" Dont come to me when youre lonely.', 'Scroll 1.11 "The Meadows" Hit it high up, lock to the target and glide it.', 'Scroll 1.12 "The Meadows" Busy as a bee, tranquil as an ox.', 'Scroll 1.13 "The Meadows" Dry it up, then soak it again.', 'Scroll 1.14 "The Meadows" Stop the press, stop the press, stop it.', 'Scroll 1.15 "The Meadows" Extremate again.', 'Scroll 1.16 "The Meadows" Youre just an NPC (Non-Playable Character)', 'Scroll 2.1 "Ecstacy" Happiness is a must.', 'Scroll 2.2 "Ecstacy" Company is equitable.', 'Scroll 2.3 "Ecstacy" Nano-particles', 'Scroll 2.4 "Ecstacy" Kill me softly, softly.', 'Scroll 2.5 "Ecstacy" Stop and just look and just listen.', 'Scroll 2.6 "Ecstacy" Indicate the trajectory, to come up with a map.', 'Scroll 2.7 "Ecstacy" Go far, go longing, go straight ahead!', 'Scroll 2.8 "Ecstacy" Hit me up on my phone.', 'Scroll 2.9 "Ecstacy" Projectile vomit sometimes.', 'Scroll 2.10 "Ecstacy" Build me up, continue.', 'Scroll 2.11 "Ecstacy" Build me a temple too.', 'Scroll 2.12 "Ecstacy" Supper is served.', 'Scroll 3.1 "The End" This poison, it got me.', 'Scroll 3.2 "The End" Never minding anything, I take flight.', 'Scroll 3.3 "The End" Its not even this, but you get my point.', 'Scroll 3.4 "The End" Quite experimental, yet successful in personal terms.', 'Scroll 3.5 "The End" This scroll means something to us.', 'Scroll 3.6 "The End" Indica or Sativa? or not at all, never?', 'Scroll 3.7 "The End" Pump it up.', 'Scroll 3.8 "The End" Run on your free time.']
            heBrews = (random.choice(heBrews1), random.choice(heBrews1), random.choice(heBrews1), random.choice(heBrews1))
            verse = random.sample(heBrews, 4)
            ct = datetime.datetime.now()
            brews = "heBrews:"
            print(brews, verse, ct)

        def teletubby():
            ct = datetime.datetime.now()
            print("You think of a command", ct)
            time.sleep(2)

        def herbs():
            while True:
                try:
                    number = int(input("Indicate number of (herbals) results: "))
                except ValueError:
                    print("Invalid value")
                else:
                    break
            number
            time.sleep(1)
            print()
            herbs = ["Acacia senegal - Gum arabic - A natural gum sourced from hardened sap of various species of acacia tree used in ancient birth control as well as a binder and emulsifier for medicinal compounds.", "Achillea millefolium - Common yarrow - Purported to be a diaphoretic, astringent, tonic, stimulant and mild aromatic.", "Actaea racemosa - Black cohosh - Historically used for arthritis and muscle pain, used more recently for conditions related to menopause and menstruation.", "Aesculus hippocastanum - Horse chestnut - Its seeds, leaves, bark, and flowers have been used medicinally for many centuries for treating joint pain, bladder and gastrointestinal problems, fever, leg cramps, and other conditions. It may be useful for treating chronic venous insufficiency. The raw plant materials are toxic unless processed.", "Ageratina altissima - White snakeroot - White snakeroot    Root tea has been used to treat diarrhea, kidney stones, and fever. A root poultice can be used on snakebites. The smoke from burning leaves is used to revive unconscious people. The plant contains the toxin tremetol which causes milk sickness, a sometimes fatal condition.", "Alcea rosea - Common hollyhock - Believed to be an emollient and laxative. It is used to control inflammation, to stop bedwetting and as a mouthwash in cases of bleeding gums.", "Alisma plantago-aquatica - Water-plantain - Used for the urinary tract.", "Allium sativum - Garlic - Purported use to lower blood cholesterol and high blood pressure.", "Aloe vera - Aloe vera - Leaves are widely used to heal burns, wounds and other skin ailments.", "Althaea officinalis - Marsh-mallow - Used historically as both a food and a medicine.", "Amorphophallus konjac - Konjac - Significant dietary source of glucomannan,[14] which is purported for use in treating obesity, constipation,[15] and reducing cholesterol.", "Anemone hepatica - Common hepatica - Historically used to treat liver diseases, it is still used in alternative medicine today. Other modern applications by herbalists include treatments for pimples, bronchitis and gout.", "Angelica archangelica - Garden angelica  - Roots have been used in the traditional Austrian medicine internally as tea or tincture for treatment of disorders of the gastrointestinal tract, respiratory tract, nervous system, and also against fever, infections, and flu.", "Angelica sinensis - Dong quai - Used for thousands of years in Asia, primarily in women's health.", "Apium graveolens - Celery - Seed is used only occasionally in tradition medicine. Modern usage is primarily as a diuretic.", "Arctium lappa - Burdock - Used traditionally as a diuretic and to lower blood sugar and, in traditional Chinese medicine as a treatment for sore throat and symptoms of the common cold.", "Arnica montana - Arnica - Used as an anti-inflammatory and for osteoarthritis. The US Food and Drug Administration has classified Arnica montana as an unsafe herb because of its toxicity. It should not be taken orally or applied to broken skin where absorption can occur.", "Astragalus propinquus - Astragalus - Long used in traditional Chinese medicine.", "Atropa belladonna - Belladonna - Although toxic, was used historically in Italy by women to enlarge their pupils, as well as a sedative, among other uses. The name itself means 'beautiful woman' in Italian.", "Azadirachta indica - Neem", "Used in India to treat worms, malaria, rheumatism and skin infections among many other things. Its many uses have led to neem being called 'the village dispensary' in India.", "Bellis perennis - Daisy - Flowers have been used in the traditional Austrian medicine internally as tea (or the leaves as a salad) for treatment of disorders of the gastrointestinal and respiratory tract.", "Berberis vulgaris - Barberry - Long history of medicinal use, dating back to the Middle Ages particularly among Native Americans. Uses have included skin ailments, scurvy and gastro-intestinal ailments.", "Borago officinalis - Borage - Used in hyperactive gastrointestinal, respiratory and cardiovascular disorders, such as gastrointestinal (colic, cramps, diarrhea), airways (asthma, bronchitis), cardiovascular, (cardiotonic, antihypertensive and blood purifier), urinary (diuretic and kidney/bladder disorders).", "Broussonetia kurzii - Salae - Known as Salae in Thailand where this species is valued as a medicinal plant.", "Calendula officinalis - Marigold - Also named calendula, has a long history of use in treating wounds and soothing skin.", "Cannabis - Hemp, Cannabis, Marijuana, Indian hemp, Ganja  - Used worldwide since ancient times as treatment for various conditions and ailments including pain, inflammation, gastrointestinal issues such as IBS, muscle relaxation, anxiety, Alzheimer's and dementia, ADHD, autism, cancer, cerebral palsy, recurring headaches, Crohn's disease, depression, epilepsy, glaucoma, insomnia, and neuropathy among others.", "Capsicum annuum - Cayenne - Type of chili that has been used as both food and medicine for thousands of years. Uses have included reducing pain and swelling, lowering triglyceride and cholesterol levels and fighting viruses and harmful bacteria, due to high levels of Vitamin C.", "Capsicum frutescens - Chili - Its active ingredient, capsaicine, is the basic of commercial pain-relief ointments in Western medicine. The low incidence of heart attack in Thais may be related to capsaicine's fibronolytic action (dissolving blood clots).", "Carica papaya - Papaya - Used for treating wounds and stomach troubles.", "Cassia occidentalis - Coffee senna - Used in a wide variety of roles in traditional medicine, including in particular as a broad-spectrum internal and external antimicrobial, for liver disorders, for intestinal worms and other parasites and as an immune-system stimulant.", "Catha edulis - Khat - Mild stimulant used for thousands of years in Yemen, and is banned today in many countries. Contains the amphetamine-like substance cathinone.", "Cayaponia espelina - São Caetano melon  - It is a diuretic and aid in the treatment of diarrhea and syphilis.", "Centaurea cyanus - Cornflower  - In herbalism, a decoction of cornflower is effective in treating conjunctivitis and as a wash for tired eyes.", "Chrysopogon zizanioides - Vetiver - Used for skin care.", "Cinchona spec. - Cinchona - Genus of about 38 species of trees whose bark is a source of alkaloids, including quinine. Its use as a febrifuge was first popularized in the 17th century by Peruvian Jesuits.", "Citrus × aurantium - Bitter orange - Used in traditional Chinese medicine and by indigenous peoples of the Amazon for nausea, indigestion and constipation.", "Citrus limon - Lemon - Along with other citruses, it has a long history of use in Chinese and Indian traditional medicine. In contemporary use, honey and lemon is common for treating coughs and sore throat.", "Citrus trifoliata - Trifoliate orange, bitter orange - Fruits of Citrus trifoliata are widely used in Oriental medicine as a treatment for allergic inflammation.", "Cissampelos pareira - Velvetleaf - Used for a wide variety of conditions.", "Cnicus benedictus - Blessed thistle - Used during the Middle Ages to treat bubonic plague. In modern times, herbal teas made from blessed thistle are used for loss of appetite, indigestion and other purposes.", "Crataegus monogyna and Crataegus laevigata - Hawthorn - Fruit has been used for centuries purportedly for heart disease, digestive and kidney related problems.", "Curcuma longa - Turmeric - Spice that lends its distinctive yellow color to Indian curries, has long been used in Ayurvedic and traditional Chinese medicine to aid digestion and liver function, relieve arthritis pain, and regulate menstruation.", "Cypripedium parviflorum - Yellow lady's slipper - The Cypripedium species have been used in native remedies for dermatitis, tooth aches, anxiety, headaches, as an antispasmodic, stimulant and sedative. However, the preferred species for use are Cyp. parviflorum and Cyp.acaule, used as topical applications or tea.", "Digitalis lanata - Digitalis or foxglove - It came into use in treating cardiac disease in late 18th century England in spite of its high toxicity.a Its use has been almost entirely replaced by the pharmaceutical derivative Digoxin, which has a shorter half-life in the body, and whose toxicity is therefore more easily managed. Digoxin is used as an antiarrhythmic agent and inotrope.[", "Echinacea purpurea - Purple coneflower - This plant and other species of Echinacea have been used for at least 400 years by Native Americans to treat infections and wounds, and as a general 'cure-all' (panacea). It is currently used for symptoms associated with cold and flu.", "Echinopsis pachanoi - San Pedro cactus - The San Pedro cactus contains the entheogen mescaline and has a long history of being used in Andean traditional medicine.", "Ephedra sinica - Ephedra - It has been used in traditional Chinese medicine for more than 2,000 years.[58][59] Native Americans and Mormon pioneers drank a tea brewed from other Ephedra species, called 'Mormon tea' and 'Indian tea'. It contains the alkaloids ephedrine and pseudoephedrine, which are used as breathing aids (bronchodilators and decongestants).", "Equisetum arvense - Horsetail - Dates back to ancient Roman and Greek medicine, when it was used to stop bleeding, heal ulcers and wounds, and treat tuberculosis and kidney problems.", "Eriodictyon crassifolium - Yerba Santa - Used by the Chumash people to keep airways open for proper breathing. The US Forest Service profile for Eriodictyon crassifolium provides information on species distribution; taxonomic relationships; ecological and evolutionary considerations for restoration; growth form and distinguishing traits; habitat characteristics; projected future suitable habitat; growth, reproduction and dispersal; biological interactions; ecological genetics; seed characteristics, germination requirements and processing; and plant uses including agriculture, restoration, and traditional products, plus an extensive bibliography. It is part of Riverside-Corona Resource Conservation District's resource materials collection on native plant recommendations for southern California ecoregions.", "Erythroxylum coca - Coca - Used as coca tea or chewed, traditionally as a stimulant to overcome fatigue, hunger, thirst, and altitude sickness.[64] Also used as an anesthetic and analgesic.", "Eschscholzia californica - Californian poppy - Used as a herbal remedy: an aqueous extract of the plant has sedative and anxiolytic actions.", "Eucalyptus globulus - Eucalyptus - Leaves were widely used in traditional medicine as a febrifuge.[67] Eucalyptus oil is commonly used in over-the-counter cough and cold medications, as well as for an analgesic.", "Euonymus atropurpureus - Wahoo - Plant is a purgative and might affect the heart.", "Euphorbia hirta - Asthma-plant - Used traditionally in Asia to treat bronchitic asthma and laryngeal spasm. It is used in the Philippines for dengue fever.", "Euphrasia - Eyebright - Used for eye problems, mental depression, oxygenation and radiation poisoning.", "Euterpe oleracea - Açai - Although açai berries are a longstanding food source for indigenous people of the Amazon, there is no evidence that they have effectiveness for any health-related purpose.", "Ferula assa-foetida - Asafoetida - Might be useful for IBS, high cholesterol, and breathing problems.", "Frangula alnus - Alder buckthorn - Bark (and to a lesser extent the fruit) has been used as a laxative, due to its 3 – 7% anthraquinone content. Bark for medicinal use is dried and stored for a year before use, as fresh bark is violently purgative; even dried bark can be dangerous if taken in excess.", "Fumaria officinalis - Fumitory - Traditionally thought to be good for the eyes and to remove skin blemishes. In modern times herbalists use it to treat skin diseases and conjunctivitis, as well as to cleanse the kidneys. However, Howard (1987) warns that fumitory is poisonous and should only be used under the direction of a medical herbalist.", "Galanthus - Snowdrop - It contains an active substance called galantamine, which is an acetylcholinesterase inhibitor. Galantamine (or galanthamine) can be helpful in the treatment of Alzheimer's disease, though it is not a cure.", "Geranium robertianum - Robert geranium  - In traditional herbalism, it was used as a remedy for toothache and nosebleeds[79] and as a vulnerary (used for or useful in healing wounds).", "Ginkgo biloba - Ginkgo - The leaf extract has been used to treat asthma, bronchitis, fatigue, Alzheimer's and tinnitus.", "Glechoma hederacea - Ground-ivy - It has been used as a 'lung herb'. Other traditional uses include as an expectorant, astringent, and to treat bronchitis. The essential oil of the plant has been used for centuries as a general tonic for colds and coughs, and to relieve congestion of the mucous membranes.", "Glycyrrhiza glabra - Licorice root - Purported uses include stomach ulcers, bronchitis, and sore throat.", "Hamamelis virginiana - Common witch-hazel - It produces a specific kind of tannins called hamamelitannins. One of those substances displays a specific cytotoxic activity against colon cancer cells.", "Hippophae rhamnoides - Sea buckthorn - The leaves are used as herbal medicine to alleviate cough and fever, pain, and general gastrointestinal disorders as well as to cure dermatologic disorders. Similarly, the fruit juice and oils can be used in the treatment of liver disease, gastrointestinal disorders, chronic wounds or other dermatological disorders.", "Hoodia gordonii - Hoodia - The plant is traditionally used by Kalahari San (Bushmen) to reduce hunger and thirst. It is marketed as an appetite suppressant.", "Hydrastis canadensis - Goldenseal - Although used traditionally by Native Americans to treat skin diseases and ulcers, there is no scientific evidence to support the use of goldenseal for treating any disease.", "Hypericum perforatum - St. John's wort - Widely used within herbalism for depression. Evaluated for use as an antidepressant, but with ambiguous results.", "Hyssopus officinalis - Hyssop - It is purported for digestive and intestinal problems, and for respiratory problems.", "Ilex paraguariensis - Yerba mate - Mate contains compounds that may improve mood.", "Illicium verum - Star anise - It is the major source of the chemical compound shikimic acid, a primary precursor in the pharmaceutical synthesis of anti-influenza drug oseltamivir (Tamiflu).", "Inula helenium - Elecampane - It is used in herbal medicine as an expectorant and for water retention.", "Jasminum officinale - Jasmine - It is purported as either an antiseptic or anti-inflammatory agent.", "Knautia arvensis - Field scabious - The whole plant is astringent and mildly diuretic.", "Larrea tridentata - Chaparral - The leaves and twigs are used by Native Americans to make a herbal tea used for a variety of conditions. Chaparral has also been shown to have high liver toxicity, and has led to kidney failure, and is not recommended for any use by the U.S. Food and Drug Administration or American Cancer Society.", "Laurus nobilis - Bay laurel - Aqueous extracts of bay laurel can be used as astringents and even as a reasonable salve for open wounds.", "Lavandula angustifolia - Lavender - It was traditionally used as an antiseptic and for mental health purposes. It was also used in ancient Egypt in mummifying bodies. There is little scientific evidence that use of lavender affects health.", "Lawsonia inermis - Henna", "Leucojum aestivum - Summer snowflake", "Linum usitatissimum - Flaxseed - The plant is most commonly used as a laxative. Flaxseed oil is used for different conditions, including arthritis.", "Magnolia officinalis - Magnolia-bark - The bark contains magnolol and honokiol, two polyphenolic compounds.", "Malva sylvestris - Mallow - The seeds are used internally in a decoction or herbal tea as a demulcent and diuretic, and the leaves made into poultices as an emollient for external applications. ",\
             "Matricaria recutita and Anthemis nobilis - Chamomile - It has been used over history for a variety of conditions, including sleeplessness and anxiety.", "Medicago sativa - Alfalfa - The leaves are purported to lower cholesterol, and treat kidney and urinary tract ailments, although there is insufficient scientific evidence for its efficacy.", "Melaleuca alternifolia - Tea tree oil - It has been used over history by Australian aboriginal people. Modern usage is primarily as an antibacterial or antifungal agent, but there is insufficient scientific evidence for such effects.", "Melissa officinalis - Lemon balm - Lemon balm  It is purported as a sleep aid and digestive aid.", "Mentha x piperita - Peppermint - Its oil, from a cross between water mint and spearmint, has a history of purported use for various conditions, including nausea, indigestion, and symptoms of the common cold.", "Mitragyna speciosa - Kratom - Kratom leaves are chewed to relieve musculoskeletal pain and increase energy, appetite, and sexual desire in ways similar to khat and coca.", "Momordica charantia - Bitter melon", "Morinda citrifolia - Noni - It is purported for joint pain and skin conditions.", "Moringa oleifera - Drumstick tree  - It is used for food and traditional medicine.", "Nasturtium officinale - Watercress", "Nelumbo nucifera - Lotus - Insufficient evidence for any biological effect.", "Nigella sativa - Nigella, black-caraway, black-cumin, and kalonji - One meta-analysis of clinical trials concluded that N. sativa has a short-term benefit on lowering systolic and diastolic blood pressure.", "Ocimum tenuiflorum - Tulsi or holy basil - It is used for a variety of purposes in traditional medicine; tulsi is taken in many forms: as herbal tea, dried powder, fresh leaf or mixed with ghee. Essential oil extracted from Karpoora tulasi is mostly used for medicinal purposes and in herbal cosmetics.", "Oenothera - Evening primrose - Its oil has been used since the 1930s for eczema, and more recently as an anti-inflammatory, but there is insufficient evidence for it having any effect.", "Origanum vulgare - Oregano", "Panax spec. - Ginseng - Asian ginseng may affect glucose metabolism and lower blood sugar levels, but the poor quality of research prevents conclusions about such effects.", "Papaver somniferum - Opium poppy - The plant is the plant source of morphine, used for pain relief. Morphine made from the refined and modified sap is used for pain control in people with severe cancer.", "Passiflora - Passion flower", "Peganum harmala - Syrian Rue (common name Harmal)", "Pelargonium sidoides - Umckaloabo, or South African Geranium - Possibly useful for treating respiratory infections.", "Piper methysticum - Kava - The plant has been used for centuries in the South Pacific to make a ceremonial drink with sedative and anesthetic properties, with potential for causing liver injury.", "Piscidia erythrina / Piscidia piscipula - Jamaica dogwood - The plant is used in traditional medicine for the treatment of insomnia and anxiety, despite serious safety concerns. A 2006 study suggested medicinal potential.", "Plantago lanceolata - Plantain - It is used frequently in herbal teas and other herbal remedies. A tea from the leaves is used as a highly effective cough medicine. In the traditional Austrian medicine Plantago lanceolata leaves have been used internally (as syrup or tea) or externally (fresh leaves) for treatment of disorders of the respiratory tract, skin, insect bites, and infections.", "Platycodon grandiflorus - Platycodon, balloon flower - The extracts and purified platycoside compounds (saponins) from the roots may exhibit neuroprotective, antimicrobial, anti-inflammatory, anti-cancer, anti-allergy, improved insulin resistance, and cholesterol-lowering properties.", "Polemonium reptans - Abscess root - It is used to reduce fever, inflammation, and cough.", "Psidium guajava - Guava - It has a rich history of use in traditional medicine. It is traditionally used to treat diarrhea; however, evidence of its effectiveness is very limited.", "Ptelea trifoliata - Wafer Ash - The root bark is used for the digestive system. Also known as hoptree.", "Pulmonaria officinalis - Lungwort - Used since the Middle Ages to treat and/or heal various ailments of the lungs and chest", "Quassia amara - Amargo, bitter-wood - A 2012 study found a topical gel with 4% Quassia extract to be a safe and effective cure of rosacea.", "Reichardia tingitana - False sowthistle - Uses in folk medicine have been recorded in the Middle East, its leaves being used to treat ailments such as constipation, colic and inflamed eyes.", "Rosa majalis - Cinnamon rose - It yields edible hip fruits rich in vitamin C, which are used in medicine and to produce rose hip syrup.", "Rosmarinus officinalis - Rosemary - It has been used medicinally from ancient times.", "Ruellia tuberosa - Minnieroot, fever root, snapdragon root - In folk medicine and Ayurvedic medicine it has been used as a diuretic, anti-diabetic, antipyretic, analgesic, antihypertensive, gastroprotective, and to treat gonorrhea.", "Rumex crispus - Curly dock or yellow dock  - In Western herbalism the root is often used for treating anemia, due to its high level of iron. The plant will help with skin conditions if taken internally or applied externally to things like itching, scrofula, and sores. It is also used for respiratory conditions, specifically those with a tickling cough that is worse when exposed to cold air. It mentions also passing pains, excessive itching, and that it helps enlarged lymphs.", "Salix alba - White willow - Plant source of salicylic acid, white willow is like the chemical known as aspirin, although more likely to cause stomach upset as a side effect than aspirin itself which can cause the lining of the stomach to be destroyed. Used from ancient times for the same uses as aspirin.", "Salvia officinalis - Sage - Shown to improve cognitive function in patients with mild to moderate Alzheimer's disease.", "Sambucus nigra - Elderberry - The berries and leaves have traditionally been used to treat pain, swelling, infections, coughs, and skin conditions and, more recently, flu, common cold, fevers, constipation, and sinus infections.", "Santalum album - Indian sandalwood - Sandalwood oil has been widely used in folk medicine for treatment of common colds, bronchitis, skin disorders, heart ailments, general weakness, fever, infection of the urinary tract, inflammation of the mouth and pharynx, liver and gallbladder complaints and other maladies.", "Santolina chamaecyparissus - Cotton lavender - Most commonly, the flowers and leaves are made into a decoction used to expel intestinal parasites.", "Saraca indica - Ashoka tree - The plant is used in Ayurvedic traditions to treat gynecological disorders. The bark is also used to combat oedema or swelling.", "Satureja hortensis - Summer savory - Its extracts show antibacterial and antifungal effects on several species including some of the antibiotic resistant strains.", "Sceletium tortuosum - Kanna - African treatment for depression. Suggested to be an SSRI or have similar effects, but unknown mechanism of activity.", "Senna auriculata - Avaram senna - The root is used in decoctions against fevers, diabetes, diseases of urinary system and constipation. The leaves have laxative properties. The dried flowers and flower buds are used as a substitute for tea in case of diabetes patients. The powdered seed is also applied to the eye, in case of chronic purulent conjunctivitis.", "Sesuvium portulacastrum - Shoreline purslane - The plant extract showed antibacterial and anticandidal activities and moderate antifungal activity.", "Silybum marianum - Milk thistle - It has been used for thousands of years for a variety of medicinal purposes, in particular liver problems.", "Stachytarpheta cayennensis - Blue snakeweed - Extracts of the plant are used to ease the symptoms of malaria. The boiled juice or a tea made from the leaves or the whole plant is taken to relieve fever and other symptoms. It is also used for dysentery, pain, and liver disorders. A tea of the leaves is taken to help control diabetes in Peru and other areas. Laboratory tests indicate that the plant has anti-inflammatory properties.", "Stellaria media - Common chickweed - It has been used as a remedy to treat itchy skin conditions and pulmonary diseases. 17th century herbalist John Gerard recommended it as a remedy for mange. Modern herbalists prescribe it for iron-deficiency anemia (for its high iron content), as well as for skin diseases, bronchitis, rheumatic pains, arthritis and period pain.", "Strobilanthes callosus - Karvy - The plant is anti-inflammatory, antimicrobial, and anti-rheumatic.", "Symphytum officinale - Comfrey - It has been used as a vulnerary and to reduce inflammation. It was also used internally in the past, for stomach and other ailments, but its toxicity has led a number of other countries, including Canada, Brazil, Australia, and the United Kingdom, to severely restrict or ban the use of comfrey.", "Syzygium aromaticum - Clove - The plant is used for upset stomach and as an expectorant, among other purposes. The oil is used topically to treat toothache.", "Tanacetum parthenium - Feverfew - The plant has been used for centuries for fevers, headaches, stomach aches, toothaches, insect bites and other conditions.", "Taraxacum officinale - Dandelion - It was most commonly used historically to treat liver diseases, kidney diseases, and spleen problems.", "Teucrium scordium - Water germander - It has been used for asthma, diarrhea, fever, intestinal parasites, hemorrhoids, and wounds.", "Thymus vulgaris - Thyme - The plant is used to treat bronchitis and cough. It serves as an antispasmodic and expectorant in this role. It has also been used in many other medicinal roles in Asian and Ayurvedic medicine, although it has not been shown to be effective in non-respiratory medicinal roles.", "Tilia cordata - Small-leaved linden - In the countries of Central, Southern and Western Europe, linden flowers are a traditional herbal remedy made into a herbal tea called tisane.", "Tradescantia zebrina - Inchplant - It is used in southeast Mexico in the region of Tabasco as a cold herbal tea, which is named Matali. Skin irritation may result from repeated contact with or prolonged handling of the plant, particularly from the clear, watery sap (a characteristic unique to T. zebrina as compared with other types).", "Trema orientalis - Charcoal-tree - The leaves and the bark are used to treat coughs, sore throats, asthma, bronchitis, gonorrhea, yellow fever, toothache, and as an antidote to general poisoning.", "Trifolium pratense - Red clover - The plant is an ingredient in some recipes for essiac tea. Research has found no benefit for any human health conditions.", "Trigonella foenum-graecum - Fenugreek - It has long been used to treat symptoms of menopause, and digestive ailments. More recently, it has been used to treat diabetes, loss of appetite and other conditions.", "Triticum aestivum - Wheatgrass - It may contain antioxidant and anti-inflammatory compounds.", "Turnera subulata - White buttercup - It is used for skin, gastrointestinal, and respiratory ailments.", "Uncaria tomentosa - Cat's claw - It has a long history of use in South America to prevent and treat disease.", "Urtica dioica - Common nettle, stinging nettle - It has been used in the traditional Austrian medicine internally (as tea or fresh leaves) to treat disorders of the kidneys and urinary tract, gastrointestinal tract, locomotor system, skin, cardiovascular system, hemorrhage, influenza, rheumatism, and gout.", "Vaccinium spec. - Blueberries - They are of current medical interest as an antioxidant and for urinary tract ailments.", "Vaccinium macrocarpon - Cranberry - It was used historically as a vulnerary and for urinary disorders, diarrhea, diabetes, stomach ailments, and liver problems. Modern usage has concentrated on urinary tract related problems.", "Vaccinium myrtillus - Bilberry - It is used to treat diarrhea, scurvy, and other conditions.", "Valeriana officinalis - Valerian - It has been used since at least ancient Greece and Rome for sleep disorders and anxiety.", "Verbascum thapsus - Common mullein  - It contains glycyrrhizin compounds with bactericide and potential anti-tumoral action. These compounds are concentrated in the flowers.", "Verbena officinalis - Verbena - It is used for sore throats and respiratory tract diseases.", "Vernonia amygdalina - Bitter leaf - The plant is used by both primates and indigenous peoples in Africa to treat intestinal ailments such as dysentery.", "Veronica officinalis - Veronica - The plant is used for sinus and ear infections.", "Viburnum tinus - Laurustinus - V. tinus has medicinal properties. The active ingredients are viburnin (a substance or more probably a mixture of compounds) and tannins. Tannins can cause stomach upset. The leaves when infused have antipyretic properties. The fruits have been used as purgatives against constipation. The tincture has been used lately in herbal medicine as a remedy for depression. The plant also contains iridoid glucosides.", "Viola tricolor - Wild pansy - It is one of many viola plant species containing cyclotides. These small peptides have proven to be useful in drug development due to their size and structure giving rise to high stability. Many cyclotides, found in Viola tricolor are cytotoxic. This feature means that it could be used to treat cancers.", "Viscum album - European mistletoe - It has been used to treat seizures, headaches, and other conditions.", "Vitex agnus-castus - Chasteberry - It has been used for over thousands of years for menstrual problems, and to stimulate lactation.", "Vitis vinifera - Grape - The leaves and fruit have been used medicinally since the ancient Greeks.", "Withania somnifera -   Ashwagandha - The plant's long, brown, tuberous roots are used in traditional medicine. In Ayurveda, the berries and leaves are applied externally to tumors, tubercular glands, carbuncles, and ulcers.", "Xanthoparmelia scabrosa - Sexy footpath lichen - It is a lichen used for sexual dysfunction.", "Youngia japonica -      Japanese hawkweed - The plant is antitussive and febrifuge. It is also used in the treatment of boils and snakebites.", "Zingiber officinale - Ginger - Ginger is effective for the relief of nausea."]
            herbal = random.sample(herbs, number)
            h = "herbals:"
            letters1 = ["A", "a", "B", "b", "C", "c", "D", "d", "E", "e", "F", "f", "G", "g", "H", "h", "I", "i", "J", "j", "K", "k", "L", "l", "M", "m", "N", "n", "O", "o", "P", "p", "Q", "q", "R", "r", "S", "s", "T", "t", "U", "u", "V", "v", "W", "w", "X", "x", "Y", "y", "Z", "z"]
            letters2 = ["A", "a", "B", "b", "C", "c", "D", "d", "E", "e", "F", "f", "G", "g", "H", "h", "I", "i", "J", "j", "K", "k", "L", "l", "M", "m", "N", "n", "O", "o", "P", "p", "Q", "q", "R", "r", "S", "s", "T", "t", "U", "u", "V", "v", "W", "w", "X", "x", "Y", "y", "Z", "z"]
            letters3 = ["A", "a", "B", "b", "C", "c", "D", "d", "E", "e", "F", "f", "G", "g", "H", "h", "I", "i", "J", "j", "K", "k", "L", "l", "M", "m", "N", "n", "O", "o", "P", "p", "Q", "q", "R", "r", "S", "s", "T", "t", "U", "u", "V", "v", "W", "w", "X", "x", "Y", "y", "Z", "z"]
            letters4 = ["A", "a", "B", "b", "C", "c", "D", "d", "E", "e", "F", "f", "G", "g", "H", "h", "I", "i", "J", "j", "K", "k", "L", "l", "M", "m", "N", "n", "O", "o", "P", "p", "Q", "q", "R", "r", "S", "s", "T", "t", "U", "u", "V", "v", "W", "w", "X", "x", "Y", "y", "Z", "z"]
            letters5 = ["A", "a", "B", "b", "C", "c", "D", "d", "E", "e", "F", "f", "G", "g", "H", "h", "I", "i", "J", "j", "K", "k", "L", "l", "M", "m", "N", "n", "O", "o", "P", "p", "Q", "q", "R", "r", "S", "s", "T", "t", "U", "u", "V", "v", "W", "w", "X", "x", "Y", "y", "Z", "z"]
            letter1 = random.sample(letters1, 1)
            letter2 = random.sample(letters2, 1)
            letter3 = random.sample(letters3, 1)
            letter4 = random.sample(letters4, 1)
            letter5 = random.sample(letters5, 1)
            value = (round(random.random()*9999999999,10))
            ct = datetime.datetime.now()
            print(h, letter1, letter2, letter3, letter4, letter5, value, herbal, ct)

        def legal_terms():
            dd = list(legal_terms1)
            while True:
                try:
                    number = int(input("Indicate number of (legal_terms) results: "))
                except ValueError:
                    print("Invalid value")
                else:
                    break
            number
            time.sleep(1)
            print()
            law = random.sample(dd, number)
            ct = datetime.datetime.now()
            l = "law:"
            print(l, law, ct)

        def degree():
            dd = list(degrees1)
            while True:
                try:
                    number = int(input("Indicate number of (degree/major) results: "))
                except ValueError:
                    print("Invalid value")
                else:
                    break
            number
            time.sleep(1)
            print()
            degree = random.sample(dd, number)
            value = (round(random.random()*9999,4))
            d = "degree/major:"
            bu = "-from Boston University website (bu.edu)"
            ct = datetime.datetime.now()
            print(d, value, degree, ct)
            print()
            print(bu)

        def biology():
            dd = list(biology1)
            while True:
                try:
                    number = int(input("Indicate number of (biology) results: "))
                except ValueError:
                    print("Invalid value")
                else:
                    break
            number
            time.sleep(0)
            print()
            b = random.sample(dd, number)
            ct = datetime.datetime.now()
            bio = "biology:"
            print(bio, b, ct)

        def chemistry():
            dd = list(chemistry1)
            while True:
                try:
                    number = int(input("Indicate number of (chemistry) results: "))
                except ValueError:
                    print("Invalid value")
                else:
                    break
            number
            print()
            time.sleep(.4)
            ch = random.sample(dd, number)
            ct = datetime.datetime.now()
            chem = "chemistry:"
            print(chem, ch, ct)

        def patient_simu():
            time.sleep(0)
            print()
            t_time = datetime.datetime.now()
            patient = "PATIENT:"
            initials = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
            name = random.sample(initials, 1)
            surname = random.sample(initials, 1)
            n = "name:"
            ages = (round(random.random()*100))
            age = "age:"
            genders = ["male", "female"]
            gender = random.sample(genders, 1)
            g = "gender:"
            localities = ["local", "global"]
            locality = random.sample(localities, 1)
            l = "locality:"
            temperature = random.randrange(25, 45)
            temp = "body temperature:"
            pulse = random.randrange(30, 200)
            pu = "pulse rate:"
            respiration = random.randrange(5, 45)
            rr = "respiration rate:"
            bloodp = ["normal", "normal", "normal", "elevated", "elevated", "stage 1", "stage 2"]
            pressure = random.sample(bloodp, 1)
            bp = "blood pressure:"
            symptoms1 = ["chills", "fever", "numbness and/or tingling and/or electric tweaks", "light-headed", "dizzy", "mouth is dry", "nauseated", "sick (flu, need to vomit etc.)", "short of breath", "sleepy", "sweaty", "thirsty", "tired", "weak",  "n/a", "n/a", "n/a", "n/a", "n/a", "n/a", "n/a", "n/a", "n/a", "n/a"]
            symptoms = (random.choice(symptoms1), random.choice(symptoms1), random.choice(symptoms1), random.choice(symptoms1), random.choice(symptoms1), random.choice(symptoms1), random.choice(symptoms1), random.choice(symptoms1), random.choice(symptoms1), random.choice(symptoms1), random.choice(symptoms1), random.choice(symptoms1))
            symptom = random.sample(symptoms, random.randint(1,12))
            s = "symptoms:"
            others1 = ["can't breathe normally", "losing hearing", "sounds are too loud", "ringing or hissing in my ears", "can't move one side", "can't defecate normally", "can't urinate normally", "can't remember normally", "blindness", "double vision", "blurred vision", "can't sleep normally", "can't smell things normally", "can't speak normally", "can't excrete solid feces", "can't stop scratching", "can't stop sweating", "can't swallow normally", "can't taste properly", "can't walk normally", "can't write normally", "n/a", "n/a", "n/a", "n/a", "n/a", "n/a", "n/a", "n/a", "n/a", "n/a", "n/a", "n/a", "n/a", "n/a", "n/a", "n/a", "n/a", "n/a", "n/a", ]
            others = (random.choice(others1), random.choice(others1), random.choice(others1), random.choice(others1), random.choice(others1), random.choice(others1), random.choice(others1), random.choice(others1), random.choice(others1), random.choice(others1), random.choice(others1), random.choice(others1), )
            osymptoms = random.sample(others, random.randint(1,12))
            othersy = "other symptoms:"
            msymptoms1 = ["anxiety", "social phobias", "panic disorders", "obsessive compulsive disorder", "post-traumatic stress disorder", "opossitional defiant disorder", "conduct disorder", "attention deficit hyperactivity disorder", "bipolar disorder", "depression", "amnesia", "depersonalisation disorder" ,"dissociative identity disorder", "anorexia", "bulimia nervosa", "binge eating disorder", "paranoid personality disorder", "delusional (paranoid) disorder" ,"schizophrenia", "post-traumatic stress disorder", "psychosis", "n/a", "n/a", "n/a", "n/a", "n/a", "n/a", "n/a", "n/a", "n/a", "n/a", "n/a", "n/a", "n/a", "n/a", "n/a", "n/a", "n/a", "n/a", "n/a", "n/a", "n/a", "n/a"]
            msymptoms = (random.choice(msymptoms1), random.choice(msymptoms1))
            missue = random.sample(msymptoms, 2)
            m = "mental issue:"
            print(t_time, patient, n, name, surname, age, ages, g, gender, l, locality, temp, temperature, pu, pulse, rr, respiration, bp, pressure, s, symptom, othersy, osymptoms, m, missue)

        def earth_science():
            dd = list(science1)
            while True:
                try:
                    number = int(input("Indicate number of (earth_science) results: "))
                except ValueError:
                    print("Invalid value")
                else:
                    break
            number
            time.sleep(1)
            print
            earth = random.sample(dd, number)
            ct = datetime.datetime.now()
            sci = "earth science:"
            print(sci, earth, ct)

        def psychology():
            dd = list(psychology1)
            while True:
                try:
                    number = int(input("Indicate number of (psychology) results: "))
                except ValueError:
                    print("Invalid value")
                else:
                    break
            number
            time.sleep(0)
            print()
            psych = random.sample(dd, number)
            ct = datetime.datetime.now()
            p = "psychology:"
            print(p, psych, ct)

        def medicals():
            dd = list(medicals1)
            while True:
                try:
                    number = int(input("Indicate number of (medical) results: "))
                except ValueError:
                    print("Invalid value")
                else:
                    break
            number
            time.sleep(0)
            print()
            medical = random.choices(dd, k=number)
            ct = datetime.datetime.now()
            med = "Medicals:"
            print(med, medical, ct)

        def MIMS():
            dd = list(mims)
            while True:
                try:
                    number = int(input("Indicate number of (MIMS) results: "))
                except ValueError:
                    print("Invalid value")
                else:
                    break
            number
            time.sleep(0)
            print()
            mimss = random.choices(dd, k=number)
            ct = datetime.datetime.now()
            mim = "MIMS:"
            print(mim, mimss, ct)

        def license():
            license = ["You have no license", "You have no license", "You have a license"]
            lice = random.sample(license, 1)
            ct = datetime.datetime.now()
            lic = "License:"
            print(lic, lice, ct)

        def police():
            time.sleep(0)
            code = ["Code Red", "Code Blue", "Code Green", "Code Orange", "Code Yellow", "Code Black", "Code White", "Code Purple", "Code Pink"]
            cod = random.sample(code, 1)
            urgency = ["Critical", "High", "Medium", "Low", "Lowest"]
            urge = random.sample(urgency, 1)
            polis = ["3511 A vehicle that has been impounded for a mandatory 30 days", "A.P.S. Arizona Public Service", "A.S.A.P. As soon as possible", "A.T.F. Bureau of Alcohol, Tobacco, and Firearms", "BAILED OUT Subject jumped out of car and ran", "BYFRND Boyfriend", "BEER RUN Shoplifting beer", "BONDOUT Prisoner who is going to post bail and be released", "BEEN MADE/BURNED Undercover officer's ID is known", "BHND Behind", "BIKE Motorcycle", "BIKERS Motorcycle riders", "BOOKING Booking prisoner into jail", "BREAKING UP Radio transmissions are not being received clearly", "BUSTED Arrested", "C.C.W. Carrying concealed weapon", "C.O. Civilian observer", "COMP Complainant", "C.L.D. Citation in lieu of detention", "CRACK, ROCK Smokeable form of cocaine", "D.E.B. Drug Enforcement Bureau", "DIX Detectives", "D.O.A. Dead on arrival", "D.O.B. Date of birth", "D.O.C. Department of Corrections", "D.P.S. Department of Public Safety", "DRIVE BY Shots fired from a moving vehicle", "E.O.C. Emergency Operations Center", "EQUIPMENT Police vehicle", "E.R. Emergency Room", "E.T.A. Estimated time of arrival", "F.A.A. Federal Aviation Administration", "B.I. Federal Bureau of Investigation", "F.I. Field Interrogation (Form 36 card)", "FILE STOP Notation put in police record; File Stops are confirmed by R&I Bureau", "FLIR Device used by aircraft to check for heat sources", "F.O.J. From other jurisdiction", "FRONT DESK Information Desk at main station", "FUGITIVE A wanted person", "GAS WASH/WASHDOWN Fire Department needed to wash gas down", "G.C.I. /B.A. Test used to determine blood alcohol content", "G.I.B. General Investigations Bureau", "GOT THE EYE In view (on a code 5)", "GRN Green", "HOND Honda", "HIT Subject or item wanted", "H.G.N. Horizontal Gaze Nystagmus (a test for detecting drug / alcohol use)", "HOBBLES Nylon rope used for legs and hand restraint", "HOOK Wrecker", "HSE House", "ICE, CRYSTAL Smokeable methamphetamine", "J.C.C. Juvenile Corrections Center", "J.P. Justice of the Peace", "JUMPED ON Assaulted", "JUMPER Person attempting suicide by jumping", "LADDER Fire Department ladder truck", "MARQUIS Test for narcotics", "M.D.C. Mobile Digital Computer (Police car computer)", "MEDICS Paramedics", "MERZ Mercedes Benz", "MHP Mobile Home Park", "MOTOR Solo motor unit", "NUMBER 1 SITUATION Probable cause for arrest", "NUMBER 9's Citations", "OD Overdose", "ONE FROM LIST Contract wrecker (926)", "ONE ON ONE Suspect / witness I.D.", "ONE ROLL Fingerprints", "O.V. On view, officer just witnessed an incident", "PAGE 2 Additional charges filed on a subject already in custody", "P.C. Probable cause", "PLE Purple", "P.O. Probation officer", "RESTRAINTS Leather straps used to restrain prisoners", "RINGER Audible alarm", "ROLLOVER Accident involving overturned vehicle", "R.P. Responsible party", "S/E/C Southeast corner", "SEIZURE Impound a vehicle; subject having convulsions", "SGT Sergeant", "SILENT Silent alarm", "SLIM JIM Device used to open locked vehicle", "SMASH & GRAB Broke out window, grabbed items and ran", "S.O./M.C.S.O. Maricopa County Sheriff's Office", "S.R.P. Salt River Project", "STRIPPED Vehicle stripped", "TECH Radio or computer technician", "THIRTY-SIX Field interrogation (or form 36)", "THREE WHEELER Police 3-wheeled motorcycle", "TILL TAP Grab money from register", "DISPATCH AN ANIMAL To shoot an animal", "TRAFFIC BOX KEY Key used to open traffic signal control box", "XHUSB Ex-husband", "WAGON/WAGON Police paddy wagon"]
            pol = random.sample(polis, random.randint(1, 8))
            locate = ["Local", "Local", "Foreign"]
            loc = random.sample(locate, 1)
            direction = ["South", "North", "West", "East", "Southwest", "Southeast", "Northwest", "Northeast"]
            dire = random.sample(direction, 1)
            suspectcode = (round(random.random()*26))
            sus = "Suspect Code:"
            location = (round(random.random()*99999999,10))
            ct = datetime.datetime.now()
            po = "police:"
            print(po, cod, urge, sus, suspectcode, pol, loc, dire, location, ct)

        def clearance():
            time.sleep(0)
            clearance = ["You are not cleared", "You are cleared"]
            clear = random.sample(clearance, 1)
            ct = datetime.datetime.now()
            med = "Clearance:"
            print(med, clear, ct)

        def entry():
            _entry = "Entry: "
            gates = ["Gate 1", "Gate 2", "Gate 3", "Gate 4", "Gate 5", "Gate 6", "Gate 7", "Gate 8", "Gate 9"]
            phases = ["Phase 1", "Phase 2", "Phase 3", "Phase 4", "Phase 5", "Phase 6", "Phase 7", "Phase 8", "Phase 9", "Phase 10"]
            floors = (round(random.random()*102))
            _floor = "Floor"
            gate = random.sample(gates, 1)
            phase = random.sample(phases, 1)
            rooms = (round(random.random()*102))
            ct = datetime.datetime.now()
            _room = "Room"
            print(_entry, gate, phase, _floor, floors, _room, rooms, ct)

        def zuz():
            dd = (diction)
            ct = datetime.datetime.now()
            nano = (random.choice(dd), random.choice(dd), random.choice(dd), random.choice(dd), random.choice(dd), random.choice(dd))
            result = random.sample(nano, random.randint(1, 6))
            sitar = ">"
            random_result = [random.choice(dd)]
            result_text = ", ".join(random_result)
            speak(result_text)
            print(sitar, result_text, result, ct)

        def micasa():
            time.sleep(1)
            mic = "home:"
            rooms = ["living room", "kitchen", "bedroom", "garden", "patio", "guest room", "garage", "work room", "library", "art room", "meditation room", "bath room", "temple"]
            micasa = random.sample(rooms, 1)
            ct = datetime.datetime.now()
            print(mic, micasa, ct)

        def stuff():
            stu = "stuff:"
            stuffd = ["sofa", "tv", "radio", "computer", "tablet", "phone", "refrigerator", "bed", "sink", "oven", "stove", "clock", "refreshments", "snacks", "cookies", "easel", "sketchpad", "laptop", "postcard", "table", "study table", "desk", "kitchen counter", "bible", "dining table", "chair", "gaming chair", "lamp", "light", "fruit", "speaker", "guitar", "piano", "synthesizer", "photo", "painting", "cdj", "vinyl", "electric guitar", "bass guitar", "monitor", "camera", "vinyl player", "gun", "iPod", "cctv", "bike", "car", "window", "door", "sweater", "ps5", "pillow", "blanket", "clothes", "dresser", "safe", "dhammapada", "keyboard", "koran", "paint", "paper", "brush", "tree", "pencil", "spraypaint", "drawing tablet", "drawing", "buddha", "air conditioner", "duster", "walkie", "grass", "mirror", "tools", "pen", "magazine", "book", "carpet", "mat", "zafu", "weed", "kush"]
            stuff = (random.choice(stuffd), random.choice(stuffd), random.choice(stuffd), random.choice(stuffd), random.choice(stuffd), random.choice(stuffd), random.choice(stuffd), random.choice(stuffd))
            stuffs = random.sample(stuff, random.randint(1, 8))
            ct = datetime.datetime.now()
            print(stu, stuffs, ct)

        def worship():
            ct = datetime.datetime.now()
            time.sleep(1)
            wor = "worship:"
            worship = "You worship in silence.."
            print(wor, worship, ct)
            time.sleep(3)

        def posting():
            ct = datetime.datetime.now()
            _have = "You have"
            _posting = "job postings with"
            _default = "defaults"
            _post = "Posting:"
            postings = (round(random.random()*5))
            defaults = (round(random.random()*15))
            print(_post, _have, postings, _posting, defaults, _default, ct)

        def speech(text):
            if platform.system() == "Linux" and shutil.which("termux-tts-speak"):
                try:
                    subprocess.run(["termux-tts-speak", text], check=True)
                    return
                except (subprocess.CalledProcessError, FileNotFoundError) as e:
                    print(f"Termux-TTS error: {e}")

            # Find the correct binary name for eSpeak
            cmd = shutil.which("espeak-ng") or shutil.which("espeak")
            
            if cmd:
                try:
                    # -v en+f2 is the built-in female variant for English
                    # We only pass 'cmd', not 'cmd' AND 'espeak'
                    subprocess.run([cmd, "-v", "en+f2", text], check=True)
                    return
                except subprocess.CalledProcessError as e:
                    print(f"eSpeak error: {e}")
                except Exception as e:
                    print(f"An unexpected error occurred: {e}")
            else:
                print("Error: eSpeak or espeak-ng not found on system.")
                   
        def muslim_prayer():
            def prayer():
                time.sleep(3)
                print("Allah Hu Akbar")
                speech("Allah Hu Akbar")
                time.sleep(2)
                print("Allah Hu Akbar")
                speech("Allah Hu Akbar")
                time.sleep(2)
                print()
                print("Glorious is my Lord the most Great, Glorious is my Lord the most great, Glorious is my Lord the most great")
                speech("Glorious is my Lord the most Great, Glorious is my Lord the most great, Glorious is my Lord the most great")
                time.sleep(4)
                print()
                print("Allah hears those who praise him, our Lord all praise is for you, praise which is abundant, excellent, and blessed")
                speech("Allah hears those who praise him, our Lord all praise is for you, praise which is abundant, excellent, and blessed")
                time.sleep(6)
                print()
                print("Glorious is my Lord the most Great, Glorious is my Lord the most great, Glorious is my Lord the most great")
                speech("Glorious is my Lord the most Great, Glorious is my Lord the most great, Glorious is my Lord the most great")
                time.sleep(4)
                print()
                print("Allah Hu Akbar")
                speech("Allah Hu Akbar")
                time.sleep(2)
                print()
                print("Glorious is my Lord the most high, Glorious is my Lord the most high, Glorious is my Lord the most high")
                speech("Glorious is my Lord the most high, Glorious is my Lord the most high, Glorious is my Lord the most high")
                time.sleep(5)
                print()
                print("Oh Allah, forgive me, have mercy on me, strengthen me, raise me in status, pardon me and grant me provision")
                speech("Oh Allah, forgive me, have mercy on me, strengthen me, raise me in status, pardon me and grant me provision")
                time.sleep(8)
                print()
                print("Glorious is my Lord the most high, Glorious is my Lord the most high, Glorious is my Lord the most high")
                speech("Glorious is my Lord the most high, Glorious is my Lord the most high, Glorious is my Lord the most high")
                time.sleep(5)
                print()
                print("Allah Hu Akbar")
                speech("Allah Hu Akbar")
                time.sleep(5)
                print()
                print("Allah Hu Akbar")
                speech("Allah Hu Akbar")
                time.sleep(2)
                print("Allah Hu Akbar")
                speech("Allah Hu Akbar")
                time.sleep(2)
                print()
                print("Glorious is my Lord the most Great, Glorious is my Lord the most great, Glorious is my Lord the most great")
                speech("Glorious is my Lord the most Great, Glorious is my Lord the most great, Glorious is my Lord the most great")
                time.sleep(4)
                print()
                print("Allah hears those who praise him, our Lord all praise is for you, praise which is abundant, excellent, and blessed")
                speech("Allah hears those who praise him, our Lord all praise is for you, praise which is abundant, excellent, and blessed")
                time.sleep(6)
                print()
                print("Glorious is my Lord the most Great, Glorious is my Lord the most great, Glorious is my Lord the most great")
                speech("Glorious is my Lord the most Great, Glorious is my Lord the most great, Glorious is my Lord the most great")
                time.sleep(4)
                print()
                print("Allah Hu Akbar")
                speech("Allah Hu Akbar")
                time.sleep(2)
                print()
                print("Glorious is my Lord the most high, Glorious is my Lord the most high, Glorious is my Lord the most high")
                speech("Glorious is my Lord the most high, Glorious is my Lord the most high, Glorious is my Lord the most high")
                time.sleep(5)
                print()
                print("Oh Allah, forgive me, have mercy on me, strengthen me, raise me in status, pardon me and grant me provision")
                speech("Oh Allah, forgive me, have mercy on me, strengthen me, raise me in status, pardon me and grant me provision")
                time.sleep(8)
                print()
                print("Glorious is my Lord the most high, Glorious is my Lord the most high, Glorious is my Lord the most high")
                speech("Glorious is my Lord the most high, Glorious is my Lord the most high, Glorious is my Lord the most high")
                time.sleep(5)
                print()
                print("Allah Hu Akbar")
                speech("Allah Hu Akbar")
                time.sleep(2)
                print()
                print("All compliments, prayers, and pure words are due to Allah, Peace be upon you oh Prophet and the mercy of Allah and his blessings")
                speech("All compliments, prayers, and pure words are due to Allah, Peace be upon you oh Prophet and the mercy of Allah and his blessings")
                time.sleep(8)
                print()
                print("Peace be upon us and upon the righteous slaves of Allah, I bear witness that there is no God except Allah and I bear witness that Muhammad is his slave and messenger")
                speech("Peace be upon us and upon the righteous slaves of Allah, I bear witness that there is no God except Allah and I bear witness that Muhammad is his slave and messenger")
                time.sleep(8)
                print()
                print("Oh Allah, bless Muhammad and the family of Muhammad as you blessed Ibrahim and the family of Ibrahim.. You are indeed worthy of praise, full of glory")
                speech("Oh Allah, bless Muhammad and the family of Muhammad as you blessed Ibrahim and the family of Ibrahim.. You are indeed worthy of praise, full of glory")        
                time.sleep(9)
                print()
                print("Oh Allah, send prayers upon Muhammad and the family of Muhammad as you sent prayers upon Ibrahim and the family of Ibrahim.. you are indeed worthy of praise, full of glory")
                speech("Oh Allah, send prayers upon Muhammad and the family of Muhammad as you sent prayers upon Ibrahim and the family of Ibrahim.. you are indeed worthy of praise, full of glory")
                time.sleep(9)
                print()
                print("Allah Hu Akbar")
                speech("Allah Hu Akbar")
                time.sleep(5)
                print()
                print("Assalamu Alaikum Wa Rammatullahi Wa Barakatuhu")
                speech("Assalamu Alaikum Wa Rammatullahi Wa Barakatuhu")
                time.sleep(5)
                print()
                print("Assalamu Alaikum Wa Rammatullahi Wa Barakatuhu")
                speech("Assalamu Alaikum Wa Rammatullahi Wa Barakatuhu")
                time.sleep(5)
                print()
                print("Allah Hu Akbar")
                speech("Allah Hu Akbar")
                time.sleep(5)

            def main_loop():
                prayer()

            try:
                main_loop()
            except KeyboardInterrupt:
                print("\nStopped by user.")

        def muslim_prayer2():
            def prayer():
                time.sleep(3)
                print("Allah Hu Akbar")
                speech("Allah Hu Akbar")
                time.sleep(2)
                print("Allah Hu Akbar")
                speech("Allah Hu Akbar")
                time.sleep(2)
                print()
                print("Glorious is my Lord the most Great, Glorious is my Lord the most great, Glorious is my Lord the most great")
                speech("Glorious is my Lord the most Great, Glorious is my Lord the most great, Glorious is my Lord the most great")        
                time.sleep(4)
                print()
                print("Allah hears those who praise him, our Lord all praise is for you, praise which is abundant, excellent, and blessed")
                speech("Allah hears those who praise him, our Lord all praise is for you, praise which is abundant, excellent, and blessed")
                time.sleep(6)
                print()
                print("Glorious is my Lord the most Great, Glorious is my Lord the most great, Glorious is my Lord the most great")
                speech("Glorious is my Lord the most Great, Glorious is my Lord the most great, Glorious is my Lord the most great")
                time.sleep(4)
                print()
                print("Allah Hu Akbar")
                speech("Allah Hu Akbar")
                time.sleep(2)
                print()
                print("Glorious is my Lord the most high, Glorious is my Lord the most high, Glorious is my Lord the most high")
                speech("Glorious is my Lord the most high, Glorious is my Lord the most high, Glorious is my Lord the most high")
                time.sleep(5)
                print()
                print("Oh Allah, forgive me, have mercy on me, strengthen me, raise me in status, pardon me and grant me provision")
                speech("Oh Allah, forgive me, have mercy on me, strengthen me, raise me in status, pardon me and grant me provision")
                time.sleep(8)
                print()
                print("Glorious is my Lord the most high, Glorious is my Lord the most high, Glorious is my Lord the most high")
                speech("Glorious is my Lord the most high, Glorious is my Lord the most high, Glorious is my Lord the most high")
                time.sleep(5)
                print()
                print("Allah Hu Akbar")
                speech("Allah Hu Akbar")
                time.sleep(5)
                print()
                print("Allah Hu Akbar")
                speech("Allah Hu Akbar")
                time.sleep(2)
                print("Allah Hu Akbar")
                speech("Allah Hu Akbar")
                time.sleep(2)
                print()
                print("Glorious is my Lord the most Great, Glorious is my Lord the most great, Glorious is my Lord the most great")
                speech("Glorious is my Lord the most Great, Glorious is my Lord the most great, Glorious is my Lord the most great")
                time.sleep(4)
                print()
                print("Allah hears those who praise him, our Lord all praise is for you, praise which is abundant, excellent, and blessed")
                speech("Allah hears those who praise him, our Lord all praise is for you, praise which is abundant, excellent, and blessed")
                time.sleep(6)
                print()
                print("Glorious is my Lord the most Great, Glorious is my Lord the most great, Glorious is my Lord the most great")
                speech("Glorious is my Lord the most Great, Glorious is my Lord the most great, Glorious is my Lord the most great")
                time.sleep(4)
                print()
                print("Allah Hu Akbar")
                speech("Allah Hu Akbar")
                time.sleep(2)
                print()
                print("Glorious is my Lord the most high, Glorious is my Lord the most high, Glorious is my Lord the most high")
                speech("Glorious is my Lord the most high, Glorious is my Lord the most high, Glorious is my Lord the most high")
                time.sleep(5)
                print()
                print("Oh Allah, forgive me, have mercy on me, strengthen me, raise me in status, pardon me and grant me provision")
                speech("Oh Allah, forgive me, have mercy on me, strengthen me, raise me in status, pardon me and grant me provision")
                time.sleep(8)
                print()
                print("Glorious is my Lord the most high, Glorious is my Lord the most high, Glorious is my Lord the most high")
                speech("Glorious is my Lord the most high, Glorious is my Lord the most high, Glorious is my Lord the most high")
                time.sleep(5)
                print()
                print("Allah Hu Akbar")
                speech("Allah Hu Akbar")
                time.sleep(2)
                print()
                print("All compliments, prayers, and pure words are due to Allah, Peace be upon you oh Prophet and the mercy of Allah and his blessings")
                speech("All compliments, prayers, and pure words are due to Allah, Peace be upon you oh Prophet and the mercy of Allah and his blessings")
                time.sleep(8)
                print()
                print("Peace be upon us and upon the righteous slaves of Allah, I bear witness that there is no God except Allah and I bear witness that Muhammad is his slave and messenger")
                speech("Peace be upon us and upon the righteous slaves of Allah, I bear witness that there is no God except Allah and I bear witness that Muhammad is his slave and messenger")
                time.sleep(8)
                print()
                print("Oh Allah, bless Muhammad and the family of Muhammad as you blessed Ibrahim and the family of Ibrahim.. You are indeed worthy of praise, full of glory")
                speech("Oh Allah, bless Muhammad and the family of Muhammad as you blessed Ibrahim and the family of Ibrahim.. You are indeed worthy of praise, full of glory")
                time.sleep(9)
                print()
                print("Oh Allah, send prayers upon Muhammad and the family of Muhammad as you sent prayers upon Ibrahim and the family of Ibrahim.. you are indeed worthy of praise, full of glory")
                speech("Oh Allah, send prayers upon Muhammad and the family of Muhammad as you sent prayers upon Ibrahim and the family of Ibrahim.. you are indeed worthy of praise, full of glory")
                time.sleep(9)
                print()
                print("Allah Hu Akbar")
                speech("Allah Hu Akbar")
                time.sleep(2)
                print()
                print("Allah Hu Akbar")
                speech("Allah Hu Akbar")
                time.sleep(2)
                print("Allah Hu Akbar")
                speech("Allah Hu Akbar")
                time.sleep(2)
                print()
                print("Glorious is my Lord the most Great, Glorious is my Lord the most great, Glorious is my Lord the most great")
                speech("Glorious is my Lord the most Great, Glorious is my Lord the most great, Glorious is my Lord the most great")
                time.sleep(4)
                print()
                print("Allah hears those who praise him, our Lord all praise is for you, praise which is abundant, excellent, and blessed")
                speech("Allah hears those who praise him, our Lord all praise is for you, praise which is abundant, excellent, and blessed")
                time.sleep(6)
                print()
                print("Glorious is my Lord the most Great, Glorious is my Lord the most great, Glorious is my Lord the most great")
                speech("Glorious is my Lord the most Great, Glorious is my Lord the most great, Glorious is my Lord the most great")
                time.sleep(4)
                print()
                print("Allah Hu Akbar")
                speech("Allah Hu Akbar")
                time.sleep(2)
                print()
                print("Glorious is my Lord the most high, Glorious is my Lord the most high, Glorious is my Lord the most high")
                speech("Glorious is my Lord the most high, Glorious is my Lord the most high, Glorious is my Lord the most high")
                time.sleep(5)
                print()
                print("Oh Allah, forgive me, have mercy on me, strengthen me, raise me in status, pardon me and grant me provision")
                speech("Oh Allah, forgive me, have mercy on me, strengthen me, raise me in status, pardon me and grant me provision")
                time.sleep(8)
                print()
                print("Glorious is my Lord the most high, Glorious is my Lord the most high, Glorious is my Lord the most high")
                speech("Glorious is my Lord the most high, Glorious is my Lord the most high, Glorious is my Lord the most high")
                time.sleep(5)
                print()
                print("Allah Hu Akbar")
                speech("Allah Hu Akbar")
                time.sleep(5)
                print()
                print("Allah Hu Akbar")
                speech("Allah Hu Akbar")
                time.sleep(2)
                print("Allah Hu Akbar")
                speech("Allah Hu Akbar")
                time.sleep(2)
                print()
                print("Glorious is my Lord the most Great, Glorious is my Lord the most great, Glorious is my Lord the most great")
                speech("Glorious is my Lord the most Great, Glorious is my Lord the most great, Glorious is my Lord the most great")
                time.sleep(4)
                print()
                print("Allah hears those who praise him, our Lord all praise is for you, praise which is abundant, excellent, and blessed")
                speech("Allah hears those who praise him, our Lord all praise is for you, praise which is abundant, excellent, and blessed")
                time.sleep(6)
                print()
                print("Glorious is my Lord the most Great, Glorious is my Lord the most great, Glorious is my Lord the most great")
                speech("Glorious is my Lord the most Great, Glorious is my Lord the most great, Glorious is my Lord the most great")
                time.sleep(4)
                print()
                print("Allah Hu Akbar")
                speech("Allah Hu Akbar")
                time.sleep(2)
                print()
                print("Glorious is my Lord the most high, Glorious is my Lord the most high, Glorious is my Lord the most high")
                speech("Glorious is my Lord the most high, Glorious is my Lord the most high, Glorious is my Lord the most high")
                time.sleep(5)
                print()
                print("Oh Allah, forgive me, have mercy on me, strengthen me, raise me in status, pardon me and grant me provision")
                speech("Oh Allah, forgive me, have mercy on me, strengthen me, raise me in status, pardon me and grant me provision")
                time.sleep(8)
                print()
                print("Glorious is my Lord the most high, Glorious is my Lord the most high, Glorious is my Lord the most high")
                speech("Glorious is my Lord the most high, Glorious is my Lord the most high, Glorious is my Lord the most high")
                time.sleep(5)
                print()
                print("Allah Hu Akbar")
                speech("Allah Hu Akbar")
                time.sleep(5)
                print()
                print("Assalamu Alaikum Wa Rammatullahi Wa Barakatuhu")
                speech("Assalamu Alaikum Wa Rammatullahi Wa Barakatuhu")
                time.sleep(5)
                print()
                print("Assalamu Alaikum Wa Rammatullahi Wa Barakatuhu")
                speech("Assalamu Alaikum Wa Rammatullahi Wa Barakatuhu")
                time.sleep(5)
                print()
                print("Allah Hu Akbar")
                speech("Allah Hu Akbar")
                time.sleep(5)

            def main_loop():
                prayer()

            try:
                main_loop()
            except KeyboardInterrupt:
                print("\nStopped by user.")

        def muslim_prayer3():
            def prayer():
                time.sleep(3)
                print("Allah Hu Akbar")
                speech("Allah Hu Akbar")
                time.sleep(2)
                print("Allah Hu Akbar")
                speech("Allah Hu Akbar")
                time.sleep(2)
                print()
                print("Glorious is my Lord the most Great, Glorious is my Lord the most great, Glorious is my Lord the most great")
                speech("Glorious is my Lord the most Great, Glorious is my Lord the most great, Glorious is my Lord the most great")        
                time.sleep(4)
                print()
                print("Allah hears those who praise him, our Lord all praise is for you, praise which is abundant, excellent, and blessed")
                speech("Allah hears those who praise him, our Lord all praise is for you, praise which is abundant, excellent, and blessed")
                time.sleep(6)
                print()
                print("Glorious is my Lord the most Great, Glorious is my Lord the most great, Glorious is my Lord the most great")
                speech("Glorious is my Lord the most Great, Glorious is my Lord the most great, Glorious is my Lord the most great")
                time.sleep(4)
                print()
                print("Allah Hu Akbar")
                speech("Allah Hu Akbar")
                time.sleep(2)
                print()
                print("Glorious is my Lord the most high, Glorious is my Lord the most high, Glorious is my Lord the most high")
                speech("Glorious is my Lord the most high, Glorious is my Lord the most high, Glorious is my Lord the most high")
                time.sleep(5)
                print()
                print("Oh Allah, forgive me, have mercy on me, strengthen me, raise me in status, pardon me and grant me provision")
                speech("Oh Allah, forgive me, have mercy on me, strengthen me, raise me in status, pardon me and grant me provision")
                time.sleep(8)
                print()
                print("Glorious is my Lord the most high, Glorious is my Lord the most high, Glorious is my Lord the most high")
                speech("Glorious is my Lord the most high, Glorious is my Lord the most high, Glorious is my Lord the most high")
                time.sleep(5)
                print()
                print("Allah Hu Akbar")
                speech("Allah Hu Akbar")
                time.sleep(5)
                print()
                print("Allah Hu Akbar")
                speech("Allah Hu Akbar")
                time.sleep(2)
                print("Allah Hu Akbar")
                speech("Allah Hu Akbar")
                time.sleep(2)
                print()
                print("Glorious is my Lord the most Great, Glorious is my Lord the most great, Glorious is my Lord the most great")
                speech("Glorious is my Lord the most Great, Glorious is my Lord the most great, Glorious is my Lord the most great")
                time.sleep(4)
                print()
                print("Allah hears those who praise him, our Lord all praise is for you, praise which is abundant, excellent, and blessed")
                speech("Allah hears those who praise him, our Lord all praise is for you, praise which is abundant, excellent, and blessed")
                time.sleep(6)
                print()
                print("Glorious is my Lord the most Great, Glorious is my Lord the most great, Glorious is my Lord the most great")
                speech("Glorious is my Lord the most Great, Glorious is my Lord the most great, Glorious is my Lord the most great")
                time.sleep(4)
                print()
                print("Allah Hu Akbar")
                speech("Allah Hu Akbar")
                time.sleep(2)
                print()
                print("Glorious is my Lord the most high, Glorious is my Lord the most high, Glorious is my Lord the most high")
                speech("Glorious is my Lord the most high, Glorious is my Lord the most high, Glorious is my Lord the most high")
                time.sleep(5)
                print()
                print("Oh Allah, forgive me, have mercy on me, strengthen me, raise me in status, pardon me and grant me provision")
                speech("Oh Allah, forgive me, have mercy on me, strengthen me, raise me in status, pardon me and grant me provision")
                time.sleep(8)
                print()
                print("Glorious is my Lord the most high, Glorious is my Lord the most high, Glorious is my Lord the most high")
                speech("Glorious is my Lord the most high, Glorious is my Lord the most high, Glorious is my Lord the most high")
                time.sleep(5)
                print()
                print("Allah Hu Akbar")
                speech("Allah Hu Akbar")
                time.sleep(2)
                print()
                print("All compliments, prayers, and pure words are due to Allah, Peace be upon you oh Prophet and the mercy of Allah and his blessings")
                speech("All compliments, prayers, and pure words are due to Allah, Peace be upon you oh Prophet and the mercy of Allah and his blessings")
                time.sleep(8)
                print()
                print("Peace be upon us and upon the righteous slaves of Allah, I bear witness that there is no God except Allah and I bear witness that Muhammad is his slave and messenger")
                speech("Peace be upon us and upon the righteous slaves of Allah, I bear witness that there is no God except Allah and I bear witness that Muhammad is his slave and messenger")
                time.sleep(8)
                print()
                print("Oh Allah, bless Muhammad and the family of Muhammad as you blessed Ibrahim and the family of Ibrahim.. You are indeed worthy of praise, full of glory")
                speech("Oh Allah, bless Muhammad and the family of Muhammad as you blessed Ibrahim and the family of Ibrahim.. You are indeed worthy of praise, full of glory")
                time.sleep(9)
                print()
                print("Oh Allah, send prayers upon Muhammad and the family of Muhammad as you sent prayers upon Ibrahim and the family of Ibrahim.. you are indeed worthy of praise, full of glory")
                speech("Oh Allah, send prayers upon Muhammad and the family of Muhammad as you sent prayers upon Ibrahim and the family of Ibrahim.. you are indeed worthy of praise, full of glory")
                time.sleep(9)
                print()
                print("Allah Hu Akbar")
                speech("Allah Hu Akbar")
                time.sleep(2)
                print()
                print("Allah Hu Akbar")
                speech("Allah Hu Akbar")
                time.sleep(2)
                print("Allah Hu Akbar")
                speech("Allah Hu Akbar")
                time.sleep(2)
                print()
                print("Glorious is my Lord the most Great, Glorious is my Lord the most great, Glorious is my Lord the most great")
                speech("Glorious is my Lord the most Great, Glorious is my Lord the most great, Glorious is my Lord the most great")
                time.sleep(4)
                print()
                print("Allah hears those who praise him, our Lord all praise is for you, praise which is abundant, excellent, and blessed")
                speech("Allah hears those who praise him, our Lord all praise is for you, praise which is abundant, excellent, and blessed")
                time.sleep(6)
                print()
                print("Glorious is my Lord the most Great, Glorious is my Lord the most great, Glorious is my Lord the most great")
                speech("Glorious is my Lord the most Great, Glorious is my Lord the most great, Glorious is my Lord the most great")
                time.sleep(4)
                print()
                print("Allah Hu Akbar")
                speech("Allah Hu Akbar")
                time.sleep(2)
                print()
                print("Glorious is my Lord the most high, Glorious is my Lord the most high, Glorious is my Lord the most high")
                speech("Glorious is my Lord the most high, Glorious is my Lord the most high, Glorious is my Lord the most high")
                time.sleep(5)
                print()
                print("Oh Allah, forgive me, have mercy on me, strengthen me, raise me in status, pardon me and grant me provision")
                speech("Oh Allah, forgive me, have mercy on me, strengthen me, raise me in status, pardon me and grant me provision")
                time.sleep(8)
                print()
                print("Glorious is my Lord the most high, Glorious is my Lord the most high, Glorious is my Lord the most high")
                speech("Glorious is my Lord the most high, Glorious is my Lord the most high, Glorious is my Lord the most high")
                time.sleep(5)
                print()
                print("Allah Hu Akbar")
                speech("Allah Hu Akbar")
                time.sleep(5)
                print()
                print("Assalamu Alaikum Wa Rammatullahi Wa Barakatuhu")
                speech("Assalamu Alaikum Wa Rammatullahi Wa Barakatuhu")
                time.sleep(5)
                print()
                print("Assalamu Alaikum Wa Rammatullahi Wa Barakatuhu")
                speech("Assalamu Alaikum Wa Rammatullahi Wa Barakatuhu")
                time.sleep(5)
                print()
                print("Allah Hu Akbar")
                speech("Allah Hu Akbar")
                time.sleep(5)

            def main_loop():
                prayer()

            try:
                main_loop()
            except KeyboardInterrupt:
                print("\nStopped by user.")

        def meditate():
            while True:
                try:
                    number = int(input("Enter meditation time in seconds: "))
                except ValueError:
                    print("Invalid value")
                else:
                    break
            number
            ct = datetime.datetime.now()
            print()
            print("You sit and start to meditate...", ct)
            time.sleep(number)
            ct2 = datetime.datetime.now()
            print("You finished meditating", ct2)
            time.sleep(3)

        def sleep():
            ct = datetime.datetime.now()
            print("You lay down and doze off...", ct)
            time.sleep(29)
            print("You wake up", ct)
            time.sleep(3)

        def eat():
            ct = datetime.datetime.now()
            print("You prepare food and start to consume a meal...")
            time.sleep(5)
            print("You have eaten", ct)
            time.sleep(3)

        def find_coins():
            ct = datetime.datetime.now()
            print("You start to search around for coins...")
            time.sleep(10)
            print("You found:")
            tin = (random.randint(0,100))
            coins = "coins: "
            print(coins, tin, ct)
            time.sleep(3)

        def slot():
            ct = datetime.datetime.now()
            print("You pull on the slot lever...")
            time.sleep(5)
            slot = random.choices(range(10), k=3)
            slots = "slot: "
            print(slots, slot, ct)
            time.sleep(3)

        def draw_card():
            dd = list(deck1)
            while True:
                try:
                    number = int(input("Enter number of cards: "))
                except ValueError:
                    print("Invalid value")
                else:
                    break
            number
            ct = datetime.datetime.now()
            print()
            print("You draw a card from a deck...")
            time.sleep(2)
            card = random.sample(dd, number)
            print("You drew:")
            cards = "card: "
            print(cards, card, ct)
            time.sleep(3)

        def search_for_items():
            print("You search around...")
            time.sleep(2)
            itemd = ["empty bottle", "bottle of wine", "wine glass", "bottle of iced tea", "energy drink", "lemon juice", "pack of green peas", "shirt", "bed", "headphones", "earphones", "blanket", "tablet", "kindle", "pills", "pack of coffee beans", "cup of coffee", "junkfood", "medicine", "spoon", "fork", "Nintendo Switch", "laptop", "mobile phone", "electric fan", "chair", "guitar", "keyboard", "piano", "tv", "monitor", "oil", "hashish", "marijuana", "cigarette", "vape", "pillow", "dog food", "bike", "car", "scooter", "skateboard", "printer", "shards of glass", "garbage", "strips of sleather", "food", "bottle of water", "bible", "Dhammapada", "yoga mat", "helmet", "chewing gum", "vitamins", "shirt", "sweater", "pants", "working pants", "skirt", "underwear", "parachute", "gun", "knife", "sword", "katana", "oatmeal", "chain", "slippers", "shoes", "book", "wires", "credit card", "stove", "oven", "hat", "bucket hat", "baseball cap", "beanie", "hoodie", "necklace", "ring", "gold ring", "diamond ring", "diamond", "diamonds", "painting", "pencil", "ballpoint pen", "sketchpad", "crayon", "box of crayons", "paint", "spray paint", "fruit", "lettuce", "carrot", "watermelon", "orange", "apple", "banana", "pear", "gold", "gold bar", "pistol", "lantern", "lamp", "umbrella", "newspaper", "Sega", "ecstasy", "Nintendo 64", "calculator", "brownies", "pie", "loaf bread", "aviator shades", "shutter shades", "CD", "floppy disk", "mp3 player", "walkman", "cassette", "ticket", "food stub", "ski mask", "spear", "nunchucks", "frying pan", "beans", "charger", "guitar pick", "mic", "digicam", "GoPro", "night vision goggles", "sniper rifle", "DS4 Playstation controller", "CDJ", "Raybans", "smartwatch", "modem", "axe", "backpack", "tent", "sleeping bag", "compass", "flashlight", "batteries", "rope", "duct tape", "multi-tool", "first aid kit", "whistle", "matches", "lighter", "candle", "map", "binoculars", "walkie-talkie", "solar charger", "power bank", "usb cable", "memory card", "external hard drive", "webcam", "microphone", "speaker", "drone", "VR headset", "tablet stand", "mouse", "mechanical keyboard", "gaming chair", "racing wheel", "action figure", "board game", "playing cards", "chess set", "dice set", "rubik's cube", "puzzle", "coloring book", "markers", "pastels", "clay", "canvas", "easel", "brush set", "palette knife", "glue gun", "sewing kit", "yarn", "knitting needles", "embroidery hoop", "toolbox", "hammer", "screwdriver set", "wrench", "pliers", "measuring tape", "level", "utility knife", "safety goggles", "work gloves", "dust mask", "ear plugs", "padlock", "safe", "fire extinguisher", "smoke detector", "thermostat", "humidifier", "air purifier", "fan heater", "space heater", "electric blanket", "heating pad", "ice pack", "cooler", "thermos", "water filter", "camping stove", "propane tank", "mess kit", "canteen", "hammock", "camping chair", "cooler bag", "fishing rod", "fishing tackle", "hunting knife", "survival kit", "flare gun", "first aid manual", "wilderness guide", "plant identification guide", "star chart", "telescope", "microscope set"]
            items = (random.choice(itemd), random.choice(itemd))
            item = random.sample(items, 2)
            ct = datetime.datetime.now()
            print("You found:")
            items = "items: "
            print(items, item, ct)
            time.sleep(3)

        def fly():
            print("You go to the airport and board a plane...")
            time.sleep(2)
            print("You arrived in:")
            countries = ["Canada", "Sweden", "China", "Beijing", "New York", "California", "L.A.", "San Francisco", "Detroit", "Colorado", "Newark", "New Jersey", "Australia", "Gold Coast", "Thailand", "North Korea", "Pyongyang", "Seoul", "Tokyo", "Osaka", "Japan", "Fujian", "Kyoto", "Manila", "Palawan", "Siargao", "Sultan Kudarat", "Davao", "Sydney", "Poland", "Uzbekistan", "Kyrgystan", "Turkey", "Iraq", "Iran", "Bolivia", "Iceland", "Lithuania", "Greenland", "UK", "France", "Spain", "Rome", "Greece", "Amsterdam", "Netherlands", "Boracay", "Indonesia", "Russia", "Ukraine", "Africa", "Antarctica", "Alaska", "South Carolina", "North Carolina", "Philadelphia", "Brooklyn", "Mexico", "Brazil", "Taiwan", "Burma", "Cambodia", "Vietnam", "India", "Bangladesh", "New Delhi", "Bombay", "Philippines"]
            country = random.sample(countries, 1)
            ct = datetime.datetime.now()
            fly = "fly: "
            print(fly, country, ct)
            time.sleep(3)

        def drink_coffee():
            print("You have coffee and feel the effect of caffeine...")
            time.sleep(7)
            ct = datetime.datetime.now()
            print("You finished drinking your coffee", ct)
            time.sleep(3)

        def drink_tea():
            print("You have tea...")
            time.sleep(7)
            ct = datetime.datetime.now()
            print("You finish your tea", ct)
            time.sleep(3)

        def surf():
            print("You enter the water and wait for a wave...")
            time.sleep(random.randint(1,8))
            print("You surfed:")
            time.sleep(3)
            modnar = (round(random.random()*60,2))
            ct = datetime.datetime.now()
            surf = "surfed: "
            print(surf, modnar, ct)
            print("..meters before you wiped-out")
            time.sleep(3)

        def collections():
            print("You recall")
            time.sleep(3)
            semit = (round(random.random()*666))
            collections = "collections: "
            print(semit)
            print("items out of 666 with")
            time.sleep(1)
            sitch  = (round(random.random()*100,3))
            print(sitch)
            ct = datetime.datetime.now()
            print("in your Satchel")

        def doodling():
            print("You pick up a calculator...")
            time.sleep(5)
            print()
            print("You draw:")
            time.sleep(1)
            print()
            print()
            mondar = (round(random.random()*999,8))
            ct = datetime.datetime.now()
            doodling = "doodling: "
            print(doodling, mondar, ct)
            print()

        def zen_melody():
            keys = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
            key = random.sample(keys, 1)
            raondam = (round(random.random()*9999,9))
            ct = datetime.datetime.now()
            zenmelody = "zen melody: "
            print(zenmelody, key, raondam, ct)

        def value():
            letters1 = ["A", "a", "B", "b", "C", "c", "D", "d", "E", "e", "F", "f", "G", "g", "H", "h", "I", "i", "J", "j", "K", "k", "L", "l", "M", "m", "N", "n", "O", "o", "P", "p", "Q", "q", "R", "r", "S", "s", "T", "t", "U", "u", "V", "v", "W", "w", "X", "x", "Y", "y", "Z", "z"]
            letters2 = ["A", "a", "B", "b", "C", "c", "D", "d", "E", "e", "F", "f", "G", "g", "H", "h", "I", "i", "J", "j", "K", "k", "L", "l", "M", "m", "N", "n", "O", "o", "P", "p", "Q", "q", "R", "r", "S", "s", "T", "t", "U", "u", "V", "v", "W", "w", "X", "x", "Y", "y", "Z", "z"]
            letters3 = ["A", "a", "B", "b", "C", "c", "D", "d", "E", "e", "F", "f", "G", "g", "H", "h", "I", "i", "J", "j", "K", "k", "L", "l", "M", "m", "N", "n", "O", "o", "P", "p", "Q", "q", "R", "r", "S", "s", "T", "t", "U", "u", "V", "v", "W", "w", "X", "x", "Y", "y", "Z", "z"]
            letters4 = ["A", "a", "B", "b", "C", "c", "D", "d", "E", "e", "F", "f", "G", "g", "H", "h", "I", "i", "J", "j", "K", "k", "L", "l", "M", "m", "N", "n", "O", "o", "P", "p", "Q", "q", "R", "r", "S", "s", "T", "t", "U", "u", "V", "v", "W", "w", "X", "x", "Y", "y", "Z", "z"]
            letters5 = ["A", "a", "B", "b", "C", "c", "D", "d", "E", "e", "F", "f", "G", "g", "H", "h", "I", "i", "J", "j", "K", "k", "L", "l", "M", "m", "N", "n", "O", "o", "P", "p", "Q", "q", "R", "r", "S", "s", "T", "t", "U", "u", "V", "v", "W", "w", "X", "x", "Y", "y", "Z", "z"]
            letter1 = random.sample(letters1, 1)
            letter2 = random.sample(letters2, 1)
            letter3 = random.sample(letters3, 1)
            letter4 = random.sample(letters4, 1)
            letter5 = random.sample(letters5, 1)
            value = (round(random.random()*9999999999,10))
            ct = datetime.datetime.now()
            values = "value:"
            print(values, letter1, letter2, letter3, letter4, letter5, value, ct)

        def bump():
            ct = datetime.datetime.now()
            time.sleep(1.5)
            print("You can do it!", ct)
            time.sleep(3)

        def ma():
            time.sleep(2)
            mstyles = ["Africa and African America", "Aikido", "Animal and Imitative Systems in Chinese Martial Arts", "Archery, Japanese", "Baguazhang (Pa Kua Ch' uan)", "Boxing, Chinese", "Boxing, Chinese Shaolin Styles", "Boxing, European", "Brazilian Jiu Jitsu", "Budo, Bujutsu, and Bugei", "Capoeira", "China", "Chivalry", "Combatives: Military and Police Martial Art Training", "Dueling", "Europe", "External vs. Internal Chinese Martial Arts", "Folklore in the Martial Arts", "Form/Xing/Kata/Pattern Practice", "Gladiators", "Gunfighters","Hapkido", "Heralds", "Iaido", "India", "Japan", "Japanese Martial Arts, Chinese Influences on", "Jeet Kune Do", "Judo", "Kajukenbo", "Kalarippayattu", "Karate, Japanese", "Karate, Okinawan", "Kendo", "Kenpo", "Ki/Qi", "Knights", "Kobudo, Okinawan", "Korea", "Korean Martial Arts, Chinese Influences On", "Koryu Bugei, Japanese", "Krav Maga", "Kung Fu/Gungfu/Gongfu", "Masters of Defense", "Medicine, Traditional Chinese", "Meditation", "Middle East", "Mongolia", "Muay Thai", "Ninjutsu", "Okinawa", "Orders of Knighthood, Secular", "Pacific Islands", "Pankration", "Performing Arts", "Philippines", "Political Conflict and the Martial Arts", "Rank", "Religion and Spiritual Development: Ancient Mediterranean and Medieval West", "Religion and Spiritual Development: China", "Religion and Spiritual Development: India", "Religion and Spiritual Development: Japan", "Sambo", "Samurai", "Savate", "Silat", "Social Uses of the Martial Arts", "Southeast Asia", "Stage Combat", "Stickfighting, Non-Asian", "Sword, Japanese", "Swordsmanship, European Medieval", "Swordsmanship, European Renaissance", "Swordsmanship, Japanese", "Swordsmanship, Korean/Hankuk Haedong Kumdo", "T'aek'kyon", "Taekwondo", "Taijiquan (Tai Chi Ch'uan)", "Thaing", "Thang-Ta", "Training Area", "Varma Ati", "Vovinam/Viet Vo Dao", "Warrior Monks, Japanese/Sohei", "Women in the Martial Arts", "Women in the Martial Arts: Britain and North America", "Women in the Martial Arts: China", "Women in the Martial Arts: Japan", "Wrestling and Grappling: China", "Wrestling and Grappling: Europe", "Wrestling and Grappling: India", "Wrestling and Grappling: Japan", "Wrestling, Professional", "Written Texts: China", "Written Texts: India", "Written Texts: Japan", "Xingyiquan (Hsing I Ch'uan)", "Yongchun/Wing Chun"]
            mart = random.sample(mstyles, random.randint(1, 6))
            ct = datetime.datetime.now()
            MA = "MA: "
            print(MA, mart, ct)
            print()
            print("-from the contents of Martial Arts of the World: An Encyclopedia")
            time.sleep(6)

        def skate():
            time.sleep(5)
            print("You ride your trickboard and did a")
            tricks = ["Backside 180", "Backside 360", "Backside Caballerial", "Backside Half Cab", "Fakie Ollie", "Frontside 180", "Frontside 360", "Frontside Caballerial", "Frontside Half Cab", "Kickturn", "Nollie", "Nollie Backside 180", "Nollie Backside 360", "Nollie Frontside 180", "Nollie Frontside 360", "Ollie", "Ollie North", "Ollie South", "Switch Backside 180", "Switch Backside 360", "Switch Frontside 180", "Switch Frontside 360", "Switch Ollie", "Tic-Tac", "360 Flip", "360 Hardflip", "360 Ollie Heelflip", "360 Ollie Kickflip", "360 Pop Shove-it", "360 Shuvit", "540 Flip", "720 Flip", "Alpha Flip", "Anti Casper Flip", "Backside Bigspin", "Backside Flip", "Backside Half Cab Heelflip", "Backside Half Cab Kickflip", "Backside Heelflip", "Backside Kickflip", "Big Heelflip", "Bigflip", "Biggerflip", "Biggerspin", "Bigspin", "Bubble Flip", "Bullflip", "Caballerial Flip", "Camel Flip", "Casper Flip", "Daydream Flip", "De Comply", "Disco Flip", "Double Heelflip", "Double Kickflip", "Dragon Flip", "Fakie 360 Flip", "Fakie 360 Hardflip", "Fakie Backside Bigspin", "Fakie Backside Pop Shove-it", "Fakie Frontside Bigspin", "Fakie Frontside Pop Shove-it", "Fakie Hardflip", "Fakie Heelflip", "Fakie Inward Heelflip", "Fakie Kickflip", "Fakie Varial Heelflip", "Fakie Varial Kickflip", "Feather Flip", "Fingerflip", "Forward Flip", "Front Foot Impossible", "Frontside 360 Pop Shove it", "Frontside Bigspin", "Frontside Flip", "Frontside Half Cab Heelflip", "Frontside Half Cab Kickflip", "Frontside Heelflip", "Frontside Kickflip", "Frontside Pop Shove-it", "Gazelle Flip", "Gazelle Spin", "Ghetto Bird", "Gingersnap", "Grape Flip", "Half Cab", "Handstand Flip", "Hardflip", "Haslam Flip", "Heelflip", "Hospital Flip", "Illusion Flip", "Impossible", "Inward Heelflip", "Jesus Flip", "Kickback Flip", "Kickflip", "Kiwi Flip", "Laser Flip", "Late Kickflip", "Nerd Flip", "Nightmare Flip", "No Comply", "540", "720", "900", "Airwalk", "Benihana", "Cannonball", "Christ Air", "Crossbone", "Delmar Indy", "Indy", "Indy Grab", "Invert", "Japan Air", "Judo Air", "Madonna", "McTwist", "Melancholy Grab", "Melon", "Method Air", "Mute Air", "Nose Grab", "Rocket Air", "Sal Flip", "Seatbelt Grab", "Stiffy", "Superman Grab", "Varial", "Egg Plant", "Manual", "Nose Manual", "Varial Heelflip", "Varial Kickflip",\
                         "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", "bail", ]
            trick = random.sample(tricks, 1)
            ct = datetime.datetime.now()
            skate = "skate: "
            print(skate, trick, ct)
            time.sleep(3)

        def art():
            time.sleep(4)
            print("You make a piece in the style of")
            styles = ["Abstract Art", "Abstract Expressionism", "Academicism", "Analytical Cubism", "Art Deco", "Art Nouveau", "Ashcan School", "Banksy", "Baroque", "Byzantine Art", "Classicism", "Cloisonnism", "Color Field", "Conceptual Art", "Constructivism", "Cubism", "Cubo-Futurism", "Dadaism", "Dutch Golden Age", "Early Netherlandish", "Early Renaissance", "Expressionism", "Fauvism", "Futurism", "Geometric Abstract Art", "Gothic Art", "High Renaissance", "Hudson River School", "Impressionism", "Italian Renaissance", "Kitsch", "Luminism", "Mannerism", "Metaphysical Art", "Minimalism", "Modernism", "Naive Art/ Primitivism", "Neo-Baroque", "Neo-Classicism", "Neo-Dada", "Neo Expressionism", "Neoplasticism", "New Realism", "Northern Renaissance", "Op-Art", "Orientalism", "Orphism", "Pointilism", "Pop Art", "Pop Surrealism", "Post-Impressionism", "Pre-Raphaelites", "Precisionism", "Proto Renaissance", "Purism", "Realism", "Regionalism", "Renaissance", "Rococo", "Romanticism", "Social Realism", "Socialist Realism", "Suprematism", "Surrealism", "Symbolism", "Synthetic Cubism", "Synthetism", "Tenebrism", "Tonalism", "Tubism", "Ukiyo-E", "Verism"]
            art = random.sample(styles, 1)
            ct = datetime.datetime.now()
            arts = "art: "
            print(arts, art, ct)
            time.sleep(3)

        def radio():
            time.sleep(2)
            print("You tune in to the radio and listen to:")
            time.sleep(1)
            genres = ["Alternative", "Anime", "Blues", "Classical", "Comedy", "Commercials", "Country", "Dance", "Easy Listening", "Electronic", "Enka", "French Pop", "Folk Music", "German Folk", "German Pop", "Fitness and Workout", "Hip-Hop/Rap", "Holiday Music", "Indie Pop", "Industrial", "Inspirational", "Instrumental", "Jazz", "K-Pop", "Karaoke", "Latin", "Metal", "New Age", "Opera", "Pop", "R&B/Soul", "Reggae", "Rock", "Soundtracks", "Spoken Word", "Tex-Mex/Tejano", "Vocal", "World"]
            music = random.sample(genres, 1)
            ct = datetime.datetime.now()
            radio = "radio: "
            print(radio, music, ct)
            time.sleep(3)

        def give_alms():
            ct = datetime.datetime.now()
            time.sleep(3)
            print("You gave alms to the needy", ct)
            time.sleep(3)

        def brawl():
            time.sleep(1)
            actions = ["You met", "You fought with", "You fought with", "You defeated", "You defeated","You defeated", "You were sent to the hospital by", "You were defeated by", "You healed", "You were healed by", "You jailed", "You pranked", "You were pranked by", "You were jailed by", "you were beat by", "you were K.Ode by"]
            action = random.sample(actions, 1)
            people = ["a stranger", "a child", "an emo", "a doctor", "a soldier", "a police", "a homeless person", "a mom", "a gamer", "a dancer", "an artist", "a peasant", "a prince", "a princess", "a King", "a Queen", "a lawyer", "a vendor", "an alien", "a Mexican", "a nurse", "a lizard", "a woman", "a girl", "a boy", "an optometrist", "a physician", "a psychologist", "a psychiatrist", "a teacher", "White Tara", "Green Tara", "a ninja", "a gangster"]
            person = random.sample(people, 1)
            ct = datetime.datetime.now()
            brawl = "brawl: "
            brawls = brawl, action, person
            print(brawls, ct)
            time.sleep(3)
            print()
            print("With A Score Of:")
            time.sleep(2)
            randit = (random.randint(50,100))
            ct = datetime.datetime.now()
            print(randit)
            time.sleep(3)

        def karate():
            time.sleep(1)
            print("Movement:")
            time.sleep(3)
            print()
            radnti = (random.randint(0,999))
            opponents = ["You", "Sensei", "Opponent", "Opponent"]
            opponent = random.sample(opponents, 1)
            ct = datetime.datetime.now()
            karate = "karate: "
            print(karate, radnti, opponent, ct)
            time.sleep(3)

        def koans():
            time.sleep(2)
            print()
            koans = ['One day, the World-Honored One ascended to the rostrum. Manjusri struck the table with the gavel and said, “Contemplate clearly the Dharma of the Dharma-King! The Dharma of the Dharma-King is like this.” Thereupon, the World-Honored One descended from the rostrum.', 'Emperor Bu of Ryo asked Great Master Bodhidharma, “What is the highest meaning of the holy reality?” Bodhidharma replied, “Vast and void, no holiness.” The emperor said, “Who are you in front of me?” Bodhidharma said, “I don’t know.” The emperor did not match him. Finally, Bodhidharma crossed the Yangtse River and came to the Shorin Temple. There he sat for nine years, facing the wall.', 'A king of Eastern India invited the twenty-seventh patriarch, Prajna Tara, for a meal. The king asked, “Why don’t you recite sutras?” The patriarch said, “The poor way [1] does not stay in the world of subject when breathing in, and has nothing to do with the world of objects when breathing out. I am always reciting the suchness-sutra in millions and millions of volumes.” [1]: i.e., “I.”', 'When the World-Honored One was walking with his assembly, he pointed to the ground with his hand and said, “This place is good for building a temple.” Indra [1] took a stalk of grass and stuck it in the ground and said, “The temple has been built.” The World-Honored One smiled. [1]: Exactly: Sakra Devendra. The lord god of the Trayastrimasa Heaven.', 'A monk asked Seigen, “What is the essence of Buddhism?” Seigen said, “What is the price of rice in Roryo?”', 'A monk asked Great Master Ba, “Apart from the Four Phrases, beyond one hundred Negations, please tell me directly, Master, the meaning of Bodhidharma’s coming from the West.” Master Ba said, “I am tired today, I can’t explain it to you. Go and ask Chizo.” The monk asked Chizo about it. Chizo said, “Why don’t you ask our master?” The monk said, “He told me to ask you.” Chizo said, “I have a headache today, I can’t explain it to you. Go and ask Brother Kai.” The monk asked Brother Kai about it. Kai said, “I don’t understand nothing about that question.” The monk told Great Master Ba about it. Great Master said, “Chizo’s head is white, Kai’s head is black.”', 'Yakusan had not ascended the rostrum for a long time. The temple steward said, “All the assembly has been wishing for instruction for a long time. Please, Master, give your assembly a sermon.” Yakusan had the bell rung. The assembly gathered. Yakusan ascended the rostrum and sat there for a while. Then he descended and returned to his room. The temple steward followed him and asked, “You said a while ago that you would give the assembly a sermon. Why didn’t you speak even a word?” Yakusan said, “For sutras, there are sutra specialists; for sastras [1], there are sastra specialists. Why do you have doubts about this old monk [2] ?” [1]: Books on Buddhist doctrines, written by ancient Buddhist philosophers. [2]: i.e. Yakusan.', 'Whenever Master Hyakujo delivered a sermon, an old man was always there listening with the monks. When they left, he left too. One day, however, he remained behind. Hyakujo asked him, “What man are you, standing there?” The old man replied, “In the past, in the time of Kashyapa Buddha, I lived on this mountain as a Zen priest. Once a monk came and asked me, ‘Does a perfectly enlightened person fall under the law of cause and effect or not?’ I said to him, He does not.’ Because of this answer, I fell into the state of a fox for 500 lives. Now, I beg you, Master, please say a turning word.” Hyakujo said, “The law of cause and effect cannot be obscured.” Upon hearing this, the old man became greatly enlightened.', 'Once the monks of the eastern and western Zen halls in Nansen’s temple were quarrelling about a cat. As he saw this, Nansen held up the cat and said, “You monks! If one of you can say a word, I will not slay the cat.” No one could answer. Nansen cut the cat in two. Nansen told Joshu what had happened, and asked him for his view. Joshu thereupon took his sandals, put them upon his head and went away. Nansen said, “If you had been there, I could have spared the cat.”', 'There was an old woman on the way to Taizan. Whenever a monk asked her how to get to Taizan, she would answer, “Go straight on.” After the monk had gone a few steps, she would say, “This good and naïve fellow goes off that way, too.” Later a monk told Joshu about this. Joshu said, “Wait a bit. I will go and see through her for you.” He went and asked the same question. The next day, Joshu ascended the rostrum and said, “I have seen through the old woman for you.”', 'Great Master Unmon said, “When the light does not penetrate, there are two diseases. Everything is unclear and things hang before you: this is one disease. Even after you have realized the emptiness of all things, somehow you feel as if there were still something there. This shows that the light has not yet penetrated thoroughly. Also there are two diseases concerning the Dharma-body. You have reached the Dharma-body, but you remain attached to the Dharma and cannot extinguish your own view; therefore you lead a corrupt life around the Dharma-body: this is one disease. Suppose you have truly penetrated to the end, if you give up further efforts, it will not do. You examine yourself minutely and say you have no flaw: this is nothing but a disease.”', 'Jizo asked Shuzanshu, “Where have you come from?” Shuzanshu said, “I have come from the South.” Jizo said, “How is Buddhism in the South these days?” Shuzanshu said, “There is much lively discussion.” Jizo said, “How could that match with our planting the rice field here and making rice-balls to eat?” Shuzanshu said, “How could you then save the beings of the Three Worlds?” Jizo said, “What do you call ‘the Three Worlds’?”', 'When Rinzai was about to die, he entrusted Sansho with his Dharma and said, “After my passing, do not destroy my treasury of the Eye of the true Dharma [1].” Sansho said, “How would I dare destroy your treasury of the Eye of the true Dharma?” Rinzai said, “If someone asks you about it, how will you answer?” Sansho instantly shouted his Kaatz. Rinzai said, “Who knows that my treasury of the Eye of the true Dharma has been destroyed by this blind donkey?” [1]: Originally: shobogenzo.', 'Attendant Kaku asked Tokusan, “Where have all the past saints gone?” Tokusan said, “What? What?” Kaku said, “I gave the command for an excellent horse like a flying dragon to spring forth, but there came out only a lame tortoise.” Tokusan was silent. The next day, when Tokusan came out of the bath, Kaku served him tea. Tokusan passed his hand gently over Kaku’s back. Kaku said, “This old fellow has gotten a glimpse for the first time.” Again, Tokusan was silent.', 'Isan asked Kyozan, “Where have you come from?” Kyozan said, “From the rice field.” Isan said, “How many people are there in the rice field?” Kyozan thrust his hoe into the ground and stood with his hands folded on his chest. Isan said, “There are a great number of people cutting thatch on the South Mountain.” Kyozan took up his hoe and left immediately.', 'Mayoku, with his ring-staff in hand, came to Shokei. He circled Shokei’s dais three times, shook the ring-staff and stood there bolt upright. Shokei said, “Right, right!” Mayoku then came to Nansen. He circled Nansen’s dais three times, shook the ring-staff and stood there bolt upright. Nansen said, “Not right, not right!” Then, Mayoku said, “Master Shokei said, ‘Right, right!’ Why, Master, do you say, ‘Not right, not right!’?” Nansen said, “With Shokei it is right, but with you it is not right. This is nothing but a whirling of the wind. In the end, it will perish.”', 'Hogen asked Shuzanshu, “"If there is only a hairsbreadth of difference, it is the distance between heaven and earth."[1] How do you understand that?” Shuzanshu said, “If there is only a hairsbreadth of difference, it is the distance between heaven and earth.” Hogen said, “If that’s your understanding, how could you ever attain IT?” Shuzanshu said, “My view is just that. How about you, Master?” Hogen said, “If there only is a hairsbreadth of difference, it is the distance between heaven and earth.” Shuzanshu made a deep bow. [1]: Cited from the Shinjinmei (A Hymn of Sincere Mind), a work by the Third Patriarch Sosan.', 'A monk asked Joshu, “Does the dog have buddha-nature, or not?” Joshu said, “It has” [U]. The monk said, “If it has it, why did it creep into that skin bag?” Joshu said, “Because it does so knowingly.” Another monk asked, “Does the dog have buddha-nature, or not?” Joshu said, “It has not” [Mu]. The monk said, “All living beings have buddha-nature [2]. Why doesn’t the dog have any?” Joshu said, “Because it is in its karma-consciousness.” [1]: see case 1 of Mumonkan: the Shoyoroku case presents a fuller text of the dialogue. [2]: Quotation from the Nirvana Sutra 7, 25.', 'A monk asked Unmon, “Not a single thought arises: is there any fault or not?” Unmon said, “Mt. Sumeru. [1]” [1]: The highest and most massive mountain in the world according to the Indian cosmology.', 'Jizo asked Hogen, “Where are you going, senior monk? [1]” Hogen said, “I am on pilgrimage [2], following the wind.” Jizo said, “What are you on pilgrimage for?” Hogen said, “I don’t know.” Jizo said, “Non knowing is most intimate.” Hogen suddenly attained great enlightenment. [1]: “Senior monk” (joza) is an honorific for a monk who has practiced more than 10 years. [2]: Originally: angya.', 'When Ungan was sweeping the ground, Dogo said, “You are having a hard time!” Ungan said, “You should know there is one who doesn’t have a hard time.” Dogo said, “If that’s true, you mean there is a second moon?” Ungan held up his broom and said, “What number of moon is this?” Dogo was silent. Gensha said, “That is precisely the second moon.” Unmon said, “The servant greets the maid politely.”', 'Ganto came to Tokusan. He straddled the threshold of the gate and asked, “Is this ordinary or is this holy?” Tokusan shouted, “Kaatz!” Ganto made a deep bow. Hearing of this, Tozan said, “Hardly anyone but Ganto could have accepted it that way.” Ganto said, “Old Tozan can’t tell between good and bad. At that time, I raised up with one hand and suppressed with the other.”', 'Whenever Roso saw a monk coming, he immediately sat facing the wall. Hearing of this, Nansen said, “I usually tell my people to realize what has existed before the kalpa of emptiness [1], or to understand what has been before Buddhas appeared in the world. Still, I haven’t acknowledged one disciple or even a half. If he continues that way, he will go on even until the year of the donkey [2].” [1]: One of the “four kalpas” or periods of cosmic changes: the kalpa of creation, the kalpa of existence, the kalpa of destruction, and the kalpa of emptiness. [2]: Since there is no “year of the donkey” in the Chinese zodiac, the expression “until the year of donkey” means endlessly.', 'Seppo, instructing the assembly, said, “There’s a poisonous snake on the southern side of the mountain. All of you should look at it carefully!” Chokei said, “Today in the Zen hall there are many people. They have lost their body and life.” A monk told this to Gensha, who said, “Only Elder Brother Ryo [2] could say something like that. However, I wouldn’t talk like that.” The monk asked, “What then would you say, Master”? Gensha replied, “Why does it have to be ‘the southern side of the mountain’?” Unmon threw his staff in front of Seppo and acted frightened. [1]: see case 22 of Hekiganroku. [2]: i.e. Chokei.', 'One day, Enkan called to his attendant, “Bring me the rhinoceros fan.” The attendant said, “It is broken.” Enkan said, “If the fan is already broken, bring me the rhinoceros himself.” The attendant gave no answer. Shifuku drew a circle and wrote the ideograph “ox [2]” in it. [1]: see case 91 of Hekiganroku. [2]: The Chinese character for “ox” (gyu) is one of the two characters for “rhinoceros” (saigyu = sai + gyu).', 'Kyozan pointed to the snow lion [1] and said, “Is there any [2] that goes beyond this color?” Unmon said [3], “I would have pushed it over for him at once.” Setcho said [4], “He only knows how to push it over, but he doesn’t know how to help it up.” [1]: Probably a lion made of snow or a stone lion covered with snow. [2]: I.e., “anyone” or “anything.” [3]: I.e., later. [4]: I.e., hearing of this.', 'Hogen pointed to the bamboo blinds with his hand. At that moment, two monks who were there went over to the blinds together and rolled them up. Hogen said, “One has gained, one has lost.”', 'A monk asked Gokoku, “How about when a crane perches on a withered pine tree?” Gokoku said, “It is a disgrace when seen from the ground.” The monk asked, “What about when every drop of water is frozen at once?” Gokoku said, “It’s a disgrace after the sun has risen.” The monk asked, “At the time of the Esho Persecution [1], where did the good Guardian Deities [2] of the Dharma go?” Gokoku said, “It is a disgrace for the two of them on both sides of the temple gate.” [1]: Buddhism was suppressed by order of Emperor Bu (about 840). [2]: Nio-figures representing the two Deva kings on each side of the main gate of a Buddhist temple. They are considered to be protectors of the Dharma.', 'When he was staying at the government office of the Province Ei, Fuketsu entered the hall [to preach] and said, “The heart seal [stamp] of the patriarch resembles the activity of the iron ox. When it goes away, the [impression of the] seal remains; when it stays there, the [impression of the] seal is brought to naught. If it neither goes away nor stays, would it be right to give a seal [of approval] or not?” Then Elder Rohi came up and said, “I have the activities of the iron ox. [However,] I ask you, Master, not to give me the seal.” Fuketsu said, “I am accustomed to leveling the great ocean through fishing whales. But, alas, now I find instead a frog wriggling about in the mud.” Rohi stood there considering. Fuketsu shouted “Kaatz!” and said, “Why don’t you say anything else, Elder?” Rohi was perplexed. Fuketsu hit him with his whisk and said, “Do you remember what you said? Say something, I’ll check it for you.” Rohi tried to say something. Fuketsu hit him again with his whisk. The Magistrate said, “Buddha’s law and the King’s law are of the same nature.” Fuketsu said, “What principle do you see in them?” The Magistrate said, “If you do not make a decision where a decision should be made, you are inviting disorder.” Fuketsu descended from the rostrum.', 'A monk asked Daizui, “When the great kalpa fire bursts out, the whole universe [2] will be destroyed. I wonder if IT will also be destroyed or not.” Daizui said, “Destroyed.” The monk said, “If so, will IT be gone with the other [3]?” Daizui said, “Gone with the other.” A monk asked Ryusai, “When the great kalpa fire bursts out, the whole universe will be destroyed. I wonder if IT will also be destroyed or not.” Ryusai said, “Not destroyed.” The monk said, “Why is it not destroyed?” Ryusai said, “Because it is the same as the whole universe.” [1]: see case 29 of Hekiganroku: The Shoyoroku case has an additional part with Ryusai. [2]: Literally: “a billion worlds.” [3]: The word “the other” means “the universe.”', 'Unmon, instructing the assembly, said, “The old buddha and a pillar intersect each other. What number of activity is that?” The assembly was silent. He said on their behalf, “Clouds gather over the South Mountain; rain falls on the North Mountain.”', 'Kyozan asked a monk, “Where do you come from?” The monk said, “I am from Yu Province” Kyozan said, “Do you think of that place?” The monk said, “I always do.” Kyozan said, “That which thinks is the mind [1]. That which is thought about is the objective world. Within that are mountains, rivers and the great earth, towers, palaces, people, animals, and other things. Reflect upon the mind that thinks. Are there a lot of things there?” The monk said, “I don’t see anything at all there.” Kyozan said, “That’s right for the stage of understanding, but not yet for the stage of personalization.” The monk said, “Do you have any special advice, Master?”\
                     Kyozan said, “It is not right to say that there is or there is not. Your insight shows that you have obtained only one side of the mystery. Sitting down, putting on clothes, from now on you see by yourself.” [1]: Originally: kokoro.', 'Sansho asked Seppo, “When a fish with golden scales has passed through the net, what should it get for food?” Seppo said, “I will tell you when you have passed through the net.” Sansho said, “A great Zen master with 1500 disciples doesn’t know how to speak.” Seppo said, “The old monk is just too busy with temple affairs.”', 'Fuketsu, giving instruction, said, “If one raises a speck of dust, the house and the nation prosper. If one does not raise a speck of dust, they perish.” Setcho held up his staff and said, “Is there anyone who lives and dies with this?”', 'Rakuho came to Kassan and without bowing stood facing him. Kassan said, “A chicken dwells in the phoenix nest. It’s not of the same class. Go away.” Rakuho said, “I have come from far away, hearing much about you. Please, Master, I beg you to guide me.” Kassan said, “Before my eyes there is no you, and here there is no old monk [1].” Rakuho shouted, “Kaatz!” Kassan said, “Stop it, stop it. Don’t be so careless and hasty. Clouds and the moon are the same; valleys and mountains are different from each other. It is not difficult to cut off the tongues of the people under heaven. But how can you make a tongueless person speak?” Rakuho said nothing. Kassan hit him. With this, Rakuho started to obey Kassan. [1]: I.e., “I.”', 'Great Master Ba was seriously ill. The temple steward asked him, “Master, how are you feeling these days?” Great Master said, “Sun-faced Buddha, Moon-faced Buddha.”', 'Isan asked Kyozan, “Suppose a man asks you, saying, ‘All living beings are tossed in a vast karma-consciousness, and have no foundation to rely upon.’ How would you check him?” Kyozan said, “If such a monk appears, I call out to him, ‘Mr. So-and-so!’ When he turns his head, instantly I say, ‘What is this?’ If he hesitates, then I say to him, "Not only is there a vast karma-consciousness, but also there is no foundation to rely upon."” Isan said, “Good.”', 'Rinzai instructed his assembly and said, “There is one true person of no rank, always coming out and going in through the gates of your face [1]. Beginners who have not yet witnessed that, look! look!” Then a monk came out and asked, “What is the one true person of no rank?” Rinzai descended from the rostrum and grabbed him. The monk hesitated. Rinzai pushed him away and said, “The true person of no rank — what a shit-stick you are!” [1]: I.e., sense organs such as eyes, nose, ears, tongue, etc.', 'A monk asked Joshu, “I have just entered this monastery. I beg you, Master, please give me instructions.” Joshu asked, “Have you eaten your rice gruel yet?” The monk answered, “Yes, I have.” Joshu said, “Then wash your bowls.”', 'Unmon asked Kempo, “May I ask for your answer [1]?” Kempo said, “Have you ever reached this old monk or not?” Unmon said, “If so, I must say I was too late.” Kempo said, “Is that so? Is that so?” Unmon said, “I thought I was Marquis White, but I find that here is Marquise Black [2].” [1]: A literal translation. It is possible to understand the word simply as “instruction.” [2]: Marquis White and Marquise Black are noted thieves in Chinese folklore. Marquise Black, a female thief, seems to have been the cleverer of the two.', 'When he was about to die, Rakuho addressed his assembly and said, “I have one matter to ask you about. If you say ‘yes’ to this, you are putting another head on your own. If you say ‘no,’ you are looking for life by cutting off your head.” The head monk said, “The green mountain always lifts up its legs; you don’t need to carry a lantern in the daylight.” [1] Rakuho said, “What time is this to utter such a saying?” A senior monk named Genjo stepped forward and said, “Apart from these two ways, I beg you, Master, not to ask.” Rakuho said, “That’s not enough. Say some more.” Genjo said, “I cannot say it fully.” Rakuho said, “I don’t care whether or not you can say it fully.” Genjo said, “I feel just like an attendant who has nothing to respond to his master.” [2] That evening, Rakuho called Genjo to him and said, “Your response today had something quite reasonable. You have to realize what our late master [3] said, "There are no dharmas before the eyes, Yet consciousness is before the eyes. IT is not the Dharma before the eyes, IT cannot be reached by eyes and ears."" Which phrase is the guest? Which phrase is the host? If you can sort them out, I will transmit the bowl and robe to you.” Genjo said, “I don’t understand.” Rakuho said, “You must understand.” Genjo said, “I really don’t understand.” Rakuho uttered a kaatz and said, “Miserable, miserable!” [Another] monk asked, “What would you like to say, Master?” Rakuho said, “The boat of compassion is not rowed over pure waves. It’s been wasted labor releasing wooden geese down the precipitous strait [4].” [1]: Most probably a saying formed by Rakuho himself. [2]: Apparently an idiomatic expression meaning, “I can’t describe it in words.” [3]: Rinzai or Kassan. [4]: It was a custom that the boat rushing down the stream through a gorge released pieces of wood ahead as a warning so that a possible crash with the boat coming upstream could be avoided. These wooden chips were called “wooden geese.”', 'A monk asked National Teacher Chu of Nanyo, “What is the essential body [1] of Vairocana Buddha [2]?” National Teacher said, “Pass me that water jug.” The monk passed him the water jug. National Teacher said, “Put it back where it was.” The monk asked again, “What is the essential body of Vairocana Buddha?” National Teacher said, “The old Buddha is long gone.” [1]: The so-called “Dharma-body” or dharmakaya. [2]: The principal Buddha.', 'Razan asked Ganto, “What if things appear and disappear without ceasing?” Ganto scolded him saying, “Who appears and disappears?”', 'A monk asked Master Ho of Koyo, “The great dragon has emerged from the ocean, calming heaven and earth. How will you treat him when he suddenly appears before you?” Master Ho said, “Suparnin [1], the king of birds, absorbs the entire universe. Who can stick his head within him?” The monk said, “But how about when he does appear?” Ho said, “It is like a falcon catching a pigeon. If you don’t realize it, you will learn the truth through the ‘inspection before the balcony.’ [2]” The monk said, “If so, then I’ll fold my hands on my chest and retreat three steps.” Ho said, “You black tortoise under the Sumeru altar. [3] Don’t wait to be struck on the forehead again and get hurt.” [1]: A giant bird that eats even dragons. [2]: A reference to a story in which Heigenkun Chosho, the brother of the king of Cho and a wealthy landlord with 3,000 dependents, built a grand palace with a balcony that overlooked the main road. One day a crippled person was passing by and one of the concubines saw him and laughed. The crippled person was angered and demanded Heigenkun her head. Heigenkun presented the head of an executed convict as the head of the concubine. His dependents knew of his deception, lost faith in their master and gradually all left him. His fortunes declined, so at last he cut off the head of the concubine and presented it for the crippled person to inspect. After that the dependents returned and his fortunes were restored. The story is an allusion to the fact that you can never hide away the real truth. [3]: A reference to one of the four carved figures, representing black tortoises, underneath the Sumeru altar (with the Buddha statue). It is used here as a symbol of someone who has lost the freedom of movement.', 'The Engaku [1] Sutra says: “At all times, you do not raise the delusive mind. When there are all kinds of illusory thoughts, you do not extinguish them. Dwelling in the delusory state of mind, you do not add understanding. Where there is no understanding, you do not distinguish the truth.” [1]: “Engaku” means the perfect awakening of Buddha.', 'Great Master Tokusan Emmyo instructed his assembly and said, “If you have exhausted to the end, you will realize right away that all buddhas in the three worlds have stuck their mouths to the wall [1]. Yet there is still one person ¡© he is giving a great laugh. If you can recognize that person, you have accomplished your study.” [1]: I.e., they are unable to open their mouths.', 'A monk asked Joshu, “What is the meaning of the patriarch’s coming from the West?” Joshu said, “The oak tree there in the garden.”', 'Vimalakirti asked Manjusri, “What does it mean that the Bodhisattva enters the Dharma-gate of Not-Two?” Manjusri said, “I see it like this: in all phenomena, there are neither words nor explanations, neither presentations nor knowledge; it is beyond all questions and answers. That is what I understand with /to enter the Dharma-gate of Not-Two/.” Then Manjusri asked Vimalakirti, “All of us have finished giving our explanations. Now you should give your explanation. What does it mean that the Bodhisattva enters the Dharma-gate of Not-Two?” Vimalakirti remained silent.', 'When Tozan held a memorial service for Ungan before his portrait, he mentioned the episode with the portrait [1]. A monk came forward and asked, “When Ungan said, ‘Just this!’ what did that mean?” Tozan said, “At that time, I almost misunderstood my master’s meaning.” The monk said, “I wonder whether or not Ungan really knew that IT is.” Tozan said, “If he did not know that it is, how could he say like that? If he knew that it is, how did he dare say like that?” [1]: Tozan was still a young monk under Ungan. One day, when he was leaving his master, he asked Ungan, “After your passing, if I am asked by someone whether I have your portrait, what should I answer?” Ungan was silent for a while and then said, “Just this.”', 'When Seppo was living in a hermitage, two monks came to pay their respects. When he saw them coming, Seppo thrust open the gate of his hermitage with his hands, jumped out, and said, “What is this?” The monks also said, “What is this?” Seppo hung his head and retired into his hermitage. Later, the monks came to Ganto. He asked them, “Where have you come from?” The monks said, “From Reinan.” Ganto said, “Did you ever visit Seppo?” The monks said, “Yes, we visited him.” Ganto said, “What did he say?” The monks related what had happened. Ganto said, “What else did he say?” The monks said, “Not a word; he hung his head and retired into his hermitage.” Ganto said, “Oh, how I regret now that in those days I did not tell him the last word! If I had told it to him, no one under heaven could do anything against him.” At the end of the summer practice period the monks came back to this conversation and asked him about its meaning. Ganto said, “Why didn’t you ask me about it sooner?” The monks said, “We could not dare to ask you about it.” Ganto said, “Seppo was born on the same stem as I, but he will not die on the same stem. If you want to know the last word, it is just this.”']
            koan = random.sample(koans, 1)
            ct = datetime.datetime.now()
            koans = "koans: "
            print(koans, koan, ct)
            print()
            print("-Shoyoroku (E. Book of Serenity, C. Ts’ung-jung lu) A collection of 100 koans (50 are in LIFE), originally compiled in the 12th century by Wanshi Shogaku (C. Hung-chih Cheng-chüeh)")

        def hipster_tarot():
            while True:
                try:
                    number = int(input("Indicate number of (tarot) cards: "))
                except ValueError:
                    print("Invalid value")
                else:
                    break
            number
            numberstr = str(number)
            print()
            print("You draw" + "" + " " + "" + numberstr + "" + " " + "" + "cards from a deck...")
            time.sleep(4)
            deck = ["The Fool | Upright | Beginnings, innocence, spontaneity, a free spirit", "The Fool | Reversed | Holding back, recklessness, risk-taking", "The Fool | Upright | Manifestation, resourcfulness, power, inspired action", "The Fool | Reversed | Manipulation, poor planning, untapped talents", "The High Priestess | Upright | Intuition, sacred knowledge, the subconscious mind", "The High Priestess | Reversed | Secrets, disconnected from intuition, withdrawal and silence", "The Empress | Upright | Femininity, beauty, nature, nurturing, abundance", "The Empress | Reversed | Creative block, dependence on others", "The Emperor | Upright | Authority, establishment, structure, a father figure", "The Emperor | Reversed | Domination, excessive control, lack of discipline, inflexibility", "The Hierophant | Upright | Spiritual wisdom, religious beliefs, conformity, tradition,institutions", "The Hierophant | Reversed | Personal beliefs, freedom, challenging the status quo", "The Lovers | Upright | Love, harmony, relationships, values alignment, choices", "The Lovers | Reversed | Self-love, disharmony, imbalance, misalignment of values", "The Chariot | Upright | Control, willpower, success, action, determination", "The Chariot | Reversed | Self-discipline, opposition, lack of direction", "Strength | Upright | Strength, courage, persuasion, influence, compassion", "Strength | Reversed | Inner strength, self-doubt, low energy, raw emotion", "The Hermit | Upright | Soul-searching, introspection, being alone, inner guidance", "The Hermit | Reversed | Isolation, loneliness, withdrawal", "Wheel Of Fortune | Upright | Good luck, karma, life cycles, destiny, a turning point", "Wheel Of Fortune | Reversed | Bad luck, resistance to change, breaking cycles", "Justice | Upright | Justice, fairness, truth, cause and effect, law", "Justice | Reversed | Unfairness, lack of accountability, dishonesty", "The Hanged Man | Upright | Pause, surrender, letting go, new perspectives", "The Hanged Man | Reversed | Delays, resistance, stalling, indecision", "Death | Upright | Endings, change, transformation, transition", "Death | Reversed | Resistance to change, personal transformation, inner purging", "Temperance | Upright | Balance, moderation, patience, purpose", "Temperance | Reversed | Imbalance, excess, self-healing, re-alignment", "The Devil | Upright | Shadow self, attachment, addiction, restriction, sexuality", "The Devil | Reversed | Releasing limiting beliefs, exploring dark thoughts, detachment", "The Tower | Upright | Sudden change, upheaval, chaos, revelation, awakening", "The Tower | Reversed | Personal transformation, fear of change, averting disaster", "The Star | Upright | Hope, faith, purpose, renewal, spirituality", "The Star | Reversed | Lack of faith, despair, self-trust, disconnection", "The Moon | Upright | Lack of faith, despair, self-trust, disconnection", "The Moon | Reversed | Release of fear, repressed emotion, inner confusion", "The Sun | Upright | Positivity, fun, warmth, success, vitality", "The Sun | Reversed | Inner child, feeling down, overly optimistic", "Judgement | Upright | Judgement, rebirth, inner calling, absolution", "Judgement | Reversed | Self-doubt, inner critic, ignoring the call", "The World | Upright | Completion, integration, accomplishment, travel", "The World | Reversed | Seeking personal closure, short-cuts, delays", "Ace Of Cups | Upright | Love, new relationships, compassion, creativity.", "Ace Of Cups | Reversed | Self-love, intuition, repressed emotions." "Two Of Cups | Upright | Unified love, partnership, mutual attraction", "Two Of Cups | Reversed | Self-love, break-ups, disharmony, distrust.", "Three Of Cups | Upright | Celebration, friendship, creativity, collaborations.", "Three Of Cups | Reversed | Independence, alone time, hardcore partying, ‘three’s a crowd’.", "Four Of Cups | Upright | Meditation, contemplation, apathy, reevaluation.", "Four Of Cups | Reversed | Retreat, withdrawal, checking in for alignment.", "Five Of Cups | Upright | Retreat, withdrawal, checking in for alignment.", "Five Of Cups | Reversed | Personal setbacks, self-forgiveness, moving on.", "Six Of Cups | Upright | Revisiting the past, childhood memories, innocence, joy.", "Six Of Cups | Reversed | Living in the past, forgiveness, lacking playfulness.", "Seven Of Cups | Upright | Opportunities, choices, wishful thinking, illusion.", "Seven Of Cups | Reversed | Alignment, personal values, overwhelmed by choices.", "Eight Of Cups | Upright | Disappointment, abandonment, withdrawal, escapism.", "Eight Of Cups | Reversed | Trying one more time, indecision, aimless drifting, walking away.", "Nine Of Cups | Upright | Contentment, satisfaction, gratitude, wish come true.", "Nine Of Cups | Reversed | Inner happiness, materialism, dissatisfaction, indulgence.", "Ten Of Cups | Upright | Divine love, blissful relationships, harmony, alignment.", "Ten Of Cups | Reversed | Disconnection, misaligned values, struggling relationships.", "Page Of Cups | Upright | Creative opportunities, intuitive messages, curiosity, possibility.", "Page Of Cups | Reversed | New ideas, doubting intuition, creative blocks, emotional immaturity.", "Knight Of  Cups | Upright | Creativity, romance, charm, imagination, beauty.", "Knight Of Cups | Reversed | Overactive imagination, unrealistic, jealous, moody.", "Queen Of Cups | Upright | Compassionate, caring, emotionally stable, intuitive, in flow.", "Queen Of Cups | Reversed | Inner feelings, self-care, self-love, co-dependency.", "King Of Cups | Upright | Emotionally balanced, compassionate, diplomatic.", "King Of Cups | Reversed | Self-compassion, inner feelings, moodiness, emotionally manipulative.", "Ace Of Swords | Upright | Breakthroughs, new ideas, mental clarity, success", "Ace of Swords | Reversed | Inner clarity, re-thinking an idea, clouded judgement", "Two Of Swords | Upright | Difficult decisions, weighing up options, an impasse, avoidance", "Two Of Swords | Reversed | Indecision, confusion, information overload, stalemate", "Three Of Swords | Upright | Heartbreak, emotional pain, sorrow, grief, hurt", "Three Of Swords | Reversed | Negative self-talk, releasing pain, optimism, forgiveness", "Four Of Swords | Upright | Rest, relaxation, meditation, contemplation, recuperation", "Four Of Swords | Reversed | Exhaustion, burn-out, deep contemplation, stagnation", "Five Of Swords | Upright | Conflict, disagreements, competition, defeat, winning at all costs", "Five Of Swords | Reversed | Reconciliation, making amends, past resentment", "Six Of Swords | Upright | Transition, change, rite of passage, releasing baggage.", "Six Of Swords | Reversed | Personal transition, resistance to change, unfinished business", "Seven Of Swords | Upright | Betrayal, deception, getting away with something, acting strategically", "Seven Of Swords | Reversed | Imposter syndrome, self-deceit, keeping secrets", "Eight Of Swords | Upright | Negative thoughts, self-imposed restriction, imprisonment, victim mentality", "Eight Of Swords | Reversed | Self-limiting beliefs, inner critic, releasing negative thoughts, open to new perspectives", "Nine Of Swords | Upright | Anxiety, worry, fear, depression, nightmares", "Nine Of Swords | Reversed | Inner turmoil, deep-seated fears, secrets, releasing worry", "Ten Of Swords | Upright | Painful endings, deep wounds, betrayal, loss, crisis", "Ten Of Swords | Reversed | Recovery, regeneration, resisting an inevitable end", "Page Of Swords | Upright | New ideas, curiosity, thirst for knowledge, new ways of communicating", "Page Of Swords | Reversed | Self-expression, all talk and no action, haphazard action, haste", "Knight Of Swords | Upright | Ambitious, action-oriented, driven to succeed, fast-thinking", "Knight Of Swords | Reversed | Restless, unfocused, impulsive, burn-out", "Queen Of Swords | Upright | Independent, unbiased judgement, clear boundaries, direct communication", "Queen Of Swords | Reversed | Overly-emotional, easily influenced, bitchy, cold-hearted", "King Of Swords | Upright | Mental clarity, intellectual power, authority, truth", "King Of Swords | Reversed | Quiet power, inner truth, misuse of power, manipulation", "Ace Of Pentacles | Upright | A new financial or career opportunity, manifestation, abundance", "Ace Of Pentacles | Reversed | Lost opportunity, lack of planning and foresight", "Two Of Pentacles | Upright | Multiple priorities, time management, prioritisation, adaptability.", "Two Of Pentacles | Reversed | Over-committed, disorganisation, reprioritisation.", "Three Of Pentacles | Upright | Teamwork, collaboration, learning, implementation.", "Three Of Pentacles | Reversed | Disharmony, misalignment, working alone.", "Four Of Pentacles | Upright | Saving money, security, conservatism, scarcity, control.", "Four Of Pentacles | Reversed | Over-spending, greed, self-protection.", "Five Of Pentacles | Upright | Financial loss, poverty, lack mindset, isolation, worry.", "Five Of Pentacles | Reversed | Recovery from financial loss, spiritual poverty.", "Six Of Pentacles | Upright | Giving, receiving, sharing wealth, generosity, charity.", "Six Of Pentacles | Reversed | Self-care, unpaid debts, one-sided charity.", "Seven Of Pentacles | Upright | Long-term view, sustainable results, perseverance, investment.", "Seven Of Pentacles | Reversed | Lack of long-term vision, limited success or reward.", "Eight Of Pentacles | Upright | Apprenticeship, repetitive tasks, mastery, skill development.", "Eight Of Pentacles | Reversed | Self-development, perfectionism, misdirected activity.", "Nine Of Pentacles | Upright | Abundance, luxury, self-sufficiency, financial independence.", "Nine Of Pentacles | Reversed | Self-worth, over-investment in work, hustling.", "Ten Of Pentacles | Upright | Wealth, financial security, family, long-term success, contribution.", "Ten Of Pentacles | Reversed | The dark side of wealth, financial failure or loss.", "Page Of Pentacles | Upright | Manifestation, financial opportunity, skill development.", "Page Of Pentacles | Reversed | Lack of progress, procrastination, learn from failure.", "Knight Of Pentacles | Upright | Hard work, productivity, routine, conservatism.", "Knight Of Pentacles | Reversed | Self-discipline, boredom, feeling ‘stuck’, perfectionism.", "Queen Of Pentacles | Upright | Nurturing, practical, providing financially, a working parent.", "Queen Of Pentacles | Reversed | Financial independence, self-care, work-home conflict", "King Of Pentacles | Upright | Wealth, business, leadership, security, discipline, abundance.", "King Of Pentacles | Reversed | Financially inept, obsessed with wealth and status, stubborn.", "Ace Of Wands | Upright | Inspiration, new opportunities, growth, potential", "Ace Of Wands | Reversed | An emerging idea, lack of direction, distractions, delays", "Two Of Wands | Upright | Future planning, progress, decisions, discovery", "Two Of Wands | Reversed | Personal goals, inner alignment, fear of unknown, lack of planning", "Three Of Wands | Upright | Progress, expansion, foresight, overseas opportunities", "Three Of Wands | Reversed | Playing small, lack of foresight, unexpected delays", "Four Of Wands | Upright | Celebration, joy, harmony, relaxation, homecoming", "Four Of Wands | Reversed | Personal celebration, inner harmony, conflict with others, transition.", "Five Of Wands | Upright | Conflict, disagreements, competition, tension, diversity", "Five Of Wands | Reversed | Inner conflict, conflict avoidance, tension release", "Six Of Wands | Upright | Success, public recognition, progress, self-confidence", "Six Of Wands | Reversed | Private achievement, personal definition of success, fall from grace, egotism", "Seven Of Wands | Upright | Challenge, competition, protection, perseverance", "Seven Of Wands | Reversed | Exhaustion, giving up, overwhelmed", "Eight Of Wands | Upright | Movement, fast paced change, action, alignment, air travel", "Eight Of Wands | Reversed | Delays, frustration, resisting change, internal alignment", "Nine Of Wands | Upright | Resilience, courage, persistence, test of faith, boundaries", "Nine Of Wands | Reversed | Inner resources, struggle, overwhelm, defensive, paranoia", "Ten Of Wands | Upright | Burden, extra responsibility, hard work, completion", "Ten Of Wands | Reversed | Doing it all, carrying the burden, delegation, release", "Page Of Wands | Upright | Inspiration, ideas, discovery, limitless potential, free spirit", "Page Of Wands | Reversed | Newly-formed ideas, redirecting energy, self-limiting beliefs, a spiritual path", "Knight Of Wands | Upright | Energy, passion, inspired action, adventure, impulsiveness", "Knight Of Wands | Reversed | Passion project, haste, scattered energy, delays, frustration", "Queen Of Wands | Upright | Courage, confidence, independence, social butterfly, determination", "Queen Of Wands | Reversed | Self-respect, self-confidence, introverted, re-establish sense of self", "King Of Wands | Upright | Natural-born leader, vision, entrepreneur, honour", "King Of Wands | Reversed |  Impulsiveness, haste, ruthless, high expectations"]
            card = random.sample(deck, number)
            print("You drew:")
            print()
            ct = datetime.datetime.now()
            tarot = "tarot: "
            print(tarot, card, ct)

        def hack():
            time.sleep(0)
            youm = "You manage to connect to..."
            print(youm)
            time.sleep(2)
            countries = ["Canada", "Sweden", "China", "Beijing", "New York", "California", "L.A.", "San Francisco", "Detroit", "Colorado", "Newark", "New Jersey", "Australia", "Gold Coast", "Thailand", "North Korea", "Pyongyang", "Seoul", "Tokyo", "Osaka", "Japan", "Fujian", "Kyoto", "Manila", "Palawan", "Siargao", "Sultan Kudarat", "Davao", "Sydney", "Poland", "Uzbekistan", "Kyrgystan", "Turkey", "Iraq", "Iran", "Bolivia", "Iceland", "Lithuania", "Greenland", "UK", "France", "Spain", "Rome", "Greece", "Amsterdam", "Netherlands", "Boracay", "Indonesia", "Russia", "Ukraine", "Africa", "Antarctica", "Alaska", "South Carolina", "North Carolina", "Philadelphia", "Brooklyn", "Mexico", "Brazil", "Taiwan", "Burma", "Cambodia", "Vietnam", "India", "Bangladesh", "New Delhi", "Bombay", "Philippines", "Italy", "Belgium", "Denmark", "Colombia", "Argentina", "Albania", "Algeria", "Andora", "Angola", "Antigua and Barbuda", "Armenia", "Austria", "Azerbaijan", "Bahamas", "Bahrain", "Belarus", "Belize", "Benin", "Bhutan", "Bosnia", "Botswana", "Brunei", "Bulgaria", "Burkina Faso", "Burundi", "Cabo Verde", "Cameroon", "Chad", "Chile", "Costa Rica", "Croatia", "Cuba", "Cyprus", "Czechia", "Congo", "Djibouti", "Dominica", "Dominican Republic", "Ecuador", "Egypt", "El Salvador", "Guinea", "Estonia", "Swaziland", "Ethiopia", "Fiji", "Gabon", "Gambia", "Ghana", "Guatemala", "Guyana", "Haiti", "Honduras", "Hungary", "Israel", "Italy", "Jamaica", "Kenya", "Jordan", "Laos", "Latvia", "Lebanon", "Liberia", "Liechtenstein", "Luxembourg", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Mauritiana", "Mauritius", "Micronesia", "Moldova", "Monaco", "Mongolia", "Montenegro", "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauru", "Nepal", "Nicaragua", "Niger", "Nigeria", "North Macedonia", "Oman", "Pakistan", "Palau", "Palestine State", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Portugal", "Qatar", "Romania", "Rwanda", "Saint Kitts and Nevis", "Saint Lucia", "Saint Vincent and the Grenadines", "Samoa", "San Marino", "Sao Tome and Principe", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovakia", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Korea", "South Sudan", "Sri Lanka", "Sudan", "Suriname", "Switzerland", "Syria", "Tajikistan", "Tanzania", "Timor-Leste", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkmenistan", "Tuvalu", "Uganda", "United Arab Emirates", "Uruguay", "USA", "Vanuatu", "Vatican City", "Venezuela", "Yemen", "Zambia", "Zimbabwe"]
            country = random.choice(countries)
            print(country)
            serv = "Server at:"
            print(serv)
            time.sleep(1)
            lat = round(random.uniform(-90, 90), 4)
            lon = round(random.uniform(-180, 180), 4)
            print(lat)
            print(lon)
            time.sleep(2)
            andg = "and got away with:"
            print(andg)
            time.sleep(3)
            tidnar = (random.randint(0,999999999))
            print(tidnar)
            monies = ["Dollars", "Rupies", "Yen", "Pesos", "Pounds", "Coins", "Arcade Coins", "Mickey Mouse Money", "Francs", "Shekels", "Tugriks", "Indian Rupees", "Singapore Dollars", "Rubles", "Dinars", "Yuans", "Bahts", "Afghanis", "Riyals", "Kronas", "Riels", "DDOS attacks", "Botnets", "Credit Card Numbers", "E-mail addresses", "Business Addresses", "Home Addresses", "Passwords", "Mobile Numbers", "Telephone Numbers", "STD", "spits", "garbage", "sickness", "nudes", "hate", "likes"]
            money = random.choice(monies)
            ct = datetime.datetime.now()
            print(money, ct)
            hack = "hack:"
            time.sleep(3)

        def spar():
            time.sleep(4)
            actions = ["You connected with a", "You connected a", "You anticipate to give a", "You hit your opponent with a", "You give a", "You waited and gave a", "You missed with a", "You missed with a", "You attempted a", "You recieved a", "Your opponent connected with a", "Your opponent missed with a", "Your opponent waited and gave a", "Your opponent anticipated to give a", "You blocked a", "You blocked a", "You blocked a", "You blocked a", "You blocked a", "Your opponent blocked a", "Your opponent blocked a", "Your opponent blocked a", "Your opponent blocked a"]
            action = random.sample(actions, 1)
            kicks = ["45 kick", "45 kick", "45 kick", "45 kick", "45 kick", "front kick", "stretching kick", "turning-side kick", "turning-side kick", "side kick", "side kick", "punching kick", "axe kick", "axe kick", "full moon kick","full moon kick", "turning-long", "turning-long", "turning-jumping 45 kick", "out-in kick", "in-out kick", "turning-jumping out-in", "roundhouse kick", "roundhouse kick", "roundhouse kick", "turning-jumping roundhouse kick", "punch", "punch", "punch", "punch", "bullet 45 kick", "double 45 kick", "triple 45 kick", "jumping 45 kick", "jumping roundhouse kick", "jumping axe kick", "jumping front kick", "jumping out-in kick", "jumping in-out kick", "jumping side kick", "jumping turning-side kick", "jumping full moon kick"]
            kick = random.sample(kicks, 1)
            ct = datetime.datetime.now()
            spar = "spar: "
            print(spar, action, kick, ct)
            time.sleep(3)

        def train():
            time.sleep(2)
            print("You did:")
            time.sleep(5)
            nums = [10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 20, 20, 20, 20, 30, 30, 40, 40, 50, 50, 60, 70, 80, 90, 100]
            num = random.sample(nums, 1)
            ct = datetime.datetime.now()
            train = "train: "
            print(train, num, ct)
            print("push-ups")
            time.sleep(3)

        def rest():
            ct = datetime.datetime.now()
            print("You start to rest...", ct)
            time.sleep(8)
            print("You rested", ct)
            time.sleep(3)

        def haiku():
            time.sleep(4)
            starting = ["in the depths of soul", "in as much as I want", "nevertheless", "coming up with it", "i don't know this", "thinking of it", "thinking of you", "thinking of us", "i never want to but", "carry me all the way", "i am happy", "starting", "i never know how", "as much as i would", "killing me softly", "killing us", "the quietest weather", "gray clouds above", "i see the clear sky", "while the sky is bluest", "i've never been apart", "how would i know", "will i see you again", "it came up to me", "i was surprised", "surprising", "i would", "come to me", "start with this", "a few words", "lenten season is upon us", "i love", "thinking", "stop"]
            start = random.sample(starting, 1)
            middle = ["i wish i would have", "consider me", "i am looking for food", "while i am clothed", "walking the distance", "i still end up with you", "consider my wish", "halfed tree", "searching", "unsure", "not minding everyone", "listening to music", "on my computer", "typing", "eating", "sleeping", "thinking", "never missing", "stopping", "staring", "resting", "excruciating pain", "this sadness", "while im without", "collecting", "listening", "happiness", "the surf", "inspired", "rocking the music", "travelling", "playing", "while music plays", "stirring things up", "taking a bath", "walking on the shore", "grinding"]
            mid = random.sample(middle, 1)
            ending = ["i never knew how", "i be at it", "considered everything", "i died", "i slept", "its wrapped", "made a union", "the sky bleeds", "music is spoken", "chilled", "i am spoiled", "this bringeth happiness", "its up to me", "the weather is", "i stay awake", "pillows", "grains", "half of the time", "it ends here", "i take flight", "distance is", "i like this", "forever", "lets meet", "gathered my wits"]
            end = random.sample(ending, 1)
            ct = datetime.datetime.now()
            haiku = "haiku: "
            print(haiku, start, mid, end, ct)

        def psalms():
            dd = list(verses1)
            time.sleep(5)
            print("From the Bible (King James Version), The Book of Psalms 1-21,")
            print()
            time.sleep(2)
            verse = random.sample(dd, 1)
            ct = datetime.datetime.now()
            psalms = "psalms: "
            print(psalms, verse, ct)

        def bible_verses():
            dd = list(bible1)
            while True:
                try:
                    number = int(input("Indicate number of (Bible) verses: "))
                except ValueError:
                    print("Invalid value")
                else:
                    break
            number
            print()
            time.sleep(.4)
            verse = random.sample(dd, number)
            ct = datetime.datetime.now()
            bible_ref = "bible: "
            print(bible_ref, verse, ct)

        def dhammapada():
            dd = list(dhammapada1)
            while True:
                try:
                    number = int(input("Indicate number of verses (1 or 2 is a good starting point): "))
                except ValueError:
                    print("Invalid value")
                else:
                    break
            number
            time.sleep(1)
            print()
            print()
            print("Here are verses from Buddha's text, The Dhammapada")
            print()
            time.sleep(1)
            verse = random.sample(dd, number)
            ct = datetime.datetime.now()
            dhammapad = "dhammapada: "
            print(dhammapad, verse, ct)
            print()

        def pr0verbs():
            dd = list(proverbs)
            while True:
                try:
                    number = int(input("Indicate number of (proverbs) verses: "))
                except ValueError:
                    print("Invalid value")
                else:
                    break
            number
            time.sleep(.2)
            print()
            verse = random.sample(dd, number)
            ct = datetime.datetime.now()
            prverbs = "proverbs:"
            print(prverbs, verse, ct)
            print()

        def maryjane():
            dd = list(strains)
            while True:
                try:
                    number = int(input("Indicate number of (strains) results: "))
                except ValueError:
                    print("Invalid value")
                else:
                    break
            number
            time.sleep(.2)
            print()
            strain = random.sample(dd, number)
            ct = datetime.datetime.now()
            mj = "maryjane:"
            print(mj, strain, ct)
            print()

        def koran():
            koran = list(koran1)
            while True:
                try:
                    number = int(input("Indicate number of (koran) verses: "))
                except ValueError:
                    print("Invalid value")
                else:
                    break
            number
            time.sleep(1)
            print()
            time.sleep(2)
            verse = random.sample(koran, number)
            ct = datetime.datetime.now()
            kor = "koran: "
            print(kor, verse, ct)
            print()

        def message():
            chat = input("$ ")
            while True:
                try:
                    number = int(input("Indicate number of (lh) results: "))
                except ValueError:
                    print("Invalid value")
                else:
                    break
            number
            ctd = datetime.datetime.now()
            lh = "lh: "
            print(lh + "" + "$" + "" + " " + "" + usr, chat)
            for _ in range(number):
                def generate_random_letters():
                    random1 = random.choice(string.ascii_letters)
                    random2 = random.choice(string.ascii_letters)
                    random3 = random.choice(string.ascii_letters)
                    letters = [random1, random2, random3]
                    random.shuffle(letters)
                    return letters
                random_letters = generate_random_letters()
                time.sleep(random.randint(0,4))
                print()
                nano = (diction)
                sitch  = (round(random.random()*9999,4))
                lokalhost = "LOKALHOST: "
                chat = random.sample(nano, random.randint(0,5))
                ct = datetime.datetime.now()
                print(lokalhost, random_letters, sitch, chat, ct)

        def souls():
            nano = (diction)
            while True:
                try:
                    number = int(input("Indicate number of (souls) results: "))
                except ValueError:
                    print("Invalid value")
                else:
                    break
            number
            time.sleep(4)
            print()
            for _ in range(number):
                time.sleep(1)
                print()
                anrdom = (round(random.random()*999,8))
                soulchat = random.sample(nano, 1)
                ct = datetime.datetime.now()
                souls = "souls: "
                print(souls, anrdom, soulchat, ct)

        def c():
            chat2 = input("chat: ")
            print()
            print(usr + "" + " " + "" + "You: " + "" + chat2)
            for _ in range(6):
                print()
                time.sleep(random.randint(1,4))
                kpop = ["AK", "Joji", "Kiera", "Ape"]
                kchatz = random.sample(kpop, 1)
                chatso = ["how are you", "i am fine", "youre welcome", "i dont know", "maybe", "hi", "hello", "whats up", "im thinking of you", "i miss you", "i love you", "i love you deeply", "i love you so much", "i love you always", "i love you much", "where are you", "ill come over", "come over here", "lets meet", "playing", "just joking", "youre in my mind", "whenever", "i saw you", "we were together", "we met", "we met a while ago", "we just met", "you saw me", "im studying", "im in school", "im travelling", "im in transit", "im at work", "im playing", "im shopping", "im at the grocery", "im at the parlor", "im at home", "where you are", "i adore you", "you are adored", "you are special", "am i special", "do you love me?", "yes", "no", "maybe", "lets meet again", "i hope to see you again", "what are you thinking", "youre always in my mind", "in the depths of soul", "in as much as I want", "nevertheless", "coming up with it", "i don't know this", "thinking of it", "thinking of you", "thinking of us", "i never want to but", "carry me all the way", "i am happy", "starting", "i never know how", "as much as i would", "killing me softly", "killing us", "the quietest weather", "gray clouds above", "i see the clear sky", "while the sky is bluest", "i've never been apart", "how would i know", "will i see you again", "it came up to me", "i was surprised", "surprising", "i would", "come to me", "start with this", "a few words", "lenten season is upon us", "i love", "thinking", "stop", "i wish i would have", "consider me", "i am looking for food", "while i am clothed", "walking the distance", "i still end up with you", "consider my wish", "halfed tree", "searching", "unsure", "not minding everyone", "listening to music", "on my computer", "typing", "eating", "sleeping", "thinking", "never missing", "stopping", "staring", "resting", "excruciating pain", "this sadness", "while im without", "collecting", "listening", "happiness", "the surf", "inspired", "rocking the music", "travelling", "playing", "while music plays", "stirring things up", "taking a bath", "walking on the shore", "grinding", "i never knew how", "i be at it", "considered everything", "i died", "i slept", "its wrapped", "made a union", "the sky bleeds", "music is spoken", "chilled", "i am spoiled", "this bringeth happiness", "its up to me", "the weather is", "i stay awake", "pillows", "grains", "half of the time", "it ends here", "i take flight", "distance is", "i like this", "forever", "lets meet", "gathered my wits", "what is?", "what is ?", "ouch!", "**", "that?", "ok", "ok bye", "really?", "why not..", "aww why?", "tell me!", "what s it?", "don't do that to me", "hi sir", "oh uhm..", "I honestly don't know", "I know", "this", "did you see", "good boy", "good pinsan", "do you have a gf?", "*kisses*", "feel good!", "like this", "like thus", "what are you doing to me?", "shall we talk about something else?", "oh yes..", "because", "I might consider it", "yes you :)", "you and me", "I like that more", "me?", "I agree", "I love you more", "I will", "IDK", "stuff", "sorry you cant do this here", "I love it", "oh no", ""]
                kchat = random.sample(chatso, 1)
                c = "c: "
                print(c, kchatz, kchat)

        def asciii():
            print()
            ctm = datetime.datetime.now()
            def generate_random_letters():
                random1 = random.choice(string.ascii_letters)
                random2 = random.choice(string.ascii_letters)
                random3 = random.choice(string.ascii_letters)
                letters = [random1, random2, random3]
                random.shuffle(letters)
                return letters
            random_letters = generate_random_letters()
            sitch  = (round(random.random()*9999,4))
            asc = "ascii:"
            print(asc, usr, random_letters, sitch, ctm)
            pr1 = (round(random.random()*99999999999999999999999999999999999999999))
            pr2 = (round(random.random()*99999999999999999999999999999999999999999))
            pr3 = (round(random.random()*99999999999999999999999999999999999999999))
            pr4 = (round(random.random()*99999999999999999999999999999999999999999))
            pr5 = (round(random.random()*99999999999999999999999999999999999999999))
            pr6 = (round(random.random()*99999999999999999999999999999999999999999))
            pr7 = (round(random.random()*99999999999999999999999999999999999999999))
            pr8 = (round(random.random()*99999999999999999999999999999999999999999))
            pr9 = (round(random.random()*99999999999999999999999999999999999999999))
            pr10 = (round(random.random()*99999999999999999999999999999999999999999))
            pr11 = (round(random.random()*99999999999999999999999999999999999999999))
            pr12 = (round(random.random()*99999999999999999999999999999999999999999))
            pr13 = (round(random.random()*99999999999999999999999999999999999999999))
            pr14 = (round(random.random()*99999999999999999999999999999999999999999))
            pr15 = (round(random.random()*99999999999999999999999999999999999999999))
            pr16 = (round(random.random()*99999999999999999999999999999999999999999))
            print()
            colors = [GREEN, RED, RESET]
            print()
            print(''.join(f"{random.choice(colors)}{d}{RESET}" for d in str(pr1)))
            print(''.join(f"{random.choice(colors)}{d}{RESET}" for d in str(pr2)))
            print(''.join(f"{random.choice(colors)}{d}{RESET}" for d in str(pr3)))
            print(''.join(f"{random.choice(colors)}{d}{RESET}" for d in str(pr4)))
            print(''.join(f"{random.choice(colors)}{d}{RESET}" for d in str(pr5)))
            print(''.join(f"{random.choice(colors)}{d}{RESET}" for d in str(pr6)))
            print(''.join(f"{random.choice(colors)}{d}{RESET}" for d in str(pr7)))
            print(''.join(f"{random.choice(colors)}{d}{RESET}" for d in str(pr8)))
            print(''.join(f"{random.choice(colors)}{d}{RESET}" for d in str(pr9)))
            print(''.join(f"{random.choice(colors)}{d}{RESET}" for d in str(pr10)))
            print(''.join(f"{random.choice(colors)}{d}{RESET}" for d in str(pr11)))
            print(''.join(f"{random.choice(colors)}{d}{RESET}" for d in str(pr12)))
            print(''.join(f"{random.choice(colors)}{d}{RESET}" for d in str(pr13)))
            print(''.join(f"{random.choice(colors)}{d}{RESET}" for d in str(pr14)))
            print(''.join(f"{random.choice(colors)}{d}{RESET}" for d in str(pr15)))
            print(''.join(f"{random.choice(colors)}{d}{RESET}" for d in str(pr16)))

        def mp3():
            print("You queue five tracks from an mp3 player that you found on the train...")
            time.sleep(4)
            music = random.sample(tracks, 5)
            ct = datetime.datetime.now()
            mp3 = "mp3: "
            print(mp3, music, ct)
            time.sleep(3)

        def monopoly():
            print("You rolled:")
            time.sleep(2)
            dice1 = ["1", "2", "3", "4", "5", "6", "7", "8"]
            dice2 = ["1", "2", "3", "4", "5", "6", "7", "8"]
            roll1 = random.sample(dice1, 1)
            roll2 = random.sample(dice2, 1)
            print(roll1)
            print(roll2)
            time.sleep(2)
            boxes = ["Mediterranean Avenue", "Community Chest", "Baltic Avenue", "INCOME TAX", "Reading Railroad", "Oriental Avenue", "Chance", "Vermont Avenue", "Connecticut Avenue", "Jail", "St. Charles Palace", "Electric Company", "States Avenue", "Virginia Avenue", "Pennsylvania Railroad", "St. James Place", "Community Chest", "Free Parking", "Kentucky Avenue", "Chance", "Indiana Avenue", "Illinois Avenue", "B&O Railroad", "Atlantic Avenue", "Ventnor Avenue", "Water Works", "Marvin Gardens", "GO TO JAIL", "Pacific Avenue", "North Carolina Avenue", "Community Chest", "Pennsylvania Avenue", "Short Line", "Chance", "Park Place", "LUXURY TAX", "Boardwalk"]
            box = random.sample(boxes, 1)
            print("And landed in =")
            ct = datetime.datetime.now()
            monopoly = "monopoly: "
            print(monopoly, box, ct)
            time.sleep(3)

        def equips():
            time.sleep(0)
            print("head:")
            headgear = ["samurai helmet", "bike helmet", "motorcycle helmet", "astronaut helmet", "pilot helmet", "aviator hat", "baseball cap", "backwards baseball cap", "trucker cap", "backwards trucker cap", "construction helmet", "miner helmet", "skate helmet", "ski mask", "facemask", "beanie", "birthday party hat", "pantyhose", "f13th mask", "jabbawockee mask", "none", "poring hat", "beehive", "idea bubble", "speech bubble", "bucket hat", "black bucket hat", "beige bucket hat", "orange bucket hat", "blue bucket hat", "american football helmet", "rugby helmet", "emo hair", "mohawk", "blonded semi-balded", "skinhead", "tropika", "glasses", "raybans", "shades", "spectacles", "night-vision goggles", "pilot goggles", "black-rimmed glasses", "nostril piercing", "tibetan headgear", "sikh headgear", "muslim hat", "skullcap", "muslim skullhat", "long hair", "salt and pepper", "blonde", "headphones", "earphones", "visor hat", "headband", "cat headband", "rabbit headband", "afro", "curly curls", "facial mask", "face paint", "warpaint", "unipaint", "maked-up", "bush headgear", "soldier helmet", "buddhahead", "game-night drink", "cig", "tobacco", "spliff", "straw", "british army guard headgear", "police helmet", "police mask", "hanja mask", "java mask", "african continent mask", "feather", "chef hat", "indian chief headgear", "black paint", "hijab", "baseball cap", "trucker hat", "snapback", "fitted cap", "beanie", "knit cap", "wool hat", "ski cap", "fedora", "trilby", "panama hat", "straw hat", "cowboy hat", "stetson", "ten gallon hat", "top hat", "bowler hat", "derby hat", "newsboy cap", "flat cap", "beret", "headband", "sweatband", "bandana", "do-rag", "visor", "sun visor", "bucket hat", "ushanka", "deerstalker", "sombrero", "cloche hat", "fascinator", "pillbox hat", "sunglasses", "aviators", "wayfarers", "ski goggles", "swim goggles", "safety goggles", "welding mask", "snorkel mask", "scuba mask", "ski mask", "balaclava", "neck gaiter", "face shield", "surgical mask", "n95 respirator", "dust mask", "bicycle helmet", "motorcycle helmet", "skateboard helmet", "equestrian helmet", "football helmet", "hockey helmet", "baseball helmet", "lacrosse helmet", "rock climbing helmet", "construction hard hat", "miner's helmet", "firefighter helmet", "combat helmet", "kevlar helmet", "ballistic helmet", "ops-core helmet", "bump helmet", "pasgt helmet", "ach helmet", "mich helmet", "boonie hat", "patrol cap", "garrison cap", "field cap", "pilot helmet", "tank crewman helmet", "riot helmet", "bomb disposal helmet", "gas mask", "respirator", "night vision goggles", "thermal goggles", "tactical headset", "comms headset", "iron helmet", "steel helmet", "bronze helm", "great helm", "bascinet", "sallet", "barbute", "kettle hat", "burgonet", "morion", "armet", "chainmail coif", "leather cap", "horned helm", "winged helm", "crown", "royal crown", "silver circlet", "gold diadem", "jeweled tiara", "hood", "cowl", "monk's hood", "wizard's hat", "pointed wizard hat", "witch's hat", "jester's cap", "ranger's hood", "assassin's hood", "combat visor", "hud glasses", "ar headset", "vr helmet", "cyber goggles", "neural interface", "chrome helmet", "power armor helmet", "space helmet", "environmental hood", "oxygen mask", "breathing apparatus", "exosuit helmet", "mecha pilot helmet", "stealth hood", "cybernetic eye", "scrap helmet", "raider helmet", "welder's mask", "hockey mask", "bandit mask", "skull mask", "patched cap", "wasteland goggles", "leather hood", "samurai kabuto", "ashigaru helmet", "ninja hood", "viking horned helm", "spartan helmet", "centurion helm", "gladiator helmet", "pirate tricorne", "pirate bandana", "feathered headdress", "war bonnet", "turban", "keffiyeh", "shemagh", "fez", "yarmulke", "biretta", "mitre", "crown of thorns", "laurel wreath", "antler crown", "demon mask", "skull crown", "phantom mask", "plague doctor mask", "hannya mask", "oni mask", "kitsune mask", "carnival mask", "venetian mask", "halloween mask", "alien mask", "tiki mask"]
            head= random.sample(headgear, 1)
            print(head)
            print("torso:")
            torsogear = ["knight armor", "police armor", "samurai armor", "karate uniform", "police uniform", "soldier uniform", "korean robe", "japanese robe", "barong", "polo", "shirt", "black shirt", "sweater", "tanktop", "backpack", "slingbag", "none", "chest hair", "kevlar", "press vest", "bush gear", "hoodie", "white hoodie", "blue hoodie", "tight shirt", "nikes", "puma", "adidas", "coca-cola retro shirt", "rasta shirt", "sash", "soccer uniform", "american football armor", "football shirt", "soccer shirt", "referee shirt", "pacemaker", "bra", "bikini", "chest bag", "tuxedo", "suit", "bowtie", "tie", "apron", "chef uniform", "red paint", "black paint", "astronaut suit", "diving suit", "rashguard", "jersey", "bathrobe", "farmer gear", "lanyard", "muslim clothing", "sikh clothing", "tourguide uniform", "boyscout uniform", "girlscout uniform", "black sweater", "scarf", "shawl", "green hoodie", "pink hoodie", "jacket", "windbreaker", "varsity jacket", "jock jacket", "vest", "coat", "t-shirt", "tank top", "polo shirt", "button-up shirt", "dress shirt", "flannel shirt", "henley shirt", "v-neck shirt", "crew neck shirt", "long-sleeve shirt", "sweater", "cardigan", "hoodie", "pullover", "sweatshirt", "vest", "waistcoat", "leather jacket", "denim jacket", "bomber jacket", "trench coat", "raincoat", "parka", "windbreaker", "peacoat", "blazer", "suit jacket", "tuxedo", "duster coat", "overcoat", "puffer jacket", "fleece jacket", "field jacket", "lab coat", "chef coat", "nurse scrubs", "doctor's coat", "uniform shirt", "police uniform", "fireman jacket", "ranger jacket", "bulletproof vest", "kevlar vest", "plate carrier", "tactical vest", "bandolier", "chest rig", "military fatigues", "camo jacket", "flak jacket", "battle dress uniform", "combat shirt", "assault vest", "load bearing vest", "war belt", "ammo vest", "chainmail hauberk", "plate mail", "breastplate", "cuirass", "leather armor", "studded leather", "ringmail", "scale mail", "splint mail", "lamellar armor", "gambeson", "padded armor", "cloth robe", "mage robe", "silk robe", "monk robe", "priest robe", "royal cloak", "noble doublet", "peasant tunic", "linen shirt", "woolen jerkin", "wizard cloak", "fur cloak", "ranger cloak", "hooded cloak", "silken vestments", "embroidered tabard", "knight's surcoat", "heraldic tabard", "powered armor", "exosuit", "space suit", "environmental suit", "vacuum suit", "reflective armor", "nanofiber suit", "combat exoskeleton", "mech pilot suit", "cyber jacket", "chrome chestplate", "energy shield vest", "stealth suit", "cloaking suit", "hardsuit", "plasma armor", "patched jacket", "raider chest plate", "scrap armor", "hazmat suit", "radiation suit", "biker jacket", "spiked jacket", "leather duster", "wastelander vest", "samurai do", "ninja gi", "viking hauberk", "pirate coat", "captain's coat", "gladiator harness", "centurion cuirass", "dragonscale armor", "mithril shirt", "adamantine breastplate", "kimono", "yukata", "haori", "toga", "tunic", "royal robes", "ceremonial garb", "demon armor", "bone armor", "skull cuirass", "obsidian armor", "crystal mail", "starmetal plate"]
            torso= random.sample(torsogear, 1)
            print(torso)
            print("hand:")
            handgear = ["sword", "samurai", "club", "knife", "machete", "ice cream", "food", "coffee", "pizza", "camera", "gun", "staff", "ruler", "katana", "arnis", "nunchucks", "cat", "tablet", "phone", "iphone", "android", "fruitshake", "vape", "bong", "spliff", "joint", "beer", "champagne", "chainsaw", "folder", "testpaper", "pen", "macbook", "laptop", "linux computer", "pencil", "paintbrush", "tire pump", "fire extinguisher", "measuring device", "scalpel", "diamond cutter", "diamond", "diamonds", "trash", "water", "none", "empty-hand", "spraypaint", "smartwatch", "dynamite", "c4", "whisker", "whiskey", "liquor", "flask", "leaf", "feather", "book", "novel", "junkfood", "rifle", "sniper", "handgun", "laser", "keys", "guitar", "electric guitar", "classical guitar", "ukulele", "keyboard", "burger", "twig", "plank", "paddel", "coins", "money", "dollar bills", "fruit", "vegetable", "ps4 controller", "xbox controller", "ipod", "yarn", "spear", "bow", "work gloves", "leather gloves", "driving gloves", "winter gloves", "boxing gloves", "mma gloves", "baseball mitt", "catcher's mitt", "gardening gloves", "rubber gloves", "surgical gloves", "ski gloves", "snowboard gloves", "fingerless gloves", "evening gloves", "opera gloves", "combat gloves", "tactical gloves", "nomex gloves", "kevlar gloves", "shooting gloves", "nbc gloves", "iron gauntlets", "steel gauntlets", "chainmail mittens", "leather bracers", "studded gauntlets", "mithril gauntlets", "dragonhide gloves", "mage gloves", "spell-casting bracers", "enchanted bracers", "wizard's gloves", "assassin's gloves", "thief's gloves", "power gauntlets", "nano-fiber gloves", "cyber gloves", "chrome gauntlets", "plasma gloves", "gravity gloves", "exoskeleton hands", "pistol", "revolver", "semi-automatic pistol", "rifle", "hunting rifle", "shotgun", "pump-action shotgun", "assault rifle", "sniper rifle", "submachine gun", "machine gun", "rocket launcher", "grenade launcher", "flamethrower", "tactical knife", "combat knife", "bowie knife", "hunting knife", "machete", "crowbar", "baseball bat", "hammer", "wrench", "screwdriver", "chainsaw", "fire axe", "pickaxe", "shovel", "flashlight", "binoculars", "radio", "walkie-talkie", "compass", "multitool", "swiss army knife", "map", "gps device", "smartphone", "tablet", "laptop", "camera", "first aid kit", "bandage", "syringe", "stimpack", "rope", "grappling hook", "lockpick", "keycard", "longsword", "shortsword", "broadsword", "claymore", "katana", "wakizashi", "rapier", "saber", "cutlass", "scimitar", "falchion", "estoc", "dagger", "dirk", "stiletto", "great axe", "battle axe", "hand axe", "tomahawk", "mace", "morning star", "flail", "warhammer", "maul", "club", "cudgel", "staff", "quarterstaff", "spear", "pike", "halberd", "glaive", "naginata", "trident", "war scythe", "war pick", "bow", "longbow", "shortbow", "crossbow", "heavy crossbow", "hand crossbow", "recurve bow", "composite bow", "sling", "blowgun", "throwing knives", "throwing axes", "shuriken", "javelin", "shield", "buckler", "tower shield", "kite shield", "round shield", "heater shield", "pavise", "magic wand", "magic staff", "spellbook", "grimoire", "orb", "crystal ball", "holy symbol", "prayer beads", "rune stone", "wizard's tome", "scroll case", "wand of fire", "staff of healing", "torch", "lantern", "candle", "oil lamp", "whip", "chain whip", "kusarigama", "nunchaku", "tonfa", "sai", "kama", "laser pistol", "laser rifle", "plasma gun", "plasma rifle", "ion blaster", "pulse rifle", "railgun", "gauss rifle", "energy sword", "lightsaber", "vibroblade", "chainsword", "power fist", "gravity hammer", "needle gun", "emp grenade", "frag grenade", "smoke grenade", "plasma grenade", "stun baton", "shock prod", "neural disruptor"]
            hand= random.sample(handgear, 1)
            print(hand)
            print("legs:")
            leggear = ["tights", "shorts", "cycling shorts", "skirt", "bushwear", "pants", "leggings", "elephant pants", "skinny jeans", "jeans", "none", "trunks", "pants", "pants", "pants", "holster", "bruise", "slacks", "hiking pants", "karate pants", "taekwondo pants", "mma shorts", "briefs", "sleather pants", "jeans", "khakis", "cargo pants", "slacks", "dress pants", "shorts", "cargo shorts", "denim shorts", "bermuda shorts", "swim trunks", "board shorts", "leggings", "tights", "yoga pants", "sweatpants", "track pants", "joggers", "skinny jeans", "bell-bottoms", "chinos", "pajama pants", "thermal underwear", "long johns", "boxer shorts", "boxer briefs", "bdu pants", "combat trousers", "camo pants", "tactical pants", "military fatigue pants", "flight suit pants", "fatigue trousers", "ripstop pants", "chainmail leggings", "plate greaves", "leather pants", "studded leggings", "cloth pants", "breeches", "woolen trousers", "knight greaves", "mage skirt", "monk pants", "ranger leggings", "padded leg armor", "hide leggings", "mithril greaves", "dragonscale leggings", "lamellar leggings", "scale leggings", "tabard skirt", "powered leggings", "exoskeleton legs", "space suit legs", "mech leg armor", "cyber leggings", "nano-leggings", "chrome greaves", "armored greaves", "patched jeans", "biker pants", "raider leggings", "scrap greaves", "duster pants", "hazmat pants", "wasteland trousers", "samurai hakama", "ninja pants", "viking trousers", "pirate breeches", "gladiator skirt", "kilt", "toga", "sarong", "loincloth", "lederhosen"]
            legs= random.sample(leggear, 1)
            print(legs)
            print("feet:")
            feetgear = ["slippers", "hotel slippers", "shoes", "shoes", "shoes", "shoes", "boots", "beige boots", "black army boots", "nikes", "adidas", "puma", "converse", "chucks", "none", "socks", "clogs", "leather shoes", "white shoes", "skateboard", "longboard", "sneakers", "new balance", "world balance", "fluffy shoes", "fluffy slippers", "sandals", "sneakers", "running shoes", "basketball shoes", "tennis shoes", "dress shoes", "loafers", "oxfords", "derby shoes", "monk straps", "boat shoes", "moccasins", "sandals", "flip-flops", "crocs", "slippers", "espadrilles", "huaraches", "ballet flats", "high heels", "stilettos", "platform shoes", "wedges", "mary janes", "pumps", "hiking boots", "work boots", "snow boots", "rain boots", "cowboy boots", "biker boots", "combat boots", "steel-toe boots", "ski boots", "knee-high boots", "ankle boots", "chelsea boots", "ugg boots", "duck boots", "skate shoes", "soccer cleats", "football cleats", "baseball cleats", "track spikes", "climbing shoes", "wrestling shoes", "boxing boots", "cycling shoes", "golf shoes", "jungle boots", "desert boots", "arctic boots", "jump boots", "tanker boots", "airborne boots", "tactical boots", "speed lace boots", "side-zip boots", "iron boots", "steel boots", "plate sabatons", "chainmail boots", "leather boots", "studded boots", "riding boots", "knight sabatons", "mage slippers", "monk sandals", "thief's boots", "ranger boots", "dwarven boots", "elven boots", "mithril boots", "dragonhide boots", "fur-lined boots", "winged boots", "powered boots", "mag boots", "gravity boots", "jet boots", "nanofiber boots", "space boots", "environmental boots", "stealth boots", "raider boots", "scrap boots", "bandage-wrapped feet", "salvaged sneakers", "samurai geta", "ninja tabi", "viking shoes", "pirate boots", "gladiator sandals", "roman caligae", "zori", "okobo"]
            feet= random.sample(feetgear, 1)
            print(feet)
            print()
            ct = datetime.datetime.now()
            equips = "equips: "
            print(equips, head, torso, hand, legs, feet, ct)

        def rpg():
            while True:
                try:
                    number = int(input("Indicate number of (rpg) results: "))
                except ValueError:
                    print("Invalid value")
                else:
                    break
            number
            paths = ["You level up", "You level up", "You level up", "You walk in a field", "You encounter an animal", "You encounter a monster", "You encounter an enemy", "You encounter a friend", "You encounter an ally", "You enter an alley", "It is night time", "The sun just rised", "It is dawn", "It is dusk", "You enter the university", "You sit down on your computer", "You just chill", "You chill in a cafe", "You feel sleepy", "You are hungry", "You walk on", "You run straight", "You run in loops", "You are tired", "You are bullied", "You are sent to the hospital", "You go on a roadtrip", "You hike", "You mine", "You are out of money", "You just earned your salary", "You spend your time waiting", "You just nearly died", "You do your assignment", "You paint", "You hum", "You rap", "You sing", "You hear someone singing", "You compose rap", "You compose a classical track", "You feel lonely", "You feel happy", "You feel ecstatic", "You yearn for something", "You feel you should meditate", "You feel you should pray", "You walk in a church", "You walk in a temple", "You walk in a mosque", "You walk in a forest", "You walk in a jungle", "You walk along the road", "You're in the city", "You ride a bus", "You ride a cab", "You take out the trash", "You find a job", "Someone gave you work", "You worship", "You're in transit", "You surf the internet", "You got hacked", "You got scammed", "You exercise", "You were commissioned in the army", "You were commisioned in the police force", "You were commissioned in the airforce", "You were commissioned in the marines", "You have a mission", "You feel inspired", "You feel uninspired", "You feel creative block", "You feel like dancing", "You hear music", "You watch TV", "You hear the radio", "You are fatigued", "You enter war", "You meet someone", "You view film showing schedules", "You browse through courses", "You walk into a market", "You think of getting souvenirs", "You explore the place", "the sun is up", "the sun rises", "the sun blazes overhead", "the sun is setting", "the sun sinks below the horizon", "the sun peeks through clouds", "the sun is hidden", "the moon is full", "the moon is new", "the moon is a crescent", "the moon glows red", "the moon is silver", "two moons rise", "stars appear", "stars twinkle", "constellations form patterns", "the milky way spans the sky", "a shooting star falls", "a comet streaks past", "the aurora shimmers", "northern lights dance", "dawn breaks", "dusk arrives", "twilight falls", "midnight passes", "noon strikes", "morning mist lifts", "evening shadows lengthen", "an eclipse darkens the sun", "a lunar eclipse begins", "clouds gather overhead", "storm clouds roll in", "the sky darkens", "rain begins to fall", "rain patters on leaves", "rain pours down", "a downpour soaks you", "drizzle dampens the air", "thunder rumbles in the distance", "thunder cracks loudly", "lightning flashes", "lightning splits the sky", "lightning strikes a tree", "hail begins to fall", "hail pounds your shield", "snow drifts down", "snow blankets the ground", "a blizzard rages", "snowflakes melt on your skin", "icicles form on branches", "frost covers the ground", "ice crackles underfoot", "fog rolls in", "mist surrounds you", "a rainbow arcs overhead", "wind picks up", "wind howls through the trees", "a gust nearly knocks you over", "a hurricane approaches", "a tornado spins in the distance", "a sandstorm engulfs the dunes", "ash falls like snow", "embers float on the breeze", "the air grows cold", "the air turns warm", "humidity thickens", "the air feels electric", "a strange wind blows", "you walk in an alley", "you stroll down a cobbled street", "you traverse a marketplace", "you enter a tavern", "you push open the inn door", "you walk through a village square", "you cross a wooden bridge", "you cross a stone bridge", "you cross a rope bridge", "you climb a hill", "you descend a slope", "you trek through a forest", "you stand in a clearing", "you enter a cave", "you exit a dungeon", "you arrive at a castle", "you cross a drawbridge", "you stand before a temple", "you enter a chapel", "you walk through a graveyard", "you reach a lighthouse", "you find a hidden grove", "you discover ancient ruins", "you enter a throne room", "you visit the blacksmith", "you enter the library", "you walk into an alchemist shop", "you enter the stables", "you climb a tower", "you ascend a spiral staircase", "you descend into a crypt", "you walk along a beach", "you cross a desert", "you trek through a swamp", "you climb a mountain", "you reach a summit", "you ford a river", "you sail across the sea", "you board a ship", "you disembark at a port", "you enter a city", "you leave the village", "you camp under the stars", "you hide behind a tree", "you crouch in the bushes", "you walk on the plank", "you climb down a ladder", "you slide down a slope", "you swim across a lake", "you wade through a stream", "you jump over a pit", "you leap across a chasm", "you fall into a hole", "you tumble down a hill", "you sneak past guards", "you tiptoe down a corridor", "you run through the woods", "you sprint across the field", "you flee from danger", "you back away slowly", "you step forward cautiously", "you crawl through a tunnel", "you squeeze through a gap", "you push aside a curtain", "you step over a fallen log", "you balance on a beam", "you tightrope across a wire", "you ride a horse", "you mount your steed", "you dismount near a tree", "you ride a wagon", "you steer a chariot", "you pilot a small boat", "you row across a pond", "you set sail at dawn", "you anchor in a cove", "you fly on a griffon", "you ride a dragon", "you teleport to a new realm", "you fall through a portal", "you step through a gateway", "you cross a planar threshold", "you see a forest", "you spot a dragon overhead", "you see smoke rising", "you notice a strange symbol", "you see torches flickering", "you spot a figure in the shadows", "you see a glint of gold", "you notice fresh tracks", "you see a campfire", "you spot bandits ahead", "you see a merchant caravan", "you notice a hidden door", "you discover ancient runes", "you see a trapdoor", "you spot a secret passage", "you see footprints in the snow", "you notice claw marks on a tree", "you see broken branches", "you spot an arrow embedded in a wall", "you see blood on the ground", "you notice a pile of bones", "you spot a corpse", "you see a skull on a stake", "you spot a watchtower", "you see a windmill", "you spot a farmhouse", "you see a herd of deer", "you spot a wolf pack", "you see a flock of crows", "you spot an eagle circling", "you see a snake slithering", "you spot rats scurrying", "you see a black cat", "you spot a white owl", "you see a unicorn", "you glimpse a phoenix", "you spot a centaur", "you see a mermaid", "you glimpse a fairy", "you spot a goblin", "you see a troll", "you spot an ogre", "you see a giant", "you spot a kobold", "you see a skeleton", "you spot a zombie", "you see a ghost", "you spot a wraith", "you see a vampire", "you spot a werewolf", "you draw your sword", "you nock an arrow", "you ready your shield", "you raise your axe", "you grip your dagger", "you brandish your staff", "you wield a hammer", "you swing your sword", "you slash an enemy", "you stab a goblin", "you parry an attack", "you block a strike", "you dodge an arrow", "you sidestep a blow", "you roll out of harm's way", "you counter the attack", "you riposte", "you feint left", "you strike a critical blow", "you land a heavy hit", "you miss your target", "your weapon breaks", "your shield shatters", "your armor dents", "you lose your footing", "you fall to one knee", "you rise to your feet", "you charge into battle", "you retreat to safety", "you flank the enemy", "you ambush the bandits", "you set a trap", "you trigger a snare", "you fall into a pit", "you spring from cover", "you fire an arrow", "you loose a volley", "you reload your crossbow", "you toss a knife", "you hurl a javelin", "you sling a stone", "you throw a bomb", "you light a fuse", "you cast a spell", "you summon a familiar", "you conjure a fireball", "you cast lightning bolt", "you cast frost ray", "you cast healing", "you cast shield", "you cast invisibility", "you cast haste", "you cast slow", "you cast fear", "you cast charm", "you cast sleep", "you cast dispel", "you channel mana", "you exhaust your magic", "you tap into dark energy", "you bless your weapon", "you imbue your blade", "you sharpen your sword", "an orc charges at you", "a goblin throws a knife", "a bandit attacks", "a wolf lunges", "a bear roars", "a dragon breathes fire", "a wizard casts a spell", "an archer fires", "a knight charges", "a giant swings a club", "a skeleton raises a sword", "a zombie shambles forward", "a ghost wails", "a vampire bares its fangs", "a werewolf howls", "you are wounded", "you bleed heavily", "you stagger from a blow", "you fall unconscious", "you collapse", "you die", "you respawn", "you rise from the dead", "you are revived", "you slay your enemy", "you behead a goblin", "you defeat the boss", "you triumph in battle", "you spare your enemy", "you take a prisoner", "you interrogate a captive", "you torture a foe", "you free a hostage", "you find a gold coin", "you discover a treasure chest", "you pick up a healing potion", "you grab a torch", "you find a magic ring", "you uncover a jeweled crown", "you find an ancient scroll", "you discover a spellbook", "you pick up a key", "you find a map", "you grab a lantern", "you find a flask of oil", "you discover a vial of poison", "you find an antidote", "you pick up a magic wand", "you discover a staff of power", "you find an enchanted bow", "you uncover a cursed amulet", "you find a holy symbol", "you discover a relic", "you find ancient bones", "you uncover a skull", "you find a journal", "you discover a letter", "you find a love note", "you discover a contract", "you find a will", "you uncover a treasure map", "you find a deed", "you discover a recipe", "you find a poem", "you uncover a song", "you find a riddle", "you discover a cipher", "you uncover a gemstone", "you find a ruby", "you discover an emerald", "you find a sapphire", "you uncover a diamond", "you find a pearl", "you discover an opal", "you find an obsidian shard", "you uncover crystal shards", "you find holy water", "you discover an elixir", "you find a stamina draught", "you uncover a mana potion", "you find a strength elixir", "you discover an invisibility potion", "you find a fire resistance potion", "you uncover a frost ward", "you find a charm of protection", "you discover a talisman", "you find a ward against undead", "you level up", "you gain experience", "your health is low", "your mana is depleted", "your stamina runs out", "you become poisoned", "you are paralyzed", "you are blinded", "you are deafened", "you are silenced", "you are cursed", "you are blessed", "you are charmed", "you fall asleep", "you wake up", "you regain consciousness", "you feel rejuvenated", "you are exhausted", "you grow weak", "you grow strong", "you feel hungry", "you feel thirsty", "you eat a meal", "you drink water", "you rest by a fire", "you sleep in an inn", "you sleep in the wilderness", "you have a nightmare", "you have a vision", "you receive a prophecy", "you gain a new ability", "you learn a new spell", "you master a skill", "you forget a spell", "you lose a memory", "your alignment shifts", "your reputation grows", "your reputation suffers", "you become infamous", "you become a hero", "you become a villain", "you become an outlaw", "you become noble", "a stranger approaches", "a beggar asks for coin", "a knight offers help", "a priest blesses you", "a witch curses you", "a child runs past", "a bard sings a tale", "a thief slips away", "a guard challenges you", "a merchant haggles", "an innkeeper greets you", "a barmaid serves ale", "a stableboy tends horses", "a smithy hammers metal", "a fisherman casts a net", "a farmer tills the field", "a hunter tracks game", "a sailor sings a shanty", "a soldier marches by", "a queen welcomes you", "a king summons you", "a princess pleads for help", "a prince offers a quest", "a noble dines lavishly", "a peasant complains", "a wizard mutters incantations", "a sorcerer reveals a secret", "an oracle speaks in riddles", "a seer foresees doom", "a healer tends wounds", "a monk meditates", "a cultist chants", "a heretic preaches", "a paladin patrols", "an assassin watches", "a spy slips away", "a noble bows", "a guard salutes", "a child laughs", "a woman weeps", "a man shouts", "a crowd gathers", "a mob forms", "rioters fill the streets", "soldiers march in formation", "monks chant in unison", "the king dies", "the queen mourns", "an heir is born", "a wedding takes place", "a funeral procession passes", "a coronation begins", "a tournament is announced", "a duel is challenged", "a treaty is signed", "war is declared", "peace is brokered", "wolves howl in the night", "bells ring in the distance", "you hear a scream", "footsteps echo behind you", "drums beat in the dark", "horns sound the alarm", "trumpets herald arrival", "a baby cries", "a horse whinnies", "a dog barks", "a cat purrs", "a rooster crows", "owls hoot", "crickets chirp", "bees buzz", "birds sing at dawn", "ravens caw ominously", "a flute plays softly", "a lute strums", "drums beat war rhythms", "a chant rises", "a hymn echoes", "you hear whispers", "you hear distant chanting", "you hear breathing behind you", "you hear a sword unsheath", "you hear a bowstring twang", "you hear a door creak", "you hear glass shatter", "you hear water dripping", "you hear a heart beating", "you hear footsteps approaching", "you hear running water", "you hear waves crashing", "thunder rolls", "lightning cracks", "wind whistles through cracks", "fire crackles", "wood pops in the fire", "metal clangs against metal", "stone grinds on stone", "the earth rumbles", "rocks fall from above", "trees creak in the wind", "leaves rustle", "grass sways", "water laps the shore", "ice cracks under foot", "snow crunches underfoot", "you hear nothing at all", "the king summons you to court", "a quest is offered", "the prophecy is revealed", "you complete the mission", "you receive a reward", "you are knighted", "you are exiled", "you are imprisoned", "you escape captivity", "you are pardoned", "you swear an oath", "you break a vow", "you betray a friend", "you save a life", "you start a revolution", "you end a war", "you assassinate a tyrant", "you defeat a dark lord", "you slay a dragon", "you free the kingdom", "you steal a crown", "you crown yourself king", "you marry royalty", "you found a guild", "you build a fortress", "you commission a temple", "you fund an orphanage", "you broker peace", "you negotiate a truce", "you challenge a champion", "you accept a duel", "you decline an offer", "you find your destiny", "you fulfill a prophecy", "you defy fate", "you change history", "you forge an alliance", "you betray an ally", "you uncover a conspiracy", "you expose a traitor", "you rescue a captive", "you escort a caravan", "you guard a noble", "you slay an assassin", "you save a village", "you destroy a stronghold", "you raid a camp", "you sack a city", "you defend a wall", "you breach a gate", "a portal opens", "a rift tears reality", "a wizard appears", "a demon manifests", "an angel descends", "a god speaks", "a goddess blesses you", "a spirit guides you", "a ghost haunts the halls", "a poltergeist throws objects", "a banshee shrieks", "a lich rises", "a phylactery glows", "a soul is captured", "a soul is freed", "a curse is broken", "a curse takes hold", "a hex is cast", "a ritual begins", "a sacrifice is made", "blood is offered", "a pact is sealed", "a contract is signed in blood", "a familiar appears", "an imp giggles", "a dragon awakens", "an elemental forms", "a golem stomps forward", "a homunculus is created", "a chimera attacks", "a hydra grows a head", "a basilisk turns stone", "a medusa stares", "a kraken surfaces", "a leviathan rises", "a phoenix is reborn", "a unicorn emerges", "a pegasus flies past", "a manticore roars", "a sphinx asks a riddle", "a minotaur charges", "a cyclops throws a boulder", "a gorgon hisses", "a chimera breathes fire", "a banshee wails", "a wraith drifts past", "a specter forms", "a poltergeist rattles chains", "a doppelganger mimics you", "a shapeshifter transforms", "you forge a sword", "you craft armor", "you brew a potion", "you enchant a weapon", "you inscribe a scroll", "you carve a rune", "you weave a cloak", "you tan a hide", "you skin a deer", "you cook a meal", "you bake bread", "you ferment ale", "you distill liquor", "you grind herbs", "you blend spices", "you sharpen a blade", "you polish armor", "you string a bow", "you fletch arrows", "you mold leather", "you cobble shoes", "you sew clothes", "you mend a tear", "you patch a hole", "you sell goods", "you buy supplies", "you barter for food", "you negotiate a price", "you haggle with a merchant", "you steal an item", "you pickpocket a noble", "you cheat at dice", "you win a wager", "you lose a bet", "you gamble away gold", "you sing for coin", "you dance in the streets", "you tell a story", "you share a tale", "you spread a rumor", "you bow to royalty", "you curtsy politely", "you nod in greeting", "you wave farewell", "you embrace a friend", "you kiss a lover", "you slap a rival", "you punch a foe", "you spit at a coward", "you laugh heartily", "you cry softly", "you sob uncontrollably", "you grin wickedly", "you smile warmly", "you frown deeply", "you scowl in anger", "you sigh wearily", "you yawn", "you stretch", "you shudder", "you tremble", "you wink playfully", "you flirt with a barmaid", "you proposition a noble", "you reject an advance", "you accept a kiss", "you propose marriage", "you accept a proposal", "you decline an offer of love", "you toast to victory", "you raise a glass", "you drink to fallen friends", "you sing a song", "you play a tune", "you recite a poem", "you tell a joke", "you laugh at a jest", "you mock a fool", "you praise a hero", "you criticize a leader", "you whisper a secret", "you eavesdrop on a conversation", "you spread gossip", "you confess a sin", "you seek absolution", "you forgive an enemy", "you hold a grudge", "you swear vengeance", "smoke billows from a chimney", "incense burns in a temple", "candles flicker", "a bonfire roars", "embers glow", "ashes settle", "a forge burns hot", "lava bubbles", "a geyser erupts", "a volcano rumbles", "an earthquake shakes the ground", "a tsunami approaches", "a flood rises", "a landslide falls", "an avalanche descends", "a sinkhole opens", "a crevasse splits", "the ground gives way", "a tree falls", "a branch snaps", "leaves fall from trees", "petals drift through the air", "pollen dusts the ground", "spores float by", "mushrooms glow in the dark", "moss covers stones", "vines crawl up walls", "ivy strangles a tree", "weeds break through cobbles", "grass sprouts in cracks", "flowers bloom in spring", "leaves change color", "trees lose their leaves", "snow melts", "ice thaws", "rivers flow free", "streams babble", "waterfalls cascade", "rapids surge", "whirlpools spin", "waves crash on the shore", "tides pull back", "tides rise", "the moon affects the seas", "stars guide your way", "the north star shines bright", "the wind changes direction", "a draft sweeps the room", "dust motes float in light", "cobwebs hang from beams", "rats scurry in walls", "spiders spin webs", "snakes slither in the grass", "lizards bask on rocks", "frogs croak by the pond", "fireflies blink at dusk", "mosquitoes buzz around", "a riddle is posed", "a puzzle confronts you", "a code must be cracked", "a cipher is revealed", "a clue is found", "a hint is offered", "a mystery deepens", "a secret is revealed", "a lie is exposed", "the truth comes out", "a witness speaks", "an alibi crumbles", "a confession is made", "a body is found", "blood splatters the floor", "a murder is committed", "a crime is solved", "a thief is caught", "a murderer confesses", "a traitor is unmasked", "a spy is exposed", "a plot is foiled", "an assassination is prevented", "a kidnapping is thwarted", "a hostage is freed", "you make camp", "you build a fire", "you set up a tent", "you unpack supplies", "you cook a stew", "you roast game", "you forage for berries", "you fish in a stream", "you hunt deer", "you trap rabbits", "you milk a cow", "you feed your horse", "you water your steed", "you brush your horse", "you saddle up", "you check your gear", "you sharpen your weapons", "you patch your armor", "you bind your wounds", "you apply a poultice", "you stitch a cut", "you set a broken bone", "you treat a fever", "you cure a disease", "you fight off infection", "you cleanse a wound", "you boil water", "you purify drinking water", "you pack your bedroll", "you stow your belongings", "you pack your saddlebags", "you load your wagon", "you set off at dawn", "you travel through the night", "you reach a crossroads", "you choose a path", "you take the high road", "you take the low road", "you wander off the path", "you become lost", "you find your way", "you read a signpost", "you consult a map", "you check a compass", "you follow the stars", "you trust your instincts", "you light a torch in the dark", "you carry a lantern", "you check for traps", "you disarm a snare", "you trigger a tripwire", "spikes shoot from walls", "a boulder rolls toward you", "darts fire from holes", "a pit yawns open", "a wall slides aside", "a hidden door reveals itself", "a chest creaks open", "the lid swings shut", "a lock clicks", "a key turns", "a mechanism whirs", "gears grind", "a portcullis drops", "a gate slams shut", "a bridge collapses", "stairs spiral downward", "tunnels branch endlessly", "passages narrow", "ceilings lower", "walls close in", "the air grows stale", "water seeps through walls", "dripping echoes", "shadows dance on walls", "shapes shift in darkness", "eyes gleam in the gloom", "growls echo from depths", "claws scrape stone", "wings flap in shadow", "a festival begins", "fireworks light the sky", "lanterns float skyward", "a parade marches through", "a feast is laid out", "wine flows freely", "a toast is raised", "music fills the air", "dancers twirl", "minstrels play", "jesters joke", "fools entertain", "acrobats tumble", "fire eaters perform", "magicians astound", "puppeteers tell tales", "a play unfolds", "an opera begins", "a procession winds through streets", "a coronation is held", "a wedding ceremony begins", "vows are exchanged", "rings are given", "a kiss seals the union", "guests cheer", "a funeral procession moves slowly", "mourners weep", "a eulogy is delivered", "a body is burned", "a body is buried", "a tomb is sealed", "an urn is placed", "a grave is dug", "headstones stand silent", "a memorial is built", "a poison dart strikes", "a wave of acid sweeps over you", "a fireball explodes", "an icy blast freezes", "lightning arcs between targets", "a wave of necrotic energy hits", "a holy aura burns the undead", "a curse drains your soul", "a beam of light pierces the dark", "a wall of fire blocks your path", "a wall of ice forms", "a wall of stone rises", "a wall of force shimmers", "a portal sucks you in", "a vortex pulls everything", "a void opens beneath you", "gravity reverses", "you float in zero gravity", "you fall upward", "you fall down", "you crash into rocks", "you splash into water", "you sink to the bottom", "you swim to the surface", "you gasp for air", "you cough up water", "you pull yourself ashore", "a comet portends doom", "a prophecy comes true", "the chosen one is revealed", "the sword is pulled from the stone", "the seal is broken", "the gate is opened", "the ancient evil awakens", "the world is saved", "the world ends", "a new age begins", "an empire falls", "a republic rises", "a kingdom unites", "lands are divided", "borders shift", "maps are redrawn", "history is rewritten", "legends are born", "myths take form", "gods walk the earth", "demons invade", "the dead rise", "the living fall", "darkness covers the land", "light returns", "balance is restored", "chaos reigns", "order prevails", "love conquers all", "hate consumes hearts", "fear grips the populace", "hope blooms anew", "courage stirs", "wisdom is gained", "knowledge spreads", "ignorance fades", "you spot treasure on the floor", "you find a glowing crystal", "you stumble upon a magical orb", "you discover a leyline", "you sense a disturbance in the magic", "you feel watched", "you sense danger nearby", "you feel a chill down your spine", "your hair stands on end", "your blood runs cold", "your heart races", "your hands tremble", "your breath catches", "your legs grow weak", "your stomach knots", "your mind goes blank", "your vision blurs", "your ears ring", "you smell smoke", "you smell blood", "you smell sulfur", "you smell roses", "you smell decay", "you smell incense", "you taste copper in your mouth", "you taste salt on the wind", "you feel the ground shake", "you feel a presence", "you feel cold steel against your throat", "you feel a gust of wind", "you feel rain on your face", "you feel snow on your skin", "you feel sand between your toes", "you feel mud squelch underfoot", "a voice whispers your name", "a shadow follows you", "an unseen force pushes you", "the air grows thin", "the floor tilts", "the walls seem to breathe", "the ceiling drips blood", "candles snuff out one by one", "all sound disappears", "time slows to a crawl", "time speeds up", "you experience deja vu", "you remember a past life", "you forget who you are", "you discover your true name", "you uncover your heritage", "you meet your father", "you confront your mother", "you find a bow on the ground", "you spot a quiver of arrows", "you discover a forgotten armory", "you find dusty tomes", "you uncover a hidden cache", "you find a war banner", "you discover a battle standard", "you find a knight's grave", "you uncover a champion's tomb", "you find an ancient battlefield", "you stumble on a ritual circle", "you find a summoning altar", "you discover a sacrificial slab", "you find chains in a dungeon", "you uncover instruments of torture", "you find a prisoner in chains", "you free a captive from a cell", "you cut a noose", "you save someone from drowning", "you pull a child from a fire", "you carry an injured ally", "you bandage a wound", "you splint a broken arm", "you craft a stretcher", "you administer last rites", "you whisper a prayer", "you light a candle in remembrance", "you place flowers on a grave", "you say goodbye to a friend", "you bury the dead", "you scatter ashes to the wind", "you build a cairn", "you mark the spot", "you carve a name in stone", "you write in a journal", "you draft a letter", "you seal a missive", "you send a raven", "you receive a message", "you read a proclamation", "you announce news", "you spread the word", "you ring the bell", "you sound the horn", "you raise the alarm", "you call for aid", "you signal allies", "you light a beacon", "you wave a flag", "you lower the flag", "you brew tea", "you smoke a pipe", "you chew on jerky", "you suck on a hard candy", "you eat a hearty stew", "you drink mulled wine", "you sip honey mead", "you taste fine wine", "you gulp down water", "you bite an apple", "you peel an orange", "you slice cheese", "you tear bread", "you crack a nut", "you spit out a pit", "you wash dishes", "you scrub a floor", "you sweep ashes from a hearth", "you tend a garden", "you plant seeds", "you harvest crops", "you milk a goat", "you shear a sheep", "you collect eggs", "you slaughter livestock", "you butcher meat", "you cure ham", "you smoke fish", "you preserve fruit", "you store grain", "you stockpile supplies", "you ration food", "you trade with locals", "you tip a servant", "you bribe a guard", "you offer a gift", "you accept a present", "you refuse a token", "you decline a favor", "you owe a debt", "you pay your dues", "you settle a score", "you make amends", "you seek redemption", "you find peace", "you face your fears", "you conquer your demons", "you embrace your fate", "you choose your path", "the adventure continues"]
            path = random.choices(paths, k=number)
            ct = datetime.datetime.now()
            rpg = "rpg: "
            print(rpg, path, ct)
            time.sleep(3)

        def archery():
            time.sleep(2)
            print()
            print("You aim your bow..")
            time.sleep(2)
            print("You hit:")
            num = (round(random.random()*30,3))
            print(num)
            print("centimeters from the bullseye with")
            raditn = (random.randint(50,100))
            print(raditn)
            ct = datetime.datetime.now()
            print("percent accuracy", ct)
            archery = "archery: "
            time.sleep(3)

        def color_key():
            time.sleep(1)
            color = ["red", "crimson", "maroon", "scarlet", "orange", "amber", "rust", "salmon", "green", "emerald", "lime", "olive", "yellow", "gold", "lemon", "mustard", "blue", "azure", "indigo", "teal", "purple", "lavender", "magenta", "violet", "brown", "beige", "chocolate", "sienna", "gray", "charcoal", "silver", "slate", "black", "ebony", "jet", "onyx", "white", "alabaster", "ivory", "pearl", "pink", "sky blue", "neon green", "neon yellow", "neon orange", "neon blue"]
            colors = random.sample(color, 5)
            ct = datetime.datetime.now()
            colorkey = "color key: "
            print(colorkey, colors, ct)

        def magic():
            opp = "OPPONENT"
            print(opp)
            print()
            deck1 = ["Forest", "Forest", "Forest", "Forest", "Forest", "Forest", "Forest", "Forest", "Forest", "Forest", "Forest", "Forest", "Forest", "Island", "Island", "Island", "Island", "Island", "Island", "Island", "Island", "Island", "Island", "Island", "Island", "Joint Assault (Spell, 1 Forest)", "Joint Assault (Spell, 1 Forest)", "Ice Cage (Spell, 1 Land and 1 Island)", "Lair Delve (Spell, 2 Land and 1 Forest)", "Lair Delve (Spell, 2 Land and 1 Forest)", "Overrun (Spell, 2 Land and 3 Forest)", "Llanowar Elves (Creature, 1 Forest)", "Llanowar Elves (Creature, 1 Forest)", "Nephalia Smuggler (Creature, 1 Island)", "Wingcrafter (Creature, 1 Island)", "Wingcrafter (Creature, 1 Island)", "Runeclaw Bear (Creature, 1 Land and 1 Forest)", "Nightshade Peddler (Creature, 1 Land and 1 Forest)", "Nightshade Peddler (Creature, 1 Land and 1 Forest)", "Tandem Lookout (Creature, 2 Land and 1 Island)", "Tandem Lookout (Creature, 2 Land and 1 Island)", "Trusted Forcemage (2 Land and 1 Forest)", "Trusted Forcemage (Creature, 2 Land and 1 Forest)", "Trusted Forcemage (Creature, 2 Land and 1 Forest)", "Latch Seeker (Creature, 1 Land and 2 Island)", "Latch Seeker (Creature, 1 Land and 2 Island)", "Wolfir Avenger (Creature, 1 Land and 2 Forest", "Druid's Familiar (Creature, 3 Land and 1 Forest)", "Druid's Familiar (Creature, 3 Land and 1 Forest)", "Elgaud Shieldmate (Creature, 3 Land and 1 Island)", "Elgaud Shieldmate (Creature, 3 Land and 1 Island)", "Flowering Lumberknot (Creature, 3 Land and 1 Forest)", "Flowering Lumberknot (Creature, 3 Land and 1 Forest)", "Geist Trapper (Creature, 4 Land and 1 Forest)", "Acidic Slime (Creature, 3 Land and 2 Forest)", "Wolfir Silverheart (Creature, 3 Land and 2 Forest)", "Vorstclaw (Creature, 4 Land and 2 Forest)", "Vorstclaw (Creature, 4 Land and 2 Forest)", "Deadeye Navigator (Creature, 4 Land and 2 Island)", "Pathbreaker Wurm (Creature, 4 Land and 2 Forest)"]
            hand1 = random.sample(deck1, 1)
            hand2 = random.sample(deck1, 1)
            hand3 = random.sample(deck1, 1)
            hand4 = random.sample(deck1, 1)
            hand5 = random.sample(deck1, 1)
            hand6 = random.sample(deck1, 1)
            hand7 = random.sample(deck1, 1)
            next1 = random.sample(deck1, 10)
            hand = "Hand:"
            print(hand)
            print(hand1)
            print(hand2)
            print(hand3)
            print(hand4)
            print(hand5)
            print(hand6)
            print(hand7)
            print()
            nexto = "Next on deck:"
            print(nexto)
            print(next1)
            print()
            fromb = "-from Bound by Strength deck"
            print(fromb)
            print()
            you = "YOU"
            print(you)
            print()
            deck2 = ["Evolving Wilds", "Forest", "Forest", "Forest", "Forest", "Forest", "Forest", "Forest", "Plains", "Plains", "Plains", "Plains", "Plains", "Plains", "Plains", "Plains","Plains", "Plains", "Plains", "Plains", "Plains", "Plains", "Plains", "Tranquil Expanse", "Immolating Glare (Spell, 1 Land and 1 Plain)", "Lead by Example (Spell, 1 Land and 1 Forest)", "Lead by Example (Spell, 1 Land and 1 Forest)", "Mighty Leap (Spell, 1 Land and 1 Plain)", "Shoulder to Shoulder (Spell, 2 Land and 1 Plain)", "Shoulder to Shoulder (Spell, 2 Land and 1 Plain)", "Isolation Zone (Spell, 2 Land and 2 Plain)", "Isolation Zone (Spell, 2 Land and 2 Plain)", "Iona's Blessing (Spell, 3 Land and 3 Plain)", "Allied Reinforcements (Spell, 3 Land and 3 Plain)", "Expedition Envoy (Creature, 1 Plain)", "Expedition Envoy (Creature, 1 Plain)", "Kitesail Scout (Creature, 1 Plain)", "Kitesail Scout (Creature, 1 Plain)", "Cliffside Lookout (Creature, 1 Plain)","Cliffside Lookout (Creature, 1 Plain)", "Oran-Rief Invoker (Creature, 1 Land and 1 Forest)", "Makindi Aeronaut (Creature, 1 Land and 1 Plain)", "Makindi Aeronaut (Creature, 1 Land and 1 Plain)", "Kor Castigator (Creature, 1 Land and 1 Plain)", "Kor Castigator (Creature, 1 Land and 1 Plain)", "Joraga Auxiliary (Creature, 1 Land and 1 Forest and 1 Plain)", "Joraga Auxiliary (Creature, 1 Land and 1 Forest and 1 Plain)", "Veteran Warleader (Creature, 1 Land and 1 Forest and 1 Plain)", "Shadow Glider (Creature, 2 Land and 1 Plain)", "Shadow Glider (Creature, 2 Land and 1 Plain)", "Kor Sky Climber (Creature, 2 Land and 1 Plain)", "Kor Sky Climber (Creature, 2 Land and 1 Plain)", "Relief Captain (Creature, 2 Land and 2 Plain)", "Relief Captain (Creature, 2 Land and 2 Plain)", "Saddleback Lagac (Creature, 3 Land and 1 Forest)", "Expedition Raptor (Creature, 3 Land and 2 Plain)", "Expedition Raptor (Creature, 3 Land and 2 Plain)", "Steppe Glider (Creature, 4 Land and 1 Plain)", "Angel of Renewal (Creature, 5 Land and 1 Plain)", "Gladeheart Cavalry (Creature, 5 Land and 2 Forest)"]
            hand21 = random.sample(deck2, 1)
            hand22 = random.sample(deck2, 1)
            hand23 = random.sample(deck2, 1)
            hand24 = random.sample(deck2, 1)
            hand25 = random.sample(deck2, 1)
            hand26 = random.sample(deck2, 1)
            hand27 = random.sample(deck2, 1)
            next2 = random.sample(deck2, 10)
            print(hand)
            print(hand21)
            print(hand22)
            print(hand23)
            print(hand24)
            print(hand25)
            print(hand26)
            print(hand27)
            print()
            print(nexto)
            print(next2)
            print()
            fromc = "-from Concerted Effort deck"
            print(fromc)
            print()
            turn = ["First turn is yours", "Opponent is first turn"]
            turnt = random.sample(turn, 1)
            ct = datetime.datetime.now()
            print(turnt, ct)
            magic = "magic:"

        def football():
            football = ["touchdown", "touchdown", "touchdown", "first down", "first down", "first down", "first down", "second down", "second down", "second down", "third down", "the path is clear", "the path is clear", "the path is clear", "the path is clear", "the path is clear", "the path is clear", "the path is clear", "the path is clear", "the path is clear", "there are 3 guards ahead of you", "there are 3 guards ahead of you", "there are 3 guards ahead of you", "there are 4 guards ahead of you", "there are 2 guards ahead of you", "there are 2 guards ahead of you", "there are 2 guards ahead of you", "there is 1 guard ahead of you", "there is 1 guard ahead of you"]
            fball= random.sample(football, 1)
            ct = datetime.datetime.now()
            footballs = "football: "
            print(footballs, fball, ct)

        def mapp():
            dd = list(diction)
            while True:
                try:
                    number = int(input("Indicate number of (map) results: "))
                except ValueError:
                    print("Invalid value")
                else:
                    break
            number
            time.sleep(0)
            print()
            mapped = random.choices(dd, k=number)
            ct = datetime.datetime.now()
            mapd = "map:"
            print(mapd, mapped, ct)

        def auto_mat():
            while True:
                try:
                    number = int(input("Indicate number of processes: "))
                except ValueError:
                    print("Invalid value")
                else:
                    break
            number
            numberstr = str(number)
            time.sleep(1)
            print()
            print(numberstr + "" + " " + "" + "processes will be queued...")
            time.sleep(3)
            for _ in range(number):
                print()
                time.sleep(2)
                function_list = [version, print_time, pray, climb, prayer, stats, progress, light_incense, hebrews, teletubby, legal_terms, biology, chemistry, patient_simu, earth_science, psychology, medicals, license, police, clearance, nano, entry, micasa, stuff, worship, posting, meditate, sleep, eat, find_coins, slot, draw_card, search_for_items, fly, drink_coffee, drink_tea, surf, collections, doodling, zen_melody, value, bump, ma, skate, art, radio, give_alms, brawl, karate, koans, hipster_tarot, hack, spar, train, rest, haiku, psalms, dhammapada, koran, message, souls, c, asciii, mp3, monopoly, equips, rpg, archery, color_key, magic, football, mapp, ID, IDC, fuzz, msgs, tag, atag, frames, chichars, tinie_N, kata, hangu, generate_secure_string, pr0verbs, maryjane, insta_ghost_write, n1, rhospital, MIMS, bible_verses, tsearch]
                random.choice(function_list)()
            print()
            ct = datetime.datetime.now()
            print("/processes finished!", ct)
            print()

        def ID():
            ct = datetime.datetime.now()
            ID = "ID:"
            log = "[Logged-in]"
            print(usr, ID, log, ct)

        def IDC():
            ct = datetime.datetime.now()
            IDC = "IDC:"
            log = "[Logged-out]"
            print(usr, IDC, log, ct)

        def weapon_start():
            print("Ctrl+C to stop")
            print()
            def generate_random_result():
                nano = (diction)
                letters1 = ["A", "a", "B", "b", "C", "c", "D", "d", "E", "e", "F", "f", "G", "g", "H", "h", "I", "i", "J", "j", "K", "k", "L", "l", "M", "m", "N", "n", "O", "o", "P", "p", "Q", "q", "R", "r", "S", "s", "T", "t", "U", "u", "V", "v", "W", "w", "X", "x", "Y", "y", "Z", "z"]
                letters2 = ["A", "a", "B", "b", "C", "c", "D", "d", "E", "e", "F", "f", "G", "g", "H", "h", "I", "i", "J", "j", "K", "k", "L", "l", "M", "m", "N", "n", "O", "o", "P", "p", "Q", "q", "R", "r", "S", "s", "T", "t", "U", "u", "V", "v", "W", "w", "X", "x", "Y", "y", "Z", "z"]
                letters3 = ["A", "a", "B", "b", "C", "c", "D", "d", "E", "e", "F", "f", "G", "g", "H", "h", "I", "i", "J", "j", "K", "k", "L", "l", "M", "m", "N", "n", "O", "o", "P", "p", "Q", "q", "R", "r", "S", "s", "T", "t", "U", "u", "V", "v", "W", "w", "X", "x", "Y", "y", "Z", "z"]
                letters4 = ["A", "a", "B", "b", "C", "c", "D", "d", "E", "e", "F", "f", "G", "g", "H", "h", "I", "i", "J", "j", "K", "k", "L", "l", "M", "m", "N", "n", "O", "o", "P", "p", "Q", "q", "R", "r", "S", "s", "T", "t", "U", "u", "V", "v", "W", "w", "X", "x", "Y", "y", "Z", "z"]
                letters5 = ["A", "a", "B", "b", "C", "c", "D", "d", "E", "e", "F", "f", "G", "g", "H", "h", "I", "i", "J", "j", "K", "k", "L", "l", "M", "m", "N", "n", "O", "o", "P", "p", "Q", "q", "R", "r", "S", "s", "T", "t", "U", "u", "V", "v", "W", "w", "X", "x", "Y", "y", "Z", "z"]
                letters6 = ["A", "a", "B", "b", "C", "c", "D", "d", "E", "e", "F", "f", "G", "g", "H", "h", "I", "i", "J", "j", "K", "k", "L", "l", "M", "m", "N", "n", "O", "o", "P", "p", "Q", "q", "R", "r", "S", "s", "T", "t", "U", "u", "V", "v", "W", "w", "X", "x", "Y", "y", "Z", "z"]
                letters7 = ["A", "a", "B", "b", "C", "c", "D", "d", "E", "e", "F", "f", "G", "g", "H", "h", "I", "i", "J", "j", "K", "k", "L", "l", "M", "m", "N", "n", "O", "o", "P", "p", "Q", "q", "R", "r", "S", "s", "T", "t", "U", "u", "V", "v", "W", "w", "X", "x", "Y", "y", "Z", "z"]
                letters8 = ["A", "a", "B", "b", "C", "c", "D", "d", "E", "e", "F", "f", "G", "g", "H", "h", "I", "i", "J", "j", "K", "k", "L", "l", "M", "m", "N", "n", "O", "o", "P", "p", "Q", "q", "R", "r", "S", "s", "T", "t", "U", "u", "V", "v", "W", "w", "X", "x", "Y", "y", "Z", "z"]
                letters9 = ["A", "a", "B", "b", "C", "c", "D", "d", "E", "e", "F", "f", "G", "g", "H", "h", "I", "i", "J", "j", "K", "k", "L", "l", "M", "m", "N", "n", "O", "o", "P", "p", "Q", "q", "R", "r", "S", "s", "T", "t", "U", "u", "V", "v", "W", "w", "X", "x", "Y", "y", "Z", "z"]
                letters10 = ["A", "a", "B", "b", "C", "c", "D", "d", "E", "e", "F", "f", "G", "g", "H", "h", "I", "i", "J", "j", "K", "k", "L", "l", "M", "m", "N", "n", "O", "o", "P", "p", "Q", "q", "R", "r", "S", "s", "T", "t", "U", "u", "V", "v", "W", "w", "X", "x", "Y", "y", "Z", "z"]
                letter1 = random.sample(letters1, 1)
                letter2 = random.sample(letters2, 1)
                letter3 = random.sample(letters3, 1)
                letter4 = random.sample(letters4, 1)
                letter5 = random.sample(letters5, 1)
                letter6 = random.sample(letters1, 1)
                letter7 = random.sample(letters2, 1)
                letter8 = random.sample(letters3, 1)
                letter9 = random.sample(letters4, 1)
                letter10 = random.sample(letters5, 1)
                value = (round(random.random()*9999999999,10))
                value2 = (round(random.random()*9999999999,10))
                hlevel = (round(random.random()*100,6))
                mthreshold = (round(random.random()*100,6))
                cpercentage = (round(random.random()*100,6))
                values = "value:"
                hlev = "H-level:"
                mthresh = "M-threshold:"
                cpercent = "C-percentage:"
                print()
                print(hlev, hlevel)
                print(mthresh, mthreshold)
                print(cpercent, cpercentage)
                print()
                time.sleep(5.5)
                print(values, letter1, letter2, letter3, letter4, letter5, value)
                print(values, letter6, letter7, letter8, letter9, letter10, value2)
                print()
                time.sleep(.2)
                print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
                print()
                time.sleep(.3)
                print("OM MANI PADME HUM")
                print()
                time.sleep(.3)
                print("You light an incense")
                print()
                time.sleep(.5)
                result = random.sample(nano, 1)
                result2 = random.sample(nano, 1)
                result3 = random.sample(nano, 1)
                print(result)
                print(result2)
                print(result3)
                time.sleep(.5)
                print()
                print("--------------------------------------------")

            def main_loop():
                while True:
                    time.sleep(.3)
                    generate_random_result()

            try:
                main_loop()
            except KeyboardInterrupt:
                print("\nStopped by user.")

        def speak(text):
            if platform.system() == "Linux" and shutil.which("termux-tts-speak"):
                try:
                    subprocess.run(["termux-tts-speak", text], check=True)
                    return
                except subprocess.CalledProcessError as e:
                    print(f"Termux-TTS error: {e}")
                except FileNotFoundError:
                    pass

            if shutil.which("espeak"):
                try:
                    if platform.system() == "Windows":
                        subprocess.run(["espeak", "-v", "en+f1", text], check=True)
                    else:
                        subprocess.run(["espeak", "-v", "en+f1", text], check=True)
                    return
                except subprocess.CalledProcessError as e:
                    print(f"eSpeak error: {e}")
                    return
                except Exception as e:
                    print(f"An unexpected error occurred with eSpeak: {e}")
                    return d
            else:
                print()
                print("ERROR: Neither 'termux-tts-speak' nor 'espeak' was found.")
                print("Install 'termux-api' (and the Android Termux:API app) or 'sudo apt install espeak / pkg install espeak'.")

        def spik(text):
            if platform.system() == "Linux" and shutil.which("termux-tts-speak"):
                try:
                    subprocess.run(["termux-tts-speak", text], check=True)
                    return
                except subprocess.CalledProcessError as e:
                    print(f"Termux-TTS error: {e}")
                except FileNotFoundError:
                    pass

            if shutil.which("espeak"):
                try:
                    if platform.system() == "Windows":
                        subprocess.run(["espeak", "-v", "ru+f2", text], check=True)
                    else:
                        subprocess.run(["espeak", "-v", "ru+f2", text], check=True)
                    return
                except subprocess.CalledProcessError as e:
                    print(f"eSpeak error: {e}")
                    return
                except Exception as e:
                    print(f"An unexpected error occurred with eSpeak: {e}")
                    return d
            else:
                print()
                print("ERROR: Neither 'termux-tts-speak' nor 'espeak' was found.")
                print("Install 'termux-api' (and the Android Termux:API app) or 'sudo apt install espeak / pkg install espeak'.")

        def call():
            maroon = " st"
            nano = (diction)
            title = input("call name: ")
            print()
            def generate_random_result():
                ctm = datetime.datetime.now()
                def generate_random_letters():
                    random1 = random.choice(string.ascii_letters)
                    random2 = random.choice(string.ascii_letters)
                    random3 = random.choice(string.ascii_letters)
                    letters = [random1, random2, random3]
                    return letters
                def generate_ans():
                    ans = (alphabeta)
                    anschar = random.choices(ans, k=random.randint(5,6))
                    sstr = ''.join(anschar)
                    return sstr
                anschar_str = generate_ans()
                speak("alert!")
                time.sleep(1.6)
                random_letters = generate_random_letters()
                sitch  = (round(random.random()*9999,4))
                kchat = random.sample(nano, random.randint(1,7))
                random_result = random.choices(nano, k=random.randint(1,7))
                result_text = "  ".join(random_result)
                print(maroon, anschar_str, sitch, result_text, ctm)
                speak(anschar_str)
                time.sleep(.2)
                speak(result_text)
                print()
            
            def main_loop():
                while True:
                    time.sleep(random.randint(0,5))
                    integer = (round(random.random()*25))
                    if integer > 15:
                        if random.choice([True, False]):
                            generate_random_result()

            try:
                main_loop()
            except KeyboardInterrupt:
                print("\nStopped by user.")

        def time_call():
            maroon = " st"
            nano = (diction)
            title = input("time-call name: ")
            ct = datetime.datetime.now()
            while True:
                try:
                    buffer = float(input("time-buffer in seconds: "))
                except ValueError:
                    print("Invalid value")
                else:
                    break
            buffer
            monitor = "time-call-start:"
            print(usr, monitor, title, ct)
            print()
            def generate_random_result():
                ctm = datetime.datetime.now()
                def generate_random_letters():
                    random1 = random.choice(string.ascii_letters)
                    random2 = random.choice(string.ascii_letters)
                    random3 = random.choice(string.ascii_letters)
                    letters = [random1, random2, random3]
                    return letters
                def generate_ans():
                    ans = (alphabeta)
                    anschar = random.choices(ans, k=random.randint(5,6))
                    sstr = ''.join(anschar)
                    return sstr
                anschar_str = generate_ans()
                speak("alert!")
                time.sleep(2.9)
                random_letters = generate_random_letters()
                sitch  = (round(random.random()*9999,4))
                kchat = random.sample(nano, random.randint(1,7))
                random_result = random.choices(nano, k=random.randint(1,7))
                result_text = "  ".join(random_result)
                print(maroon, anschar_str, sitch, result_text, ctm)
                speak(anschar_str)
                time.sleep(.2)
                speak(result_text)
                print()
                time.sleep(buffer)
            
            def main_loop():
                while True:
                    generate_random_result()

            try:
                main_loop()
            except KeyboardInterrupt:
                print("\nStopped by user.")

        def ruh_time_call():
            maroon = " st"
            
            nano = ["а", "б", "в", "г", "д", "е", "ё", "ж", "з", "и", "й", "к", "л", "м", "н", "о", "п", "р", "с", "т", "у", "ф", "х", "ц", "ч", "ш", "щ", "ъ", "ы", "ь", "э", "ю", "я", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "]

            title = input("ruh-TC name: ")
            ct = datetime.datetime.now()
            while True:
                try:
                    buffer = float(input("time-buffer in seconds: "))
                except ValueError:
                    print("Invalid value")
                else:
                    break
            buffer
            monitor = "ruh-TC-start:"
            print(usr, monitor, title, ct)
            print()
            def generate_random_result():
                ctm = datetime.datetime.now()
                def generate_random_letters():
                    random1 = random.choice(string.ascii_letters)
                    random2 = random.choice(string.ascii_letters)
                    random3 = random.choice(string.ascii_letters)
                    letters = [random1, random2, random3]
                    return letters
                def generate_ans():
                    ans = (alphabeta)
                    anschar = random.choices(ans, k=random.randint(5,6))
                    sstr = ''.join(anschar)
                    return sstr
                anschar_str = generate_ans()
                spik("alert!")
                time.sleep(1.6)
                random_letters = generate_random_letters()
                sitch  = (round(random.random()*9999,4))
                kchat = random.sample(nano, random.randint(1,7))
                random_result = random.choices(nano, k=random.randint(1,22))
                result_text = "".join(random_result)
                print(maroon, anschar_str, sitch, result_text, ctm)
                spik(result_text)
                print()
                time.sleep(buffer)
            
            def main_loop():
                while True:
                    generate_random_result()

            try:
                main_loop()
            except KeyboardInterrupt:
                print("\nStopped by user.")

        def spheak():
            sph = input("speak: ")
            print()
            print(sph)
            speak(sph)

        def kata_monitor():
            maroon = " st"
            nano = (katakana)
            title = input("kata-monitor name: ")
            ct = datetime.datetime.now()
            monitor = "kata-monitor-start:"
            print(usr, monitor, title, ct)
            print()
            def generate_random_result():
                ctm = datetime.datetime.now()
                def generate_random_letters():
                    random1 = random.choice(string.ascii_letters)
                    random2 = random.choice(string.ascii_letters)
                    random3 = random.choice(string.ascii_letters)
                    letters = [random1, random2, random3]
                    return letters
                random_letters = generate_random_letters()
                sitch  = (round(random.random()*9999,4))
                kkhat = random.choices(nano, k=random.randint(1,15))
                kkhat_str = ''.join(kkhat)
                print(maroon, kkhat_str, sitch, random_letters, ctm)
                print()

            def main_loop():
                while True:
                    time.sleep(random.randint(0,5))
                    integer = (round(random.random()*25))
                    if integer > 15:
                        if random.choice([True, False]):
                            generate_random_result()

            try:
                main_loop()
            except KeyboardInterrupt:
                print("\nStopped by user.")

        def hangu_monitor():
            maroon = " st"
            nano = (jamo)
            title = input("jamo-monitor name: ")
            ct = datetime.datetime.now()
            monitor = "jamo-monitor-start:"
            print(usr, monitor, title, ct)
            print()
            def generate_random_result():
                ctm = datetime.datetime.now()
                def generate_random_letters():
                    random1 = random.choice(string.ascii_letters)
                    random2 = random.choice(string.ascii_letters)
                    random3 = random.choice(string.ascii_letters)
                    letters = [random1, random2, random3]
                    return letters
                random_letters = generate_random_letters()
                sitch  = (round(random.random()*9999,4))
                kkhat = random.choices(nano, k=random.randint(1,20))
                kkhat_str = ''.join(kkhat)
                print(maroon, kkhat_str, random_letters, sitch, ctm)
                print()

            def main_loop():
                while True:
                    time.sleep(random.randint(0,5))
                    integer = (round(random.random()*25))
                    if integer > 15:
                        if random.choice([True, False]):
                            generate_random_result()

            try:
                main_loop()
            except KeyboardInterrupt:
                print("\nStopped by user.")

        def ch_monitor():
            maroon = " st"
            nano = (chi_chars)
            title = input("ch-monitor name: ")
            ct = datetime.datetime.now()
            monitor = "ch-monitor-start:"
            print(usr, monitor, title, ct)
            print()
            def generate_random_result():
                ctm = datetime.datetime.now()
                def generate_random_letters():
                    random1 = random.choice(string.ascii_letters)
                    random2 = random.choice(string.ascii_letters)
                    random3 = random.choice(string.ascii_letters)
                    letters = [random1, random2, random3]
                    return letters
                random_letters = generate_random_letters()
                sitch  = (round(random.random()*9999,4))
                cchat = random.choices(nano, k=random.randint(1,12))
                print(maroon, random_letters, sitch, cchat, ctm)
                print()

            def main_loop():
                while True:
                    time.sleep(random.randint(0,5))
                    integer = (round(random.random()*25))
                    if integer > 15:
                        if random.choice([True, False]):
                            generate_random_result()
                            
            try:
                main_loop()
            except KeyboardInterrupt:
                print("\nStopped by user.")

        def ruh_monitor():
            maroon = " st"
            
            nano = ["а", "б", "в", "г", "д", "е", "ё", "ж", "з", "и", "й", "к", "л", "м", "н", "о", "п", "р", "с", "т", "у", "ф", "х", "ц", "ч", "ш", "щ", "ъ", "ы", "ь", "э", "ю", "я", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "]

            title = input("ruh-monitor name: ")
            ct = datetime.datetime.now()
            monitor = "ruh-monitor-start:"
            print(usr, monitor, title, ct)
            print()
            def generate_random_result():
                ctm = datetime.datetime.now()
                def generate_random_letters():
                    random1 = random.choice(string.ascii_letters)
                    random2 = random.choice(string.ascii_letters)
                    random3 = random.choice(string.ascii_letters)
                    letters = [random1, random2, random3]
                    return letters
                random_letters = generate_random_letters()
                sitch  = (round(random.random()*9999,4))
                kkhat = random.choices(nano, k=random.randint(1,22))
                kkhat_str = ''.join(kkhat)
                print(maroon, kkhat_str, sitch, random_letters, ctm)
                print()

            def main_loop():
                while True:
                    time.sleep(random.randint(0,5))
                    integer = (round(random.random()*25))
                    if integer > 15:
                        if random.choice([True, False]):
                            generate_random_result()

            try:
                main_loop()
            except KeyboardInterrupt:
                print("\nStopped by user.")

        def ghost_write():
            nano = (diction)
            print()
            def generate_random_result():
                kchat = " ".join(random.choices(nano, k=random.randint(1,7)))
                print(kchat)

            def main_loop():
                while True:
                  time.sleep(random.randint(2,10))
                  generate_random_result()

            try:
                main_loop()
            except KeyboardInterrupt:
                print()
                print("\nStopped by user.")

        def insta_ghost_write():
            nano = (diction)
            while True:
                try:
                    number = int(input("Indicate number of (i-GhostWrite) results: "))
                except ValueError:
                    print("Invalid value")
                else:
                    break
            number
            print()
            for _ in range(number):
                kchat = " ".join(random.choices(nano, k=random.randint(1,7)))
                print(kchat)

        def monitor_start():
            maroon = " st"
            nano = (diction)
            title = input("monitor name: ")
            print()
            def generate_random_result():
                ctm = datetime.datetime.now()
                def generate_random_letters():
                    random1 = random.choice(string.ascii_letters)
                    random2 = random.choice(string.ascii_letters)
                    random3 = random.choice(string.ascii_letters)
                    letters = [random1, random2, random3]
                    return letters
                def generate_ans():
                    ans = (alphabeta)
                    anschar = random.choices(ans, k=random.randint(5,6))
                    sstr = ''.join(anschar)
                    return sstr
                anschar_str = generate_ans()
                random_letters = generate_random_letters()
                sitch  = (round(random.random()*9999,4))
                kchat = "  ".join(random.choices(nano, k=random.randint(1,9)))
                random_color = get_random_color()
                print(f"{maroon} {anschar_str} {sitch} {random_color}{kchat}{RESET} {ctm}")
                print()

            def main_loop():
                while True:
                    time.sleep(random.randint(0,5))
                    integer = (round(random.random()*25))
                    if integer > 15:
                        if random.choice([True, False]):
                            generate_random_result()

            try:
                main_loop()
            except KeyboardInterrupt:
                print("\nStopped by user.")

        def acad_monitor():
            maroon = " st"
            nano = (diction)
            acad = (acadlist)
            title = input("a-monitor name: ")
            print()
            def generate_random_result():
                ctm = datetime.datetime.now()
                def generate_random_letters():
                    random1 = random.choice(string.ascii_letters)
                    random2 = random.choice(string.ascii_letters)
                    random3 = random.choice(string.ascii_letters)
                    letters = [random1, random2, random3]
                    random.shuffle(letters)
                    return letters
                random_letters = generate_random_letters()
                sitch  = (round(random.random()*9999,4))
                kchat = "  ".join(random.choices(nano, k=random.randint(1,9)))
                kchat2 = random.choices(acad, k=random.randint(1,7))
                random_color = get_random_color()
                print(f"{maroon} {random_letters} {sitch} {random_color}{kchat} {kchat2}{RESET} {ctm}")
                print("_______________________________________")
                print()

            def main_loop():
                while True:
                    time.sleep(random.randint(0,14))
                    integer = (round(random.random()*25))
                    if integer > 15:
                        if random.choice([True, False]):
                            generate_random_result()
            
            try:
                main_loop()
            except KeyboardInterrupt:
                print("\nStopped by user.")

        def fntcci_monitor():
            maroon = " st"
            aono = (fcci)
            nano = (diction)
            acad = (acadlist)
            title = input("FNTCCI-monitor name: ")
            ct = datetime.datetime.now()
            monitor = "FNTCCI-monitor-start:"
            print()
            print(usr, monitor, title, ct)
            print()
            def Wonraoyerjishibli():
                cci = random.choices(aono, k=random.randint(1,10))
                cchat = "  ".join(random.choices(nano, k=random.randint(1,9)))
                acadl = random.choices(acad, k=random.randint(1,7))
                wonyao_str = ''.join(cci)
                dash = "-"
                ctm = datetime.datetime.now()
                print(maroon, wonyao_str, dash, cchat, acadl, ctm)
                print("_______________________________________")
                print()

            def main_loop():
                while True:
                    time.sleep(random.randint(0,12))
                    integer = (round(random.random()*35))
                    if integer > 17:
                        if random.choice([True, False]):
                            Wonraoyerjishibli()
            
            try:
                main_loop()
            except KeyboardInterrupt:
                print("\nStopped by user.")

        def time_monitor():
            maroon = " st"
            nano = (diction)
            acad = (acadlist)
            title = input("t-monitor name: ")
            while True:
                try:
                    buffer = float(input("time-buffer in seconds: "))
                except ValueError:
                    print("Invalid value")
                else:
                    break
            buffer
            print()
            def generate_random_result():
                time.sleep(buffer)
                ctm = datetime.datetime.now()
                def generate_random_letters():
                    random1 = random.choice(string.ascii_letters)
                    random2 = random.choice(string.ascii_letters)
                    random3 = random.choice(string.ascii_letters)
                    letters = [random1, random2, random3]
                    random.shuffle(letters)
                    return letters
                random_letters = generate_random_letters()
                sitch  = (round(random.random()*9999,4))
                kchat = "  ".join(random.choices(nano, k=random.randint(1,9)))
                kchat2 = random.choices(acad, k=random.randint(1,7))
                random_color = get_random_color()
                print(f"{maroon} {random_letters} {sitch} {random_color}{kchat} {kchat2}{RESET} {ctm}")
                print("_______________________________________")
                print()

            def main_loop():
                while True:
                    generate_random_result()
            
            try:
                main_loop()
            except KeyboardInterrupt:
                print("\nStopped by user.")

        def s_time_monitor():
            maroon = " st"
            nano = (diction)
            acad = (acadlist)
            title = input("t-monitor name: ")
            while True:
                try:
                    buffer = float(input("time-buffer in seconds: "))
                except ValueError:
                    print("Invalid value")
                else:
                    break
            buffer
            print()
            def generate_random_result():
                time.sleep(buffer)
                ctm = datetime.datetime.now()
                def generate_random_letters():
                    random1 = random.choice(string.ascii_letters)
                    random2 = random.choice(string.ascii_letters)
                    random3 = random.choice(string.ascii_letters)
                    letters = [random1, random2, random3]
                    random.shuffle(letters)
                    return letters
                random_letters = generate_random_letters()
                sitch  = (round(random.random()*9999,4))
                kchat = "  ".join(random.choices(nano, k=random.randint(1,9)))
                kchat2 = random.choices(acad, k=random.randint(1,7))
                random_result = [random.choice(nano)]
                result_text = ", ".join(random_result)
                print(maroon, random_letters, sitch, kchat, kchat2, result_text, ctm)
                print("_______________________________________")
                speak(result_text)
                print()

            def main_loop():
                while True:
                    generate_random_result()
            
            try:
                main_loop()
            except KeyboardInterrupt:
                print("\nStopped by user.")

        def programs():
            maroon = " st"
            nano = list(diction)
            acad = list(acadlist)
            medica = list(medicals1)
            scienc = list(science1)
            psycholog = list(psychology1)
            biolog = list(biology1)
            dhamma = list(dhammapada1)
            chemis = list(chemistry1)
            legal_t = list(legal_terms1)
            degre = list(degrees1)
            vers = list(verses1)
            dec = list(deck1)
            kora = list(koran1)
            provrb = list(proverbs)
            bible_verse = list(bible1)

            def police2():
                time.sleep(0)   
                code = ["Code Red", "Code Blue", "Code Green", "Code Orange", "Code Yellow", "Code Black", "Code White", "Code Purple", "Code Pink"]
                cod = random.sample(code, 1)[0]
                urgency = ["Critical", "High", "Medium", "Low", "Lowest"]
                urge = random.sample(urgency, 1)[0]
                polis = ["3511 A vehicle that has been impounded for a mandatory 30 days", "A.P.S. Arizona Public Service", "A.S.A.P. As soon as possible", "A.T.F. Bureau of Alcohol, Tobacco, and Firearms", "BAILED OUT Subject jumped out of car and ran", "BYFRND Boyfriend", "BEER RUN Shoplifting beer", "BONDOUT Prisoner who is going to post bail and be released", "BEEN MADE/BURNED Undercover officer's ID is known", "BHND Behind", "BIKE Motorcycle", "BIKERS Motorcycle riders", "BOOKING Booking prisoner into jail", "BREAKING UP Radio transmissions are not being received clearly", "BUSTED Arrested", "C.C.W. Carrying concealed weapon", "C.O. Civilian observer", "COMP Complainant", "C.L.D. Citation in lieu of detention", "CRACK, ROCK Smokeable form of cocaine", "D.E.B. Drug Enforcement Bureau", "DIX Detectives", "D.O.A. Dead on arrival", "D.O.B. Date of birth", "D.O.C. Department of Corrections", "D.P.S. Department of Public Safety", "DRIVE BY Shots fired from a moving vehicle", "E.O.C. Emergency Operations Center", "EQUIPMENT Police vehicle", "E.R. Emergency Room", "E.T.A. Estimated time of arrival", "F.A.A. Federal Aviation Administration", "B.I. Federal Bureau of Investigation", "F.I. Field Interrogation (Form 36 card)", "FILE STOP Notation put in police record; File Stops are confirmed by R&I Bureau", "FLIR Device used by aircraft to check for heat sources", "F.O.J. From other jurisdiction", "FRONT DESK Information Desk at main station", "FUGITIVE A wanted person", "GAS WASH/WASHDOWN Fire Department needed to wash gas down", "G.C.I. /B.A. Test used to determine blood alcohol content", "G.I.B. General Investigations Bureau", "GOT THE EYE In view (on a code 5)", "GRN Green", "HOND Honda", "HIT Subject or item wanted", "H.G.N. Horizontal Gaze Nystagmus (a test for detecting drug / alcohol use)", "HOBBLES Nylon rope used for legs and hand restraint", "HOOK Wrecker", "HSE House", "ICE, CRYSTAL Smokeable methamphetamine", "J.C.C. Juvenile Corrections Center", "J.P. Justice of the Peace", "JUMPED ON Assaulted", "JUMPER Person attempting suicide by jumping", "LADDER Fire Department ladder truck", "MARQUIS Test for narcotics", "M.D.C. Mobile Digital Computer (Police car computer)", "MEDICS Paramedics", "MERZ Mercedes Benz", "MHP Mobile Home Park", "MOTOR Solo motor unit", "NUMBER 1 SITUATION Probable cause for arrest", "NUMBER 9's Citations", "OD Overdose", "ONE FROM LIST Contract wrecker (926)", "ONE ON ONE Suspect / witness I.D.", "ONE ROLL Fingerprints", "O.V. On view, officer just witnessed an incident", "PAGE 2 Additional charges filed on a subject already in custody", "P.C. Probable cause", "PLE Purple", "P.O. Probation officer", "RESTRAINTS Leather straps used to restrain prisoners", "RINGER Audible alarm", "ROLLOVER Accident involving overturned vehicle", "R.P. Responsible party", "S/E/C Southeast corner", "SEIZURE Impound a vehicle; subject having convulsions", "SGT Sergeant", "SILENT Silent alarm", "SLIM JIM Device used to open locked vehicle", "SMASH & GRAB Broke out window, grabbed items and ran", "S.O./M.C.S.O. Maricopa County Sheriff's Office", "S.R.P. Salt River Project", "STRIPPED Vehicle stripped", "TECH Radio or computer technician", "THIRTY-SIX Field interrogation (or form 36)", "THREE WHEELER Police 3-wheeled motorcycle", "TILL TAP Grab money from register", "DISPATCH AN ANIMAL To shoot an animal", "TRAFFIC BOX KEY Key used to open traffic signal control box", "XHUSB Ex-husband", "WAGON/WAGON Police paddy wagon"]
                pol_str = " , over, ".join(random.sample(polis, random.randint(1, 8)))
                locate = ["Local", "Local", "Foreign"]
                loc = random.sample(locate, 1)[0]
                direction = ["South", "North", "West", "East", "Southwest", "Southeast", "Northwest", "Northeast"]
                dire = random.sample(direction, 1)[0]  
                suspectcode = (round(random.random()*26))
                sus = "Suspect Code:"
                location = (round(random.random()*99999999,10))
                ct = datetime.datetime.now()
                po = "police:"
                final_result_string = f"{po} {cod}, Urgency: {urge}, {sus} {suspectcode}, Terms: ({pol_str}), Location Type: {loc}, Direction: {dire}, Coords: {location}"
                return final_result_string 

            title = input("programs-monitor name: ")

            while True:
                try:
                    buffer = float(input("time-buffer in seconds: "))
                except ValueError:
                    print("Invalid value")
                else:
                    break
            buffer
            ct = datetime.datetime.now()
            monitor = "programs-monitor-start:"
            print(usr, monitor, title, ct)
            print()

            def generate_random_result():
                time.sleep(buffer)
                ctm = datetime.datetime.now()
                def generate_random_letters():
                    random1 = random.choice(string.ascii_letters)
                    random2 = random.choice(string.ascii_letters)
                    random3 = random.choice(string.ascii_letters)
                    letters = [random1, random2, random3]
                    random.shuffle(letters)
                    return letters
                random_letters = generate_random_letters()
                sitch  = (round(random.random()*9999,4))
                random_result = (random.choice(nano), random.choice(nano), random.choice(nano), random.choice(acad), random.choice(medica), random.choice(scienc), random.choice(psycholog), random.choice(biolog), random.choice(dhamma), random.choice(dhamma), random.choice(chemis), random.choice(legal_t), random.choice(degre), random.choice(vers), random.choice(dec), police2(), police2(), police2(), police2(), police2(), random.choice(kora), random.choice(kora), random.choice(kora), random.choice(provrb), random.choice(provrb), random.choice(provrb), random.choice(provrb), random.choice(bible_verse), random.choice(bible_verse), random.choice(bible_verse), random.choice(bible_verse), random.choice(bible_verse), random.choice(bible_verse))
                result = random.sample(random_result, 1)
                result_text = ", ".join(result)
                print(maroon, random_letters, sitch, result, ctm)
                speak(result_text)
                print()

            def main_loop():
                while True:
                    generate_random_result()
            
            try:
                main_loop()
            except KeyboardInterrupt:
                print("\nStopped by user.")

        def msgs():
            kk = (katakana)
            j = (jamo)
            cc = (chi_chars)
            while True:
                try:
                    number = int(input("Indicate number of scans: "))
                except ValueError:
                    print("Invalid value")
                else:
                    break
            number
            numberstr = str(number)
            print()
            print("Scanning...")
            print()
            time.sleep(2)
            for _ in range(number):
                time.sleep(.1)
                integer = (round(random.random()*25))
                if integer > 15:
                    if random.choice([True, False]):
                        ctm = datetime.datetime.now()
                        nano = (diction)
                        acad = (acadlist)
                        def generate_random_letters():
                            random1 = random.choice(string.ascii_letters)
                            random2 = random.choice(string.ascii_letters)
                            random3 = random.choice(string.ascii_letters)
                            letters = [random1, random2, random3]
                            random.shuffle(letters)
                            return letters
                        random_letters = generate_random_letters()
                        sitch  = (round(random.random()*9999,4))
                        kkchar = random.choices(kk, k=random.randint(1,40))
                        hchar = random.choices(j, k=random.randint(1,40))
                        cchat = random.choices(cc, k=random.randint(1,40))
                        kkchar_str = ''.join(kkchar)
                        hchar_str = ''.join(hchar)
                        kchat = "  ".join(random.sample(nano, random.randint(0,27)))
                        kchat2 = random.sample(acad, random.randint(0,8))
                        msg = "msg:"
                        print(usr, msg, random_letters, sitch, kchat, kchat2, kkchar_str, cchat, hchar_str, ctm)
                        print()                 
            print()
            ct = datetime.datetime.now()
            print("/scanning finished!", ct)
            print()

        def fuzz():
            ct = datetime.datetime.now()
            fuzz = "fuzzing..."
            print(fuzz, ct)
            time.sleep(3)
            print("#")
            time.sleep(.2)
            print("#")
            time.sleep(.2)
            print("#")
            time.sleep(.2)
            print("%")
            time.sleep(.2)
            print("%")
            time.sleep(.2)
            print("%")
            time.sleep(.2)
            print(">")
            time.sleep(.2)
            print(">")
            time.sleep(.2)
            print(">")
            time.sleep(.2)
            print("#")
            time.sleep(.2)
            print("#")
            time.sleep(.2)
            print("#")
            time.sleep(.2)
            print("%")
            time.sleep(.2)
            print("%")
            time.sleep(.2)
            print("%")
            time.sleep(.2)
            print(">")
            time.sleep(.2)
            print(">")
            time.sleep(.2)
            print(">")
            time.sleep(.2)
            print()
            print("You light an incense...")
            time.sleep(4)

        def tag():   
            rtag = input("tag: ")
            while True:
                try:
                    number = int(input("Number of results: "))
                except ValueError:
                    print("Invalid value")
                else:
                    break
            number
            for _ in range(number):
                time.sleep(.103)
                nano = (diction)
                ct = datetime.datetime.now()
                tag = "tag:"
                ctm = datetime.datetime.now()
                def generate_random_letters():
                    random1 = random.choice(string.ascii_letters)
                    random2 = random.choice(string.ascii_letters)
                    random3 = random.choice(string.ascii_letters)
                    letters = [random1, random2, random3]
                    random.shuffle(letters)
                    return letters
                random_letters = generate_random_letters()
                sitch  = (round(random.random()*9999,4))
                kchat = "  ".join(random.choices(nano, k=random.randint(1,7)))
                print()
                print(tag, rtag, random_letters, sitch, kchat, ctm)

        def atag():   
            rtag = input("a-tag: ")
            while True:
                try:
                    number = int(input("Number of results: "))
                except ValueError:
                    print("Invalid value")
                else:
                    break
            number
            for _ in range(number):
                time.sleep(.103)
                nano = (diction)
                acad = (acadlist)
                ct = datetime.datetime.now()
                tag = "a-tag:"
                ctm = datetime.datetime.now()
                def generate_random_letters():
                    random1 = random.choice(string.ascii_letters)
                    random2 = random.choice(string.ascii_letters)
                    random3 = random.choice(string.ascii_letters)
                    letters = [random1, random2, random3]
                    random.shuffle(letters)
                    return letters
                random_letters = generate_random_letters()
                sitch  = (round(random.random()*9999,4))
                kchat = "  ".join(random.choices(nano, k=random.randint(1,8)))
                kchat2 = random.choices(acad, k=random.randint(1,7))
                print()
                print(tag, rtag, random_letters, sitch, kchat, kchat2, ctm)

        def ntag():  
            ctag = input("n-tag: ")
            while True:
                try:
                    number = int(input("Number of results: "))
                except ValueError:
                    print("Invalid value")
                else:
                    break
            number
            for _ in range(number):
                time.sleep(.103)
                an = (fcci) 
                nano = (diction)
                acad = (acadlist)
                ct = datetime.datetime.now()
                tag = "n-tag:"
                ctm = datetime.datetime.now()
                def generate_random_letters():
                    random1 = random.choice(string.ascii_letters)
                    random2 = random.choice(string.ascii_letters)
                    random3 = random.choice(string.ascii_letters)
                    letters = [random1, random2, random3]
                    random.shuffle(letters)
                    return letters
                def generate_ans():
                    ans = (alphabeta)
                    anschar = random.choices(ans, k=random.randint(5,6))
                    sstr = ''.join(anschar)
                    return sstr
                anschar_str = generate_ans()
                random_letters = generate_random_letters()
                sitch  = (round(random.random()*9999,4))
                nn = random.choices(an, k=random.randint(1,10))
                wonyao_str = ''.join(nn)
                cchat = "  ".join(random.choices(nano, k=random.randint(1,9)))
                acadl = random.sample(acad, random.randint(1,7))
                dash = "-"
                random_color = get_random_color()
                print()
                print(f"{tag} {ctag} {anschar_str} {sitch} {wonyao_str} {dash} {random_color}{cchat} {acadl}{RESET} {ctm}")

        def MAI():
            import time
            while True:
                try:
                    number = int(input("Indicate number of (MedProc AI) results: "))
                except ValueError:
                    print("Invalid value")
                else:
                    break
            number
            time.sleep(2)
            for _ in range(number):
                time.sleep(1.5)
                print()
                ctm = datetime.datetime.now()
                def generate_random_letters():
                    random1 = random.choice(string.ascii_letters)
                    random2 = random.choice(string.ascii_letters)
                    random3 = random.choice(string.ascii_letters)
                    letters = [random1, random2, random3]
                    random.shuffle(letters)
                    return letters
                random_letters = generate_random_letters()
                sitch  = (round(random.random()*9999,4))
                asc = "ascii:"
                print(asc, usr, random_letters, sitch, ctm)
                pr1 = (round(random.random()*99999999999999999999999999999999999999999))
                pr2 = (round(random.random()*99999999999999999999999999999999999999999))
                pr3 = (round(random.random()*99999999999999999999999999999999999999999))
                pr4 = (round(random.random()*99999999999999999999999999999999999999999))
                pr5 = (round(random.random()*99999999999999999999999999999999999999999))
                pr6 = (round(random.random()*99999999999999999999999999999999999999999))
                pr7 = (round(random.random()*99999999999999999999999999999999999999999))
                pr8 = (round(random.random()*99999999999999999999999999999999999999999))
                pr9 = (round(random.random()*99999999999999999999999999999999999999999))
                pr10 = (round(random.random()*99999999999999999999999999999999999999999))
                pr11 = (round(random.random()*99999999999999999999999999999999999999999))
                pr12 = (round(random.random()*99999999999999999999999999999999999999999))
                print()
                print(pr1)
                print(pr2)
                print(pr3)
                print(pr4)
                print(pr5)
                print(pr6)
                print(pr7)
                print(pr8)
                print(pr9)
                print(pr10)
                print(pr11)
                print(pr12)
                print()
                time.sleep(2)
                if True:
                    nano = (diction)
                    acad = (acadlist)
                    integer = (round(random.random()*25))
                    if integer > 15:
                        if random.choice([True, False]):
                            time.sleep(1.5)
                            ct = datetime.datetime.now()
                            tag = "a-tag:"
                            ctm = datetime.datetime.now()
                            def generate_random_letters():
                                random1 = random.choice(string.ascii_letters)
                                random2 = random.choice(string.ascii_letters)
                                random3 = random.choice(string.ascii_letters)
                                letters = [random1, random2, random3]
                                random.shuffle(letters)
                                return letters
                            random_letters = generate_random_letters()
                            sitch  = (round(random.random()*9999,4))
                            kchat = random.choices(nano, k=random.randint(1,8))
                            kchat2 = random.choices(acad, k=random.randint(1,7))
                            print()
                            print(usr, random_letters, sitch, kchat2, kchat, ctm)
                            print()
                            time.sleep(4.2)
                if True:
                    integer = (round(random.random()*25))
                    if integer > 15:
                        if random.choice([True, False]):
                            time.sleep(1.5)
                            t  = (round(random.random()*10))
                            for _ in range(t):
                                ctm = datetime.datetime.now()
                                hashes = ("#", "#####", "##########", "##########################", "##########################", "##########################")
                                hashh = random.sample(hashes, random.randint(1,1))
                                print(usr, hashh)
                                print()
                                time.sleep(.5)
                if True:
                    integer = (round(random.random()*25))
                    if integer > 20:
                        if random.choice([True, False]):
                            time.sleep(1.5)
                            t  = (round(random.random()*8))
                            for _ in range(t):
                                ctm = datetime.datetime.now()
                                hashes = ("V", "    V", "          V", "                    V", "                              V", "                                        V")
                                hashh = random.sample(hashes, random.randint(1,1))
                                print(usr, hashh)
                                print()
                                time.sleep(.5)

                if True:
                    integer = (round(random.random()*25))
                    if integer > 20:
                        if random.choice([True, False]):
                            time.sleep(1.5)
                            t  = (round(random.random()*8))
                            for _ in range(t):
                                ctm = datetime.datetime.now()
                                hashes = ("v", "    v", "          v", "                    v", "                              v", "                                        v")
                                hashh = random.sample(hashes, random.randint(1,1))
                                print(usr, hashh)
                                print()
                                time.sleep(.5)

                if True:
                    integer = (round(random.random()*25))
                    if integer > 20:
                        if random.choice([True, False]):
                            time.sleep(1.5)
                            t  = (round(random.random()*8))
                            for _ in range(t):
                                ctm = datetime.datetime.now()
                                hashes = ("O", "    O", "          O", "                    O", "                              O", "                                        O")
                                hashh = random.sample(hashes, random.randint(1,1))
                                print(usr, hashh)
                                print()
                                time.sleep(.5)

                if True:
                    integer = (round(random.random()*25))
                    if integer > 20:
                        if random.choice([True, False]):
                            time.sleep(1.5)
                            t  = (round(random.random()*8))
                            for _ in range(t):
                                ctm = datetime.datetime.now()
                                hashes = ("o", "    o", "          o", "                    o", "                              o", "                                        o")
                                hashh = random.sample(hashes, random.randint(1,1))
                                print(usr, hashh)
                                print()
                                time.sleep(.5)

                if True:
                    integer = (round(random.random()*25))
                    if integer > 20:
                        if random.choice([True, False]):
                            time.sleep(1.5)
                            t  = (round(random.random()*8))
                            for _ in range(t):
                                ctm = datetime.datetime.now()
                                hashes = ("0", "    0", "          0", "                    0", "                              0", "                                        0")
                                hashh = random.sample(hashes, random.randint(1,1))
                                print(usr, hashh)
                                print()
                                time.sleep(.5)

                if True:
                    integer = (round(random.random()*25))
                    if integer > 20:
                        if random.choice([True, False]):
                            time.sleep(1.5)
                            t  = (round(random.random()*8))
                            for _ in range(t):
                                ctm = datetime.datetime.now()
                                hashes = ("H", "    H", "          H", "                    H", "                              H", "                                        H")
                                hashh = random.sample(hashes, random.randint(1,1))
                                print(usr, hashh)
                                print()
                                time.sleep(.5)

                if True:
                    integer = (round(random.random()*25))
                    if integer > 20:
                        if random.choice([True, False]):
                            time.sleep(1.5)
                            t  = (round(random.random()*8))
                            for _ in range(t):
                                ctm = datetime.datetime.now()
                                hashes = ("h", "    h", "          h", "                    h", "                              h", "                                        h")
                                hashh = random.sample(hashes, random.randint(1,1))
                                print(usr, hashh)
                                print()
                                time.sleep(.5)

                if True:
                    integer = (round(random.random()*25))
                    if integer > 20:
                        if random.choice([True, False]):
                            time.sleep(1.5)
                            t  = (round(random.random()*8))
                            for _ in range(t):
                                ctm = datetime.datetime.now()
                                hashes = ("Q", "    Q", "          Q", "                    Q", "                              Q", "                                        Q")
                                hashh = random.sample(hashes, random.randint(1,1))
                                print(usr, hashh)
                                print()
                                time.sleep(.5)

                if True:
                    integer = (round(random.random()*25))
                    if integer > 20:
                        if random.choice([True, False]):
                            time.sleep(1.5)
                            t  = (round(random.random()*8))
                            for _ in range(t):
                                ctm = datetime.datetime.now()
                                hashes = ("q", "    q", "          q", "                    q", "                              q", "                                        q")
                                hashh = random.sample(hashes, random.randint(1,1))
                                print(usr, hashh)
                                print()
                                time.sleep(.5)

                if True:
                    integer = (round(random.random()*25))
                    if integer > 20:
                        if random.choice([True, False]):
                            time.sleep(1.5)
                            t  = (round(random.random()*8))
                            for _ in range(t):
                                ctm = datetime.datetime.now()
                                hashes = ("Y", "    Y", "          Y", "                    Y", "                              Y", "                                        Y")
                                hashh = random.sample(hashes, random.randint(1,1))
                                print(usr, hashh)
                                print()
                                time.sleep(.5)

                if True:
                    integer = (round(random.random()*25))
                    if integer > 20:
                        if random.choice([True, False]):
                            time.sleep(1.5)
                            t  = (round(random.random()*8))
                            for _ in range(t):
                                ctm = datetime.datetime.now()
                                hashes = ("y", "    y", "          y", "                    y", "                              y", "                                        y")
                                hashh = random.sample(hashes, random.randint(1,1))
                                print(usr, hashh)
                                print()
                                time.sleep(.5)

                if True:
                    integer = (round(random.random()*25))
                    if integer > 20:
                        if random.choice([True, False]):
                            time.sleep(1.5)
                            t  = (round(random.random()*8))
                            for _ in range(t):
                                ctm = datetime.datetime.now()
                                hashes = ("I", "    I", "          I", "                    I", "                              I", "                                        I", "                              III", "                                        III")
                                hashh = random.sample(hashes, random.randint(1,1))
                                print(usr, hashh)
                                print()
                                time.sleep(.5)

                if True:
                    integer = (round(random.random()*25))
                    if integer > 20:
                        if random.choice([True, False]):
                            time.sleep(1.5)
                            t  = (round(random.random()*8))
                            for _ in range(t):
                                ctm = datetime.datetime.now()
                                hashes = ("i", "    i", "          i", "                    i", "                              i", "                                        i", "                              iii", "                                        iii")
                                hashh = random.sample(hashes, random.randint(1,1))
                                print(usr, hashh)
                                print()
                                time.sleep(.5)

                if True:
                    integer = (round(random.random()*25))
                    if integer > 20:
                        if random.choice([True, False]):
                            time.sleep(1.5)
                            t  = (round(random.random()*8))
                            for _ in range(t):
                                ctm = datetime.datetime.now()
                                hashes = ("L", "    L", "          L", "                    L", "                              L", "                                        L")
                                hashh = random.sample(hashes, random.randint(1,1))
                                print(usr, hashh)
                                print()
                                time.sleep(.5)

                if True:
                    integer = (round(random.random()*25))
                    if integer > 20:
                        if random.choice([True, False]):
                            time.sleep(1.5)
                            t  = (round(random.random()*8))
                            for _ in range(t):
                                ctm = datetime.datetime.now()
                                hashes = ("l", "    l", "          l", "                    l", "                              l", "                                        l")
                                hashh = random.sample(hashes, random.randint(1,1))
                                print(usr, hashh)
                                print()
                                time.sleep(.5)

                if True:
                    integer = (round(random.random()*25))
                    if integer > 20:
                        if random.choice([True, False]):
                            time.sleep(1.5)
                            t  = (round(random.random()*8))
                            for _ in range(t):
                                ctm = datetime.datetime.now()
                                hashes = ("X", "    X", "          X", "                    X", "                              X", "                                        X")
                                hashh = random.sample(hashes, random.randint(1,1))
                                print(usr, hashh)
                                print()
                                time.sleep(.5)

                if True:
                    integer = (round(random.random()*25))
                    if integer > 20:
                        if random.choice([True, False]):
                            time.sleep(1.5)
                            t  = (round(random.random()*8))
                            for _ in range(t):
                                ctm = datetime.datetime.now()
                                hashes = ("x", "    x", "          x", "                    x", "                              x", "                                        x")
                                hashh = random.sample(hashes, random.randint(1,1))
                                print(usr, hashh)
                                print()
                                time.sleep(.5)

                if True:
                    integer = (round(random.random()*25))
                    if integer > 20:
                        if random.choice([True, False]):
                            time.sleep(1.5)
                            t  = (round(random.random()*8))
                            for _ in range(t):
                                ctm = datetime.datetime.now()
                                hashes = ("U", "    U", "          U", "                    U", "                              U", "                                        U")
                                hashh = random.sample(hashes, random.randint(1,1))
                                print(usr, hashh)
                                print()
                                time.sleep(.5)

                if True:
                    integer = (round(random.random()*25))
                    if integer > 20:
                        if random.choice([True, False]):
                            time.sleep(1.5)
                            t  = (round(random.random()*8))
                            for _ in range(t):
                                ctm = datetime.datetime.now()
                                hashes = ("u", "    u", "          u", "                    u", "                              u", "                                        u")
                                hashh = random.sample(hashes, random.randint(1,1))
                                print(usr, hashh)
                                print()
                                time.sleep(.5)

                if True:
                    integer = (round(random.random()*25))
                    if integer > 20:
                        if random.choice([True, False]):
                            time.sleep(1.5)
                            t  = (round(random.random()*8))
                            for _ in range(t):
                                ctm = datetime.datetime.now()
                                hashes = ("G", "    G", "          G", "                    G", "                              G", "                                        G")
                                hashh = random.sample(hashes, random.randint(1,1))
                                print(usr, hashh)
                                print()
                                time.sleep(.5)

                if True:
                    integer = (round(random.random()*25))
                    if integer > 20:
                        if random.choice([True, False]):
                            time.sleep(1.5)
                            t  = (round(random.random()*8))
                            for _ in range(t):
                                ctm = datetime.datetime.now()
                                hashes = ("g", "    g", "          g", "                    g", "                              g", "                                        g")
                                hashh = random.sample(hashes, random.randint(1,1))
                                print()
                                time.sleep(.5)

                if True:
                    integer = (round(random.random()*25))
                    if integer > 20:
                        if random.choice([True, False]):
                            time.sleep(1.5)
                            t  = (round(random.random()*8))
                            for _ in range(t):
                                ctm = datetime.datetime.now()
                                hashes = ("B", "    B", "          B", "                    B", "                              B", "                                        B")
                                hashh = random.sample(hashes, random.randint(1,1))
                                print(usr, hashh)
                                print()
                                time.sleep(.5)

                if True:
                    integer = (round(random.random()*25))
                    if integer > 20:
                        if random.choice([True, False]):
                            time.sleep(1.5)
                            t  = (round(random.random()*8))
                            for _ in range(t):
                                ctm = datetime.datetime.now()
                                hashes = ("b", "    b", "          b", "                    b", "                              b", "                                        b")
                                hashh = random.sample(hashes, random.randint(1,1))
                                print(usr, hashh)
                                print()
                                time.sleep(.5)

                if True:
                    integer = (round(random.random()*25))
                    if integer > 20:
                        if random.choice([True, False]):
                            time.sleep(1.5)
                            t  = (round(random.random()*8))
                            for _ in range(t):
                                ctm = datetime.datetime.now()
                                hashes = ("P", "    P", "          P", "                    P", "                              P", "                                        P")
                                hashh = random.sample(hashes, random.randint(1,1))
                                print(usr, hashh)
                                print()
                                time.sleep(.5)

                if True:
                    integer = (round(random.random()*25))
                    if integer > 20:
                        if random.choice([True, False]):
                            time.sleep(1.5)
                            t  = (round(random.random()*8))
                            for _ in range(t):
                                ctm = datetime.datetime.now()
                                hashes = ("p", "    p", "          p", "                    p", "                              p", "                                        p")
                                hashh = random.sample(hashes, random.randint(1,1))
                                print(usr, hashh)
                                print()
                                time.sleep(.5)

                if True:
                    integer = (round(random.random()*25))
                    if integer > 20:
                        if random.choice([True, False]):
                            time.sleep(1.5)
                            t  = (round(random.random()*8))
                            for _ in range(t):
                                ctm = datetime.datetime.now()
                                hashes = ("T", "    T", "          T", "                    T", "                              T", "                                        T")
                                hashh = random.sample(hashes, random.randint(1,1))
                                print(usr, hashh)
                                print()
                                time.sleep(.5)

                if True:
                    integer = (round(random.random()*25))
                    if integer > 20:
                        if random.choice([True, False]):
                            time.sleep(1.5)
                            t  = (round(random.random()*8))
                            for _ in range(t):
                                ctm = datetime.datetime.now()
                                hashes = ("t", "    t", "          t", "                    t", "                              t", "                                        t")
                                hashh = random.sample(hashes, random.randint(1,1))
                                print(usr, hashh)
                                print()
                                time.sleep(.5)

                if True:
                    integer = (round(random.random()*25))
                    if integer > 20:
                        if random.choice([True, False]):
                            time.sleep(1.5)
                            t  = (round(random.random()*8))
                            for _ in range(t):
                                ctm = datetime.datetime.now()
                                hashes = ("C", "    C", "          C", "                    C", "                              C", "                                        C")
                                hashh = random.sample(hashes, random.randint(1,1))
                                print(usr, hashh)
                                print()
                                time.sleep(.5)

                if True:
                    integer = (round(random.random()*25))
                    if integer > 20:
                        if random.choice([True, False]):
                            time.sleep(1.5)
                            t  = (round(random.random()*8))
                            for _ in range(t):
                                ctm = datetime.datetime.now()
                                hashes = ("c", "    c", "          c", "                    c", "                              c", "                                        c")
                                hashh = random.sample(hashes, random.randint(1,1))
                                print(usr, hashh)
                                print()
                                time.sleep(.5)

                if True:
                    integer = (round(random.random()*25))
                    if integer > 20:
                        if random.choice([True, False]):
                            time.sleep(1.5)
                            t  = (round(random.random()*8))
                            for _ in range(t):
                                ctm = datetime.datetime.now()
                                hashes = ("Z", "    Z", "          Z", "                    Z", "                              Z", "                                        Z")
                                hashh = random.sample(hashes, random.randint(1,1))
                                print(usr, hashh)
                                print()
                                time.sleep(.5)

                if True:
                    integer = (round(random.random()*25))
                    if integer > 20:
                        if random.choice([True, False]):
                            time.sleep(1.5)
                            t  = (round(random.random()*8))
                            for _ in range(t):
                                ctm = datetime.datetime.now()
                                hashes = ("z", "    z", "          z", "                    z", "                              z", "                                        z")
                                hashh = random.sample(hashes, random.randint(1,1))
                                print(usr, hashh)
                                print()
                                time.sleep(.5)

                if True:
                    integer = (round(random.random()*25))
                    if integer > 17:
                        if random.choice([True, False]):
                            time.sleep(1.5)
                            t  = (round(random.random()*10))
                            for _ in range(t):
                                ctm = datetime.datetime.now()
                                hashes = ("-======================", "-================", "-======================", "-================")
                                hashh = random.sample(hashes, random.randint(1,1))
                                print(usr, hashh)
                                print()
                                time.sleep(.5)

                if True:
                    integer = (round(random.random()*25))
                    if integer > 15:
                        if random.choice([True, False]):
                            time.sleep(1.5)
                            t  = (round(random.random()*10))
                            for _ in range(t):
                                ctm = datetime.datetime.now()
                                hashes = ("#", "#####", "##########", "##########################", "##########################", "##########################")
                                hashh = random.sample(hashes, random.randint(1,1))
                                print(usr, hashh)
                                print()
                                time.sleep(.5)

        def MAIc():
            import time
            print("Ctrl+C to stop")
            print()
            def generate_random_result():
                time.sleep(1.5)
                print()
                ctm = datetime.datetime.now()
                def generate_random_letters():
                    random1 = random.choice(string.ascii_letters)
                    random2 = random.choice(string.ascii_letters)
                    random3 = random.choice(string.ascii_letters)
                    letters = [random1, random2, random3]
                    random.shuffle(letters)
                    return letters
                random_letters = generate_random_letters()
                sitch  = (round(random.random()*9999,4))
                asc = "ascii:"
                print(asc, usr, random_letters, sitch, ctm)
                pr1 = (round(random.random()*99999999999999999999999999999999999999999))
                pr2 = (round(random.random()*99999999999999999999999999999999999999999))
                pr3 = (round(random.random()*99999999999999999999999999999999999999999))
                pr4 = (round(random.random()*99999999999999999999999999999999999999999))
                pr5 = (round(random.random()*99999999999999999999999999999999999999999))
                pr6 = (round(random.random()*99999999999999999999999999999999999999999))
                pr7 = (round(random.random()*99999999999999999999999999999999999999999))
                pr8 = (round(random.random()*99999999999999999999999999999999999999999))
                pr9 = (round(random.random()*99999999999999999999999999999999999999999))
                pr10 = (round(random.random()*99999999999999999999999999999999999999999))
                pr11 = (round(random.random()*99999999999999999999999999999999999999999))
                pr12 = (round(random.random()*99999999999999999999999999999999999999999))
                print()
                print(pr1)
                print(pr2)
                print(pr3)
                print(pr4)
                print(pr5)
                print(pr6)
                print(pr7)
                print(pr8)
                print(pr9)
                print(pr10)
                print(pr11)
                print(pr12)
                print()
                time.sleep(2)
                if True:
                    nano = (diction)
                    acad = (acadlist)
                    integer = (round(random.random()*25))
                    if integer > 15:
                        if random.choice([True, False]):
                            time.sleep(1.5)
                            ct = datetime.datetime.now()
                            tag = "a-tag:"
                            ctm = datetime.datetime.now()
                            def generate_random_letters():
                                random1 = random.choice(string.ascii_letters)
                                random2 = random.choice(string.ascii_letters)
                                random3 = random.choice(string.ascii_letters)
                                letters = [random1, random2, random3]
                                random.shuffle(letters)
                                return letters
                            random_letters = generate_random_letters()
                            sitch  = (round(random.random()*9999,4))
                            kchat = random.choices(nano, k=random.randint(1,8))
                            kchat2 = random.choices(acad, k=random.randint(1,7))
                            print()
                            print(usr, random_letters, sitch, kchat2, kchat, ctm)
                            print()
                            time.sleep(4.2)
                if True:
                    integer = (round(random.random()*25))
                    if integer > 15:
                        if random.choice([True, False]):
                            time.sleep(1.5)
                            t  = (round(random.random()*10))
                            for _ in range(t):
                                ctm = datetime.datetime.now()
                                hashes = ("#", "#####", "##########", "##########################", "##########################", "##########################")
                                hashh = random.sample(hashes, random.randint(1,1))
                                print(usr, hashh)
                                print()
                                time.sleep(.5)
                if True:
                    integer = (round(random.random()*25))
                    if integer > 20:
                        if random.choice([True, False]):
                            time.sleep(1.5)
                            t  = (round(random.random()*8))
                            for _ in range(t):
                                ctm = datetime.datetime.now()
                                hashes = ("V", "    V", "          V", "                    V", "                              V", "                                        V")
                                hashh = random.sample(hashes, random.randint(1,1))
                                print(usr, hashh)
                                print()
                                time.sleep(.5)

                if True:
                    integer = (round(random.random()*25))
                    if integer > 20:
                        if random.choice([True, False]):
                            time.sleep(1.5)
                            t  = (round(random.random()*8))
                            for _ in range(t):
                                ctm = datetime.datetime.now()
                                hashes = ("v", "    v", "          v", "                    v", "                              v", "                                        v")
                                hashh = random.sample(hashes, random.randint(1,1))
                                print(usr, hashh)
                                print()
                                time.sleep(.5)

                if True:
                    integer = (round(random.random()*25))
                    if integer > 20:
                        if random.choice([True, False]):
                            time.sleep(1.5)
                            t  = (round(random.random()*8))
                            for _ in range(t):
                                ctm = datetime.datetime.now()
                                hashes = ("O", "    O", "          O", "                    O", "                              O", "                                        O")
                                hashh = random.sample(hashes, random.randint(1,1))
                                print(usr, hashh)
                                print()
                                time.sleep(.5)

                if True:
                    integer = (round(random.random()*25))
                    if integer > 20:
                        if random.choice([True, False]):
                            time.sleep(1.5)
                            t  = (round(random.random()*8))
                            for _ in range(t):
                                ctm = datetime.datetime.now()
                                hashes = ("o", "    o", "          o", "                    o", "                              o", "                                        o")
                                hashh = random.sample(hashes, random.randint(1,1))
                                print(usr, hashh)
                                print()
                                time.sleep(.5)

                if True:
                    integer = (round(random.random()*25))
                    if integer > 20:
                        if random.choice([True, False]):
                            time.sleep(1.5)
                            t  = (round(random.random()*8))
                            for _ in range(t):
                                ctm = datetime.datetime.now()
                                hashes = ("0", "    0", "          0", "                    0", "                              0", "                                        0")
                                hashh = random.sample(hashes, random.randint(1,1))
                                print(usr, hashh)
                                print()
                                time.sleep(.5)

                if True:
                    integer = (round(random.random()*25))
                    if integer > 20:
                        if random.choice([True, False]):
                            time.sleep(1.5)
                            t  = (round(random.random()*8))
                            for _ in range(t):
                                ctm = datetime.datetime.now()
                                hashes = ("H", "    H", "          H", "                    H", "                              H", "                                        H")
                                hashh = random.sample(hashes, random.randint(1,1))
                                print(usr, hashh)
                                print()
                                time.sleep(.5)

                if True:
                    integer = (round(random.random()*25))
                    if integer > 20:
                        if random.choice([True, False]):
                            time.sleep(1.5)
                            t  = (round(random.random()*8))
                            for _ in range(t):
                                ctm = datetime.datetime.now()
                                hashes = ("h", "    h", "          h", "                    h", "                              h", "                                        h")
                                hashh = random.sample(hashes, random.randint(1,1))
                                print(usr, hashh)
                                print()
                                time.sleep(.5)

                if True:
                    integer = (round(random.random()*25))
                    if integer > 20:
                        if random.choice([True, False]):
                            time.sleep(1.5)
                            t  = (round(random.random()*8))
                            for _ in range(t):
                                ctm = datetime.datetime.now()
                                hashes = ("Q", "    Q", "          Q", "                    Q", "                              Q", "                                        Q")
                                hashh = random.sample(hashes, random.randint(1,1))
                                print(usr, hashh)
                                print()
                                time.sleep(.5)

                if True:
                    integer = (round(random.random()*25))
                    if integer > 20:
                        if random.choice([True, False]):
                            time.sleep(1.5)
                            t  = (round(random.random()*8))
                            for _ in range(t):
                                ctm = datetime.datetime.now()
                                hashes = ("q", "    q", "          q", "                    q", "                              q", "                                        q")
                                hashh = random.sample(hashes, random.randint(1,1))
                                print(usr, hashh)
                                print()
                                time.sleep(.5)

                if True:
                    integer = (round(random.random()*25))
                    if integer > 20:
                        if random.choice([True, False]):
                            time.sleep(1.5)
                            t  = (round(random.random()*8))
                            for _ in range(t):
                                ctm = datetime.datetime.now()
                                hashes = ("Y", "    Y", "          Y", "                    Y", "                              Y", "                                        Y")
                                hashh = random.sample(hashes, random.randint(1,1))
                                print(usr, hashh)
                                print()
                                time.sleep(.5)

                if True:
                    integer = (round(random.random()*25))
                    if integer > 20:
                        if random.choice([True, False]):
                            time.sleep(1.5)
                            t  = (round(random.random()*8))
                            for _ in range(t):
                                ctm = datetime.datetime.now()
                                hashes = ("y", "    y", "          y", "                    y", "                              y", "                                        y")
                                hashh = random.sample(hashes, random.randint(1,1))
                                print(usr, hashh)
                                print()
                                time.sleep(.5)

                if True:
                    integer = (round(random.random()*25))
                    if integer > 20:
                        if random.choice([True, False]):
                            time.sleep(1.5)
                            t  = (round(random.random()*8))
                            for _ in range(t):
                                ctm = datetime.datetime.now()
                                hashes = ("I", "    I", "          I", "                    I", "                              I", "                                        I", "                              III", "                                        III")
                                hashh = random.sample(hashes, random.randint(1,1))
                                print(usr, hashh)
                                print()
                                time.sleep(.5)

                if True:
                    integer = (round(random.random()*25))
                    if integer > 20:
                        if random.choice([True, False]):
                            time.sleep(1.5)
                            t  = (round(random.random()*8))
                            for _ in range(t):
                                ctm = datetime.datetime.now()
                                hashes = ("i", "    i", "          i", "                    i", "                              i", "                                        i", "                              iii", "                                        iii")
                                hashh = random.sample(hashes, random.randint(1,1))
                                print(usr, hashh)
                                print()
                                time.sleep(.5)

                if True:
                    integer = (round(random.random()*25))
                    if integer > 20:
                        if random.choice([True, False]):
                            time.sleep(1.5)
                            t  = (round(random.random()*8))
                            for _ in range(t):
                                ctm = datetime.datetime.now()
                                hashes = ("L", "    L", "          L", "                    L", "                              L", "                                        L")
                                hashh = random.sample(hashes, random.randint(1,1))
                                print(usr, hashh)
                                print()
                                time.sleep(.5)

                if True:
                    integer = (round(random.random()*25))
                    if integer > 20:
                        if random.choice([True, False]):
                            time.sleep(1.5)
                            t  = (round(random.random()*8))
                            for _ in range(t):
                                ctm = datetime.datetime.now()
                                hashes = ("l", "    l", "          l", "                    l", "                              l", "                                        l")
                                hashh = random.sample(hashes, random.randint(1,1))
                                print(usr, hashh)
                                print()
                                time.sleep(.5)

                if True:
                    integer = (round(random.random()*25))
                    if integer > 20:
                        if random.choice([True, False]):
                            time.sleep(1.5)
                            t  = (round(random.random()*8))
                            for _ in range(t):
                                ctm = datetime.datetime.now()
                                hashes = ("X", "    X", "          X", "                    X", "                              X", "                                        X")
                                hashh = random.sample(hashes, random.randint(1,1))
                                print(usr, hashh)
                                print()
                                time.sleep(.5)

                if True:
                    integer = (round(random.random()*25))
                    if integer > 20:
                        if random.choice([True, False]):
                            time.sleep(1.5)
                            t  = (round(random.random()*8))
                            for _ in range(t):
                                ctm = datetime.datetime.now()
                                hashes = ("x", "    x", "          x", "                    x", "                              x", "                                        x")
                                hashh = random.sample(hashes, random.randint(1,1))
                                print(usr, hashh)
                                print()
                                time.sleep(.5)

                if True:
                    integer = (round(random.random()*25))
                    if integer > 20:
                        if random.choice([True, False]):
                            time.sleep(1.5)
                            t  = (round(random.random()*8))
                            for _ in range(t):
                                ctm = datetime.datetime.now()
                                hashes = ("U", "    U", "          U", "                    U", "                              U", "                                        U")
                                hashh = random.sample(hashes, random.randint(1,1))
                                print(usr, hashh)
                                print()
                                time.sleep(.5)

                if True:
                    integer = (round(random.random()*25))
                    if integer > 20:
                        if random.choice([True, False]):
                            time.sleep(1.5)
                            t  = (round(random.random()*8))
                            for _ in range(t):
                                ctm = datetime.datetime.now()
                                hashes = ("u", "    u", "          u", "                    u", "                              u", "                                        u")
                                hashh = random.sample(hashes, random.randint(1,1))
                                print(usr, hashh)
                                print()
                                time.sleep(.5)

                if True:
                    integer = (round(random.random()*25))
                    if integer > 20:
                        if random.choice([True, False]):
                            time.sleep(1.5)
                            t  = (round(random.random()*8))
                            for _ in range(t):
                                ctm = datetime.datetime.now()
                                hashes = ("G", "    G", "          G", "                    G", "                              G", "                                        G")
                                hashh = random.sample(hashes, random.randint(1,1))
                                print(usr, hashh)
                                print()
                                time.sleep(.5)

                if True:
                    integer = (round(random.random()*25))
                    if integer > 20:
                        if random.choice([True, False]):
                            time.sleep(1.5)
                            t  = (round(random.random()*8))
                            for _ in range(t):
                                ctm = datetime.datetime.now()
                                hashes = ("g", "    g", "          g", "                    g", "                              g", "                                        g")
                                hashh = random.sample(hashes, random.randint(1,1))
                                print(usr, hashh)
                                print()
                                time.sleep(.5)

                if True:
                    integer = (round(random.random()*25))
                    if integer > 20:
                        if random.choice([True, False]):
                            time.sleep(1.5)
                            t  = (round(random.random()*8))
                            for _ in range(t):
                                ctm = datetime.datetime.now()
                                hashes = ("B", "    B", "          B", "                    B", "                              B", "                                        B")
                                hashh = random.sample(hashes, random.randint(1,1))
                                print(usr, hashh)
                                print()
                                time.sleep(.5)

                if True:
                    integer = (round(random.random()*25))
                    if integer > 20:
                        if random.choice([True, False]):
                            time.sleep(1.5)
                            t  = (round(random.random()*8))
                            for _ in range(t):
                                ctm = datetime.datetime.now()
                                hashes = ("b", "    b", "          b", "                    b", "                              b", "                                        b")
                                hashh = random.sample(hashes, random.randint(1,1))
                                print(usr, hashh)
                                print()
                                time.sleep(.5)

                if True:
                    integer = (round(random.random()*25))
                    if integer > 20:
                        if random.choice([True, False]):
                            time.sleep(1.5)
                            t  = (round(random.random()*8))
                            for _ in range(t):
                                ctm = datetime.datetime.now()
                                hashes = ("P", "    P", "          P", "                    P", "                              P", "                                        P")
                                hashh = random.sample(hashes, random.randint(1,1))
                                print(usr, hashh)
                                print()
                                time.sleep(.5)

                if True:
                    integer = (round(random.random()*25))
                    if integer > 20:
                        if random.choice([True, False]):
                            time.sleep(1.5)
                            t  = (round(random.random()*8))
                            for _ in range(t):
                                ctm = datetime.datetime.now()
                                hashes = ("p", "    p", "          p", "                    p", "                              p", "                                        p")
                                hashh = random.sample(hashes, random.randint(1,1))
                                print(usr, hashh)
                                print()
                                time.sleep(.5)

                if True:
                    integer = (round(random.random()*25))
                    if integer > 20:
                        if random.choice([True, False]):
                            time.sleep(1.5)
                            t  = (round(random.random()*8))
                            for _ in range(t):
                                ctm = datetime.datetime.now()
                                hashes = ("T", "    T", "          T", "                    T", "                              T", "                                        T")
                                hashh = random.sample(hashes, random.randint(1,1))
                                print(usr, hashh)
                                print()
                                time.sleep(.5)

                if True:
                    integer = (round(random.random()*25))
                    if integer > 20:
                        if random.choice([True, False]):
                            time.sleep(1.5)
                            t  = (round(random.random()*8))
                            for _ in range(t):
                                ctm = datetime.datetime.now()
                                hashes = ("t", "    t", "          t", "                    t", "                              t", "                                        t")
                                hashh = random.sample(hashes, random.randint(1,1))
                                print(usr, hashh)
                                print()
                                time.sleep(.5)

                if True:
                    integer = (round(random.random()*25))
                    if integer > 20:
                        if random.choice([True, False]):
                            time.sleep(1.5)
                            t  = (round(random.random()*8))
                            for _ in range(t):
                                ctm = datetime.datetime.now()
                                hashes = ("C", "    C", "          C", "                    C", "                              C", "                                        C")
                                hashh = random.sample(hashes, random.randint(1,1))
                                print(usr, hashh)
                                print()
                                time.sleep(.5)

                if True:
                    integer = (round(random.random()*25))
                    if integer > 20:
                        if random.choice([True, False]):
                            time.sleep(1.5)
                            t  = (round(random.random()*8))
                            for _ in range(t):
                                ctm = datetime.datetime.now()
                                hashes = ("c", "    c", "          c", "                    c", "                              c", "                                        c")
                                hashh = random.sample(hashes, random.randint(1,1))
                                print(usr, hashh)
                                print()
                                time.sleep(.5)

                if True:
                    integer = (round(random.random()*25))
                    if integer > 20:
                        if random.choice([True, False]):
                            time.sleep(1.5)
                            t  = (round(random.random()*8))
                            for _ in range(t):
                                ctm = datetime.datetime.now()
                                hashes = ("Z", "    Z", "          Z", "                    Z", "                              Z", "                                        Z")
                                hashh = random.sample(hashes, random.randint(1,1))
                                print(usr, hashh)
                                print()
                                time.sleep(.5)

                if True:
                    integer = (round(random.random()*25))
                    if integer > 20:
                        if random.choice([True, False]):
                            time.sleep(1.5)
                            t  = (round(random.random()*8))
                            for _ in range(t):
                                ctm = datetime.datetime.now()
                                hashes = ("z", "    z", "          z", "                    z", "                              z", "                                        z")
                                hashh = random.sample(hashes, random.randint(1,1))
                                print(usr, hashh)
                                print()
                                time.sleep(.5)

                if True:
                    integer = (round(random.random()*25))
                    if integer > 17:
                        if random.choice([True, False]):
                            time.sleep(1.5)
                            t  = (round(random.random()*10))
                            for _ in range(t):
                                ctm = datetime.datetime.now()
                                hashes = ("-======================", "-================", "-======================", "-================")
                                hashh = random.sample(hashes, random.randint(1,1))
                                print(usr, hashh)
                                print()
                                time.sleep(.5)

                if True:
                    integer = (round(random.random()*25))
                    if integer > 15:
                        if random.choice([True, False]):
                            time.sleep(1.5)
                            t  = (round(random.random()*10))
                            for _ in range(t):
                                ctm = datetime.datetime.now()
                                hashes = ("#", "#####", "##########", "##########################", "##########################", "##########################")
                                hashh = random.sample(hashes, random.randint(1,1))
                                print(usr, hashh)
                                print()
                                time.sleep(.5)

            def main_loop():
                while True:
                    generate_random_result()

            try:
                main_loop()
            except KeyboardInterrupt:
                print("\nStopped by user.")

        def guard():
            while True:
                try:
                    fps = float(input("Indicate speed in (halfed) seconds: "))
                except ValueError:
                    print("Invalid value")
                else:
                    break
            name = input("guard_name: ")
            fps
            print()
            print("Ctrl+C to stop")
            time.sleep(3.5)
            def generate_random_result():
                time.sleep(fps)
                ctm = datetime.datetime.now()
                def generate_random_letters():
                    random1 = random.choice(string.ascii_letters)
                    random2 = random.choice(string.ascii_letters)
                    random3 = random.choice(string.ascii_letters)
                    letters = [random1, random2, random3]
                    random.shuffle(letters)
                    return letters
                random_letters = generate_random_letters()
                sitch  = (round(random.random()*9999,4))
                asc = "guard:"
                print()
                print(asc, usr, name, random_letters, sitch, ctm)
                pr1 = (round(random.random()*99999999999999999999999999999999999999999))
                pr2 = (round(random.random()*99999999999999999999999999999999999999999))
                pr3 = (round(random.random()*99999999999999999999999999999999999999999))
                pr4 = (round(random.random()*99999999999999999999999999999999999999999))
                pr5 = (round(random.random()*99999999999999999999999999999999999999999))
                pr6 = (round(random.random()*99999999999999999999999999999999999999999))
                pr7 = (round(random.random()*99999999999999999999999999999999999999999))
                pr8 = (round(random.random()*99999999999999999999999999999999999999999))
                pr9 = (round(random.random()*99999999999999999999999999999999999999999))
                pr10 = (round(random.random()*99999999999999999999999999999999999999999))
                pr11 = (round(random.random()*99999999999999999999999999999999999999999))
                pr12 = (round(random.random()*99999999999999999999999999999999999999999))
                print()
                print(pr1)
                print(pr2)
                print(pr3)
                print(pr4)
                print(pr5)
                print(pr6)
                print(pr7)
                print(pr8)
                print(pr9)
                print(pr10)
                print(pr11)
                print(pr12)
                print()

            def main_loop():
                while True:
                    generate_random_result()

            try:
                main_loop()
            except KeyboardInterrupt:
                print("\nStopped by user.")

        def frames():
            while True:
                try:
                    number = int(input("Indicate number of (frames) results: "))
                    fps = float(input("Indicate speed in (halfed) seconds: "))
                except ValueError:
                    print("Invalid value")
                else:
                    break
            number
            fps
            name = input("frames name: ")
            for _ in range(number):
                time.sleep(fps)
                ctm = datetime.datetime.now()
                def generate_random_letters():
                    random1 = random.choice(string.ascii_letters)
                    random2 = random.choice(string.ascii_letters)
                    random3 = random.choice(string.ascii_letters)
                    letters = [random1, random2, random3]
                    random.shuffle(letters)
                    return letters
                random_letters = generate_random_letters()
                sitch  = (round(random.random()*9999,4))
                asc = "frames:"
                print()
                print(asc, usr, name, random_letters, sitch, ctm)
                pr1 = (round(random.random()*99999999999999999999999999999999999999999))
                pr2 = (round(random.random()*99999999999999999999999999999999999999999))
                pr3 = (round(random.random()*99999999999999999999999999999999999999999))
                pr4 = (round(random.random()*99999999999999999999999999999999999999999))
                pr5 = (round(random.random()*99999999999999999999999999999999999999999))
                pr6 = (round(random.random()*99999999999999999999999999999999999999999))
                pr7 = (round(random.random()*99999999999999999999999999999999999999999))
                pr8 = (round(random.random()*99999999999999999999999999999999999999999))
                pr9 = (round(random.random()*99999999999999999999999999999999999999999))
                pr10 = (round(random.random()*99999999999999999999999999999999999999999))
                pr11 = (round(random.random()*99999999999999999999999999999999999999999))
                pr12 = (round(random.random()*99999999999999999999999999999999999999999))
                print()
                print(pr1)
                print(pr2)
                print(pr3)
                print(pr4)
                print(pr5)
                print(pr6)
                print(pr7)
                print(pr8)
                print(pr9)
                print(pr10)
                print(pr11)
                print(pr12)
                print()

        def oscillator():
            print("Ctrl+C to stop")
            print()
            def generate_random_result():
                meter = ["                              ", "*                             ", " *                            ", "  *                           ", "   *                          ", "    *                         ", "     *                        ", "      *                       ", "       *                      ", "        *                     ", "         *                    ", "          *                   ", "           *                  ", "            *                 ", "             *                ", "              *               ", "               *              ", "                *             ", "                 *            ", "                  *           ", "                   *          ", "                    *         ", "                     *        ", "                      *       ", "                       *      ", "                        *     ", "                         *    ", "                          *   ", "                           *  ", "                            * ", "                             *"]
                oscill = random.sample(meter, 1)
                print(oscill)

            def main_loop():
                while True:
                    time.sleep(.1)
                    integer = (round(random.random()*5))
                    if integer > 2:
                        generate_random_result()

            try:
                main_loop()
            except KeyboardInterrupt:
                print("\nStopped by user.")

        def toscillator():
            print("Ctrl+C to stop")
            print()

            while True:
                try:
                    buffer = float(input("time-buffer in seconds: "))
                except ValueError:
                    print("Invalid value")
                else:
                    break

            def generate_random_result():
                meter = ["                              ", "*                             ", " *                            ", "  *                           ", "   *                          ", "    *                         ", "     *                        ", "      *                       ", "       *                      ", "        *                     ", "         *                    ", "          *                   ", "           *                  ", "            *                 ", "             *                ", "              *               ", "               *              ", "                *             ", "                 *            ", "                  *           ", "                   *          ", "                    *         ", "                     *        ", "                      *       ", "                       *      ", "                        *     ", "                         *    ", "                          *   ", "                           *  ", "                            * ", "                             *"]
                oscill = random.sample(meter, 1)
                print(oscill)

            def main_loop():
                while True:
                    time.sleep(buffer)
                    generate_random_result()

            try:
                main_loop()
            except KeyboardInterrupt:
                print("\nStopped by user.")

        def burner():
            nano = (diction)
            print("Not recording")
            print()
            time.sleep(.4)
            title = input("burn name: ")
            ct = datetime.datetime.now()
            monitor = "burner-start:"
            print(usr, monitor, title, ct)
            print()
            print()
            def generate_random_result():
                ctm = datetime.datetime.now()
                def generate_random_letters():
                    random1 = random.choice(string.ascii_letters)
                    random2 = random.choice(string.ascii_letters)
                    random3 = random.choice(string.ascii_letters)
                    random4 = random.choice(string.ascii_letters)
                    random5 = random.choice(string.ascii_letters)
                    random6 = random.choice(string.ascii_letters)
                    random7 = random.choice(string.ascii_letters)
                    random8 = random.choice(string.ascii_letters)
                    random9 = random.choice(string.ascii_letters)
                    random10 = random.choice(string.ascii_letters)
                    random11 = random.choice(string.ascii_letters)
                    random12 = random.choice(string.ascii_letters)
                    random13 = random.choice(string.ascii_letters)
                    random14 = random.choice(string.ascii_letters)
                    random15 = random.choice(string.ascii_letters)
                    random16 = random.choice(string.ascii_letters)
                    random17 = random.choice(string.ascii_letters)
                    random18 = random.choice(string.ascii_letters)
                    random19 = random.choice(string.ascii_letters)
                    random20 = random.choice(string.ascii_letters)
                    letters = [random1, random2, random3, random4, random5, random6, random7, random8, random9, random10, random11, random12, random13, random14, random15, random16, random17, random18, random19, random20]
                    return letters
                random_letters = generate_random_letters()
                sitch  = (round(random.random()*999999999999999,5))
                kchat = random.sample(nano, random.randint(1,2))
                print(title, ctm, random_letters, sitch, kchat)

        def cburner():
            chi_char = (chi_chars)
            print("Not recording")
            print()
            time.sleep(.4)
            title = input("c-burn name: ")
            ct = datetime.datetime.now()
            monitor = "c-burner-start:"
            print(usr, monitor, title, ct)
            print()
            print()
            def generate_random_result():
                ctm = datetime.datetime.now()
                def generate_random_characters():
                    random1 = random.choice(chi_char)
                    random2 = random.choice(chi_char)
                    random3 = random.choice(chi_char)
                    random4 = random.choice(chi_char)
                    random5 = random.choice(chi_char)
                    random6 = random.choice(chi_char)
                    random7 = random.choice(chi_char)
                    random8 = random.choice(chi_char)
                    random9 = random.choice(chi_char)
                    random10 = random.choice(chi_char)
                    random11 = random.choice(chi_char)
                    random12 = random.choice(chi_char)
                    random13 = random.choice(chi_char)
                    random14 = random.choice(chi_char)
                    random15 = random.choice(chi_char)
                    random16 = random.choice(chi_char)
                    random17 = random.choice(chi_char)
                    random18 = random.choice(chi_char)
                    random19 = random.choice(chi_char)
                    random20 = random.choice(chi_char)
                    characters = [random1, random2, random3, random4, random5, random6, random7, random8, random9, random10, random11, random12, random13, random14, random15, random16, random17, random18, random19, random20]
                    return characters
                random_characters = generate_random_characters()
                sitch  = (round(random.random()*999999999999999,5))
                print(title, ctm, random_characters, sitch)
            
            def main_loop():
                while True:
                    time.sleep(random.randint(0,1))
                    integer = (round(random.random()*10))
                    if integer > 5:
                        if random.choice([True, False]):
                            generate_random_result()

            try:
                main_loop()
            except KeyboardInterrupt:
                print("\nStopped by user.")

        def jburner():
            chi_char = (katakana)
            print("Not recording")
            print()
            time.sleep(.4)
            title = input("j-burn name: ")
            ct = datetime.datetime.now()
            monitor = "j-burner-start:"
            print(usr, monitor, title, ct)
            print()
            print()
            def generate_random_result():
                ctm = datetime.datetime.now()
                def generate_random_characters():
                    random1 = random.choice(chi_char)
                    random2 = random.choice(chi_char)
                    random3 = random.choice(chi_char)
                    random4 = random.choice(chi_char)
                    random5 = random.choice(chi_char)
                    random6 = random.choice(chi_char)
                    random7 = random.choice(chi_char)
                    random8 = random.choice(chi_char)
                    random9 = random.choice(chi_char)
                    random10 = random.choice(chi_char)
                    random11 = random.choice(chi_char)
                    random12 = random.choice(chi_char)
                    random13 = random.choice(chi_char)
                    random14 = random.choice(chi_char)
                    random15 = random.choice(chi_char)
                    random16 = random.choice(chi_char)
                    random17 = random.choice(chi_char)
                    random18 = random.choice(chi_char)
                    random19 = random.choice(chi_char)
                    random20 = random.choice(chi_char)
                    characters = [random1, random2, random3, random4, random5, random6, random7, random8, random9, random10, random11, random12, random13, random14, random15, random16, random17, random18, random19, random20]
                    return characters
                random_characters = generate_random_characters()
                sitch  = (round(random.random()*999999999999999,5))
                print(title, ctm, random_characters, sitch)
            
            def main_loop():
                while True:
                    time.sleep(random.randint(0,1))
                    integer = (round(random.random()*10))
                    if integer > 5:
                        if random.choice([True, False]):
                            generate_random_result()

            try:
                main_loop()
            except KeyboardInterrupt:
                print("\nStopped by user.")

        def tburner():
            nano = (diction)
            print("Not recording")
            print()
            time.sleep(.4)
            title = input("burn name: ")
            while True:
                try:
                    buffer = float(input("time-buffer in seconds: "))
                except ValueError:
                    print("Invalid value")
                else:
                    break
            ct = datetime.datetime.now()
            monitor = "burner-start:"
            print(usr, monitor, title, ct)
            print()
            print()
            def generate_random_result():
                ctm = datetime.datetime.now()
                def generate_random_letters():
                    random1 = random.choice(string.ascii_letters)
                    random2 = random.choice(string.ascii_letters)
                    random3 = random.choice(string.ascii_letters)
                    random4 = random.choice(string.ascii_letters)
                    random5 = random.choice(string.ascii_letters)
                    random6 = random.choice(string.ascii_letters)
                    random7 = random.choice(string.ascii_letters)
                    random8 = random.choice(string.ascii_letters)
                    random9 = random.choice(string.ascii_letters)
                    random10 = random.choice(string.ascii_letters)
                    random11 = random.choice(string.ascii_letters)
                    random12 = random.choice(string.ascii_letters)
                    random13 = random.choice(string.ascii_letters)
                    random14 = random.choice(string.ascii_letters)
                    random15 = random.choice(string.ascii_letters)
                    random16 = random.choice(string.ascii_letters)
                    random17 = random.choice(string.ascii_letters)
                    random18 = random.choice(string.ascii_letters)
                    random19 = random.choice(string.ascii_letters)
                    random20 = random.choice(string.ascii_letters)
                    letters = [random1, random2, random3, random4, random5, random6, random7, random8, random9, random10, random11, random12, random13, random14, random15, random16, random17, random18, random19, random20]
                    return letters
                random_letters = generate_random_letters()
                sitch  = (round(random.random()*999999999999999,5))
                kchat = random.sample(nano, random.randint(1,2))
                print(title, ctm, random_letters, sitch, kchat)
            
            def main_loop():
                while True:
                    time.sleep(buffer)
                    generate_random_result()

            try:
                main_loop()
            except KeyboardInterrupt:
                print("\nStopped by user.")

        def ctburner():
            chi_char = (chi_chars)
            print("Not recording")
            print()
            time.sleep(.4)
            title = input("c-burn name: ")
            while True:
                try:
                    buffer = float(input("time-buffer in seconds: "))
                except ValueError:
                    print("Invalid value")
                else:
                    break
            ct = datetime.datetime.now()
            monitor = "c-burner-start:"
            print(usr, monitor, title, ct)
            print()
            print()
            def generate_random_result():
                ctm = datetime.datetime.now()
                def generate_random_characters():
                    random1 = random.choice(chi_char)
                    random2 = random.choice(chi_char)
                    random3 = random.choice(chi_char)
                    random4 = random.choice(chi_char)
                    random5 = random.choice(chi_char)
                    random6 = random.choice(chi_char)
                    random7 = random.choice(chi_char)
                    random8 = random.choice(chi_char)
                    random9 = random.choice(chi_char)
                    random10 = random.choice(chi_char)
                    random11 = random.choice(chi_char)
                    random12 = random.choice(chi_char)
                    random13 = random.choice(chi_char)
                    random14 = random.choice(chi_char)
                    random15 = random.choice(chi_char)
                    random16 = random.choice(chi_char)
                    random17 = random.choice(chi_char)
                    random18 = random.choice(chi_char)
                    random19 = random.choice(chi_char)
                    random20 = random.choice(chi_char)
                    characters = [random1, random2, random3, random4, random5, random6, random7, random8, random9, random10, random11, random12, random13, random14, random15, random16, random17, random18, random19, random20]
                    return characters
                random_characters = generate_random_characters()
                sitch  = (round(random.random()*999999999999999,5))
                print(title, ctm, random_characters, sitch)
            
            def main_loop():
                while True:
                    time.sleep(buffer)
                    generate_random_result()

            try:
                main_loop()
            except KeyboardInterrupt:
                print("\nStopped by user.")

        def jtburner():
            chi_char = (katakana)
            print("Not recording")
            print()
            time.sleep(.4)
            title = input("j-burn name: ")
            while True:
                try:
                    buffer = float(input("time-buffer in seconds: "))
                except ValueError:
                    print("Invalid value")
                else:
                    break
            ct = datetime.datetime.now()
            monitor = "j-burner-start:"
            print(usr, monitor, title, ct)
            print()
            print()
            def generate_random_result():
                ctm = datetime.datetime.now()
                def generate_random_characters():
                    random1 = random.choice(chi_char)
                    random2 = random.choice(chi_char)
                    random3 = random.choice(chi_char)
                    random4 = random.choice(chi_char)
                    random5 = random.choice(chi_char)
                    random6 = random.choice(chi_char)
                    random7 = random.choice(chi_char)
                    random8 = random.choice(chi_char)
                    random9 = random.choice(chi_char)
                    random10 = random.choice(chi_char)
                    random11 = random.choice(chi_char)
                    random12 = random.choice(chi_char)
                    random13 = random.choice(chi_char)
                    random14 = random.choice(chi_char)
                    random15 = random.choice(chi_char)
                    random16 = random.choice(chi_char)
                    random17 = random.choice(chi_char)
                    random18 = random.choice(chi_char)
                    random19 = random.choice(chi_char)
                    random20 = random.choice(chi_char)
                    characters = [random1, random2, random3, random4, random5, random6, random7, random8, random9, random10, random11, random12, random13, random14, random15, random16, random17, random18, random19, random20]
                    return characters
                random_characters = generate_random_characters()
                sitch  = (round(random.random()*999999999999999,5))
                print(title, ctm, random_characters, sitch)
            
            def main_loop():
                while True:
                    time.sleep(buffer)
                    generate_random_result()

            try:
                main_loop()
            except KeyboardInterrupt:
                print("\nStopped by user.")

        def xcbmp():

            time.sleep(.3)

            print()
            print("DISCLAIMER: This works on Android and must have Termux and Termux-API installed from F-Droid and Google Text-to-Speech options set to 'Chinese'")
            print()
            print("Ctrl+C To Stop")
            print()
            print("'FNTCCI (C)'")
            print()

            time.sleep(.3)

            c_fcci2 = ['a', 'ai', 'an', 'ang', 'ao', 'ba', 'bai', 'ban', 'bang', 'bao', 'bei', 'ben', 'beng', 'bi', 'bian', 'biao', 'bie', 'bin', 'bing', 'bo', 'bu', 'ca', 'cai', 'can', 'cang', 'cao', 'ce', 'cei', 'cen', 'ceng', 'cha', 'chai', 'chan', 'chang', 'chao', 'che', 'chen', 'cheng', 'chi', 'chong', 'chou', 'chu', 'chua', 'chuai', 'chuan', 'chuang', 'chui', 'chun', 'chuo', 'ci', 'cong', 'cou', 'cu', 'cuan', 'cui', 'cun', 'cuo', 'da', 'dai', 'dan', 'dang', 'dao', 'de', 'dei', 'den', 'deng', 'di', 'dia', 'dian', 'diao', 'die', 'ding', 'diu', 'dong', 'dou', 'du', 'duan', 'dui', 'dun', 'duo', 'e', 'ei', 'en', 'eng', 'er', 'fa', 'fan', 'fang', 'fei', 'fen', 'feng', 'fo', 'fou', 'fu', 'ga', 'gai', 'gan', 'gang', 'gao', 'ge', 'gei', 'gen', 'geng', 'gong', 'gou', 'gu', 'gua', 'guai', 'guan', 'guang', 'gui', 'gun', 'guo', 'ha', 'hai', 'han', 'hang', 'hao', 'he', 'hei', 'hen', 'heng', 'hong', 'hou', 'hu', 'hua', 'huai', 'huan', 'huang', 'hui', 'hun', 'huo', 'ji', 'jia', 'jian', 'jiang', 'jiao', 'jie', 'jin', 'jing', 'jiong', 'jiu', 'ju', 'juan', 'jue', 'jun', 'ka', 'kai', 'kan', 'kang', 'kao', 'ke', 'kei', 'ken', 'keng', 'kong', 'kou', 'ku', 'kua', 'kuai', 'kuan', 'kuang', 'kui', 'kun', 'kuo', 'la', 'lai', 'lan', 'lang', 'lao', 'le', 'lei', 'leng', 'li', 'lia', 'lian', 'liang', 'liao', 'lie', 'lin', 'ling', 'liu', 'long', 'lou', 'lu', 'luan', 'lun', 'luo', 'lü', 'lüe', 'ma', 'mai', 'man', 'mang', 'mao', 'me', 'mei', 'men', 'meng', 'mi', 'mian', 'miao', 'mie', 'min', 'ming', 'miu', 'mo', 'mou', 'mu', 'na', 'nai', 'nan', 'nang', 'nao', 'ne', 'nei', 'nen', 'neng', 'ni', 'nian', 'niang', 'niao', 'nie', 'nin', 'ning', 'niu', 'nong', 'nou', 'nu', 'nuan', 'nuo', 'nü', 'nüe', 'o', 'ou', 'pa', 'pai', 'pan', 'pang', 'pao', 'pei', 'pen', 'peng', 'pi', 'pian', 'piao', 'pie', 'pin', 'ping', 'po', 'pou', 'pu', 'qi', 'qia', 'qian', 'qiang', 'qiao', 'qie', 'qin', 'qing', 'qiong', 'qiu', 'qu', 'quan', 'que', 'qun', 'ran', 'rang', 'rao', 're', 'ren', 'reng', 'ri', 'rong', 'rou', 'ru', 'ruan', 'rui', 'run', 'ruo', 'sa', 'sai', 'san', 'sang', 'sao', 'se', 'sen', 'seng', 'sha', 'shai', 'shan', 'shang', 'shao', 'she', 'shei', 'shen', 'sheng', 'shi', 'shou', 'shu', 'shua', 'shuai', 'shuan', 'shuang', 'shui', 'shun', 'shuo', 'si', 'song', 'sou', 'su', 'suan', 'sui', 'sun', 'suo', 'ta', 'tai', 'tan', 'tang', 'tao', 'te', 'tei', 'teng', 'ti', 'tian', 'tiao', 'tie', 'ting', 'tong', 'tou', 'tu', 'tuan', 'tui', 'tun', 'tuo', 'wa', 'wai', 'wan', 'wang', 'wei', 'wen', 'weng', 'wo', 'wu', 'xi', 'xia', 'xian', 'xiang', 'xiao', 'xie', 'xin', 'xing', 'xiong', 'xiu', 'xu', 'xuan', 'xue', 'xun', 'ya', 'yan', 'yang', 'yao', 'ye', 'yi', 'yin', 'ying', 'yo', 'yong', 'you', 'yu', 'yuan', 'yue', 'yun', 'za', 'zai', 'zan', 'zang', 'zao', 'ze', 'zei', 'zen', 'zeng', 'zha', 'zhai', 'zhan', 'zhang', 'zhao', 'zhe', 'zhei', 'zhen', 'zheng', 'zhi', 'zhong', 'zhou', 'zhu', 'zhua', 'zhuai', 'zhuan', 'zhuang', 'zhui', 'zhun', 'zhuo', 'zi', 'zong', 'zou', 'zu', 'zuan', 'zui', 'zun', 'zuo', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']
            
            maroon = " st"

            cnano2 = (c_fcci2)

            ct = datetime.datetime.now()

            monitor = "xcbmp-start:"
            print(monitor, ct)
            print()

            def generate_random_result():

                ctm = datetime.datetime.now()

                def generate_random_letters():
                    random1 = random.choice(string.ascii_letters)
                    random2 = random.choice(string.ascii_letters)
                    random3 = random.choice(string.ascii_letters)
                    letters = [random1, random2, random3]
                    return letters

                random_letters = generate_random_letters()

                sitch  = (round(random.random()*9999,4))

                cci2 = random.choices(cnano2, k=random.randint(1,10))

                result_text = "".join(cci2)

                print(maroon, random_letters, sitch, result_text, ctm)

                speak(result_text)

                print()
                
            def main_loop():
                while True:
                    time.sleep(random.randint(0,6))
                    integer = (round(random.random()*18))
                    if integer > 10:
                        if random.choice([True, False]):
                            generate_random_result()

            try:
                main_loop()
            except KeyboardInterrupt:
                print("\nStopped by user.")

        def xcbmpc():

            time.sleep(.3)

            print()
            print("DISCLAIMER: This works on Android and must have Termux and Termux-API installed from F-Droid and Google Text-to-Speech options set to 'Chinese'")
            print()
            print("Ctrl+C To Stop")
            print()
            print("'FNTCCI (CC)'")
            print()

            time.sleep(.3)

            c_fcci2 = chi_chars
            
            maroon = " st"

            cnano2 = (c_fcci2)

            ct = datetime.datetime.now()

            monitor = "xcbmpc-start:"
            print(monitor, ct)
            print()

            def generate_random_result():

                ctm = datetime.datetime.now()

                def generate_random_letters():
                    random1 = random.choice(string.ascii_letters)
                    random2 = random.choice(string.ascii_letters)
                    random3 = random.choice(string.ascii_letters)
                    letters = [random1, random2, random3]
                    return letters

                random_letters = generate_random_letters()

                sitch  = (round(random.random()*9999,4))

                cci2 = random.choices(cnano2, k=random.randint(1,25))

                result_text = "".join(cci2)

                print(maroon, random_letters, sitch, result_text, ctm)

                speak(result_text)

                print()
                
            def main_loop():
                while True:
                    time.sleep(random.randint(0,6))
                    integer = (round(random.random()*18))
                    if integer > 10:
                        if random.choice([True, False]):
                            generate_random_result()

            try:
                main_loop()
            except KeyboardInterrupt:
                print("\nStopped by user.")

        def xhbmp():

            time.sleep(.3)

            print()
            print("DISCLAIMER: This works on Android and must have Termux and Termux-API installed from F-Droid and Google Text-to-Speech options set to 'Korean'")
            print()
            print("Ctrl+C To Stop")
            print()
            print("'FNTCCI (H)'")
            print()

            time.sleep(.3)

            h_fcci2 = ["ga", "gya", "geo", "gyeo", "go", "gyo", "gu", "gyu", "geu", "gi", "gae", "gyae", "ge", "gye", "gwa", "gwae", "goe", "gwo", "gwe", "gwi", "gui", "kka", "kkya", "kkeo", "kkyeo", "kko", "kkyo", "kku", "kkyu", "kkeu", "kki", "kkae", "kkyae", "kke", "kkye", "kkwa", "kkwae", "kkoe", "kkwo", "kkwe", "kkwi", "kkui", "na", "nya", "neo", "nyeo", "no", "nyo", "nu", "nyu", "neu", "ni", "nae", "nyae", "ne", "nye", "nwa", "nwae", "noe", "nwo", "nwe", "nwi", "nui", "da", "dya", "deo", "dyeo", "do", "dyo", "du", "dyu", "deu", "di", "dae", "dyae", "de", "dye", "dwa", "dwae", "doe", "dwo", "dwe", "dwi", "dui", "tta", "ttya", "tteo", "ttyeo", "tto", "ttyo", "ttu", "ttyu", "tteu", "tti", "ttae", "ttyae", "tte", "ttye", "ttwa", "ttwae", "ttoe", "ttwo", "ttwe", "ttwi", "ttui", "ra", "rya", "reo", "ryeo", "ro", "ryo", "ru", "ryu", "reu", "ri", "rae", "ryae", "re", "rye", "rwa", "rwae", "roe", "rwo", "rwe", "rwi", "rui", "ma", "mya", "meo", "myeo", "mo", "myo", "mu", "myu", "meu", "mi", "mae", "myae", "me", "mye", "mwa", "mwae", "moe", "mwo", "mwe", "mwi", "mui", "ba", "bya", "beo", "byeo", "bo", "byo", "bu", "byu", "beu", "bi", "bae", "byae", "be", "bye", "bwa", "bwae", "boe", "bwo", "bwe", "bwi", "bui", "ppa", "ppya", "ppeo", "ppyeo", "ppo", "ppyo", "ppu", "ppyu", "ppeu", "ppi", "ppae", "ppyae", "ppe", "ppye", "ppwa", "ppwae", "ppoe", "ppwo", "ppwe", "ppwi", "ppui", "sa", "sya", "seo", "syeo", "so", "syo", "su", "syu", "seu", "si", "sae", "syae", "se", "sye", "swa", "swae", "soe", "swo", "swe", "swi", "sui", "ssa", "ssya", "sseo", "ssyeo", "sso", "ssyo", "ssu", "ssyu", "sseu", "ssi", "ssae", "ssyae", "sse", "ssye", "sswa", "sswae", "ssoe", "sswo", "sswe", "sswi", "ssui", "a", "ya", "eo", "yeo", "o", "yo", "u", "yu", "eu", "i", "ae", "yae", "e", "ye", "wa", "wae", "oe", "wo", "we", "wi", "ui", "ja", "jya", "jeo", "jyeo", "jo", "jyo", "ju", "jyu", "jeu", "ji", "jae", "jyae", "je", "jye", "jwa", "jwae", "joe", "jwo", "jwe", "jwi", "jui", "jja", "jjya", "jjeo", "jjyeo", "jjo", "jjyo", "jju", "jjyu", "jjeu", "jji", "jjae", "jjyae", "jje", "jjye", "jjwa", "jjwae", "jjoe", "jjwo", "jjwe", "jjwi", "jjui", "cha", "chya", "cheo", "chyeo", "cho", "chyo", "chu", "chyu", "cheu", "chi", "chae", "chyae", "che", "chye", "chwa", "chwae", "choe", "chwo", "chwe", "chwi", "chui", "ka", "kya", "keo", "kyeo", "ko", "kyo", "ku", "kyu", "keu", "ki", "kae", "kyae", "ke", "kye", "kwa", "kwae", "koe", "kwo", "kwe", "kwi", "kui", "ta", "tya", "teo", "tyeo", "to", "tyo", "tu", "tyu", "teu", "ti", "tae", "tyae", "te", "tye", "twa", "twae", "toe", "two", "twe", "twi", "tui", "pa", "pya", "peo", "pyeo", "po", "pyo", "pu", "pyu", "peu", "pi", "pae", "pyae", "pe", "pye", "pwa", "pwae", "poe", "pwo", "pwe", "pwi", "pui", "ha", "hya", "heo", "hyeo", "ho", "hyo", "hu", "hyu", "heu", "hi", "hae", "hyae", "he", "hye", "hwa", "hwae", "hoe", "hwo", "hwe", "hwi", "hui", ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']

            maroon = " st"

            hnano2 = (h_fcci2)

            ct = datetime.datetime.now()

            monitor = "xhbmp-start:"
            print(monitor, ct)
            print()

            def generate_random_result():

                ctm = datetime.datetime.now()

                def generate_random_letters():
                    random1 = random.choice(string.ascii_letters)
                    random2 = random.choice(string.ascii_letters)
                    random3 = random.choice(string.ascii_letters)
                    letters = [random1, random2, random3]
                    return letters

                random_letters = generate_random_letters()

                sitch  = (round(random.random()*9999,4))

                hcci2 = random.choices(hnano2, k=random.randint(1,10))

                result_text = "".join(hcci2)

                print(maroon, random_letters, sitch, result_text, ctm)

                speak(result_text)

                print()
                
            def main_loop():
                while True:
                    time.sleep(random.randint(0,6))
                    integer = (round(random.random()*18))
                    if integer > 10:
                        if random.choice([True, False]):
                            generate_random_result()

            try:
                main_loop()
            except KeyboardInterrupt:
                print("\nStopped by user.")

        def xhbmpc():

            time.sleep(.3)

            print()
            print("DISCLAIMER: This works on Android and must have Termux and Termux-API installed from F-Droid and Google Text-to-Speech options set to 'Korean'")
            print()
            print("Ctrl+C To Stop")
            print()
            print("'FNTCCI (HC)'")
            print()

            time.sleep(.3)

            h_fcci2 = jamo

            maroon = " st"

            hnano2 = (h_fcci2)

            ct = datetime.datetime.now()

            monitor = "xhbmpc-start:"
            print(monitor, ct)
            print()

            def generate_random_result():

                ctm = datetime.datetime.now()

                def generate_random_letters():
                    random1 = random.choice(string.ascii_letters)
                    random2 = random.choice(string.ascii_letters)
                    random3 = random.choice(string.ascii_letters)
                    letters = [random1, random2, random3]
                    return letters

                random_letters = generate_random_letters()

                sitch  = (round(random.random()*9999,4))

                hcci2 = random.choices(hnano2, k=random.randint(1,25))

                result_text = "".join(hcci2)

                print(maroon, random_letters, sitch, result_text, ctm)

                speak(result_text)

                print()
                
            def main_loop():
                while True:
                    time.sleep(random.randint(0,6))
                    integer = (round(random.random()*18))
                    if integer > 10:
                        if random.choice([True, False]):
                            generate_random_result()

            try:
                main_loop()
            except KeyboardInterrupt:
                print("\nStopped by user.")

        def xjbmp():

            time.sleep(.3)

            print()
            print("DISCLAIMER: This works on Android and must have Termux and Termux-API installed from F-Droid and Google Text-to-Speech options set to 'Japanese'")
            print()
            print("Ctrl+C To Stop")
            print()
            print("'FNTCCI (J)'")
            print()

            time.sleep(.3)

            jfcci2 = ["a", "i", "u", "e", "o", "ka", "ki", "ku", "ke", "ko", "kya", "kyu", "kyo", "ga", "gi", "gu", "ge", "go", "gya", "gyu", "gyo", "sa", "shi", "su", "se", "so", "sha", "shu", "sho", "za", "ji", "zu", "ze", "zo", "ja", "ju", "jo", "ta", "chi", "tsu", "te", "to", "cha", "chu", "cho", "da", "de", "do", "na", "ni", "nu", "ne", "no", "nya", "nyu", "nyo", "ha", "hi", "fu", "he", "ho", "hya", "hyu", "hyo", "ba", "bi", "bu", "be", "bo", "bya", "byu", "byo", "pa", "pi", "pu", "pe", "po", "pya", "pyu", "pyo", "ma", "mi", "mu", "me", "mo", "mya", "myu", "myo", "ya", "yu", "yo", "ra", "ri", "ru", "re", "ro", "rya", "ryu", "ryo", "wa", "wo", "n", ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']

            maroon = " st"

            jnano2 = (jfcci2)

            ct = datetime.datetime.now()

            monitor = "xjbmp-start:"
            print(monitor, ct)
            print()

            def generate_random_result():

                ctm = datetime.datetime.now()

                def generate_random_letters():
                    random1 = random.choice(string.ascii_letters)
                    random2 = random.choice(string.ascii_letters)
                    random3 = random.choice(string.ascii_letters)
                    letters = [random1, random2, random3]
                    return letters

                random_letters = generate_random_letters()

                sitch  = (round(random.random()*9999,4))

                jcci2 = random.choices(jnano2, k=random.randint(1,10))

                result_text = "".join(jcci2)

                print(maroon, random_letters, sitch, result_text, ctm)

                speak(result_text)

                print()
                
            def main_loop():
                while True:
                    time.sleep(random.randint(0,6))
                    integer = (round(random.random()*18))
                    if integer > 10:
                        if random.choice([True, False]):
                            generate_random_result()

            try:
                main_loop()
            except KeyboardInterrupt:
                print("\nStopped by user.")

        def xjbmpc():

            time.sleep(.3)

            print()
            print("DISCLAIMER: This works on Android and must have Termux and Termux-API installed from F-Droid and Google Text-to-Speech options set to 'Japanese'")
            print()
            print("Ctrl+C To Stop")
            print()
            print("'FNTCCI (JC)'")
            print()

            time.sleep(.3)

            jfcci2 = katakana

            maroon = " st"

            jnano2 = (jfcci2)

            ct = datetime.datetime.now()

            monitor = "xjbmpc-start:"
            print(monitor, ct)
            print()

            def generate_random_result():

                ctm = datetime.datetime.now()

                def generate_random_letters():
                    random1 = random.choice(string.ascii_letters)
                    random2 = random.choice(string.ascii_letters)
                    random3 = random.choice(string.ascii_letters)
                    letters = [random1, random2, random3]
                    return letters

                random_letters = generate_random_letters()

                sitch  = (round(random.random()*9999,4))

                jcci2 = random.choices(jnano2, k=random.randint(1,25))

                result_text = "".join(jcci2)

                print(maroon, random_letters, sitch, result_text, ctm)

                speak(result_text)

                print()
                
            def main_loop():
                while True:
                    time.sleep(random.randint(0,6))
                    integer = (round(random.random()*18))
                    if integer > 10:
                        if random.choice([True, False]):
                            generate_random_result()

            try:
                main_loop()
            except KeyboardInterrupt:
                print("\nStopped by user.")

        def xfbmp():

            time.sleep(.3)

            print()
            print("DISCLAIMER: This works on Android and must have Termux and Termux-API installed from F-Droid and Google Text-to-Speech options set to 'Filipino/Tagalog'")
            print()
            print("Ctrl+C To Stop")
            print()
            print("'FNTCCI (F/T)'")
            print()

            time.sleep(.3)

            t_fcci2 = ["a", "e", "i", "o", "u", "ba", "be", "bi", "bo", "bu", "ka", "ke", "ki", "ko", "ku", "da", "de", "di", "do", "du", "ga", "ge", "gi", "go", "gu", "ha", "he", "hi", "ho", "hu", "la", "le", "li", "lo", "lu", "ma", "me", "mi", "mo", "mu", "na", "ne", "ni", "no", "nu", "nga", "nge", "ngi", "ngo", "ngu", "pa", "pe", "pi", "po", "pu", "ra", "re", "ri", "ro", "ru", "sa", "se", "si", "so", "su", "ta", "te", "ti", "to", "tu", "wa", "we", "wi", "wo", "wu", "ya", "ye", "yi", "yo", "yu", ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']

            maroon = " st"

            fnano2 = (t_fcci2)

            ct = datetime.datetime.now()

            monitor = "xfbmp-start:"
            print(monitor, ct)
            print()

            def generate_random_result():

                ctm = datetime.datetime.now()

                def generate_random_letters():
                    random1 = random.choice(string.ascii_letters)
                    random2 = random.choice(string.ascii_letters)
                    random3 = random.choice(string.ascii_letters)
                    letters = [random1, random2, random3]
                    return letters

                random_letters = generate_random_letters()

                sitch  = (round(random.random()*9999,4))

                tcci2 = random.choices(fnano2, k=random.randint(1,10))

                result_text = "".join(tcci2)

                print(maroon, random_letters, sitch, result_text, ctm)

                speak(result_text)

                print()
                
            def main_loop():
                while True:
                    time.sleep(random.randint(0,6))
                    integer = (round(random.random()*18))
                    if integer > 10:
                        if random.choice([True, False]):
                            generate_random_result()

            try:
                main_loop()
            except KeyboardInterrupt:
                print("\nStopped by user.")

        def generate_secure_string():
            """
            Generates a secure, random string of mixed characters based on user input.
            """
            # 1. Get valid input length from the user
            while True:
                try:
                    gen_secure = int(input("string length: "))
                    if gen_secure <= 0:
                        print("Enter positive integer")
                        continue
                    else:
                        # Valid input received, exit the loop
                        break 
                except ValueError:
                    print("Invalid input")

            # 2. Define the character pool
            alphabet = string.ascii_letters + string.digits + string.punctuation
            
            # 3. Generate the random string
            secure_str = ''.join(secrets.choice(alphabet) for _ in range(gen_secure))
            
            # 4. Print to console
            ct = datetime.datetime.now()
            print(f"\n{BLUE}generated_string: {secure_str} | {ct}{RESET}")

        def check_ss():
            try:
                subprocess.run(["mpv", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return True
            except FileNotFoundError:
                print("-" * 50)
                print("ERROR: 'mpv' is not installed.")
                print("\nTo fix this, run:")
                print("  Termux: pkg install mpv pulseaudio")
                print("  Linux:  sudo apt install mpv")
                print("  MacOS:  brew install mpv")
                print("-" * 50)
                return False

        def sound_stream():

            if not check_ss():
                return

            sample_rate = 44100
            
            cmd = [
                "mpv",
                "--no-video",
                "--demuxer=rawaudio",  
                "--demuxer-rawaudio-rate=44100",
                "--demuxer-rawaudio-channels=1",
                "--demuxer-rawaudio-format=s16le",
                "-"  # Read from stdin
            ]

            try:
                player = subprocess.Popen(cmd, stdin=subprocess.PIPE)
                
                print("Generating tones... (Ctrl+C to stop)")

                while True:
                    pitch = random.uniform(40, 1000)
                    duration = random.uniform(0.01, 1.11) 
                    num_samples = int(sample_rate * duration)
                    
                    audio_bytes = bytearray()
                    for x in range(num_samples):
                        sample = int(16000 * math.sin(2 * math.pi * pitch * (x / sample_rate)))
                        audio_bytes.extend(struct.pack('h', sample))
                    
                    if player.poll() is not None:
                        print("\n[!] mpv exited unexpectedly.")
                        break
                        
                    player.stdin.write(audio_bytes)
                    player.stdin.flush()

            except KeyboardInterrupt:
                print("\nStopping...")
            except BrokenPipeError:
                print("\n[!] Connection to mpv was lost.")
            finally:
                if 'player' in locals():
                    player.terminate()
                    player.wait()

        def rhospital():
            hdata = random.choice(hospitals)

            ct = datetime.datetime.now()
            print()
            hlabel = "hospital: "
            print(hlabel, hdata, ct)         

        def choice():
            choice = ''
            while choice !='pray' and choice !='slot' and choice !='search for items' and choice !='surf' and choice !='sleep' and choice !='eat' and choice !='meditate' and choice !='find coins' and choice !='draw card' and choice !='fly' and choice !='drink coffee' and choice !='drink tea' and choice !='surf' and choice !='dhammapada' and choice !='skate' and choice !='art' and choice !='give alms' and choice !='radio' and choice !='hack' and choice !='message' and choice !='brawl' and choice !='souls'and choice !='hipster tarot' and choice !='mp3' and choice !='spar' and choice !='train' and choice !='rest' and choice !='psalms' and choice !='haiku' and choice !='muslim prayer' and choice !='karate' and choice !='koans' and choice !='equips' and choice !='rpg' and choice !='archery' and choice !='color key' and choice !='doodling' and choice !='BUMP' and choice !='MA' and choice !='Magic' and choice !='commands' and choice !='scmpy' and choice !='scm' and choice !='ascii' and choice !='zen melody' and choice !='monopoly' and choice !='light incense' and choice  !='stats' and choice !='prayer' and choice !='progress' and choice !='collections' and choice !='football' and choice !='c' and choice !='map' and choice !='search' and choice !='print time' and choice !='entry' and choice !='posting' and choice !='koran' and choice !='heBrews' and choice !='Medicals' and choice !='M' and choice !='Clearance' and choice !='MiCasa' and choice !='stuff' and choice !='worship' and choice !='Earth Science' and choice !='SCI' and choice !='value' and choice !='psychology' and choice !='psyc' and choice !='Patient Simu' and choice !='biology' and choice !='B' and choice !='legal terms' and choice !='Law' and choice !='the heart sutra' and choice !='License' and choice !='police' and choice !='prad' and choice !='climb' and choice !='chemistry' and choice !='ch' and choice !='weapon start' and choice !='wstart' and choice !='teletubby' and choice !='note' and choice !='save' and choice !='journal' and choice !='version' and choice !='ai' and choice !='auto-mat' and choice !='AAM' and choice !='ID' and choice !='IDC' and choice !='echo' and choice !='monitor-start' and choice !='mstart' and choice !='change username' and choice !='username' and choice !='user' and choice !='fuzz' and choice !='message-scan' and choice !='scan' and choice !='monitor-search' and choice !='msearch' and choice !='tag' and choice !='atag' and choice !='a-tag' and choice !='acad-monitor' and choice !='astart' and choice !='acad-search' and choice !='asearch' and choice !='oscillator' and choice !='oscillate' and choice !='oscill' and choice !='amror' and choice !='game' and choice !='amsearch' and choice !='amror-search' and choice !='amror search' and choice !='profile' and choice !='Profile' and choice !='herbs' and choice !='herbals' and choice !='degree' and choice !='degrees' and choice !='major' and choice !='majors' and choice !='MedProc AI' and choice !='MAI' and choice !='frames' and choice !='fsearch' and choice !='ascsearch' and choice !='alerts' and choice !='Alerts' and choice !='burner-start' and choice !='burner start' and choice !='burner' and choice !='burn' and choice !='kiomai' and choice !='KIOMAI' and choice !='GES' and choice !='call' and choice !='time-monitor' and choice !='rhospital' and choice !='rhosp' and choice !='random hospital' and choice !='ghosthunt' and choice !='update' and choice !='restart':
                global usr
                print()
                choice = input(usr)
                jot_write(f"{usr}{choice}")
                ct = datetime.datetime.now()
                _last_cmd_output = deepseek_ai.output_since_marker()
                deepseek_ai.mark_cmd_boundary()

                if choice == "version" or choice == "about" or choice == "intro":
                    version()

                if choice == "commands" or choice == "help" or choice == "-help" or choice == "--help":
                    commands()

                if choice in ("Deepseek", "deepseek", "DS", "ds"):
                    p = input(f"DS{usr}")
                    if p.strip():
                        if p.strip().lower() == "change-api":
                            deepseek_ai.change_api_key()
                            continue
                        reply = deepseek_ai.chat_once(p)
                        print(f"DS: {reply}")
                elif choice.startswith(("Deepseek ", "deepseek ", "DS ", "ds ")):
                    prompt = choice.split(" ", 1)[1].strip()
                    if prompt.lower() == "change-api":
                        deepseek_ai.change_api_key()
                        continue
                    import re
                    m = re.match(r'(.+?)\s+last\s+(\d+)\s+(?:terminal\s+)?lines\s*(.*)', prompt, re.IGNORECASE)
                    if m:
                        action = m.group(1).strip()
                        n = int(m.group(2))
                        extra = m.group(3).strip()
                        ctx = deepseek_ai.read_session_lines(n)
                        if ctx:
                            full_prompt = f"{action} the following content:\n{ctx}"
                            if extra:
                                full_prompt += f"\n\n{extra}"
                        else:
                            full_prompt = prompt
                        reply = deepseek_ai.chat_once(full_prompt)
                        print(f"DS: {reply}")
                    else:
                        reply = deepseek_ai.chat_once(prompt)
                        print(f"DS: {reply}")

                if choice == "scmpy" or choice == "scm":
                    try:
                        import scmpy
                        if not scmpy.check_dependencies():
                            return "continue"
                        scmpy.scmpy_main()
                    except Exception as e:
                        print(f"SCMPY error: {e}")
                    return "continue"

                if choice in ("ai_image", "ai-image", "ai img", "aii"):
                    import ai_image
                    ai_image.run(default_prompt=_last_cmd_output)
                    return "continue"

                if choice == "jot" or choice == "JOT":
                    if jot_active:
                        jot()
                    else:
                        path = input("Path (Enter for ./JOT.txt): ").strip()
                        jot(path if path else "JOT.txt")
                        jot_write(f"=== JOT Session: {datetime.datetime.now()} ===")
                    return "continue"

                if choice in ("dsnan", "dsnan interpret", "interpret", "interpret on", "interpret off"):
                    dsnan_interpret()

                if choice == "nano chars" or choice == "nano characters" or choice == "nano-characters" or choice == "nanochars" or choice == "nano-chars" or choice == "nnc" or choice == "NNC":
                    select_charset()

                if choice == "GES" or choice == "CAI" or choice == "CAI Environments" or choice == "CAI environments" or choice == "cai environments":
                    GES()
                    
                if choice == 'print time':
                    print_time()

                if choice == 'profile' or choice == 'Profile':
                    profile()

                if choice == 'change username' or choice == 'username' or choice == 'user':
                    change_username()
                    return "continue"

                if choice == 'alerts' or choice == 'Alerts':
                    alerts()

                if choice == 'echo':
                    echo()

                if choice == "chinese characters" or choice == "c-characters" or choice == "cchar" or choice == "cc":
                    chichars()

                if choice == "ch-monitor" or choice == "ch monitor" or choice == "CHM":
                    ch_monitor()

                if choice == "pray":
                    pray()

                if choice == "climb":
                    climb()
                    
                if choice == "prayer":
                    prayer()
                    
                if choice == "stats":
                    stats()

                if choice == "progress":
                    progress()
                    
                if choice == "light incense":
                    light_incense()

                if choice == "the heart sutra":
                    heart_sutra()

                if choice == "heBrews":
                    hebrews()

                if choice == 'teletubby':
                    teletubby()

                if choice == "herbs" or choice == "herbals":
                    herbs()

                if choice == "maryjane" or choice == "mj":
                    maryjane()

                if choice == "legal terms" or choice == "Law":
                    legal_terms()

                if choice == "degree" or choice == "degrees" or choice == "major" or choice == "majors":
                    degree()

                if choice == "biology" or choice == "B":
                    biology()

                if choice == "chemistry" or choice == "ch":
                    chemistry()

                if choice == "Patient Simu":
                    patient_simu()

                if choice == "Earth Science" or choice == "SCI":
                    earth_science()

                if choice == "psychology" or choice == "psyc":
                    psychology()

                if choice == "Medicals" or choice == "M":
                    medicals()

                if choice == "MIMS" or choice == "mim" or choice == "MIM" or choice == "Medicines":
                    MIMS()

                if choice == "License":
                    license()

                if choice == "police" or choice == "prad":
                    police()

                if choice == "Clearance":
                    clearance()

                if choice == "" or choice == "nano":
                    if interpret_active:
                        dsnan_nano()
                    else:
                        nano()

                if choice == "m" or choice == "morn" or choice == "MORN" or choice == "Morn":
                    morn()

                if choice == "n1" or choice == "   " or choice == "1-nano" or choice == "1nano":
                    n1()

                if choice == "katakana" or choice == "kata" or choice == "b":
                    kata()

                if choice == "jamo" or choice == "hangu" or choice == "n":
                    hangu()

                if choice == "chi" or choice == "CHI" or choice == "Chi" or choice == "++":
                    manton()

                if choice == "ans" or choice == "@@":
                    aans()

                if choice == "ruh" or choice == "%%":
                    ruuh()

                if choice == "kata-monitor" or choice == "kata monitor" or choice == "katakana-monitor" or choice == "katakana monitor" or choice == "kk-monitor" or choice == "kk monitor" or choice == "KM":
                    kata_monitor()

                if choice == "jamo-monitor" or choice == "jamo monitor" or choice == "j-monitor" or choice == "JM":
                    hangu_monitor()

                if choice == "ruh monitor" or choice == "ruh-monitor" or choice == "rmonitor":
                    ruh_monitor()

                if choice == "entry":
                    entry()

                if choice == "MiCasa":
                    micasa()

                if choice == "stuff":
                    stuff()

                if choice == "worship":
                    worship()

                if choice == "posting":
                    posting()

                if choice == "muslim prayer" or choice == "fajr" or choice == "before dawn":
                    muslim_prayer()

                if choice == choice == "dhuhr" or choice == "noon":
                    muslim_prayer2()

                if choice == choice == "asr" or choice == "late afternoon":
                    muslim_prayer2()

                if choice == choice == "maghrib" or choice == "at sunset":
                    muslim_prayer3()

                if choice == choice == "isha" or choice == "nighttime":
                    muslim_prayer2()

                if choice == "meditate":
                    meditate()

                if choice == "sleep":
                    sleep()

                if choice == "eat":
                    eat()

                if choice == "find coins":
                    find_coins()

                if choice == "slot":
                    slot()

                if choice == "draw card":
                    draw_card()

                if choice == "search for items":
                    search_for_items()

                if choice == "fly":
                    fly()

                if choice == "drink coffee":
                    drink_coffee()

                if choice == "drink tea":
                    drink_tea()

                if choice == "surf":
                    surf()

                if choice == "collections":
                    collections()

                if choice == "doodling":
                    doodling()

                if choice == "zen melody":
                    zen_melody()

                if choice == "value":
                    value()

                if choice == "BUMP":
                    bump()

                if choice == "MA":
                    ma()

                if choice == "skate":
                    skate()

                if choice == "ID":
                    ID()

                if choice == "IDC":
                    IDC()

                if choice == "art":
                    art()

                if choice == "radio":
                    radio()

                if choice == "give alms":
                    give_alms()

                if choice == "brawl":
                    brawl()

                if choice == "karate":
                    karate()

                if choice == "koans":
                    koans()

                if choice == "hipster tarot":
                    hipster_tarot()

                if choice == "hack":
                    hack()

                if choice == "spar":
                    spar()

                if choice == "train":
                    train()

                if choice == "rest":
                    rest()

                if choice == "haiku":
                    haiku()

                if choice == "Bible" or choice == "bible" or choice == "bb" or choice == "BB":
                    bible_verses() 

                if choice == "psalms":
                    psalms()

                if choice == "dhammapada":
                    dhammapada()

                if choice == "proverbs" or choice == "ps" or choice == "Proverbs" or choice == "PS" or choice == "PROVERBS":
                    pr0verbs()

                if choice == "koran":
                    koran()

                if choice == "message" or choice == "lh":
                    message()

                if choice == "souls":
                    souls()

                if choice == "guard" or choice == "guards":
                    guard()

                if choice == "c":
                    c()

                if choice == "ascii" or choice == "  ":
                    asciii()

                if choice == "mp3":
                    mp3()

                if choice == "monopoly":
                    monopoly()

                if choice == "equips":
                    equips()

                if choice == "rpg":
                    rpg()

                if choice == "archery":
                    archery()

                if choice == "color key":
                    color_key()

                if choice == "Magic":
                    magic()
                    
                if choice == "football":
                    football()
               
                if choice == "map":
                    mapp()

                if choice == "ai" or choice == "auto-mat" or choice == "AAM":
                    auto_mat()

                if choice == "no_color" or choice == "nc":
                    no_color()

                if choice == "donate":
                    print("Contact the developer at usvu.tech@gmail.com")
                    time.sleep(5)

                if choice == "update":
                    version_checker.perform_update()

                if choice == "restart":
                    version_checker.restart_app()

                if choice == "exit":
                    exit()
                if choice == "close":
                    exit()
                if choice == "quit":
                    exit()

                if choice == "weapon start" or choice == "wstart":
                    weapon_start()

                if choice == "call":
                    call()

                if choice == "time-call" or choice == "time call" or choice == "TC":
                    time_call()

                if choice == "RTC" or choice == "ruh time call" or choice == "ruh-time-call":
                    ruh_time_call()

                if choice == "monitor-start" or choice == "mstart":
                    monitor_start()

                if choice == "acad-monitor" or choice == "astart":
                    acad_monitor()

                if choice == "time monitor" or choice == "time-monitor" or choice == "tmonitor" or choice == "t-monitor" or choice == "tm":
                    time_monitor()

                if choice == "speech time monitor" or choice == "speech-time-monitor" or choice == "speech time-monitor" or choice == "speech tmonitor" or choice == "stmonitor":
                    s_time_monitor()

                if choice == "message-scan" or choice == "scan":
                    msgs()

                if choice == "fuzz":
                    fuzz()

                if choice == "tag":
                    tag()

                if choice == "atag" or choice == "a-tag":
                    atag()

                if choice == "MedProc" or choice == "medproc" or choice == "MedProc AI" or choice == "medproc AI" or choice == "medproc ai" or choice == "MAI" or choice == "Mai":
                    MAI()

                if choice == "MAIc" or choice == "MedProcCont" or choice == "medproccont" or choice == "MPC" or choice == "mpc":
                    MAIc()

                if choice == "frames" or choice == "fps":
                    frames()

                if choice == "oscillator" or choice == "oscillate" or choice == "oscill":
                    oscillator()

                if choice == "toscillator" or choice == "toscillate" or choice == "toscill" or choice == "time-oscill" or choice == "time-oscillate" or choice == "time-oscillator":
                    toscillator()

                if choice == "burner-start" or choice == "burner start" or choice == "burner" or choice == "burn" or choice == "Burn":
                    burner()

                if choice == "c-burner-start" or choice == "c burner start" or choice == "cburner" or choice == "cburn" or choice == "Burn":
                    cburner()

                if choice == "j-burner-start" or choice == "j burner start" or choice == "jburner" or choice == "jburn" or choice == "jBurn":
                    jburner()

                if choice == "time-burner-start" or choice == "time burner start" or choice == "time burner" or choice == "tburn" or choice == "time burn" or choice == "tburner" or choice == "tBurn" or choice == "c-time-burner":
                    tburner()

                if choice == "c-time-burner-start" or choice == "c time burner start" or choice == "c time burner" or choice == "ctburn" or choice == "c time burn" or choice == "ctburner" or choice == "ctBurn" or choice == "c-time-burner":
                    ctburner()

                if choice == "j-time-burner-start" or choice == "j time burner start" or choice == "j time burner" or choice == "jtburn" or choice == "j time burn" or choice == "jtburner" or choice == "jtBurn" or choice == "j-time-burner":
                    jtburner()

                if choice == 'search' or choice == 'fsearch':
                    search()

                if choice == 'tsearch' or choice == 'term search' or choice == "Term-Search" or choice == "term-search":
                    tsearch()

                if choice == "busearch" or choice == "burner search" or choice == "burner-search" or choice == "bsearch" or choice == "b-search":
                    busearch()

                if choice == "zuz" or choice == "ZUZ" or choice == "pp" or choice == "PP" or choice == "Zuz":
                    zuz()

                if choice == "programs" or choice == "Programs" or choice == "Prog" or choice == "PROGR" or choice == "program" or choice == "Program" or choice == "progr":
                    programs()

                if choice == "ls":
                    ls()

                if choice == "cd":
                    cd()

                if choice == "mkdir":
                    mkdir()

                if choice == "clear" or choice == "cl":
                    clear()

                if choice == "rm":
                    rm()

                if choice == "pwd":
                    pwd()

                if choice == "Tinien" or choice == "tinien" or choice == " " or choice == "**":
                    tinie_N()

                if choice == "ntag" or choice == "n-tag":
                    ntag()

                if choice == "fstart" or choice == "f-start" or choice == "fmonitor" or choice == "fmonitor" or choice == "fcci" or choice == "fcci monitor" or choice == "fcci-monitor" or choice == "FCCI" or choice == "FCCI-monitor" or choice == "FCCI monitor":
                    fntcci_monitor()

                if choice == "type-text" or choice == "type text" or choice == "typetext":
                    text()

                if choice == "threads" or choice == "Threads":
                    while True:

                            thread_stop_event = threading.Event()

                            try:
                                activate_threads(thread_stop_event) 

                            except Exception as e:
                                print(f"An unhandled error occurred: {e}")
                                thread_stop_event.set()

                            mp()

                if choice == "speak" or choice == "spk":
                    spheak()

                if choice == "xcbmp":
                    xcbmp()

                if choice == "xcbmpc":
                    xcbmpc()

                if choice == "xhbmp":
                    xhbmp()

                if choice == "xhbmpc":
                    xhbmpc()

                if choice == "xjbmp":
                    xjbmp()

                if choice == "xjbmpc":
                    xjbmpc()

                if choice == "xfbmp":
                    xfbmp()

                if choice == "gen string" or choice == "generate string" or choice == "genstring" or choice == "gstring":
                    generate_secure_string()

                if choice == "ghost write" or choice == "Ghost Write" or choice == "GW" or choice == "gw" or choice == "ghost code":
                    ghost_write()

                if choice == "insta ghost write" or choice == "Insta Ghost Write" or choice == "IGW" or choice == "igw" or choice == "insta ghost code" or choice == "iGW" or choice == "insta GW" or choice == "insta gw":
                    insta_ghost_write()

                if choice == "soundstream" or choice == "sst" or choice == "SST" or choice == "sound stream" or choice == "stream sound" or choice == "streamsound":
                    sound_stream()

                if choice == "rhospital" or choice == "random hospital" or choice == "ghosthunt" or choice == "rhosp":
                    rhospital()

                if choice == "switch" or choice == "lx" or choice == "lpro":
                    return "switch"

        parser = argparse.ArgumentParser(description="MProcs", prefix_chars='-')

        parser.add_argument("--user", "--username", nargs='?', const='ASK', help="Set username *lx-switch persistent")
        parser.add_argument("--charset", "--nanochars", "-ch", nargs='?', const='ASK', help="Set Nano charset (e.g. 1, 2a, korean) *lx-switch persistent")
        parser.add_argument("--version", "--about", "--wm", "--intro", action="store_true", help="Display intro, version, and welcome message")
        parser.add_argument("--x", "--c", "--exit", "--close", action="store_true", help="Don't continue the program")
        parser.add_argument("-nano", "-n", action="store_true")
        parser.add_argument("-morn", "-m", action="store_true")
        parser.add_argument("-n1", "-1nano", action="store_true")
        parser.add_argument("-lh", "-message", action="store_true")
        parser.add_argument("-tsearch", "-term-search", action="store_true")
        parser.add_argument("-bible", "-bb", "-BB", action="store_true")
        parser.add_argument("-cai", "-ges", action="store_true")
        parser.add_argument("-print-time", action="store_true")
        parser.add_argument("-profile", action="store_true")
        parser.add_argument("-alerts", action="store_true")
        parser.add_argument("-fsearch", action="store_true")
        parser.add_argument("-echo", action="store_true")
        parser.add_argument("-chinese-characters", "-c-characters", "-cchar", action="store_true")
        parser.add_argument("-ch-monitor", "-chm", action="store_true")
        parser.add_argument("-pray", action="store_true")
        parser.add_argument("-climb", action="store_true")
        parser.add_argument("-prayer", action="store_true")
        parser.add_argument("-stats", action="store_true")
        parser.add_argument("-progress", action="store_true")
        parser.add_argument("-light-incense", action="store_true")
        parser.add_argument("-heart-sutra", action="store_true")
        parser.add_argument("-hebrews", action="store_true")
        parser.add_argument("-teletubby", action="store_true")
        parser.add_argument("-herbs", "-herbals", action="store_true")
        parser.add_argument("-maryjane", "-mj", action="store_true")
        parser.add_argument("-legal-terms", "-law", action="store_true")
        parser.add_argument("-degrees", "-majors", action="store_true")
        parser.add_argument("-biology", action="store_true")
        parser.add_argument("-chemistry", action="store_true")
        parser.add_argument("-patient-simu", action="store_true")
        parser.add_argument("-earth-science", "-sci", action="store_true")
        parser.add_argument("-psychology", "-psyc", action="store_true")
        parser.add_argument("-medicals", "-M", action="store_true")
        parser.add_argument("-mims", "-medicines", action="store_true")
        parser.add_argument("-license", action="store_true")
        parser.add_argument("-police", "-prad", action="store_true")
        parser.add_argument("-clearance", action="store_true")
        parser.add_argument("-katakana", "-kata", action="store_true")
        parser.add_argument("-jamo", "-hangu", action="store_true")
        parser.add_argument("-chi", action="store_true")
        parser.add_argument("-ans", action="store_true")
        parser.add_argument("-ruh", action="store_true")
        parser.add_argument("-kata-monitor", "-km", action="store_true")
        parser.add_argument("-jamo-monitor", "-jm", action="store_true")
        parser.add_argument("-ruh-monitor", "-rmonitor", action="store_true")
        parser.add_argument("-entry", action="store_true")
        parser.add_argument("-micasa", action="store_true")
        parser.add_argument("-stuff", action="store_true")
        parser.add_argument("-worship", action="store_true")
        parser.add_argument("-posting", action="store_true")
        parser.add_argument("-fajr", action="store_true")
        parser.add_argument("-dhuhr", action="store_true")
        parser.add_argument("-asr", action="store_true")
        parser.add_argument("-maghrib", action="store_true")
        parser.add_argument("-isha", action="store_true")
        parser.add_argument("-meditate", action="store_true")
        parser.add_argument("-sleep", action="store_true")
        parser.add_argument("-eat", action="store_true")
        parser.add_argument("-find-coins", action="store_true")
        parser.add_argument("-slot", action="store_true")
        parser.add_argument("-draw-card", action="store_true")
        parser.add_argument("-search-items", action="store_true")
        parser.add_argument("-fly", action="store_true")
        parser.add_argument("-drink-coffee", action="store_true")
        parser.add_argument("-drink-tea", action="store_true")
        parser.add_argument("-surf", action="store_true")
        parser.add_argument("-collections", action="store_true")
        parser.add_argument("-doodling", action="store_true")
        parser.add_argument("-zen-melody", action="store_true")
        parser.add_argument("-value", action="store_true")
        parser.add_argument("-bump", action="store_true")
        parser.add_argument("-ma", "-martial-arts", action="store_true")
        parser.add_argument("-skate", action="store_true")
        parser.add_argument("-id", action="store_true")
        parser.add_argument("-idc", action="store_true")
        parser.add_argument("-art", action="store_true")
        parser.add_argument("-radio", action="store_true")
        parser.add_argument("-give-alms", action="store_true")
        parser.add_argument("-brawl", action="store_true")
        parser.add_argument("-karate", action="store_true")
        parser.add_argument("-koans", action="store_true")
        parser.add_argument("-hipster-tarot", "-tarot", action="store_true")
        parser.add_argument("-hack", action="store_true")
        parser.add_argument("-spar", action="store_true")
        parser.add_argument("-train", action="store_true")
        parser.add_argument("-rest", action="store_true")
        parser.add_argument("-haiku", action="store_true")
        parser.add_argument("-psalms", action="store_true")
        parser.add_argument("-dhammapada", action="store_true")
        parser.add_argument("-proverbs", action="store_true")
        parser.add_argument("-koran", action="store_true")
        parser.add_argument("-souls", action="store_true")
        parser.add_argument("-guard", action="store_true")
        parser.add_argument("-chat", action="store_true")
        parser.add_argument("-ascii", action="store_true")
        parser.add_argument("-mp3", action="store_true")
        parser.add_argument("-monopoly", action="store_true")
        parser.add_argument("-equips", action="store_true")
        parser.add_argument("-rpg", action="store_true")
        parser.add_argument("-archery", action="store_true")
        parser.add_argument("-color-key", action="store_true")
        parser.add_argument("-magic", action="store_true")
        parser.add_argument("-football", action="store_true")
        parser.add_argument("-map", action="store_true")
        parser.add_argument("-auto-mat", "-aam", action="store_true")
        parser.add_argument("-donate", action="store_true")
        parser.add_argument("-update", action="store_true", help="Update MProcs via pip")
        parser.add_argument("-restart", action="store_true", help="Restart the application")
        parser.add_argument("-weapon-start", "-wstart", action="store_true")
        parser.add_argument("-call", action="store_true")
        parser.add_argument("-time-call", "-tc", action="store_true")
        parser.add_argument("-monitor-start", "-mstart", action="store_true")
        parser.add_argument("-acad-monitor", "-astart", action="store_true")
        parser.add_argument("-time-monitor", "-tmonitor", action="store_true")
        parser.add_argument("-ruh-time-call", "-rtc", action="store_true")
        parser.add_argument("-speech-tmonitor", action="store_true")
        parser.add_argument("-message-scan", "-scan", action="store_true")
        parser.add_argument("-fuzz", action="store_true")
        parser.add_argument("-tag", action="store_true")
        parser.add_argument("-a-tag", "-atag", action="store_true")
        parser.add_argument("-medproc-ai", "-mai", action="store_true")
        parser.add_argument("-medproc-cont", "-mpc", "-maic", action="store_true")
        parser.add_argument("-frames", "-fps", action="store_true")
        parser.add_argument("-oscillator", "-oscill", action="store_true")
        parser.add_argument("-time-oscillator", "-toscill", action="store_true")
        parser.add_argument("-burner-start", "-burner", "-burn", action="store_true")
        parser.add_argument("-time-burner-start", "-time-burner", "-tburner", "-tburn", action="store_true")
        parser.add_argument("-c-burner-start", "-cburner", "-cburn", action="store_true")
        parser.add_argument("-c-time-burner-start", "-c-time-burner", "-ctburner", "-ctburn", action="store_true")
        parser.add_argument("-j-burner-start", "-jburner", "-jburn", action="store_true")
        parser.add_argument("-j-time-burner-start", "-j-time-burner", "-jtburner", "-jtburn", action="store_true")
        parser.add_argument("-zuz", "-pp", action="store_true")
        parser.add_argument("-programs", "-progr", action="store_true")
        parser.add_argument("-tinien", action="store_true")
        parser.add_argument("-n-tag", "-ntag", action="store_true")
        parser.add_argument("-fcci-monitor", "-fmonitor", action="store_true")
        parser.add_argument("-type-text", action="store_true")
        parser.add_argument("-threads", action="store_true")
        parser.add_argument("-speak", "-spk", action="store_true")
        parser.add_argument("-xcbmp", action="store_true")
        parser.add_argument("-xcbmpc", action="store_true")
        parser.add_argument("-xhbmp", action="store_true")
        parser.add_argument("-xhbmpc", action="store_true")
        parser.add_argument("-xjbmp", action="store_true")
        parser.add_argument("-xjbmpc", action="store_true")
        parser.add_argument("-xfbmp", action="store_true")
        parser.add_argument("-gen-string", "-gstring", action="store_true")
        parser.add_argument("-ghost-write", "-gw", action="store_true")
        parser.add_argument("-insta-ghost-write", "-igw", action="store_true")
        parser.add_argument("-sound-stream", "-sst", action="store_true")
        parser.add_argument("-rhospital", "-ghosthunt", action="store_true")
        parser.add_argument("-mprocs-commands", action="store_true")

        parser.add_argument("-scmpy", "-scm", action="store_true", help="SCMPY - Social Media CLI (Facebook, Tumblr, AI)")
        parser.add_argument("-config-keys", action="store_true", help="Configure API keys for SCMPY")
        parser.add_argument("-backup", action="store_true", help="Backup SCMPY data")
        parser.add_argument("-restore", action="store_true", help="Restore SCMPY data")
        
        # SCMPY Functions
        parser.add_argument("-web", nargs='?', const='ASK', help="Web search")
        parser.add_argument("-img", nargs='?', const='ASK', help="Image search")
        parser.add_argument("-yt", nargs='?', const='ASK', help="YouTube search")
        parser.add_argument("-gtxt", nargs='?', const='ASK', help="AI text generation")
        parser.add_argument("-gimg", nargs='?', const='ASK', help="AI image generation")
        parser.add_argument("-ai-image", "-ai_image", action="store_true", help="AI image generation (local diffusers)")
        parser.add_argument("-tyls", "-tycat", "-list", action="store_true", help="List images in current directory")
        parser.add_argument("-ltxt", "-list-text", action="store_true", help="List text files in current directory")
        parser.add_argument("-view", nargs='?', const='ASK', help="View image")
        parser.add_argument("-videos", action="store_true", help="List videos in current directory")
        parser.add_argument("-open", nargs='?', const='ASK', help="Open URL in browser")
        parser.add_argument("-dl", nargs='?', const='ASK', help="Download file")
        parser.add_argument("-dla", action="store_true", help="Download all cached images")
        parser.add_argument("-dlurl", nargs=2, metavar=('URL', 'PATH'), help="Download from URL to path")
        parser.add_argument("-fbpost", nargs='?', const='ASK', help="Facebook text post")
        parser.add_argument("-fblink", nargs=2, metavar=('URL', 'MSG'), help="Facebook link post")
        parser.add_argument("-fbimg", nargs='?', const='ASK', help="Facebook image post")
        parser.add_argument("-fblist", nargs='?', const='10', help="List Facebook posts")
        parser.add_argument("-tmpost", nargs='?', const='ASK', help="Tumblr text post")
        parser.add_argument("-tmimg", nargs='?', const='ASK', help="Tumblr image post")
        parser.add_argument("-tmlink", nargs='?', const='ASK', help="Tumblr link post")
        parser.add_argument("-tmvid", nargs='?', const='ASK', help="Tumblr video post")
        parser.add_argument("-tmlist", nargs='?', const='10', help="List Tumblr posts")
        parser.add_argument("-post", "-share", nargs='?', const='ASK', help="Post to both FB+Tumblr")
        parser.add_argument("-pimg", nargs='?', const='ASK', help="Post cached image by number")
        parser.add_argument("-plink", nargs='?', const='ASK', help="Post cached link by number")
        parser.add_argument("-pvid", nargs='?', const='ASK', help="Post cached video by number")
        parser.add_argument("-install", action="store_true", help="Install SCMPY dependencies")
        parser.add_argument("-history", action="store_true", help="Show search history")
        
        # Common options for posting
        parser.add_argument("-caption", "-msg", nargs='?', help="Caption/Message for posts")
        parser.add_argument("-tags", nargs='*', help="Tags for posts (space separated)")
        parser.add_argument("-source", "-src", choices=['url', 'file'], help="Image source: url or file")
        parser.add_argument("-title", nargs='?', help="Title for Tumblr posts")
        parser.add_argument("-description", "-desc", nargs='?', help="Description for link posts")

        parser.add_argument("-ds", "-deepseek", nargs='?', const='ASK', help="Send a prompt to Deepseek AI and exit")

        args = parser.parse_args()

        if args.ds:
            prompt = input("DS prompt: ") if args.ds == 'ASK' else args.ds
            reply = deepseek_ai.chat_once(str(prompt))
            print(f"DS: {reply}")
            sys.exit(0)

        if args.user:
            change_username(None if args.user == 'ASK' else args.user)
        
        if args.charset:
            select_charset(None if args.charset == 'ASK' else args.charset)

        if args.version:
            print()
            version()

        if args.cai:
            GES()
            
        if args.print_time:
            print_time()            

        if args.profile:
            profile()           

        if args.alerts:
            alerts()                       

        if args.echo:
            echo()
            
        if args.chinese_characters:
            chichars()            

        if args.ch_monitor:
            ch_monitor()            
            sys.exit(0)

        if args.pray:
            pray()
            
        if args.climb:
            climb()
            
        if args.prayer:
            prayer()            

        if args.stats:
            stats()
            
        if args.progress:
            progress()
            
        if args.light_incense:
            light_incense()
            
        if args.heart_sutra:
            heart_sutra()            

        if args.hebrews:
            hebrews()
            
        if args.teletubby:
            teletubby()           

        if args.herbs:
            herbs()            

        if args.maryjane:
            maryjane()

        if args.legal_terms:
            legal_terms()
            
        if args.degrees:
            degree()
            
        if args.biology:
            biology()
            
        if args.chemistry:
            chemistry()
            
        if args.patient_simu:
            patient_simu()
            
        if args.earth_science:
            earth_science()
            
        if args.psychology:
            psychology()
            
        if args.medicals:
            medicals()

        if args.mims:
            MIMS()
            
        if args.license:
            license()
            
        if args.police:
            police()
            
        if args.clearance:
            clearance()
            
        if args.nano:
            nano()

        if args.morn:
            morn()

        if args.n1:
            n1()
            
        if args.katakana:
            kata()           

        if args.jamo:
            hangu()           

        if args.chi:
            manton()

        if args.ans:
            aans()

        if args.ruh:
            ruuh()               

        if args.kata_monitor:
            kata_monitor()
            sys.exit(0)

        if args.jamo_monitor:
            hangu_monitor()
            sys.exit(0)

        if args.ruh_monitor:
            ruh_monitor()
            sys.exit(0)

        if args.entry:
            entry()
            
        if args.micasa:
            micasa()
            
        if args.stuff:
            stuff()
            
        if args.worship:
            worship()
            
        if args.posting:
            posting()
            
        if args.fajr:
            fajr()
            
        if args.dhuhr:
            dhuhr()
            
        if args.asr:
            asr()           

        if args.maghrib:
            maghrib()
            
        if args.isha:
            meditate()            

        if args.sleep:
            sleep()
            
        if args.eat:
            eat()
            
        if args.find_coins:
            find_coins()
            
        if args.slot:
            slot()
            
        if args.draw_card:
            draw_card()
            
        if args.search_items:
            search_for_items()
            
        if args.fly:
            fly()
            
        if args.drink_coffee:
            drink_coffee()            

        if args.drink_tea:
            drink_tea()
            
        if args.surf:
            surf()            

        if args.collections:
            collections()
            
        if args.doodling:
            doodling()            

        if args.zen_melody:
            zen_melody()
            
        if args.value:
            value()            

        if args.bump:
            bump()
            
        if args.ma:
            ma()
            
        if args.skate:
            skate()
            
        if args.id:
            ID()
            
        if args.idc:
            IDC()
            
        if args.art:
            art()
            
        if args.radio:
            radio()
            
        if args.give_alms:
            give_alms()
            
        if args.brawl:
            brawl()
            
        if args.karate:
            karate()
            
        if args.koans:
            koans()
            
        if args.hipster_tarot:
            hipster_tarot()
            
        if args.hack:
            hack()
            
        if args.spar:
            spar()
            
        if args.train:
            train()
            
        if args.rest:
            rest()           

        if args.haiku:
            haiku()      

        if args.bible:
            bible_verses()      

        if args.psalms:
            psalms()
            
        if args.dhammapada:
            dhammapada()            

        if args.proverbs:
            proverbs()            

        if args.koran:
            koran()            

        if args.lh:
            message()
            
        if args.souls:
            souls()
            
        if args.guard:
            guard()
            sys.exit(0)
            
        if args.chat:
            c()
            
        if args.ascii:
            asciii()
            
        if args.mp3:
            mp3()
            
        if args.monopoly:
            monopoly()
            
        if args.equips:
            equips()
            
        if args.rpg:
            rpg()
            
        if args.archery:
            archery()
            
        if args.color_key:
            color_key()
            
        if args.magic:
            magic()            

        if args.football:
            football()
            
        if args.map:
            mapp()
            
        if args.auto_mat:
            auto_mat()
            
        if args.donate:
            print("Contact the developer at usvu.tech@gmail.com")
            
        if args.weapon_start:
            weapon_start()
            sys.exit(0)            

        if args.call:
            call()
            sys.exit(0)
            
        if args.time_call:
            time_call()
            sys.exit(0)
            
        if args.monitor_start:
            monitor_start()
            sys.exit(0)
            
        if args.acad_monitor:
            acad_monitor()
            sys.exit(0)
            
        if args.time_monitor:
            time_monitor()
            sys.exit(0)
            
        if args.speech_tmonitor:
            s_time_monitor()
            sys.exit(0)

        if args.ruh_time_call:
            ruh_time_call()
            sys.exit(0)
            
        if args.message_scan:
            msgs()
            
        if args.fuzz:
            fuzz()            

        if args.tag:
            tag()
            
        if args.a_tag:
            atag()
            
        if args.medproc_ai:
            MAI()
            sys.exit(0)           

        if args.medproc_cont:
            MAIc()
            sys.exit(0)
            
        if args.frames:
            frames()           
            
        if args.oscillator:
            oscillator()
            sys.exit(0)
            
        if args.time_oscillator:
            toscillator()
            sys.exit(0)         

        if args.burner_start:
            burner()
            sys.exit(0)
            
        if args.time_burner_start:
            tburner()
            sys.exit(0)

        if args.c_burner_start:
            cburner()
            sys.exit(0)
            
        if args.c_time_burner_start:
            ctburner()
            sys.exit(0)

        if args.j_burner_start:
            jburner()
            sys.exit(0)
            
        if args.j_time_burner_start:
            jtburner()
            sys.exit(0)

        if args.fsearch:
            search()

        if args.tsearch:
            tsearch()
            
        if args.zuz:
            zuz()
            
        if args.programs:
            programs()
            sys.exit(0)           

        if args.tinien:
            tinie_N()           

        if args.n_tag:
            ntag()           

        if args.fcci_monitor:
            fntcci_monitor()
            sys.exit(0)            

        if args.type_text:
            text()
            
        if args.threads:
            while True:

                    thread_stop_event = threading.Event()

                    try:
                        activate_threads(thread_stop_event) 

                    except Exception as e:
                        print(f"An unhandled error occurred: {e}")
                        thread_stop_event.set()
                    
                    sys.exit(0)

        if args.speak:
            spheak()
            
        if args.xcbmp:
            xcbmp()
            sys.exit(0)

        if args.xcbmpc:
            xcbmpc()
            sys.exit(0)

        if args.xcbmp:
            xhbmp()
            sys.exit(0)

        if args.xcbmpc:
            xhbmpc()
            sys.exit(0)

        if args.xcbmp:
            xjbmp()
            sys.exit(0)

        if args.xcbmpc:
            xjbmpc()
            sys.exit(0)

        if args.xfbmp:
            xfbmp()
            sys.exit(0)

        if args.gen_string:
            generate_secure_string()            

        if args.ghost_write:
            ghost_write()
            sys.exit(0)    

        if args.insta_ghost_write:
            insta_ghost_write()         

        if args.sound_stream:
            sound_stream()
            sys.exit(0)

        if args.rhospital:
            rhospital()

        if args.mprocs_commands:
            commands()

        if args.scmpy:
            import scmpy
            if not scmpy.check_dependencies():
                sys.exit(1)
            try:
                scmpy.scmpy_main()
            except Exception as e:
                print(f"SCMPY error: {e}")
                sys.exit(1)

        if args.config_keys:
            import keys
            keys.configure_keys()
            sys.exit(0)
        
        if args.backup:
            import scmpy
            scmpy.backup_all_data()
            sys.exit(0)
        
        if args.restore:
            import scmpy
            scmpy.restore_from_backup()
            sys.exit(0)
        
        # SCMPY Function handlers
        if args.web is not None:
            import scmpy
            query = args.web if args.web != 'ASK' else input("Search: ").strip()
            if query:
                scmpy.web_search(query)
            sys.exit(0)
        
        if args.img is not None:
            import scmpy
            query = args.img if args.img != 'ASK' else input("Image search: ").strip()
            if query:
                scmpy.image_search(query)
            sys.exit(0)
        
        if args.yt is not None:
            import scmpy
            query = args.yt if args.yt != 'ASK' else input("YouTube search: ").strip()
            if query:
                scmpy.youtube_search(query)
            sys.exit(0)
        
        if args.gtxt is not None:
            import scmpy
            prompt = args.gtxt if args.gtxt != 'ASK' else input("AI text prompt: ").strip()
            if prompt:
                scmpy.ai_text(prompt)
            sys.exit(0)
        
        if args.gimg is not None:
            import scmpy
            prompt = args.gimg if args.gimg != 'ASK' else input("AI image prompt: ").strip()
            if prompt:
                scmpy.ai_image(prompt)
            sys.exit(0)
        
        if args.ai_image:
            import ai_image
            ai_image.run()
            sys.exit(0)
        
        if args.tyls:
            import scmpy
            scmpy.list_images()
            sys.exit(0)
        
        if args.view is not None:
            import scmpy
            fname = args.view if args.view != 'ASK' else input("Image file: ").strip()
            if fname:
                scmpy.view_image(fname)
            sys.exit(0)
        
        if args.videos:
            import scmpy
            scmpy.list_videos()
            sys.exit(0)
        
        if args.open is not None:
            import scmpy
            url = args.open if args.open != 'ASK' else input("URL: ").strip()
            if url:
                scmpy.open_url(url)
            sys.exit(0)
        
        if args.dl is not None:
            import scmpy
            fname = args.dl if args.dl != 'ASK' else input("File to download: ").strip()
            if fname:
                scmpy.download_file(fname)
            sys.exit(0)
        
        if args.dlurl:
            import scmpy
            scmpy.download_url(args.dlurl[0], args.dlurl[1])
            sys.exit(0)
        
        if args.fbpost is not None:
            import scmpy
            msg = args.fbpost if args.fbpost != 'ASK' else input("Message: ").strip()
            if msg:
                scmpy.fb_post_text(msg)
            sys.exit(0)
        
        if args.fblink:
            import scmpy
            msg = args.fblink[1] if len(args.fblink) > 1 else input("Message: ").strip()
            scmpy.fb_post_link(args.fblink[0], msg)
            sys.exit(0)
        
        if args.fbimg is not None:
            import scmpy
            msg = args.caption or args.fbimg if args.fbimg != 'ASK' else ""
            if args.fbimg == 'ASK' or msg:
                img_url = None
                filepath = None
                source_choice = args.source

                if source_choice == '1':
                    img_url = input("Image URL: ").strip()
                elif source_choice == '2':
                    filepath = input("File path: ").strip()
                elif args.fbimg != 'ASK' and args.source is None:
                    img_url = args.fbimg
                elif args.fbimg == 'ASK' and args.source is None:
                    img_url = input("Image URL: ").strip()
                
                if not msg:
                    msg = args.caption or input("Message: ").strip()
                
                if img_url:
                    scmpy.fb_post_image_url(img_url, msg)
                elif filepath:
                    scmpy.fb_post_image_file(filepath, msg)
            sys.exit(0)
        
        if args.fblist is not None:
            import scmpy
            num = int(args.fblist) if args.fblist.isdigit() else 10
            scmpy.fb_list_posts(num)
            sys.exit(0)
        
        if args.tmpost is not None:
            import scmpy
            if args.tmpost == 'ASK':
                scmpy.tumblr_post_interactive()
            else:
                title = args.title or args.tmpost.split('|')[0] if '|' in args.tmpost else args.tmpost or "Post"
                body = args.tmpost.split('|')[1] if '|' in args.tmpost else args.caption or args.tmpost
                tags = args.tags
                scmpy.tumblr_post_text(title, body, tags)
            sys.exit(0)
        
        if args.tmimg is not None:
            import scmpy
            if args.tmimg == 'ASK':
                scmpy.tumblr_post_image_interactive()
            else:
                caption = args.caption or args.tmimg or ""
                tags = args.tags
                img_url = None
                filepath = None
                source_choice = args.source

                if source_choice == '1':
                    img_url = input("Image URL: ").strip()
                elif source_choice == '2':
                    filepath = input("File path: ").strip()
                else:
                    img_url = args.tmimg if args.tmimg else input("Image URL: ").strip()
                
                result = scmpy.tumblr_post_photo(img_url, caption, tags, local_file=filepath if filepath else None)
                print(f"Tumblr: {result.get('meta', {}).get('status', 'error')}")
            sys.exit(0)
        
        if args.tmlink is not None:
            import scmpy
            if args.tmlink == 'ASK':
                scmpy.tumblr_post_link_interactive()
            else:
                title = args.title or "Link"
                url = args.tmlink if args.tmlink else input("URL: ").strip()
                desc = args.description or args.caption or ""
                tags = args.tags
                if url:
                    result = scmpy.tumblr_post_link(title, url, desc, tags)
                    print(f"Tumblr: {result.get('meta', {}).get('status', 'error')}")
            sys.exit(0)
        
        if args.tmvid is not None:
            import scmpy
            if args.tmvid == 'ASK':
                scmpy.tumblr_post_video_interactive()
            else:
                url = args.tmvid if args.tmvid else input("YouTube URL: ").strip()
                caption = args.caption or ""
                tags = args.tags
                if url:
                    result = scmpy.tumblr_post_video(url, caption, tags)
                    print(f"Tumblr: {result.get('meta', {}).get('status', 'error')}")
            sys.exit(0)
        
        if args.tmlist is not None:
            import scmpy
            num = int(args.tmlist) if args.tmlist.isdigit() else 10
            scmpy.tumblr_get_posts(num)
            sys.exit(0)
        
        if args.post is not None:
            import scmpy
            if args.post == 'ASK':
                scmpy.post_interactive()
            else:
                ptype = None
                content = None
                
                # Determine post type from args.post or numeric input
                if args.post.isdigit():
                    post_type_map = {'1': 'text', '2': 'link', '3': 'image', '4': 'video'}
                    ptype = post_type_map.get(args.post)
                    if ptype:
                        content = input(f"Enter {ptype} content: ").strip() # Prompt for content if type is numeric
                    else:
                        print("Invalid post type number. Choose 1=Text, 2=Link, 3=Image, 4=Video.")
                        sys.exit(1)
                elif args.post.startswith('text:'):
                    ptype = 'text'
                    content = args.post[5:]
                elif args.post.startswith('link:'):
                    ptype = 'link'
                    content = args.post[5:]
                elif args.post.startswith('image:'):
                    ptype = 'image'
                    content = args.post[6:]
                elif args.post.startswith('video:'):
                    ptype = 'video'
                    content = args.post[6:]
                else: # Default to text if no prefix
                    ptype = 'text'
                    content = args.post
                
                if not ptype:
                    print("Invalid post type specified.")
                    sys.exit(1)

                msg = args.caption or ""
                tags = args.tags
                title = args.title
                desc = args.description
                
                if ptype == 'text':
                    scmpy.fb_post_text(msg or content)
                    result = scmpy.tumblr_post_text(title or "Post", msg or content, tags)
                    print(f"Tumblr: {result.get('meta', {}).get('status', 'error')}")
                elif ptype == 'link':
                    url = content
                    if not url: url = input("Enter URL: ").strip()
                    scmpy.fb_post_link(url, msg)
                    result = scmpy.tumblr_post_link(title or "Link", url, desc or msg, tags)
                    print(f"Tumblr: {result.get('meta', {}).get('status', 'error')}")
                elif ptype == 'image':
                    img_url = None
                    filepath = None
                    source_choice = args.source
                    
                    if source_choice == '1':
                        img_url = input("Image URL: ").strip()
                    elif source_choice == '2':
                        filepath = input("File path: ").strip()
                    elif content: # If content provided, assume it's URL for simplicity or ask
                        if content.startswith('http'):
                            img_url = content
                        else: # Assume file if not URL
                            filepath = content
                    else:
                        if args.source == 'url':
                            img_url = input("Image URL: ").strip()
                        elif args.source == 'file':
                            filepath = input("File path: ").strip()
                        else:
                            # If no source or content, ask interactively
                            source_input = input("Image source: 1=URL, 2=File (default 1): ").strip() or "1"
                            if source_input == "1": img_url = input("Image URL: ").strip()
                            elif source_input == "2": filepath = input("File path: ").strip()

                    if not msg: msg = args.caption or input("Message: ").strip()
                    
                    if img_url:
                        scmpy.fb_post_image_url(img_url, msg)
                        result = scmpy.tumblr_post_photo(img_url, msg, tags)
                    elif filepath:
                        scmpy.fb_post_image_file(filepath, msg)
                        result = scmpy.tumblr_post_photo('', msg, tags, local_file=filepath)
                    print(f"Tumblr: {result.get('meta', {}).get('status', 'error')}")
                elif ptype == 'video':
                    url = content
                    if not url: url = input("Enter YouTube URL: ").strip()
                    scmpy.fb_post_link(url, msg) # Facebook treats video as a link post
                    result = scmpy.tumblr_post_video(url, msg, tags)
                    print(f"Tumblr: {result.get('meta', {}).get('status', 'error')}")
            sys.exit(0)
        
        if args.dla:
            import scmpy
            scmpy.download_all_images()
            sys.exit(0)
        
        if args.ltxt:
            import scmpy
            scmpy.list_text_files()
            sys.exit(0)
        
        if args.pimg is not None:
            import scmpy
            num = args.pimg if args.pimg != 'ASK' else input("Image number: ").strip()
            if num:
                try:
                    scmpy.post_image_by_number(int(num))
                except ValueError:
                    print("Invalid number")
            sys.exit(0)
        
        if args.plink is not None:
            import scmpy
            num = args.plink if args.plink != 'ASK' else input("Link number: ").strip()
            if num:
                try:
                    scmpy.post_link_by_number(int(num))
                except ValueError:
                    print("Invalid number")
            sys.exit(0)
        
        if args.pvid is not None:
            import scmpy
            num = args.pvid if args.pvid != 'ASK' else input("Video number: ").strip()
            if num:
                try:
                    scmpy.post_video_by_number(int(num))
                except ValueError:
                    print("Invalid number")
            sys.exit(0)
        
        if args.install:
            import scmpy
            scmpy.install_dependencies()
            sys.exit(0)
        
        if args.history:
            import scmpy
            scmpy.show_history()
            sys.exit(0)
        
        if args.update:
            version_checker.perform_update()
            sys.exit(0)
        
        if args.restart:
            version_checker.restart_app()

        if args.x:
            sys.exit(0)

        chooseAgain = "yes"
        while chooseAgain == "yes":
            result = choice()
            
            if result == "switch":
                return

        chooseAgain = input()

    mp()

if __name__ == "__main__":
     main()









