from transformers import pipeline

from backend.data.skill_taxonomy import TAXONOMY


class SkillExtractor:
    _ner = None

    def __init__(self):
        if SkillExtractor._ner is None:
            SkillExtractor._ner = pipeline(
                "ner",
                model="feliponi/hirly-ner-multi",
                aggregation_strategy="simple",
            )

    def _categorize(self, skill: str) -> str:
        skill_lower = skill.lower().strip()
        for category, skills in TAXONOMY.items():
            if skill_lower in skills:
                return category
        return 'other_skills'

    def extract(self, text: str, threshold: float = 0.7) -> dict:
        result = {
            "languages": [],
            "frameworks": [],
            "databases": [],
            "cloud": [],
            "soft_skills": [],
            "certifications": [],
            "other_skills": [],
            "experience": [],
        }

        if SkillExtractor._ner is None:
            raise RuntimeError("NER model not initialized")

        for ent in SkillExtractor._ner(text):
            if ent["score"] < threshold:
                continue
            word = ent["word"].strip()
            label = ent["entity_group"]

            if label == "SOFT_SKILL":
                if word not in result["soft_skills"]:
                    result["soft_skills"].append(word)
                continue

            if label == "LANG":
                if word not in result["languages"]:
                    result["languages"].append(word)
                continue

            if label == "CERT":
                if word not in result["certifications"]:
                    result["certifications"].append(word)
                continue

            if label == "EXPERIENCE_DURATION":
                if word not in result["experience"]:
                    result["experience"].append(word)
                continue

            if label == "SKILL":
                cat = self._categorize(word)
                if word not in result[cat]:
                    result[cat].append(word)

        return result
