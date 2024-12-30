from peewee import *
from playhouse.postgres_ext import *

database = PostgresqlDatabase('rocketeer', **{'host': '209.126.85.73', 'port': 5432, 'user': 'postgres', 'password': '3o6dA$Bc9YLRr&'})

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = database

class User(BaseModel):
    assets = JSONField(constraints=[SQL("DEFAULT '{}'::json")], null=True)
    created_at = DateTimeField(constraints=[SQL("DEFAULT now()")], null=True)
    email = CharField(null=True, unique=True)
    live_pass = CharField(null=True)
    position_usd_amount = DecimalField(constraints=[SQL("DEFAULT 20")], null=True)
    profile_analysis = TextField(null=True)
    slack_user_id = CharField(null=True, unique=True)
    slack_user_name = CharField(null=True)
    status = CharField(constraints=[SQL("DEFAULT 'created'::character varying")], null=True)
    stop_loss_percent = DecimalField(constraints=[SQL("DEFAULT 1")], null=True)
    take_profit_percent = DecimalField(constraints=[SQL("DEFAULT 2")], null=True)
    total_amount = DecimalField(constraints=[SQL("DEFAULT 1000")], null=True)
    total_amount_live = DecimalField(null=True)
    usd_amount = IntegerField(constraints=[SQL("DEFAULT 1000")], null=True)

    class Meta:
        table_name = 'user'

class BalanceSnapshot(BaseModel):
    assets = JSONField(null=True)
    assets_live = JSONField(null=True)
    created_at = DateTimeField(constraints=[SQL("DEFAULT now()")], null=True)
    total_amount = DecimalField(null=True)
    total_amount_live = DecimalField(null=True)
    usd_amount = DecimalField(null=True)
    user = ForeignKeyField(column_name='user_id', field='id', model=User, null=True)

    class Meta:
        table_name = 'balance_snapshot'

class BotAgent(BaseModel):
    buffer_size = IntegerField(null=True)
    name = CharField()
    prompt = TextField(null=True)
    summary_prompt = TextField(null=True)

    class Meta:
        table_name = 'bot_agent'

class BotCommand(BaseModel):
    command = CharField()
    prompt = TextField()

    class Meta:
        table_name = 'bot_command'

class Market(BaseModel):
    created_at = DateTimeField(constraints=[SQL("DEFAULT now()")], null=True)
    data = JSONField(null=True)
    last_update_at = DateTimeField(constraints=[SQL("DEFAULT (now() - '1 day'::interval)")], null=True)
    market_activity_score_1d = DecimalField(null=True)
    market_activity_score_1h = DecimalField(null=True)
    name = CharField(null=True)
    price = DecimalField(null=True)
    sentiment = TextField(null=True)
    sentiment_update_at = DateTimeField(null=True)
    short_name = CharField(null=True)
    ticker = CharField()
    trend_status = CharField(null=True)
    type = CharField(null=True)

    class Meta:
        table_name = 'market'

class Timeframe(BaseModel):
    is_watched = BooleanField(constraints=[SQL("DEFAULT false")], null=True)
    minutes = BigIntegerField(null=True, unique=True)
    name = CharField(null=True, unique=True)
    tv_id = CharField(null=True)

    class Meta:
        table_name = 'timeframe'

class TvAlert(BaseModel):
    created_at = DateTimeField(constraints=[SQL("DEFAULT now()")], null=True)
    data = JSONField(constraints=[SQL("DEFAULT '{}'::json")], null=True)
    digest_job_id = CharField(null=True)
    id = BigAutoField()
    status = CharField(constraints=[SQL("DEFAULT 'created'::character varying")], null=True)

    class Meta:
        table_name = 'tv_alert'

class Candle(BaseModel):
    close = DecimalField(null=True)
    created_at = DateTimeField(constraints=[SQL("DEFAULT now()")], null=True)
    data = JSONField(null=True)
    high = DecimalField(null=True)
    id = BigAutoField()
    ingestion_version = CharField(null=True)
    low = DecimalField(null=True)
    market_activity_score = DecimalField(null=True)
    market = ForeignKeyField(column_name='market_id', field='id', model=Market, null=True)
    open = DecimalField(null=True)
    opened_at = DateTimeField(null=True)
    opened_ts = DecimalField(null=True)
    percent_remaining = DecimalField(null=True)
    timeframe = ForeignKeyField(column_name='timeframe_id', field='id', model=Timeframe, null=True)
    tv_alert = ForeignKeyField(column_name='tv_alert_id', field='id', model=TvAlert, null=True)
    volume = DecimalField(null=True)

    class Meta:
        table_name = 'candle'
        indexes = (
            (('market', 'timeframe', 'opened_ts'), True),
            (('market', 'timeframe', 'opened_ts'), True),
        )

