# std
import os
import unittest

# lib
import confuse

# project
from src.notifier.smtp_notifier import SMTPNotifier
from .dummy_events import DummyEvents


class TestSMTPNotifier(unittest.TestCase):
    def setUp(self) -> None:
        sender = os.getenv("SMTP_SENDER")
        sender_name = os.getenv("SMTP_SENDER_NAME")
        recipient = os.getenv("SMTP_RECIPIENT")
        username_smtp = os.getenv("SMTP_USERNAME")
        password_smtp = os.getenv("SMTP_PASSWORD")
        host = os.getenv("SMTP_HOST")
        port: int = 587
        if os.getenv("SMTP_PORT"):
            port = int(os.environ["SMTP_PORT"])
        smtp_auth = True
        if os.getenv("SMTP_ENABLE_AUTH"):
            smtp_auth = os.environ["SMTP_ENABLE_AUTH"].lower() in ["true", "1", "yes"]
        self.assertIsNotNone(sender, "You must export SMTP_SENDER as env variable")
        self.assertIsNotNone(sender_name, "You must export SMTP_SENDER_NAME as env variable")
        self.assertIsNotNone(recipient, "You must export SMTP_RECIPIENT as env variable")
        self.assertIsNotNone(host, "You must export SMTP_HOST as env variable")

        self.config = confuse.Configuration("chiadog", __name__)
        self.config.set(
            {
                "enable": True,
                "daily_stats": True,
                "wallet_events": True,
                "decreasing_plot_events": True,
                "increasing_plot_events": True,
                "credentials": {
                    "sender": sender,
                    "sender_name": sender_name,
                    "recipient": recipient,
                    "enable_smtp_auth": smtp_auth,
                    "username_smtp": username_smtp,
                    "password_smtp": password_smtp,
                    "host": host,
                    "port": port,
                },
            }
        )

        self.notifier = SMTPNotifier(
            title_prefix="Test",
            config=self.config,
        )

    @unittest.skipUnless(os.getenv("SMTP_HOST"), "Run only if SMTP available")
    def testSTMPLowPriorityNotifications(self):
        success = self.notifier.send_events_to_user(events=DummyEvents.get_low_priority_events())
        self.assertTrue(success)

    @unittest.skipUnless(os.getenv("SMTP_HOST"), "Run only if SMTP available")
    def testSMTPNormalPriorityNotifications(self):
        success = self.notifier.send_events_to_user(events=DummyEvents.get_normal_priority_events())
        self.assertTrue(success)

    @unittest.skipUnless(os.getenv("SMTP_HOST"), "Run only if SMTP available")
    def testSTMPHighPriorityNotifications(self):
        success = self.notifier.send_events_to_user(events=DummyEvents.get_high_priority_events())
        self.assertTrue(success)
