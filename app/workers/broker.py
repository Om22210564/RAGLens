import dramatiq
from dramatiq.brokers.redis import RedisBroker

# This imports Dramatiq's Redis broker.
# A broker is essentially the connection between application and the queue system.
from app.core.config import get_settings

broker = RedisBroker(url=str(get_settings().redis_url))  # type: ignore[no-untyped-call]
dramatiq.set_broker(broker)
# Dramatiq creates a broker that knows how to communicate with Redis:
# "Use this Redis broker as the broker for Dramatiq."
