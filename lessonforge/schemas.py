from typing import Literal
from pydantic import BaseModel, Field

CheckStatus = Literal["PASS", "FAIL"]

class RubricCheck(BaseModel):
    status: CheckStatus
    reason: str = Field(description="Short explanation for the decision")
    correction: str = Field(default="", description="Specific change needed if failed")

class LessonEvaluation(BaseModel):
    accuracy: RubricCheck
    beginner_language: RubricCheck
    real_example: RubricCheck
    jargon_explained: RubricCheck
    key_coverage: RubricCheck
    teaching_flow: RubricCheck

    @property
    def overall_status(self) -> str:
        return "PASS" if all(
            getattr(self, name).status == "PASS"
            for name in self.model_fields
        ) else "FAIL"

    def as_dict(self) -> dict:
        data = self.model_dump()
        data["overall_status"] = self.overall_status
        return data
