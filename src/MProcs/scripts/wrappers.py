import importlib


class AppWrapper:
    name = None
    header_name = None
    package = None

    def __init__(self):
        self._lpro = None
        self._lpro_s = None

    def _vc(self):
        return importlib.import_module('MProcs.scripts.version_checker')

    def _modules(self):
        if self._lpro is None:
            try:
                self._lpro = importlib.import_module(self.package + '.scripts.lpro')
                self._lpro_s = importlib.import_module(self.package + '.scripts.lpro_s')
            except Exception:
                self._lpro = importlib.import_module('MProcs.scripts.lpro')
                self._lpro_s = importlib.import_module('MProcs.scripts.lpro_s')
        return self._lpro, self._lpro_s

    def run(self, tui, first=True):
        lpro, lpro_s = self._modules()
        _morn_swap = (self.name == 'morn')
        lpro._SWAP_NANO_MORN = _morn_swap
        lpro_s._SWAP_NANO_MORN = _morn_swap
        try:
            self._run_app(tui, lpro, lpro_s, first=first)
        finally:
            lpro._SWAP_NANO_MORN = False
            lpro_s._SWAP_NANO_MORN = False

    def _run_app(self, tui, lpro, lpro_s, first=True):
        vc = self._vc()
        tui.set_app(self)
        if first:
            latest, available = None, False
            try:
                latest, available = vc.check_for_update(timeout=2)
            except Exception:
                latest = None
            if latest is None:
                print('%s: (offline)' % vc.PACKAGE_NAME)
            elif available:
                print('%s: Update available - %s' % (vc.PACKAGE_NAME, latest))
            else:
                print('%s: Up-to-date' % vc.PACKAGE_NAME)
        session_usr = 'zeta'
        active = 's'
        while not tui.exit_requested:
            if active == 's':
                tui.mode = 'not recording'
                if first:
                    print('\nnot recording')
                try:
                    lpro_s.change_username(session_usr)
                except Exception:
                    pass
                lpro_s.main()
                session_usr = getattr(lpro_s, 'raw_usr', None) or session_usr
                active = 'l'
            else:
                tui.mode = 'recording'
                if first:
                    print('\nrecording')
                try:
                    lpro.change_username(session_usr)
                except Exception:
                    pass
                lpro.main()
                session_usr = getattr(lpro, 'raw_usr', None) or session_usr
                active = 's'


class DojicalWrapper(AppWrapper):
    name = 'Dojical'
    package = 'Dojical'


class NeonBunnyWrapper(AppWrapper):
    name = 'NeonBunny'
    package = 'NeonBunny'


class MdcciWrapper(AppWrapper):
    name = 'mdcci'
    package = 'mdcci'


class M0nkrpgWrapper(AppWrapper):
    name = 'm0nkrpg'
    package = 'm0nkrpg'


class BumerangWrapper(AppWrapper):
    name = 'bumerang'
    package = 'bumerang'


class AlokateWrapper(AppWrapper):
    name = 'alokate'
    package = 'alokate'


class MornWrapper(AppWrapper):
    name = 'morn'
    package = 'MProcs'


class DestinyWrapper(AppWrapper):
    name = 'Destiny'
    package = 'MProcs'


class VanillaWrapper(AppWrapper):
    name = 'Vanilla (Experimental)'
    header_name = 'Vanilla'
    package = 'MProcs'


ALL_APPS = [
    MdcciWrapper(),
    NeonBunnyWrapper(),
    DojicalWrapper(),
    BumerangWrapper(),
    AlokateWrapper(),
    M0nkrpgWrapper(),
    MornWrapper(),
    DestinyWrapper(),
    VanillaWrapper(),
]
