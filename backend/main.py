from fastapi import FastAPI
from pydantic import BaseModel
from algorithms.triage import Incident, TriageQueue
from backend.routing_service import find_route
from backend.allocation_service import run_allocation
from backend.hospitals_data import HOSPITALS



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
    lat: float
    lon: float

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
    global incident_id_counter

    incident = Incident(
        incident_id=incident_id_counter,
        location=incident_request.location,
        severity=incident_request.severity,
        lat=incident_request.lat,
        lon=incident_request.lon,
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

@app.post("/dispatch")
def dispatch_next_incident(place_name: str = "Kochi, Kerala, India"):
    """
    Full workflow: pulls the most urgent incident from the triage queue,
    finds the nearest hospital using real road routing, and returns the
    combined result — this is the "brain" tying the algorithms together.
    """
    incident = triage_queue.get_next_incident()
    if incident is None:
        return {"message": "No incidents in queue"}

    # For now, we don't have real incident coordinates, so we use a
    # placeholder location near the center of the given area.
    # (Later, incidents will carry their own lat/lon from the report.)
    incident_location = [incident.lat, incident.lon]

    best_hospital = None
    best_distance = float("inf")
    route_details = None

    for hospital in HOSPITALS:
        result = find_route(
            place_name=place_name,
            start_lat=incident_location[0],
            start_lon=incident_location[1],
            end_lat=hospital["location"][0],
            end_lon=hospital["location"][1],
            algorithm="astar",
        )
        if result["distance_meters"] < best_distance:
            best_distance = result["distance_meters"]
            best_hospital = hospital["name"]
            route_details = result

    return {
        "incident_id": incident.incident_id,
        "location": incident.location,
        "severity": incident.severity,
        "priority_score": round(incident.priority_score(), 2),
        "assigned_hospital": best_hospital,
        "distance_meters": best_distance,
        "route_details": route_details,
    }