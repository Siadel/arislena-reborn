import logging
from py_base.utility import CWD, FULL_DATE_FORMAT

formatter = logging.Formatter(
    "[%(asctime)s]\t[%(levelname)s]\t%(module)s.py\t%(funcName)s()\tLINE %(lineno)d\n\t%(message)s",
    datefmt=FULL_DATE_FORMAT
)

ari_file_handler = logging.FileHandler(str(CWD / "arislena.log"), encoding="utf-8", mode="w")
ari_file_handler.setFormatter(formatter)

ari_logger = logging.getLogger("arislena")
ari_logger.setLevel(logging.DEBUG)
ari_logger.addHandler(ari_file_handler)
