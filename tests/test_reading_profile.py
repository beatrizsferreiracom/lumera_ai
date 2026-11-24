from unittest.mock import patch
import pytest

from lumera.crew import extract_reading_profile
from lumera.models import ReadingProfile


@patch("lumera.crew.create_reading_profile_crew")
def test_extract_valid_reading_profile(mock_create_crew):
    expected_profile = ReadingProfile(
        genres=["fantasia"],
        themes=["romance"],
        min_pages=300,
        max_pages=500,
        series_preference=["standalone"],
    )

    mock_crew = mock_create_crew.return_value
    mock_crew.kickoff.return_value.pydantic = expected_profile

    user_request = "Quero um livro de fantasia com romance"

    profile = extract_reading_profile(user_request)

    assert isinstance(profile, ReadingProfile)
    assert profile == expected_profile

    mock_crew.kickoff.assert_called_once_with(
        inputs={"user_request": user_request}
    )


@patch("lumera.crew.create_reading_profile_crew")
def test_extract_invalid_reading_profile(mock_create_crew):
    mock_crew = mock_create_crew.return_value
    mock_crew.kickoff.return_value.pydantic = None

    with pytest.raises(
        ValueError,
        match="The agent did not return a valid reading profile",
    ):
        extract_reading_profile("Quero um livro de fantasia")


@patch("lumera.crew.create_reading_profile_crew")
def test_extract_empty_request(mock_create_crew):
    with pytest.raises(
        ValueError,
        match="User request cannot be empty",
    ):
        extract_reading_profile("   ")

    mock_create_crew.assert_not_called()
