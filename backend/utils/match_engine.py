class MatchEngine:

    @staticmethod
    def match(job_skills: dict, resume_skills: dict) -> dict:
        job_set = set()
        for items in job_skills.values():
            if isinstance(items, list):
                for item in items:
                    job_set.add(str(item).lower().strip())

        resume_set = set()
        for items in resume_skills.values():
            if isinstance(items, list):
                for item in items:
                    resume_set.add(str(item).lower().strip())

        if not job_set:
            return {
                "match_score": 0.0,
                "matched_skills": [],
                "missing_skills": [],
            }

        matched = job_set & resume_set
        missing = job_set - resume_set
        score = round(len(matched) / len(job_set) * 100, 2)

        return {
            "match_score": score,
            "matched_skills": sorted(matched),
            "missing_skills": sorted(missing),
        }
