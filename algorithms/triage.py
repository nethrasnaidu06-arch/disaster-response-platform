import heapq
import time
from dataclasses import dataclass, field


@dataclass
class Incident:
    """
    Represents a single reported emergency.
    severity: 1 (minor) to 5 (critical/life-threatening)
    """
    incident_id: int
    location: str
    severity: int  # 1-5
    reported_at: float = field(default_factory=time.time)

    def priority_score(self, urgency_weight=5):
        """
        Higher score = more urgent = served first.

        - Severity is weighted heavily (most important factor).
        - The longer someone waits, the more their priority grows,
          so low-severity cases don't get starved forever if the
          queue is backed up.

        urgency_weight controls how much waiting time matters relative
        to severity. Set to 5 based on testing: at this value, a
        30-minute wait can outweigh a one-level severity difference,
        preventing low-severity cases from waiting indefinitely while
        still letting severity dominate for genuinely critical cases.
        """
        wait_time_seconds = time.time() - self.reported_at
        wait_time_minutes = wait_time_seconds / 60

        severity_weight = self.severity * 100
        urgency_growth = wait_time_minutes * urgency_weight

        return severity_weight + urgency_growth


class TriageQueue:
    """
    A max-priority queue of incidents. Always pops the most urgent
    incident first, regardless of the order they were added in.
    """

    def __init__(self, urgency_weight=5):
        self._heap = []
        self._counter = 0  # tie-breaker so heapq never compares Incident objects directly
        self.urgency_weight = urgency_weight

    def add_incident(self, incident: Incident):
        # heapq is a MIN-heap by default, so we push the NEGATIVE score
        # to simulate a max-heap (most urgent = "smallest" negative number = popped first)
        score = -incident.priority_score(urgency_weight=self.urgency_weight)
        heapq.heappush(self._heap, (score, self._counter, incident))
        self._counter += 1

    def get_next_incident(self):
        if not self._heap:
            return None
        _, _, incident = heapq.heappop(self._heap)
        return incident

    def peek_next_incident(self):
        if not self._heap:
            return None
        return self._heap[0][2]

    def is_empty(self):
        return len(self._heap) == 0

    def size(self):
        return len(self._heap)


def test_basic_priority_order():
    queue = TriageQueue()

    queue.add_incident(Incident(incident_id=1, location="Kochi Ward 3", severity=2))
    queue.add_incident(Incident(incident_id=2, location="Kochi Ward 5", severity=5))
    queue.add_incident(Incident(incident_id=3, location="Kochi Ward 1", severity=3))
    queue.add_incident(Incident(incident_id=4, location="Kochi Ward 7", severity=1))

    print(f"Total incidents in queue: {queue.size()}\n")

    print("Serving incidents in priority order:")
    while not queue.is_empty():
        incident = queue.get_next_incident()
        print(
            f"  Incident #{incident.incident_id} "
            f"({incident.location}) — "
            f"severity={incident.severity}, "
            f"priority_score={incident.priority_score():.2f}"
        )


def test_urgency_growth():
    print("\n" + "=" * 60)
    print("Testing: does waiting longer increase priority over time?")
    print("=" * 60)

    old_incident = Incident(incident_id=101, location="Wayanad", severity=2)
    old_incident.reported_at = time.time() - (30 * 60)  # 30 minutes ago

    new_incident = Incident(incident_id=102, location="Wayanad", severity=3)

    for weight in [2, 5, 10]:
        old_score = old_incident.priority_score(urgency_weight=weight)
        new_score = new_incident.priority_score(urgency_weight=weight)
        outcome = "old wins" if old_score > new_score else "new still wins"
        print(f"urgency_weight={weight}: old={old_score:.2f}, new={new_score:.2f} -> {outcome}")


def test_default_weight():
    print("\n" + "=" * 60)
    print("Confirming the default urgency_weight is now 5")
    print("=" * 60)
    incident = Incident(incident_id=999, location="Test", severity=1)
    default_score = incident.priority_score()  # uses whatever the default is
    explicit_score = incident.priority_score(urgency_weight=5)
    print(f"Score using default: {default_score:.2f}")
    print(f"Score using urgency_weight=5 explicitly: {explicit_score:.2f}")
    if default_score == explicit_score:
        print("✅ Confirmed: default is 5")
    else:
        print("⚠️ Default is NOT 5 — check the function signature")


if __name__ == "__main__":
    test_basic_priority_order()
    test_urgency_growth()
    test_default_weight()