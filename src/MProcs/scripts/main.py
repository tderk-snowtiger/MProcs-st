import os
import sys


def run():
    if sys.stdout.isatty() and not os.environ.get("MPROCS_NO_TUI"):
        try:
            from . import tui
        except ImportError:
            import tui
        tui.run()
        return
    _run_cli()


def _run_cli():
    import lpro
    import lpro_s
    import version_checker

    class Session:
        usr_state = "zeta"

    version_checker.print_version_status()
    active = "s"
    while True:
        if active == "s":
            print("\nnot recording")
            lpro_s.change_username(Session.usr_state)
            lpro_s.main()
            Session.usr_state = lpro_s.raw_usr
            active = "l"
        else:
            print("\nrecording")
            lpro.change_username(Session.usr_state)
            lpro.main()
            Session.usr_state = lpro.raw_usr
            active = "s"


if __name__ == "__main__":
    run()
