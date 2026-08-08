import builtins
import curses
import datetime
import locale
import os
import queue
import re
import subprocess
import sys
import threading
import time
import traceback

import wrappers
import session
import version_checker

_SGR = re.compile(r'\x1b\[([0-9;]*)([a-zA-Z])')
_STRIP_SGR = re.compile(r'\x1b\[[0-9;]*m')

_FG_PAIRS = {30: 1, 31: 2, 32: 3, 33: 4, 34: 5, 35: 6, 36: 7, 37: 8}
_BASE_COLORS = (curses.COLOR_BLACK, curses.COLOR_RED, curses.COLOR_GREEN, curses.COLOR_YELLOW,
                curses.COLOR_BLUE, curses.COLOR_MAGENTA, curses.COLOR_CYAN, curses.COLOR_WHITE)

_MAX_LINES = 20000

class _ReturnToMenu(BaseException):
    pass

class _AnsiState:
    def __init__(self):
        self.bold = False
        self.underline = False
        self.fg = 0

    def attr(self):
        a = self.fg
        if self.bold:
            a |= curses.A_BOLD
        if self.underline:
            a |= curses.A_UNDERLINE
        return a


def _wch_width(ch):
    o = ord(ch)
    if o < 0x1100:
        return 1
    if o <= 0x115F:
        return 2
    if 0x2E80 <= o <= 0xA4CF:
        return 2
    if 0xAC00 <= o <= 0xD7A3:
        return 2
    if 0xF900 <= o <= 0xFAFF:
        return 2
    if 0xFE30 <= o <= 0xFE4F:
        return 2
    if 0xFF00 <= o <= 0xFF60:
        return 2
    if 0xFFE0 <= o <= 0xFFE6:
        return 2
    if 0x3000 <= o <= 0x303F:
        return 2
    if 0x1F300 <= o <= 0x1FAFF:
        return 2
    return 1


def _str_width(s):
    return sum(_wch_width(c) for c in s)


def _strip_ansi(s):
    return _STRIP_SGR.sub('', s)


def _clean_csi(text):
    out = []
    i = 0
    n = len(text)
    while i < n:
        if text[i] == '\x1b' and i + 1 < n and text[i + 1] == '[':
            j = i + 2
            while j < n and text[j] in '0123456789;':
                j += 1
            if j < n and text[j] == 'm':
                out.append(text[i:j + 1])
            i = j + 1
        else:
            out.append(text[i])
            i += 1
    return ''.join(out)


def _apply_cr(text):
    cols = []
    pos = 0
    for ch in text:
        if ch == '\r':
            pos = 0
        elif ch == '\n':
            cols.append('\n')
            pos = 0
        else:
            if pos < len(cols):
                cols[pos] = ch
            else:
                cols.append(ch)
            pos += 1
    return ''.join(cols)


class _StderrProxy:
    def __init__(self, emit, real):
        self._emit = emit
        self._real = real
        self.encoding = getattr(real, 'encoding', 'utf-8')

    def write(self, text):
        if text:
            self._emit(str(text))
        return len(str(text))

    def flush(self):
        pass

    def isatty(self):
        return True

    def fileno(self):
        return self._real.fileno()


def _apply_sgr(state, codes):
    for code in codes:
        if code == 0:
            state.bold = False
            state.underline = False
            state.fg = 0
        elif code == 1:
            state.bold = True
        elif code == 4:
            state.underline = True
        elif code == 22:
            state.bold = False
        elif code == 24:
            state.underline = False
        elif 30 <= code <= 37:
            state.fg = curses.color_pair(_FG_PAIRS.get(code, 0))
        elif 90 <= code <= 97:
            state.fg = curses.color_pair(_FG_PAIRS.get(code - 60, 0))
            state.bold = True
        elif code == 39:
            state.fg = 0


def _parse_ansi(text):
    state = _AnsiState()
    segs = []
    buf = []
    i = 0
    n = len(text)

    def flush():
        if buf:
            segs.append((state.attr(), ''.join(buf)))
            buf.clear()

    while i < n:
        if text[i] == '\x1b':
            m = _SGR.match(text, i)
            if m:
                flush()
                params = m.group(1)
                codes = [int(p) for p in params.split(';') if p.isdigit()] if params else [0]
                _apply_sgr(state, codes)
                i = m.end()
                continue
            if i + 1 < n and text[i + 1] == '[':
                j = i + 2
                while j < n and text[j] in '0123456789;':
                    j += 1
                if j < n and text[j] not in 'm':
                    i = j + 1
                    continue
            i += 1
            continue
        buf.append(text[i])
        i += 1
    flush()
    return segs


