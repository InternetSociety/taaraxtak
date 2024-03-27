from os import path
import pandas as pd
import logging
from os.path import join
import pytz
from datetime import datetime, date
import threading
from pathlib import Path

from typing import Optional

from config import config
import structlog

#
# Time
#
def now() -> pd.Timestamp:
    return pd.Timestamp.utcnow()


def is_in_future(timestamp: pd.Timestamp) -> bool:
    return timestamp > now()


def to_utc(t: datetime) -> datetime:
    return t.astimezone(pytz.utc)


#
# Type validation
#
def is_nonempty_str(my_str: str) -> bool:
    is_str = type(my_str) == str
    if is_str:
        return len(my_str) > 0
    return False


#
# Jurisdictions of providers
#
dirname = path.dirname(__file__)
pth = join(dirname, 'analysis', 'providers_labeled.csv')
provider_countries = pd.read_csv(pth).set_index('name').drop(['notes', 'url'], axis=1)
provider_countries = provider_countries['country (alpha2)'].to_dict()


def get_country(provider_name: str) -> Optional[str]:
    '''
    Returns alpha2 code (str of length 2).
    '''
    try:
        alpha2 = provider_countries[provider_name]
        if len(alpha2) == 2:
            return alpha2
        return None
    except (TypeError):
        logging.debug(f'Country code for {provider_name} is not a string: {alpha2}')
        return None
    except (KeyError):
        logging.info(f'Cannot find country for {provider_name}')
        return None


def configure_logging():
    def convert_datetimes(_logger, _log_method, event_dict):
        for k in event_dict:
            if isinstance(event_dict[k], date):
                event_dict[k] = str(event_dict[k])
        return event_dict


    processors = [
        structlog.processors.add_log_level,
        convert_datetimes,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper(fmt="iso"),
    ]

    if config["log_file"] is not None:
        processors.append(structlog.processors.JSONRenderer())
        structlog.configure(
            processors=processors,
            logger_factory=structlog.WriteLoggerFactory(file=Path(config["log_file"]).with_suffix(".log").open("wt")),
        )
    else:
        processors.append(structlog.dev.ConsoleRenderer())
        structlog.configure(processors=processors)

    return structlog.get_logger()


def run_threaded(job_func):
    job_thread = threading.Thread(target=job_func)
    job_thread.start()
