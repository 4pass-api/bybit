from pydantic import BaseModel, Field


class TextOnly(BaseModel):
    text: str = Field(..., title="Text", description="Text content")


class Token(BaseModel):
    access_token: str = Field(default='example_token')
    token_type: str = Field(default='bearer')


class Credentials(BaseModel):
    apiKey: str = Field(..., title="API Key", description="API Key")
    secretKey: str = Field(..., title="Secret Key", description="Secret Key")
