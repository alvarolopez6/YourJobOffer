from backend.utils.match_engine import MatchEngine


class TestMatchEngine:

    def test_perfect_match(self):
        job_skills = {"languages": ["python", "java"], "frameworks": ["fastapi"]}
        resume_skills = {"languages": ["python", "java"], "frameworks": ["fastapi"]}
        result = MatchEngine.match(job_skills, resume_skills)
        assert result["match_score"] == 100.0
        assert sorted(result["matched_skills"]) == ["fastapi", "java", "python"]
        assert result["missing_skills"] == []

    def test_partial_match(self):
        job_skills = {"languages": ["python", "java", "go"]}
        resume_skills = {"languages": ["python"]}
        result = MatchEngine.match(job_skills, resume_skills)
        assert result["match_score"] == pytest.approx(33.33, abs=0.01)
        assert "python" in result["matched_skills"]
        assert sorted(result["missing_skills"]) == ["go", "java"]

    def test_no_match(self):
        job_skills = {"languages": ["python"]}
        resume_skills = {"languages": ["rust"]}
        result = MatchEngine.match(job_skills, resume_skills)
        assert result["match_score"] == 0.0
        assert result["matched_skills"] == []
        assert result["missing_skills"] == ["python"]

    def test_empty_job_skills(self):
        job_skills = {}
        resume_skills = {"languages": ["python"]}
        result = MatchEngine.match(job_skills, resume_skills)
        assert result["match_score"] == 0.0
        assert result["matched_skills"] == []
        assert result["missing_skills"] == []

    def test_empty_resume_skills(self):
        job_skills = {"languages": ["python", "java"]}
        resume_skills = {}
        result = MatchEngine.match(job_skills, resume_skills)
        assert result["match_score"] == 0.0
        assert result["matched_skills"] == []
        assert sorted(result["missing_skills"]) == ["java", "python"]

    def test_case_insensitive(self):
        job_skills = {"languages": ["Python", "JAVA"]}
        resume_skills = {"languages": ["python", "java"]}
        result = MatchEngine.match(job_skills, resume_skills)
        assert result["match_score"] == 100.0
        assert sorted(result["matched_skills"]) == ["java", "python"]

    def test_whitespace_handling(self):
        job_skills = {"languages": ["  Python  ", " Java "]}
        resume_skills = {"languages": ["python", "java"]}
        result = MatchEngine.match(job_skills, resume_skills)
        assert result["match_score"] == 100.0
        assert sorted(result["matched_skills"]) == ["java", "python"]

    def test_non_list_values_ignored(self):
        job_skills = {"languages": ["python"], "count": 5, "name": "test"}
        resume_skills = {"languages": ["python"], "extra": "value"}
        result = MatchEngine.match(job_skills, resume_skills)
        assert result["match_score"] == 100.0
        assert result["matched_skills"] == ["python"]

    def test_multiple_categories_flattened(self):
        job_skills = {
            "languages": ["python"],
            "frameworks": ["fastapi"],
            "databases": ["postgresql"],
        }
        resume_skills = {
            "languages": ["python"],
            "frameworks": ["fastapi"],
            "cloud": ["aws"],
        }
        result = MatchEngine.match(job_skills, resume_skills)
        assert result["match_score"] == pytest.approx(66.67, abs=0.01)
        assert sorted(result["matched_skills"]) == ["fastapi", "python"]
        assert result["missing_skills"] == ["postgresql"]

    def test_score_rounded_to_two_decimals(self):
        job_skills = {"languages": ["a", "b", "c", "d", "e", "f", "g"]}
        resume_skills = {"languages": ["a"]}
        result = MatchEngine.match(job_skills, resume_skills)
        assert result["match_score"] == round(1 / 7 * 100, 2)

    def test_result_lists_are_sorted(self):
        job_skills = {"languages": ["go", "rust", "python", "java"]}
        resume_skills = {"languages": ["python", "java"]}
        result = MatchEngine.match(job_skills, resume_skills)
        assert result["matched_skills"] == sorted(result["matched_skills"])
        assert result["missing_skills"] == sorted(result["missing_skills"])


import pytest
