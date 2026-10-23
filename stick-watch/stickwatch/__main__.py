"""Entry point: python -m stickwatch"""

from __future__ import annotations

import signal
import sys

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from .app import App
from .settings import SettingsWindow


def main(argv: list[str] | None = None) -> int:
    QApplication.setApplicationName("stick-watch")
    qapp = QApplication(argv if argv is not None else sys.argv)
    qapp.setQuitOnLastWindowClosed(True)

    app = App()
    settings = SettingsWindow(app)
    app.settings = settings
    app.start()
    settings.show()

    # Let Ctrl-C through from a console, and still save on the way out.
    signal.signal(signal.SIGINT, lambda *_: qapp.quit())
    nudge = QTimer()
    nudge.start(250)
    nudge.timeout.connect(lambda: None)

    qapp.aboutToQuit.connect(app.shutdown)
    return qapp.exec()


if __name__ == "__main__":
    raise SystemExit(main())