class Emotion(BaseModel):
    description = CharField(null=True)
    name = CharField(null=True, unique=True)

    class Meta:
        table_name = 'emotion'

class Position(BaseModel):
    age = IntegerField(null=True)
    amount = DecimalField(null=True)
    analysis = TextField(null=True)
    closed = DecimalField(null=True)
    closed_at = DateTimeField(null=True)
    closed_ts = DecimalField(null=True)
    code = CharField(null=True)
    created_at = DateTimeField(constraints=[SQL("DEFAULT now()")], null=True)
    data = JSONField(null=True)
    description = TextField(null=True)
    do_stop_loss = BooleanField(constraints=[SQL("DEFAULT true")], null=True)
    do_take_profit = BooleanField(constraints=[SQL("DEFAULT true")], null=True)
    entered = DecimalField(null=True)
    entry = DecimalField(null=True)
    is_cleared = BooleanField(constraints=[SQL("DEFAULT false")], null=True)
    is_live = BooleanField(constraints=[SQL("DEFAULT false")])
    market = ForeignKeyField(column_name='market_id', field='id', model=Market, null=True)
    opened_at = DateTimeField(null=True)
    opened_ts = DecimalField(null=True)
    profit = DecimalField(null=True)
    result = TextField(null=True)
    status = CharField(constraints=[SQL("DEFAULT 'created'::character varying")], null=True)
    stop_loss = DecimalField(null=True)
    take_profit = DecimalField(null=True)
    timeframe = ForeignKeyField(column_name='timeframe_id', field='id', model=Timeframe, null=True)
    usd_amount = DecimalField(null=True)
    user = ForeignKeyField(column_name='user_id', field='id', model=User, null=True)

    class Meta:
        table_name = 'position'

class PositionEmotion(BaseModel):
    emotion = ForeignKeyField(column_name='emotion_id', field='id', model=Emotion, null=True)
    position = ForeignKeyField(column_name='position_id', field='id', model=Position, null=True)

    class Meta:
        table_name = 'position_emotion'
        primary_key = False

class ProfileCategory(BaseModel):
    description = TextField(null=True)
    high_result = CharField(null=True)
    low_result = CharField(null=True)
    name = CharField(null=True)

    class Meta:
        table_name = 'profile_category'

class ProfileDetail(BaseModel):
    description = TextField(null=True)
    name = CharField(null=True)
    profile_category = ForeignKeyField(column_name='profile_category_id', field='id', model=ProfileCategory, null=True)

    class Meta:
        table_name = 'profile_detail'

class PsychEvent(BaseModel):
    description = CharField(null=True)
    name = CharField(null=True)

    class Meta:
        table_name = 'psych_event'

class ScrapeTarget(BaseModel):
    name = CharField()
    reference = CharField()
    status = CharField()
    type = CharField()
    url = CharField()

    class Meta:
        table_name = 'scrape_target'

class ScrapeTweet(BaseModel):
    analysis = TextField(null=True)
    comments = TextField(null=True)
    created_at = DateTimeField(constraints=[SQL("DEFAULT now()")])
    scrape_target = ForeignKeyField(column_name='scrape_target_id', field='id', model=ScrapeTarget, null=True)
    status = CharField(constraints=[SQL("DEFAULT 'created'::character varying")])
    text = TextField()
    url = CharField()

    class Meta:
        table_name = 'scrape_tweet'

class ScrapeVideo(BaseModel):
    analysis = TextField(null=True)
    created_at = DateTimeField(constraints=[SQL("DEFAULT now()")])
    scrape_target = ForeignKeyField(column_name='scrape_target_id', field='id', model=ScrapeTarget, null=True)
    status = CharField(constraints=[SQL("DEFAULT 'created'::character varying")])
    text = TextField(null=True)
    url = CharField()

    class Meta:
        table_name = 'scrape_video'

class ScrapeWeb(BaseModel):
    analysis = TextField(null=True)
    created_at = DateTimeField(constraints=[SQL("DEFAULT now()")])
    scrape_target = ForeignKeyField(column_name='scrape_target_id', field='id', model=ScrapeTarget, null=True)
    status = CharField(constraints=[SQL("DEFAULT 'created'::character varying")])
    text = TextField()
    url = CharField()

    class Meta:
        table_name = 'scrape_web'

class Settings(BaseModel):
    api_call_counters = JSONField(null=True)
    api_rate_limits = JSONField(null=True)
    ingestion_chunk_size = SmallIntegerField(constraints=[SQL("DEFAULT 10")], null=True)
    is_singleton = BooleanField(constraints=[SQL("DEFAULT true")], primary_key=True)
    set_test_alert = BooleanField(constraints=[SQL("DEFAULT false")])

    class Meta:
        table_name = 'settings'

