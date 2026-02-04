from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix='FASTMCP_SERVER_AUTH_AWS_COGNITO_',
        env_file='.env',
        extra='ignore',
    )
    user_pool_id: str = 'xxx'  # will be read from `FASTMCP_SERVER_AUTH_AWS_COGNITO_USER_POOL_ID`
    aws_region: str = 'xxx'  # will be read from `FASTMCP_SERVER_AUTH_AWS_COGNITO_AWS_REGION`
    require_authorization_consent: bool = True  # will be read from `FASTMCP_SERVER_AUTH_AWS_COGNITO_REQUIRE_AUTHORIZATION_CONSENT`


print(Settings().model_dump())