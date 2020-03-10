""" Distributor init file

Distributors: you can add custom code here to support particular distributions
of numpy.

For example, this is a good place to put any checks for hardware requirements.

The numpy standard source distribution will not put code in this file, so you
can safely replace this file with your own version.
"""


def init_numpy_mkl():
    """Initialize numpy+MKL."""
    try:
        import os

        # Disable Intel Fortran default console event handler.
        # Disable OpenBLAS affinity setting of the main thread that limits
        #   Python threads or processes to one core.
        for env in ('FOR_DISABLE_CONSOLE_CTRL_HANDLER',
                    'OPENBLAS_MAIN_FREE',
                    'GOTOBLAS_MAIN_FREE'):
            if env not in os.environ:
                os.environ[env] = '1'

        # Add the path of the Intel runtime DLLs to the DLL search path
        path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'DLLs')
        try:
            os.add_dll_directory(path)
        except Exception:
            pass
        environ_path = os.environ.get('PATH', '')
        if path not in environ_path:
            os.environ['PATH'] = os.pathsep.join((path, environ_path))

        # Load Intel C, Fortran, and OMP runtime DLLs into the process
        import ctypes
        ctypes.CDLL(os.path.join(path, 'libmmd.dll'))
        ctypes.CDLL(os.path.join(path, 'libifcoremd.dll'))
        ctypes.CDLL(os.path.join(path, 'libiomp5md.dll'))

    except Exception:
        pass


init_numpy_mkl()

NUMPY_MKL = True