class SlackMessage(BaseModel):
    candle_id_final = ForeignKeyField(column_name='candle_id_final', field='id', model=Candle, null=True)
    candle_id_initial = ForeignKeyField(backref='candle_candle_id_initial_set', column_name='candle_id_initial', field='id', model=Candle, null=True)
    created_at = DateTimeField(constraints=[SQL("DEFAULT now()")], null=True)
    data = JSONField(constraints=[SQL("DEFAULT '{}'::json")], null=True)
    id = BigAutoField()
    is_canceled = BooleanField(constraints=[SQL("DEFAULT false")], null=True)
    market_id = IntegerField(null=True)
    message = TextField(null=True)
    message_at = DateTimeField(null=True)
    message_ts = DecimalField(null=True)
    sms_sent = BooleanField(constraints=[SQL("DEFAULT false")])
    timeframe_id = IntegerField(null=True)
    type = CharField(null=True)

    class Meta:
        table_name = 'slack_message'

class Strategy(BaseModel):
    created_at = DateTimeField(constraints=[SQL("DEFAULT now()")], null=True)
    description = TextField(null=True)
    name = CharField()
    status = CharField(null=True)
    type = CharField(null=True)

    class Meta:
        table_name = 'strategy'

class StrategyPerformance(BaseModel):
    data = JSONField(null=True)
    market = ForeignKeyField(column_name='market_id', field='id', model=Market)
    parameters = JSONField(null=True)
    strategy = ForeignKeyField(column_name='strategy_id', field='id', model=Strategy)
    timeframe = ForeignKeyField(column_name='timeframe_id', field='id', model=Timeframe)
    version = IntegerField(constraints=[SQL("DEFAULT 1")])

    class Meta:
        table_name = 'strategy_performance'

class UserBotAgent(BaseModel):
    bot_agent = ForeignKeyField(column_name='bot_agent_id', field='id', model=BotAgent)
    buffer = TextField(null=True)
    summary = TextField(null=True)
    updated_at = DateTimeField(null=True)
    user = ForeignKeyField(column_name='user_id', field='id', model=User)

    class Meta:
        table_name = 'user_bot_agent'
        indexes = (
            (('bot_agent', 'user'), True),
        )

class UserBotConversation(BaseModel):
    buffer = TextField(null=True)
    created_at = DateTimeField(constraints=[SQL("DEFAULT now()")], null=True)
    is_in_bot_memory = BooleanField(constraints=[SQL("DEFAULT false")], null=True)
    question = CharField(null=True)
    summary = TextField(null=True)
    tags = CharField(null=True)
    thread_ts = DecimalField()
    topic = CharField(null=True)
    updated_at = DateTimeField(constraints=[SQL("DEFAULT now()")], null=True)
    user_bot_agent = ForeignKeyField(column_name='user_bot_agent_id', field='id', model=UserBotAgent, null=True)

    class Meta:
        table_name = 'user_bot_conversation'
        indexes = (
            (('user_bot_agent', 'thread_ts'), True),
        )

class UserProfileCategory(BaseModel):
    created_at = DateTimeField(constraints=[SQL("DEFAULT now()")], null=True)
    description = TextField(null=True)
    profile_category = ForeignKeyField(column_name='profile_category_id', field='id', model=ProfileCategory, null=True)
    user = ForeignKeyField(column_name='user_id', field='id', model=User, null=True)
    value = DecimalField(null=True)

    class Meta:
        table_name = 'user_profile_category'
        indexes = (
            (('user', 'profile_category'), True),
        )

class UserProfileDetail(BaseModel):
    created_at = DateTimeField(constraints=[SQL("DEFAULT now()")], null=True)
    profile_detail = ForeignKeyField(column_name='profile_detail_id', field='id', model=ProfileDetail, null=True)
    user_profile_category_id = IntegerField(null=True)
    value = BigIntegerField(null=True)

    class Meta:
        table_name = 'user_profile_detail'
        indexes = (
            (('profile_detail', 'user_profile_category_id'), True),
        )

class UserPsychEvent(BaseModel):
    analysis = TextField(null=True)
    created_at = DateTimeField(constraints=[SQL("DEFAULT CURRENT_TIMESTAMP")], null=True)
    description = TextField(null=True)
    psych_event = ForeignKeyField(column_name='psych_event_id', field='id', model=PsychEvent, null=True)
    solved = BooleanField(constraints=[SQL("DEFAULT false")], null=True)
    user = ForeignKeyField(column_name='user_id', field='id', model=User, null=True)

    class Meta:
        table_name = 'user_psych_event'

class UserWatching(BaseModel):
    is_active = BooleanField(constraints=[SQL("DEFAULT true")])
    market = ForeignKeyField(column_name='market_id', field='id', model=Market)
    timeframe = ForeignKeyField(column_name='timeframe_id', field='id', model=Timeframe)
    user = ForeignKeyField(column_name='user_id', field='id', model=User)

    class Meta:
        table_name = 'user_watching'

