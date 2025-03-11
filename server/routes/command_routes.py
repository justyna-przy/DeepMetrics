from fastapi import APIRouter
import logging
from schemas import CommandIn, CommandAck
from command_queue import CommandQueue

command_queue = CommandQueue()
router = APIRouter()

@router.post("/api/commands", summary="Enqueue a new command")
def post_command(cmd: CommandIn):
    """
    Front-end calls this to enqueue a command for a given aggregator/device.
    """
    command_id = command_queue.enqueue(cmd.model_dump())
    logging.getLogger("uvicorn").info(
        "Enqueued command %s for aggregator '%s' device '%s'",
        command_id, cmd.aggregator_name, cmd.device_name
    )
    return {"message": "Command enqueued", "command_id": command_id}

@router.get("/api/aggregators/{aggregator_name}/commands", summary="Get unacked commands for aggregator")
def get_commands_for_aggregator(aggregator_name: str):
    """
    Aggregator code polls this endpoint to retrieve all unacked commands
    intended for the given aggregator.
    """
    cmds = command_queue.get_unacked_for_aggregator(aggregator_name)
    logging.getLogger("uvicorn").info(
        "Polled %d commands for aggregator '%s'",
        len(cmds), aggregator_name
    )
    return cmds

@router.post("/api/aggregators/{aggregator_name}/commands/ack", summary="Acknowledge processed commands")
def ack_commands_for_aggregator(aggregator_name: str, ack: CommandAck):
    """
    Aggregator code calls this after processing commands, so the server
    can remove them from the queue.
    """
    command_queue.ack(aggregator_name, ack.command_ids)
    logging.getLogger("uvicorn").info(
        "Acknowledged command IDs: %s for aggregator '%s'",
        ack.command_ids, aggregator_name
    )
    return {"message": "Commands acknowledged", "command_ids": ack.command_ids}
