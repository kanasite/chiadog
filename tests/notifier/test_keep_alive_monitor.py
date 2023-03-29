# std
import logging
import os
import unittest
from datetime import datetime
from time import sleep
from typing import List
from urllib.parse import urlsplit

# lib
import confuse
import vcr

# project
from src.notifier import Event, EventService, EventType, EventPriority
from src.notifier.keep_alive_monitor import KeepAliveMonitor

logging.basicConfig(level=logging.DEBUG)


def sanitize_ping_url(request):
    # Ping services tend to have path based tokens, so drop the path
    request.uri = urlsplit(request.uri)._replace(path="/").geturl()
    return request


v = vcr.VCR(
    cassette_library_dir="tests/cassette/keep_alive_monitor",
    record_mode="once",
    match_on=["method", "host"],
    before_record_request=sanitize_ping_url,
)


class DummyNotifyManager:
    def __init__(self, callback):
        self._callback = callback

    def process_events(self, events: List[Event]):
        if self._callback:
            self._callback(events)


class TestKeepAliveMonitor(unittest.TestCase):
    def setUp(self) -> None:
        self.threshold_seconds = 3
        # Services that support keepalives
        test_services = [EventService.HARVESTER, EventService.WALLET]

        self.service_count = len(test_services)
        ping_url = os.getenv("REMOTE_PING_URL") or "https://hc-ping.com/mock"
        self.config = confuse.Configuration("chiadog", __name__)
        self.config.set(
            {
                "monitored_services": [service.name for service in test_services],
                "keep_alive_monitor": {
                    "enable_remote_ping": True,
                    "ping_url": ping_url,
                    "notify_threshold_seconds": {service.name: self.threshold_seconds for service in test_services},
                },
            }
        )
        # And their events
        self.keep_alive_events = [
            Event(type=EventType.KEEPALIVE, priority=EventPriority.NORMAL, service=service, message="")
            for service in test_services
        ]
        self.keep_alive_monitor = KeepAliveMonitor(self.config)

    def tearDown(self) -> None:
        self.keep_alive_monitor.stop()
        self.config.clear()

    def testBasic(self):
        received_high_priority_event = False

        def callback(events: List[Event]):
            nonlocal received_high_priority_event
            self.assertEqual(len(events), self.service_count, "Unexpected number of events")
            self.assertEqual(events[0].type, EventType.USER, "Unexpected event type")
            self.assertEqual(events[0].priority, EventPriority.HIGH, "Unexpected event priority")
            received_high_priority_event = True

        notify_manager = DummyNotifyManager(callback)
        self.keep_alive_monitor.set_notify_manager(notify_manager)

        begin_tp = datetime.now()

        with v.use_cassette("testBasic") as cass:
            for _ in range(self.threshold_seconds):
                self.keep_alive_monitor.process_events(self.keep_alive_events)
                sleep(1)

            while not received_high_priority_event:
                logging.info(f"Waiting for high priority event, this should only take {self.threshold_seconds}s")
                sleep(1)
            self.assertTrue(cass.all_played, "Remote ping requests did not happen as expected.")

        end_tp = datetime.now()
        seconds_elapsed = (end_tp - begin_tp).seconds

        # Check that high priority event did not fire before keep-alive signal stopped
        self.assertGreater(seconds_elapsed, 2 * self.threshold_seconds - 1)
