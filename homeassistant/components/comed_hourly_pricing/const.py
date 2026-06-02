"""Constants for the ComEd hourly pricing integration."""

from datetime import timedelta

DOMAIN = "comed_hourly_pricing"
PLATFORMS = ["sensor"]

DEFAULT_OFFSET = 0.0

CONF_CURRENT_HOUR_AVERAGE = "current_hour_average"
CONF_FIVE_MINUTE = "five_minute"
CONF_MONITORED_FEED = "monitored_feed"
CONF_MONITORED_FEEDS = "monitored_feeds"
CONF_SENSOR_TYPE = "type"

# Update interval and request timeouts for the ComEd
# pricing data
SCAN_INTERVAL = timedelta(minutes=5)
REQUEST_TIMEOUT_SECONDS = 10
