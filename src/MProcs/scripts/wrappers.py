import importlib


class AppWrapper:
    name = None
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

    def run(self, tui):
        lpro, lpro_s = self._modules()
        vc = self._vc()
        tui.set_app(self)
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


ALL_APPS = [
    MdcciWrapper(),
    NeonBunnyWrapper(),
    DojicalWrapper(),
    BumerangWrapper(),
    AlokateWrapper(),
    M0nkrpgWrapper(),
]
