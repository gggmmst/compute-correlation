import logging

##
## logging
##
# https://docs.python.org/2/howto/logging.html
# https://docs.python.org/2/library/logging.config.html
#
# Level    | When it is used
# -----    | ---------------
# DEBUG    | Detailed information, typically of interest only when diagnosing problems.
# INFO     | Confirmation that things are working as expected.
# WARNING  | An indication that something unexpected happened, or indicative of some problem in the near future (e.g. 'disk space low'). The software is still working as expected.
# ERROR    | Due to a more serious problem, the software has not been able to perform some function.
# CRITICAL | A serious error, indicating that the program itself may be unable to continue running.

logfmt = '%(asctime)s|%(name)s:%(lineno)s|%(levelname)s|%(message)s')
logging.basicConfig(
    level=logging.DEBUG,
#    level=logging.INFO,
    format=logfmt,
)
