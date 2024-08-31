from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pb_portal.db import tools as db_tools
from pb_portal import pb, config


async def publish_pb() -> None:
    publish_ids = await db_tools.pop_publish_queue()
    pb.publish(publish_ids)


def scheluder() -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()
    scheduler.add_job(publish_pb, 'interval', seconds=1)#minutes=config.PUBLISH_INTERVAL)
    return scheduler
