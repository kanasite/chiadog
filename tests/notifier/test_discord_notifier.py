# std
import os
import unittest

# lib
import confuse

# project
from src.notifier.discord_notifier import DiscordNotifier
from .dummy_events import DummyEvents


class TestDiscordNotifier(unittest.TestCase):
    def setUp(self) -> None:
        webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
        self.assertIsNotNone(webhook_url, "You must export DISCORD_WEBHOOK_URL as env variable")
        self.config = confuse.Configuration("chiadog", __name__)
        self.config.set(
            {
                "enable": True,
                "daily_stats": True,
                "wallet_events": True,
                "decreasing_plot_events": True,
                "increasing_plot_events": True,
                "credentials": {"webhook_url": webhook_url},
            }
        )
        self.notifier = DiscordNotifier(
            title_prefix="Test",
            config=self.config,
        )

    @unittest.skipUnless(os.getenv("DISCORD_WEBHOOK_URL"), "Run only if webhook available")
    def testDiscordLowPriorityNotifications(self):
        success = self.notifier.send_events_to_user(events=DummyEvents.get_low_priority_events())
        self.assertTrue(success)

    @unittest.skipUnless(os.getenv("DISCORD_WEBHOOK_URL"), "Run only if webhook available")
    def testDiscordNormalPriorityNotifications(self):
        success = self.notifier.send_events_to_user(events=DummyEvents.get_normal_priority_events())
        self.assertTrue(success)

    @unittest.skipUnless(os.getenv("DISCORD_WEBHOOK_URL"), "Run only if webhook available")
    def testDiscordHighPriorityNotifications(self):
        success = self.notifier.send_events_to_user(events=DummyEvents.get_high_priority_events())
        self.assertTrue(success)
