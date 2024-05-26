from app.entities.agent_data import AgentData
from app.entities.processed_agent_data import ProcessedAgentData
from enum import Enum

class RoadState():

    flat: str = "Road is Flat. You can speed up safely"
    hole: str = "Hole on your way, slow down!"
    hump: str = "Some hump on you way, slow down!"

    hole_range: range = range(-10000000, 0)
    hump_range: range = range(8000, 1000000)



def process_agent_data(
    agent_data: AgentData,
) -> ProcessedAgentData:
    """
    Process agent data and classify the state of the road surface.
    Parameters:
        agent_data (AgentData): Agent data that containing accelerometer, GPS, and timestamp.
    Returns:
        processed_data_batch (ProcessedAgentData): Processed data containing the classified state of the road surface and agent data.
    """
    accelerometer_data = agent_data.accelerometer
    agent_data.user_id = 1

    if accelerometer_data.z in RoadState.hole_range:
        return ProcessedAgentData(road_state=RoadState.hole, agent_data=agent_data)
    elif accelerometer_data.z in RoadState.hump_range:
        return ProcessedAgentData(road_state=RoadState.hump, agent_data=agent_data)
    else:
        return ProcessedAgentData(road_state=RoadState.flat, agent_data=agent_data)
