"""Test the ComEd hourly pricing api client."""

from aiohttp import ClientError
import pytest

from homeassistant.components.comed_hourly_pricing.coordinator import ComedApiClient
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from tests.test_util.aiohttp import AiohttpClientMocker


@pytest.mark.parametrize(
    ("sensor_type", "api_type", "api_price", "expected_result"),
    [
        ("five_minute", "5minutefeed", "2.5", 0.025),
        ("current_hour_average", "currenthouraverage", "3.5", 0.035),
    ],
    ids=["five_minute", "current_hour_average"],
)
async def test_get_data_success(
    hass: HomeAssistant,
    aioclient_mock: AiohttpClientMocker,
    sensor_type: str,
    api_type: str,
    api_price: str,
    expected_result: float,
) -> None:
    """Test get_data returns data correctly."""
    aioclient_mock.get(
        f"https://hourlypricing.comed.com/api?type={api_type}",
        json=[{"price": api_price}],
    )

    session = async_get_clientsession(hass)
    client = ComedApiClient(session)
    result = await client.get_data(sensor_type)

    assert result == expected_result


async def test_get_data_unknown_sensor(hass: HomeAssistant) -> None:
    """Test get_data unknown sensor type."""
    session = async_get_clientsession(hass)
    client = ComedApiClient(session)
    with pytest.raises(ValueError, match="Unknown sensor type: unknown"):
        await client.get_data("unknown")


@pytest.mark.parametrize(
    ("exc", "json_data", "expected_exception", "match"),
    [
        (
            TimeoutError("Timeout"),
            None,
            TimeoutError,
            "Timeout",
        ),
        (
            ClientError("Error"),
            None,
            ClientError,
            "Error",
        ),
        (None, [], IndexError, "list index out of range"),
    ],
    ids=["timeout", "client_error", "value_error"],
)
async def test_get_data_errors(
    hass: HomeAssistant,
    aioclient_mock: AiohttpClientMocker,
    exc: Exception | None,
    json_data: list | None,
    expected_exception: type[Exception],
    match: str,
) -> None:
    """Test get_data handles errors."""
    if exc:
        aioclient_mock.get(
            "https://hourlypricing.comed.com/api?type=5minutefeed",
            exc=exc,
        )
    else:
        aioclient_mock.get(
            "https://hourlypricing.comed.com/api?type=5minutefeed",
            json=json_data,
        )

    session = async_get_clientsession(hass)
    client = ComedApiClient(session)
    with pytest.raises(expected_exception, match=match):
        await client.get_data("five_minute")
