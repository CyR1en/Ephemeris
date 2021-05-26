import sys

import fbs_runtime.platform
from fbs_runtime.application_context.PyQt5 import ApplicationContext

from app import EphemerisApp


def hide_rocket():
    if not fbs_runtime.platform.is_mac():
        return
    from AppKit import NSApp
    NSApp.setActivationPolicy_(1)


if __name__ == '__main__':
    app_ctx = ApplicationContext()
    hide_rocket()
    ephemeris = EphemerisApp(app_ctx)
    sys.exit(app_ctx.app.exec_())
