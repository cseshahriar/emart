import os


def get_logging_config(log_dir):
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "verbose": {"format": "[{asctime}] {levelname} {name}:{lineno} → {message}", "style": "{"},
            "simple": {"format": "{levelname} {message}", "style": "{"},
        },
        "handlers": {
            "console": {"class": "logging.StreamHandler", "formatter": "verbose"},
            "file": {
                "class": "logging.FileHandler",
                "filename": os.path.join(log_dir, "django.log"),
                "formatter": "verbose",
                "level": "INFO",
            },
            "errors": {
                "class": "logging.FileHandler",
                "filename": os.path.join(log_dir, "error.log"),
                "formatter": "verbose",
                "level": "ERROR",
            },
        },
        "root": {"handlers": ["console", "file"], "level": "INFO"},
        "loggers": {
            "django.request": {"handlers": ["errors"], "level": "ERROR", "propagate": False},
            "django.db.backends": {"handlers": ["console"], "level": "ERROR"},
        },
    }
