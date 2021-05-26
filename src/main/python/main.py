import sys

from fbs_runtime.application_context.PyQt5 import ApplicationContext

from app import EphemerisApp

if __name__ == '__main__':
    app_ctx = ApplicationContext()
    ephemeris = EphemerisApp(app_ctx)
    sys.exit(app_ctx.app.exec_())
