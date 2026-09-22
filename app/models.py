from pydantic import BaseModel, Field

class TTSRequest(BaseModel):
    text: str = Field(min_length=1, max_length=5000)
    rate: str = Field(default="+0%", pattern=r"^[+-](?:100|[0-9]{1,2})%$")
    volume: str = Field(default="+0%", pattern=r"^[+-](?:100|[0-9]{1,2})%$")

class TTSResponse(BaseModel):
    key: str
    audio_url: str
    cached: bool
