from fastapi import FastAPI
from pydantic import BaseModel
from algorithms.triage import Incident, TriageQueue
from backend.routing_service import find_route
from backend.allocation_service import run_allocation


app = FastAPI(title="Disaster Response Platform API")

# In-memory triage queue — resets every time the server restarts.
# Later this would be backed by a real database.
triage_queue = TriageQueue()
incident_id_counter = 1


class IncidentRequest(BaseModel):
    """
    Defines exactly what data the API expects when someone
    submits a new incident. FastAPI uses this to validate
    incoming requests automatically.
    """
    location: str
    severity: int  # 1 (minor) to 5 (critical)

class RouteRequest(BaseModel):
    place_name: str       # e.g. "Kochi, Kerala, India"
    start_lat: float
    start_lon: float
    end_lat: float
    end_lon: float
    algorithm: str = "astar"  # "astar" or "dijkstra"

class LocationEntry(BaseModel):
    name: str
    location: list[float]  # [latitude, longitude]


class AllocationRequest(BaseModel):
    victims: list[LocationEntry]
    resources: list[LocationEntry]


@app.get("/")
def root():
    return {"message": "Disaster Response Platform API is running"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/incidents")
def report_incident(incident_request: IncidentRequest):
    """
    Submit a new incident. It gets added to the triage priority queue.
    """
    global incident_id_counter

    incident = Incident(
        incident_id=incident_id_counter,
        location=incident_request.location,
        severity=incident_request.severity,
    )
    triage_queue.add_incident(incident)
    incident_id_counter += 1

    return {
        "message": "Incident reported successfully",
        "incident_id": incident.incident_id,
        "priority_score": round(incident.priority_score(), 2),
    }


@app.get("/incidents/next")
def get_next_incident():
    """
    Returns and removes the highest-priority incident from the queue —
    simulates a rescue team being dispatched to the most urgent case.
    """
    incident = triage_queue.get_next_incident()
    if incident is None:
        return {"message": "No incidents in queue"}

    return {
        "incident_id": incident.incident_id,
        "location": incident.location,
        "severity": incident.severity,
        "priority_score": round(incident.priority_score(), 2),
    }


@app.get("/incidents/queue-size")
def queue_size():
    return {"incidents_waiting": triage_queue.size()}

@app.post("/route")
def get_route(route_request: RouteRequest):
    """
    Computes the shortest route between two coordinates within a given
    area, using either A* (default) or Dijkstra.
    """
    result = find_route(
        place_name=route_request.place_name,
        start_lat=route_request.start_lat,
        start_lon=route_request.start_lon,
        end_lat=route_request.end_lat,
        end_lon=route_request.end_lon,
        algorithm=route_request.algorithm,
    )
    return result
@app.post("/allocate")
def allocate(allocation_request: AllocationRequest):
    """
    Given a list of victims and available resources (hospitals/shelters),
    returns the optimal victim-to-resource assignment using the
    Hungarian algorithm — minimizing total travel distance across
    everyone, not just each victim's individual nearest choice.
    """
    victims = [v.model_dump() for v in allocation_request.victims]
    resources = [r.model_dump() for r in allocation_request.resources]

    assignments = run_allocation(victims, resources)
    return {"assignments": assignments}