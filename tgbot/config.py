from dataclasses import dataclass

from environs import Env

from sqlalchemy.engine import URL


@dataclass
class DbConfig:
    host: str
    password: str
    user: str
    database: str
    port: int = 5432

    def construct_sqlalchemy_url(self) -> URL:
        return URL.create(
            drivername="postgresql+asyncpg",
            username=self.user,
            password=self.password,
            host=self.host,
            database=self.database,
            port=self.port
        )


@dataclass
class RedisConfig:
    host: str
    port: int
    db: int
    password: str

    def dsn(self):
        return f"redis://:{self.password}@{self.host}:{self.port}/{self.db}"


@dataclass
class Channels:
    search_channel_id: int
    medicine_channel_id: int
    provision_channel_id: int
    evacuation_channel_id: int


@dataclass
class TgBot:
    token: str
    admin_ids: list[int]
    use_redis: bool


@dataclass
class Miscellaneous:
    other_params: str = None


@dataclass
class Config:
    tg_bot: TgBot
    misc: Miscellaneous
    channels: Channels
    redis_config: RedisConfig
    db: DbConfig


def load_config(path: str = None):
    env = Env()
    env.read_env(path)

    return Config(
        tg_bot=TgBot(
            token=env.str("BOT_TOKEN"),
            admin_ids=list(map(int, env.list("ADMINS"))),
            use_redis=env.bool("USE_REDIS"),
        ),

        misc=Miscellaneous(),
        channels=Channels(
            search_channel_id=env.int('SEARCH_CHANNEL_ID'),
            medicine_channel_id=env.int('MEDICINE_CHANNEL_ID'),
            provision_channel_id=env.int('PROVISION_CHANNEL_ID'),
            evacuation_channel_id=env.int('EVACUATION_CHANNEL_ID')
        ),
        redis_config=RedisConfig(
            host=env.str('REDIS_HOST'),
            port=env.int('REDIS_PORT'),
            db=env.int('REDIS_DB'),
            password=env.str('REDIS_PASSWORD')
        ),

        db=DbConfig(
            host=env.str('DB_HOST'),
            password=env.str('POSTGRES_PASSWORD'),
            user=env.str('POSTGRES_USER'),
            database=env.str('POSTGRES_DB')
        ),
    )
