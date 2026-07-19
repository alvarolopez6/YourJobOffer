from unittest.mock import MagicMock, patch
from backend.utils.skill_extractor import SkillExtractor


class TestSkillExtractorCategorize:

    def setup_method(self):
        self.extractor = SkillExtractor()

    def test_categorize_known_language(self):
        assert self.extractor._categorize("python") == "languages"

    def test_categorize_known_framework(self):
        assert self.extractor._categorize("django") == "frameworks"

    def test_categorize_known_database(self):
        assert self.extractor._categorize("postgresql") == "databases"

    def test_categorize_known_cloud(self):
        assert self.extractor._categorize("aws") == "cloud"

    def test_categorize_known_soft_skill(self):
        assert self.extractor._categorize("leadership") == "soft_skills"

    def test_categorize_unknown_skill(self):
        assert self.extractor._categorize("quantum_computing") == "other_skills"

    def test_categorize_case_insensitive(self):
        assert self.extractor._categorize("Python") == "languages"
        assert self.extractor._categorize("DJANGO") == "frameworks"

    def test_categorize_strips_whitespace(self):
        assert self.extractor._categorize("  python  ") == "languages"


class TestSkillExtractorExtract:

    def setup_method(self):
        self.extractor = SkillExtractor()

    def _mock_ner(self, entities):
        mock_ner = MagicMock(return_value=entities)
        SkillExtractor._ner = mock_ner
        return mock_ner

    def test_extract_routes_by_label(self):
        self._mock_ner([
            {"word": "python", "entity_group": "LANG", "score": 0.95},
            {"word": "fastapi", "entity_group": "SKILL", "score": 0.9},
            {"word": "leadership", "entity_group": "SOFT_SKILL", "score": 0.85},
            {"word": "AWS Solutions Architect", "entity_group": "CERT", "score": 0.88},
            {"word": "5 years", "entity_group": "EXPERIENCE_DURATION", "score": 0.92},
        ])
        result = self.extractor.extract("Some text")
        assert "python" in result["languages"]
        assert "fastapi" in result["frameworks"]
        assert "leadership" in result["soft_skills"]
        assert "AWS Solutions Architect" in result["certifications"]
        assert "5 years" in result["experience"]

    def test_extract_filters_below_threshold(self):
        self._mock_ner([
            {"word": "python", "entity_group": "LANG", "score": 0.95},
            {"word": "java", "entity_group": "LANG", "score": 0.3},
        ])
        result = self.extractor.extract("Some text", threshold=0.7)
        assert "python" in result["languages"]
        assert "java" not in result["languages"]

    def test_extract_deduplicates(self):
        self._mock_ner([
            {"word": "python", "entity_group": "LANG", "score": 0.95},
            {"word": "python", "entity_group": "LANG", "score": 0.92},
        ])
        result = self.extractor.extract("Some text")
        assert result["languages"].count("python") == 1

    def test_extract_empty_result(self):
        self._mock_ner([])
        result = self.extractor.extract("Some text")
        for key in ["languages", "frameworks", "databases", "cloud",
                     "soft_skills", "certifications", "other_skills", "experience"]:
            assert result[key] == []

    def test_extract_runtime_error_when_no_model(self):
        SkillExtractor._ner = None
        extractor = SkillExtractor()
        extractor._ner = None
        SkillExtractor._ner = None
        import pytest
        with pytest.raises(RuntimeError, match="NER model not initialized"):
            self.extractor.extract("Some text")

    def test_extract_skips_unknown_skill_label(self):
        self._mock_ner([
            {"word": "something", "entity_group": "UNKNOWN", "score": 0.95},
        ])
        result = self.extractor.extract("Some text")
        for key in result:
            assert result[key] == []