def _wrap_segments(segments, width):
    tokens = []
    pending = ''
    for attr, text in segments:
        for part in re.split(r'(\S+)', text):
            if not part:
                continue
            if part[0].isspace():
                pending += part
            else:
                tokens.append((pending, attr, part))
                pending = ''
    lines = []
    cur = []
    cur_w = 0
    for ws, attr, word in tokens:
        w = _str_width(word)
        ws_w = _str_width(ws)
        if cur and cur_w + ws_w + w > width:
            lines.append(cur)
            cur = []
            cur_w = 0
        if w > width:
            if cur:
                lines.append(cur)
                cur = []
                cur_w = 0
            chunk = ''
            cw = 0
            for ch in word:
                cc = _wch_width(ch)
                if chunk and cw + cc > width:
                    lines.append([(attr, chunk)])
                    chunk = ch
                    cw = cc
                else:
                    chunk += ch
                    cw += cc
            if chunk:
                cur = [(attr, chunk)]
                cur_w = cw
        else:
            if cur:
                cur.append((attr, ws))
                cur_w += ws_w
            cur.append((attr, word))
            cur_w += w
    if cur:
        lines.append(cur)
    return lines


class MProcsTUI:
    def __init__(self):
        self._real_print = builtins.print
        self._real_input = builtins.input
        self._real_sleep = time.sleep
        self._orig_system = os.system
        self._orig_subprocess_run = subprocess.run
        self._orig_stderr = sys.stderr
        self._out_q = queue.Queue()
        self._in_q = queue.Queue()
        self._selection_q = queue.Queue()
        self.apps = wrappers.ALL_APPS
        self.menu_mode = True
        self.menu_index = 0
        self.return_to_menu = False
        self.selected_app = None
        self.session_started = False
        self.active_name = None
        self.running = True
        self.app_done = False
        self.exit_requested = False
        self._interrupt = False
        self._submit_time = 0.0
        self.input_active = False
        self.input_locked = False
        self.input_prompt = ''
        self.input_prompt_segs = []
        self.input_echo_prompt = True
        self.edit = ''
        self.cursor = 0
        self.hscroll = 0
        self.raw = []
        self.lines = []
        self.pending = ''
        self.follow = True
        self.scroll_top = 0
        self.width = 80
        self.height = 24
        self.mode = ''
        self.username = 'zeta'
        self._stdscr = None
        self._dirty = True
        self._last_clock = None

    def _emit(self, text):
        self._out_q.put(text)
        self._dirty = True

    def _process_text(self, text):
        if '\x1b[2J' in text or '\x1b[3J' in text:
            self.raw = []
            self.lines = []
            self.pending = ''
            self.follow = True
            self.scroll_top = 0
        text = _clean_csi(text)
        if not text:
            return
        text = text.replace('\t', '    ')
        text = self.pending + text
        parts = text.split('\n')
        self.pending = _apply_cr(parts.pop())
        w = max(1, self.width - 1)
        for rl in parts:
            rl = _apply_cr(rl)
            self.raw.append(rl)
            if rl == '':
                self.lines.append([])
                continue
            segs = _parse_ansi(rl)
            if _str_width(_strip_ansi(rl)) <= w:
                self.lines.append(segs)
            else:
                self.lines.extend(_wrap_segments(segs, w))
        if len(self.raw) > _MAX_LINES:
            del self.raw[:len(self.raw) - _MAX_LINES]
        if len(self.lines) > _MAX_LINES * 2:
            del self.lines[:len(self.lines) - _MAX_LINES * 2]

    def _rebuild(self):
        w = max(1, self.width - 1)
        self.lines = []
        for rl in self.raw:
            if rl == '':
                self.lines.append([])
                continue
            segs = _parse_ansi(rl)
            if _str_width(_strip_ansi(rl)) <= w:
                self.lines.append(segs)
            else:
                self.lines.extend(_wrap_segments(segs, w))

    def _make_print(self):
        def _print(*args, **kwargs):
            if self.return_to_menu:
                raise _ReturnToMenu()
            f = kwargs.pop('file', None)
            if f is not None and f not in (sys.stdout, sys.stderr):
                if f.__class__.__name__ == 'SkipLog':
                    return
                try:
                    self._real_print(*args, file=f, **kwargs)
                except Exception:
                    pass
                return
            sep = kwargs.pop('sep', ' ')
            end = kwargs.pop('end', '\n')
            kwargs.pop('flush', None)
            text = sep.join(str(a) for a in args)
            self._emit(text + end)
        return _print

    def _make_input(self):
        def _input(prompt=''):
            return self._ask_input(prompt)
        return _input

    def _make_system(self):
        def _system(command):
            if isinstance(command, str):
                c = command.strip()
                if c in ('clear', 'cls') or c.startswith('clear') or c.startswith('cls'):
                    self._emit('\x1b[2J')
                    return 0
            return self._orig_system(command)
        return _system

    def _make_subprocess_run(self):
        def _run(*args, **kwargs):
            cmd = args[0] if args else kwargs.get('args')
            is_clear = (
                (isinstance(cmd, (list, tuple)) and cmd and cmd[0] in ('clear', 'cls'))
                or (isinstance(cmd, str) and cmd.strip() in ('clear', 'cls'))
            )
            if is_clear:
                self._emit('\x1b[2J')
                text = kwargs.get('text') or kwargs.get('universal_newlines')
                return subprocess.CompletedProcess(
                    cmd if isinstance(cmd, (list, tuple)) else [cmd],
                    0,
                    '' if text else b'',
                    '' if text else b''
                )
            return self._orig_subprocess_run(*args, **kwargs)
        return _run

    def _install(self):
        builtins.print = self._make_print()
        builtins.input = self._make_input()
        os.system = self._make_system()
        subprocess.run = self._make_subprocess_run()
        time.sleep = self._make_sleep()
        sys.stderr = _StderrProxy(self._emit, self._orig_stderr)

    def _restore(self):
        builtins.print = self._real_print
        builtins.input = self._real_input
        os.system = self._orig_system
        subprocess.run = self._orig_subprocess_run
        time.sleep = self._real_sleep
        sys.stderr = self._orig_stderr

    def _make_sleep(self):
        def _sleep(secs):
            if self.return_to_menu:
                raise _ReturnToMenu()
            if self._interrupt:
                self._interrupt = False
                raise KeyboardInterrupt
            end = time.monotonic() + max(0.0, secs)
            while True:
                remaining = end - time.monotonic()
                if remaining <= 0:
                    return
                if self.return_to_menu:
                    raise _ReturnToMenu()
                if self._interrupt:
                    self._interrupt = False
                    raise KeyboardInterrupt
                self._real_sleep(min(remaining, 0.05))
        return _sleep

    def _ask_input(self, prompt=''):
        with self._lock:
            self.input_active = True
            self.input_locked = False
            self._interrupt = False
            self.input_prompt = prompt
            self.edit = ''
            self.cursor = 0
            self.hscroll = 0
            pw = _str_width(_strip_ansi(prompt))
            if pw <= max(8, self.width - 3):
                self.input_prompt_segs = _parse_ansi(prompt)
                self.input_echo_prompt = True
            else:
                self.input_prompt_segs = _parse_ansi('> ')
                self.input_echo_prompt = False
                self._emit(prompt + '\n')
        self._dirty = True
        while True:
            if self.exit_requested:
                raise SystemExit(0)
            if self.return_to_menu:
                raise _ReturnToMenu()
            try:
                value = self._in_q.get(timeout=0.1)
            except queue.Empty:
                continue
            if self.exit_requested:
                raise SystemExit(0)
            if self.return_to_menu:
                raise _ReturnToMenu()
            return value

    def _submit(self):
        value = self.edit
        prompt = self.input_prompt
        echo_prompt = self.input_echo_prompt
        self.edit = ''
        self.cursor = 0
        self.hscroll = 0
        self.input_locked = True
        self._submit_time = time.monotonic()
        self.follow = True
        self.scroll_top = 0
        line = (prompt + value) if echo_prompt else value
        self._emit(line + '\n')
        self._in_q.put(value)

    def _request_exit(self):
        self.exit_requested = True
        self.running = False
        if self.input_active:
            self._in_q.put(None)
        try:
            self._selection_q.put(None)
        except Exception:
            pass

    def _scroll_by(self, delta):
        total = len(self.lines)
        count = max(0, self.height - 4)
        first = self._first_visible(total, count)
        bottom = max(0, total - count)
        target = first + delta
        if target >= bottom:
            self.follow = True
            self.scroll_top = 0
        else:
            self.follow = False
            self.scroll_top = max(0, target)
        self._dirty = True

    def _handle_ctrl_c(self):
        if self.input_locked:
            self._interrupt = True
        else:
            self._request_exit()

    def _handle_key(self, key):
        if isinstance(key, int) and key < 0:
            return
        if key == 27 or key == '\x1b':
            self._handle_esc()
            return
        if self.menu_mode:
            self._handle_menu_key(key)
            return
        if key in (curses.KEY_PPAGE, curses.KEY_NPAGE):
            page = max(3, self.height - 4)
            self._scroll_by(-page if key == curses.KEY_PPAGE else page)
            return
        if key in (curses.KEY_UP, curses.KEY_DOWN):
            self._scroll_by(-1 if key == curses.KEY_UP else 1)
            return
        if not self.input_active:
            if key in (curses.KEY_HOME,):
                self.follow = False
                self.scroll_top = 0
            elif key in (curses.KEY_END,):
                self.follow = True
                self.scroll_top = 0
            elif isinstance(key, str) and key.lower() == 'q':
                self._request_exit()
            self._dirty = True
            return
        if self.input_locked:
            return
        if isinstance(key, int):
            if key in (10, 13, curses.KEY_ENTER):
                self._submit()
            elif key in (8, 127, curses.KEY_BACKSPACE):
                if self.cursor > 0:
                    self.edit = self.edit[:self.cursor - 1] + self.edit[self.cursor:]
                    self.cursor -= 1
            elif key == curses.KEY_DC:
                if self.cursor < len(self.edit):
                    self.edit = self.edit[:self.cursor] + self.edit[self.cursor + 1:]
            elif key == curses.KEY_LEFT:
                self.cursor = max(0, self.cursor - 1)
            elif key == curses.KEY_RIGHT:
                self.cursor = min(len(self.edit), self.cursor + 1)
            elif key == curses.KEY_HOME:
                self.cursor = 0
            elif key == curses.KEY_END:
                self.cursor = len(self.edit)
            elif key == 21:
                self.edit = ''
                self.cursor = 0
            elif key == 3:
                self._handle_ctrl_c()
            self._dirty = True
            return
        if isinstance(key, str):
            if key in ('\n', '\r'):
                self._submit()
            elif key in ('\x7f', '\x08'):
                if self.cursor > 0:
                    self.edit = self.edit[:self.cursor - 1] + self.edit[self.cursor:]
                    self.cursor -= 1
            elif key == '\x03':
                self._handle_ctrl_c()
            elif key == '\x15':
                self.edit = ''
                self.cursor = 0
            elif key == '\t':
                self.edit = self.edit[:self.cursor] + '    ' + self.edit[self.cursor:]
                self.cursor += 4
            elif key >= ' ':
                self.edit = self.edit[:self.cursor] + key + self.edit[self.cursor:]
                self.cursor += 1
            self._dirty = True

    def _handle_esc(self):
        if self.menu_mode:
            if self.session_started:
                self.menu_mode = False
        else:
            self.menu_mode = True
        self._dirty = True

    def _handle_menu_key(self, key):
        if isinstance(key, int):
            if key == curses.KEY_UP:
                self.menu_index = (self.menu_index - 1) % len(self.apps)
                self._dirty = True
                return
            if key == curses.KEY_DOWN:
                self.menu_index = (self.menu_index + 1) % len(self.apps)
                self._dirty = True
                return
            if key in (10, 13, curses.KEY_ENTER):
                self._launch(self.menu_index)
            return
        if isinstance(key, str):
            k = key.lower()
            if k in ('\n', '\r'):
                self._launch(self.menu_index)
            elif k == 'q':
                self._request_exit()
            elif k.isdigit() and 1 <= int(k) <= len(self.apps):
                self._launch(int(k) - 1)

    def _launch(self, idx):
        self.menu_index = idx
        self.selected_app = self.apps[idx]
        self.menu_mode = False
        self.app_done = False
        self.set_app(self.selected_app)
        if not self.session_started:
            self._selection_q.put(idx)
        self._dirty = True

    def set_app(self, wrapper):
        self.active_name = wrapper.name

    def _first_visible(self, total, count):
        if self.follow:
            return max(0, total - count)
        return min(self.scroll_top, max(0, total - count))

    def _render_line(self, row, segs, width):
        std = self._stdscr
        std.move(row, 0)
        std.clrtoeol()
        x = 0
        for attr, text in segs:
            if x >= width:
                return
            seg_w = _str_width(text)
            if x + seg_w <= width:
                try:
                    std.addstr(row, x, text, attr)
                except curses.error:
                    return
                x += seg_w
                continue
            for ch in text:
                cw = _wch_width(ch)
                if x + cw > width:
                    return
                try:
                    std.addstr(row, x, ch, attr)
                except curses.error:
                    return
                x += cw

    def _current_username(self):
        try:
            return session.raw_usr or self.username
        except Exception:
            return self.username or 'zeta'

    def _draw_header(self):
        std = self._stdscr
        w = self.width
        now = datetime.datetime.now()
        clock = now.strftime('%Y-%m-%d %H:%M:%S')
        if self.menu_mode:
            name = version_checker.PACKAGE_NAME
            mode = 'launcher'
        else:
            name = self.active_name or version_checker.PACKAGE_NAME
            mode = self.mode or 'idle'
        left = ' %s | %s (v%s) | snowtiger <%s> | %s ' % (
            name,
            version_checker.MPROCS_VERSION,
            version_checker.PACKAGE_VERSION,
            self._current_username(),
            mode
        )
        right = ' ' + clock + ' '
        a = curses.A_REVERSE
        std.move(0, 0)
        std.clrtoeol()
        rw = _str_width(right)
        avail = max(0, w - rw - 1)
        lw = _str_width(left)
        if lw > avail:
            left = left[:avail]
        std.addstr(0, 0, left, a)
        if rw < w:
            std.addstr(0, w - rw, right, a)
        std.move(1, 0)
        std.clrtoeol()
        for c in range(w):
            try:
                std.addch(1, c, curses.ACS_HLINE, curses.A_DIM)
            except curses.error:
                break

    def _draw_footer(self):
        std = self._stdscr
        row = self.height - 1
        w = self.width
        std.move(row, 0)
        std.clrtoeol()
        right = 'P0cket Un1-Ver$e: Authored by tderk, ISOBP'
        rw = _str_width(right)
        if rw < w:
            try:
                std.addstr(row, w - rw, right, curses.A_DIM)
            except curses.error:
                pass

    def _draw_output(self):
        std = self._stdscr
        if self.menu_mode:
            self._draw_menu()
            return
        h = self.height
        count = max(0, h - 4)
        total = len(self.lines)
        first = self._first_visible(total, count)
        for r in range(count):
            idx = first + r
            if idx < total:
                self._render_line(2 + r, self.lines[idx], self.width)
            else:
                std.move(2 + r, 0)
                std.clrtoeol()

    def _draw_menu(self):
        std = self._stdscr
        w = self.width
        h = self.height
        for r in range(2, h - 1):
            try:
                std.move(r, 0)
                std.clrtoeol()
            except curses.error:
                break

        def put(row, col, text, attr=0):
            try:
                if col + _str_width(text) <= w:
                    std.addstr(row, col, text, attr)
            except curses.error:
                pass

        put(2, 0, ' MProcs Launcher ', curses.A_BOLD | curses.A_REVERSE)
        y = 4
        for i, app in enumerate(self.apps, 1):
            marker = '>' if (i - 1) == self.menu_index else ' '
            put(y, 0, '  %s %d) %-10s' % (marker, i, app.name))
            y += 1
        put(y + 1, 0, '  q quit | 1-%d or arrows+Enter to launch | Esc back' % len(self.apps), curses.A_DIM)

    def _draw_input(self):
        std = self._stdscr
        row = self.height - 2
        w = self.width
        std.move(row, 0)
        std.clrtoeol()
        if self.menu_mode:
            return
        if not self.input_active:
            return
        if self.input_locked and time.monotonic() - self._submit_time > 1.0:
            return
        stream = []
        for attr, text in self.input_prompt_segs:
            for ch in text:
                stream.append((attr, ch))
        edit_segs = _parse_ansi(self.edit)
        for attr, text in edit_segs:
            for ch in text:
                stream.append((attr, ch))
        pw = sum(_str_width(t) for _, t in self.input_prompt_segs)
        cur_pos = _str_width(self.edit[:self.cursor])
        disp = pw + cur_pos
        visible = w
        if disp < self.hscroll:
            self.hscroll = disp
        elif disp >= self.hscroll + visible:
            self.hscroll = disp - visible + 1
        if self.hscroll < 0:
            self.hscroll = 0
        show_cursor = not self.input_locked
        x = 0
        for attr, ch in stream:
            cw = _wch_width(ch)
            if x + cw <= self.hscroll:
                x += cw
                continue
            if x >= self.hscroll + visible:
                break
            a = attr
            if show_cursor and x == disp:
                a |= curses.A_REVERSE
            try:
                std.addstr(row, x - self.hscroll, ch, a)
            except curses.error:
                pass
            x += cw
        if show_cursor and disp >= x:
            sx = disp - self.hscroll
            if sx < visible:
                try:
                    std.addstr(row, sx, ' ', curses.A_REVERSE)
                except curses.error:
                    pass

    def _draw(self):
        std = self._stdscr
        h, w = std.getmaxyx()
        self.height = max(3, h)
        self.width = max(1, w)
        self._draw_header()
        self._draw_output()
        self._draw_footer()
        self._draw_input()
        std.refresh()

    def _app_entry(self, idx):
        self.apps[idx].run(self)

    def _thread_wrapper(self):
        try:
            while not self.exit_requested:
                try:
                    idx = self._selection_q.get()
                except Exception:
                    break
                if self.exit_requested or idx is None:
                    break
                self.session_started = True
                self.app_done = False
                self.menu_mode = False
                try:
                    self._app_entry(idx)
                except SystemExit:
                    self._request_exit()
                except KeyboardInterrupt:
                    pass
                except BaseException:
                    try:
                        self._emit('\n' + traceback.format_exc() + '\n')
                    except Exception:
                        pass
                finally:
                    self._interrupt = False
                    self.app_done = True
                    self.menu_mode = True
                    self.session_started = False
        finally:
            self.app_done = True

    def _main_loop(self):
        std = self._stdscr
        std.timeout(10)
        while self.running:
            try:
                got_output = False
                try:
                    while True:
                        self._process_text(self._out_q.get_nowait())
                        got_output = True
                except queue.Empty:
                    pass
                if got_output:
                    self._dirty = True
                h, w = std.getmaxyx()
                if (h, w) != (self.height, self.width):
                    self.height = max(3, h)
                    self.width = max(1, w)
                    self._rebuild()
                    self._dirty = True
                if self._dirty:
                    self._draw()
                    self._dirty = False
                try:
                    while True:
                        try:
                            key = std.get_wch()
                        except Exception:
                            break
                        if key == -1:
                            break
                        self._handle_key(key)
                        if self._dirty:
                            self._draw()
                            self._dirty = False
                except Exception:
                    pass
                now = datetime.datetime.now()
                if self._last_clock is None or now.strftime('%S') != self._last_clock:
                    self._last_clock = now.strftime('%S')
                    self._dirty = True
                if self._dirty:
                    self._draw()
                    self._dirty = False
            except KeyboardInterrupt:
                self._handle_ctrl_c()
        self._real_sleep(0.2)

    def _main(self, stdscr):
        self._stdscr = stdscr
        stdscr.keypad(True)
        try:
            curses.curs_set(0)
        except curses.error:
            pass
        if curses.has_colors():
            curses.start_color()
            try:
                curses.use_default_colors()
            except curses.error:
                pass
            for i, color in enumerate(_BASE_COLORS, 1):
                curses.init_pair(i, color, -1)
        h, w = stdscr.getmaxyx()
        self.height = max(3, h)
        self.width = max(1, w)
        self._lock = threading.Lock()
        thread = threading.Thread(target=self._thread_wrapper, daemon=True)
        thread.start()
        self._main_loop()


def run():
    tui = MProcsTUI()
    try:
        locale.setlocale(locale.LC_ALL, '')
    except Exception:
        pass
    tui._install()
    try:
        curses.wrapper(tui._main)
    finally:
        tui._restore()


if __name__ == '__main__':
    run()
