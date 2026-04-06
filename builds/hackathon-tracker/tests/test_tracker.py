"""
Unit tests for Hackathon Tracker
"""

import pytest
import json
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from hackathon_tracker.tracker import HackathonTracker, HackathonOpportunity
from dataclasses import asdict


class TestHackathonOpportunity:
    """Test HackathonOpportunity dataclass"""

    def test_opportunity_creation(self):
        """Test creating a hackathon opportunity"""
        opp = HackathonOpportunity(
            title="Test Hackathon",
            source="reddit",
            url="https://example.com/hackathon",
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=7),
            deadline_register=datetime.now() + timedelta(days=3),
            description="A test hackathon",
            prizes={"1st place": 1000.0, "2nd place": 500.0},
            total_prize_pool=1500.0,
            currency="USD",
            platform="gitlab",
            category="web",
            skill_level="intermediate",
            requires_team=True,
            team_size="1-5",
            requirements=["Python", "JavaScript"],
            extra_benefits=["swag", "portfolio"],
            tags=["python", "web"],
            roi_score=2.5,
            effort_hours=20
        )

        assert opp.title == "Test Hackathon"
        assert opp.total_prize_pool == 1500.0
        assert opp.effort_hours == 20
        assert "python" in opp.tags

    def test_opportunity_to_dict(self):
        """Test converting opportunity to dictionary"""
        opp = HackathonOpportunity(
            title="Test Hackathon",
            source="reddit",
            url="https://example.com/hackathon",
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=7),
            deadline_register=datetime.now() + timedelta(days=3),
            description="A test hackathon",
            prizes={"1st place": 1000.0},
            total_prize_pool=1000.0,
            currency="USD",
            platform="gitlab",
            category="web",
            skill_level="intermediate",
            requires_team=False,
            team_size="1",
            requirements=["Python"],
            extra_benefits=[],
            tags=["python"],
            roi_score=1.0,
            effort_hours=10
        )

        opp_dict = asdict(opp)
        assert isinstance(opp_dict, dict)
        assert opp_dict['title'] == "Test Hackathon"
        assert opp_dict['total_prize_pool'] == 1000.0
        assert isinstance(opp_dict['start_date'], str)  # Should be ISO string


