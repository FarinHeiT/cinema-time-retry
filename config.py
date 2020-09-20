import logging


class Config:
    SECRET_KEY = "TOPSECRETKEY!"
    WTF_CSRF_SECRET_KEY = 'TOPSECRETKEY!'
    logging.getLogger('socketio').setLevel(logging.ERROR)
    logging.getLogger('engineio').setLevel(logging.ERROR)