from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pb_portal.db import tools as db_tools
from pb_portal import pb, config


async def publish_pb() -> None:
    publish_ids = await db_tools.pop_publish_queue()
    pb.publish(publish_ids)


async def pb_creators_update() -> None:
    await pb.get_creators()


def scheluder() -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()
    scheduler.add_job(publish_pb, 'interval', minutes=config.PUBLISH_INTERVAL)
    scheduler.add_job(pb_creators_update, 'interval', minutes=config.CREATORS_UPDATE_INTERVAL)

    return scheduler