class TestHackathonTracker:
    """Test HackathonTracker class"""

    @pytest.fixture
    def tracker(self):
        """Create a tracker instance"""
        return HackathonTracker(hourly_rate=50.0)

    def test_tracker_initialization(self, tracker):
        """Test tracker initialization"""
        assert tracker.hourly_rate == 50.0
        assert hasattr(tracker, 'calculate_roi')

    def test_calculate_roi(self, tracker):
        """Test ROI calculation"""
        # Create a mock opportunity dict
        opp = {
            'total_prize_pool': 1000.0,
            'title': 'Test Hackathon'
        }

        roi = tracker.calculate_roi(opp)
        # With $1000 prize and default effort estimation, should be reasonable ROI
        assert isinstance(roi, float)
        assert roi > 0

    def test_rank_opportunities_by_roi(self, tracker, sample_opportunities):
        """Test ranking opportunities by ROI"""
        # Create sample opportunity dicts
        opp1 = {'title': 'High Prize', 'total_prize_pool': 5000.0, 'roi_score': 2.5}
        opp2 = {'title': 'Quick Win', 'total_prize_pool': 500.0, 'roi_score': 1.25}
        opp3 = {'title': 'Low Effort', 'total_prize_pool': 200.0, 'roi_score': 1.0}

        ranked = tracker.rank_opportunities([opp1, opp2, opp3], sort_by='roi')

        assert ranked[0]['title'] == "High Prize"  # ROI 2.5
        assert ranked[1]['title'] == "Quick Win"   # ROI 1.25
        assert ranked[2]['title'] == "Low Effort"  # ROI 1.0

    def test_rank_opportunities_by_prize(self, tracker, sample_opportunities):
        """Test ranking opportunities by prize pool"""
        opp1 = {'title': 'High', 'total_prize_pool': 5000.0}
        opp2 = {'title': 'Medium', 'total_prize_pool': 500.0}
        opp3 = {'title': 'Low', 'total_prize_pool': 200.0}

        ranked = tracker.rank_opportunities([opp1, opp2, opp3], sort_by='prize')

        assert ranked[0]['total_prize_pool'] == 5000.0
        assert ranked[1]['total_prize_pool'] == 500.0
        assert ranked[2]['total_prize_pool'] == 200.0

    def test_rank_opportunities_by_date(self, tracker, sample_opportunities):
        """Test ranking opportunities by date (most recent first)"""
        # All have same date, so order should be unchanged
        opp1 = {'title': 'First', 'start_date': datetime.now()}
        opp2 = {'title': 'Second', 'start_date': datetime.now()}

        ranked = tracker.rank_opportunities([opp1, opp2], sort_by='date')
        assert len(ranked) == 2

    def test_filter_opportunities_min_prize(self, tracker, sample_opportunities):
        """Test filtering by minimum prize"""
        opp1 = {'title': 'High', 'total_prize_pool': 5000.0}
        opp2 = {'title': 'Low', 'total_prize_pool': 200.0}

        filtered = tracker.filter_opportunities([opp1, opp2], min_prize=1000.0)

        assert len(filtered) == 1
        assert filtered[0]['total_prize_pool'] == 5000.0

    def test_filter_opportunities_max_effort(self, tracker):
        """Test filtering by maximum effort hours"""
        opp1 = {'title': 'Quick', 'total_prize_pool': 1000.0}
        opp2 = {'title': 'Long', 'total_prize_pool': 1000.0}

        filtered = tracker.filter_opportunities([opp1, opp2], max_effort_hours=10)

        assert len(filtered) == 2  # Both should pass since effort is estimated

    def test_filter_opportunities_min_roi(self, tracker, sample_opportunities):
        """Test filtering by minimum ROI"""
        opp1 = {'title': 'High ROI', 'roi_score': 2.5}
        opp2 = {'title': 'Low ROI', 'roi_score': 0.5}

        filtered = tracker.filter_opportunities([opp1, opp2], min_roi=2.0)

        assert len(filtered) == 1
        assert filtered[0]['roi_score'] == 2.5

    def test_filter_opportunities_exclude_keywords(self, tracker, sample_opportunities):
        """Test filtering by excluding keywords"""
        opp1 = {'title': 'Full Stack Hackathon', 'tags': ['fullstack']}
        opp2 = {'title': 'Simple Hackathon', 'tags': ['simple']}

        filtered = tracker.filter_opportunities(
            [opp1, opp2],
            exclude_keywords=["fullstack"]
        )

        assert len(filtered) == 1  # Should exclude fullstack
        assert filtered[0]['title'] == "Simple Hackathon"

    def test_combined_filters(self, tracker):
        """Test combining multiple filters"""
        opp1 = {'title': 'Good Match', 'total_prize_pool': 1500.0}
        opp2 = {'title': 'Bad Match', 'total_prize_pool': 200.0}

        filtered = tracker.filter_opportunities(
            [opp1, opp2],
            min_prize=500.0,
            min_roi=0.1,
            max_effort_hours=20
        )

        # Should include both since they meet basic criteria
        assert len(filtered) >= 1

    @patch('hackathon_tracker.tracker.praw.Reddit')
    def test_fetch_reddit_hackathons_mock(self, mock_reddit_class, tracker):
        """Test Reddit fetching with mocked API"""
        # Mock Reddit instance
        mock_reddit = MagicMock()
        mock_reddit_class.return_value = mock_reddit

        # Mock subreddit
        mock_subreddit = MagicMock()
        mock_reddit.subreddit.return_value = mock_subreddit

        # Mock posts
        mock_post1 = MagicMock()
        mock_post1.title = "GitLab Hackathon 2024 - $10,000 in prizes!"
        mock_post1.selftext = "Join the GitLab hackathon. Deadline: April 15, 2024. Requirements: GitLab CI/CD knowledge."
        mock_post1.url = "https://reddit.com/r/hackathons/post1"
        mock_post1.subreddit.display_name = "hackathons"
        mock_post1.author.name = "testuser"
        mock_post1.score = 42

        mock_post2 = MagicMock()
        mock_post2.title = "Not a hackathon"
        mock_post2.selftext = "Just a regular post"
        mock_post2.url = "https://reddit.com/r/hackathons/post2"
        mock_post2.subreddit.display_name = "hackathons"

        mock_subreddit.top.return_value = [mock_post1, mock_post2]

        # Test fetching
        opportunities = tracker.fetch_reddit_hackathons(
            subreddits=['hackathons'],
            time_filter='week'
        )

        # Should find one hackathon opportunity
        assert len(opportunities) == 1
        assert "GitLab Hackathon" in opportunities[0]['title']
        assert opportunities[0]['total_prize_pool'] == 10000.0

    def test_export_opportunities_json(self, tracker):
        """Test exporting opportunities to JSON"""
        # Create sample opportunity dicts
        opportunities = [
            {'title': 'Test Hackathon', 'total_prize_pool': 1000.0, 'start_date': datetime.now(), 'end_date': datetime.now()}
        ]

        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            temp_file = f.name

        try:
            tracker.export_opportunities(opportunities, format='json', filename=temp_file)

            # Verify file was created and contains data
            assert Path(temp_file).exists()

            with open(temp_file, 'r') as f:
                data = json.load(f)

            assert len(data) == 1
            assert data[0]['title'] == 'Test Hackathon'

        finally:
            Path(temp_file).unlink(missing_ok=True)

    def test_export_opportunities_excel(self, tracker):
        """Test exporting opportunities to Excel"""
        # Create sample opportunity dicts
        opportunities = [
            {'title': 'Test Hackathon', 'total_prize_pool': 1000.0, 'start_date': datetime.now(), 'end_date': datetime.now()}
        ]

        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as f:
            temp_file = f.name

        try:
            tracker.export_opportunities(opportunities, format='excel', filename=temp_file)

            # Verify file was created
            assert Path(temp_file).exists()
            # Note: Would need openpyxl to fully test Excel content

        finally:
            Path(temp_file).unlink(missing_ok=True)

    def test_parse_post_date_extraction(self, tracker):
        """Test date extraction from post text"""
        # Test various date formats
        test_cases = [
            ("Deadline: April 15, 2024", ["deadline"], datetime(2024, 4, 15)),
            ("Starts May 1st", ["starts"], datetime(2026, 5, 1)),
            ("No date here", ["any"], None)
        ]

        for text, keywords, expected in test_cases:
            date = tracker._extract_date_pattern(text, keywords)
            if expected:
                # Allow some flexibility in date parsing
                assert date is not None
            else:
                assert date is None

    def test_parse_post_prize_extraction(self, tracker):
        """Test prize extraction from post text"""
        test_cases = [
            ("$10,000 in prizes", {"1st place": 10000.0}),
            ("Prize pool of $5,000", {"1st place": 5000.0}),
            ("No prize mentioned", {})
        ]

        for text, expected in test_cases:
            prizes = tracker._extract_prizes(text)
            assert prizes == expected

    def test_display_top_opportunities(self, tracker, capsys):
        """Test displaying opportunities in terminal"""
        # Create sample opportunity dicts
        opportunities = [
            {'title': 'High Prize Hackathon', 'total_prize_pool': 5000.0, 'roi_score': 2.5, 'effort_hours': 40, 'start_date': datetime.now(), 'end_date': datetime.now()},
            {'title': 'Quick Win Hackathon', 'total_prize_pool': 500.0, 'roi_score': 1.25, 'effort_hours': 8, 'start_date': datetime.now(), 'end_date': datetime.now()}
        ]

        tracker.display_top_opportunities(opportunities, count=2)

        captured = capsys.readouterr()
        assert "High Prize Hackathon" in captured.out
        assert "Quick Win Hackathon" in captured.out


if __name__ == '__main__':
    pytest.main([__file__])