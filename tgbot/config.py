from dataclasses import dataclass

from environs import Env



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
        )
    )
