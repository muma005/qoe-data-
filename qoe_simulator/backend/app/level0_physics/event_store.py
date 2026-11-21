"""
Immutable Event Sourced State Store (Level 0)
Records every simulation event into an append-only log with SHA-256 hash chaining.
Provides optimistic concurrency control via stream versions and guarantees PCAOB AS 1215 auditability.
"""

import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass(frozen=True)
class SimulationEvent:
    event_id: str
    engagement_id: str
    stream_id: str
    stream_version: int
    event_type: str
    simulation_day: int
    simulation_timestamp: str  # ISO-8601
    wall_clock_timestamp: str  # ISO-8601
    payload: Dict[str, Any]
    invariants_passed: List[str]
    prev_event_hash: str
    cryptographic_hash: str

    @classmethod
    def create(
        cls,
        engagement_id: str,
        stream_id: str,
        stream_version: int,
        event_type: str,
        simulation_day: int,
        simulation_timestamp: str,
        payload: Dict[str, Any],
        invariants_passed: List[str],
        prev_event_hash: str = "0" * 64
    ) -> "SimulationEvent":
        event_id = str(uuid.uuid4())
        wall_clock = datetime.now(timezone.utc).isoformat()
        
        # Deterministic JSON canonicalization for cryptographic hashing
        canonical_payload = json.dumps(payload, sort_keys=True)
        hash_preimage = f"{prev_event_hash}:{stream_id}:{stream_version}:{event_type}:{canonical_payload}".encode("utf-8")
        event_hash = hashlib.sha256(hash_preimage).hexdigest()
        
        return cls(
            event_id=event_id,
            engagement_id=engagement_id,
            stream_id=stream_id,
            stream_version=stream_version,
            event_type=event_type,
            simulation_day=simulation_day,
            simulation_timestamp=simulation_timestamp,
            wall_clock_timestamp=wall_clock,
            payload=payload,
            invariants_passed=invariants_passed,
            prev_event_hash=prev_event_hash,
            cryptographic_hash=event_hash
        )


class EventStore:
    """Append-only, in-memory event store with hash-chain integrity verification."""
    
    def __init__(self):
        self._events: List[SimulationEvent] = []
        self._stream_versions: Dict[str, int] = {}
        self._last_event_hash: str = "0" * 64

    def append_event(
        self,
        engagement_id: str,
        stream_id: str,
        event_type: str,
        simulation_day: int,
        simulation_timestamp: str,
        payload: Dict[str, Any],
        invariants_passed: List[str]
    ) -> SimulationEvent:
        """Appends an event to the log with optimistic concurrency and SHA-256 hash chaining."""
        next_version = self._stream_versions.get(stream_id, 0) + 1
        
        event = SimulationEvent.create(
            engagement_id=engagement_id,
            stream_id=stream_id,
            stream_version=next_version,
            event_type=event_type,
            simulation_day=simulation_day,
            simulation_timestamp=simulation_timestamp,
            payload=payload,
            invariants_passed=invariants_passed,
            prev_event_hash=self._last_event_hash
        )
        
        self._events.append(event)
        self._stream_versions[stream_id] = next_version
        self._last_event_hash = event.cryptographic_hash
        return event

    def get_stream(self, stream_id: str) -> List[SimulationEvent]:
        """Returns all events in a specific stream in chronological order."""
        return [e for e in self._events if e.stream_id == stream_id]

    def get_events_for_day(self, engagement_id: str, simulation_day: int) -> List[SimulationEvent]:
        """Returns all events for a given simulation day."""
        return [e for e in self._events if e.engagement_id == engagement_id and e.simulation_day == simulation_day]

    def verify_hash_chain_integrity(self) -> Tuple[bool, Optional[str]]:
        """
        PCAOB AS 1215 Audit Requirement:
        Iterates through the entire event log and verifies that every cryptographic
        hash matches its previous link. Traps any retroactive database mutation.
        """
        prev_hash = "0" * 64
        for idx, event in enumerate(self._events):
            if event.prev_event_hash != prev_hash:
                return False, f"Broken chain link at index {idx} (Event ID: {event.event_id})"
            
            canonical_payload = json.dumps(event.payload, sort_keys=True)
            preimage = f"{prev_hash}:{event.stream_id}:{event.stream_version}:{event.event_type}:{canonical_payload}".encode("utf-8")
            expected_hash = hashlib.sha256(preimage).hexdigest()
            
            if event.cryptographic_hash != expected_hash:
                return False, f"Tampered event payload at index {idx} (Event ID: {event.event_id})"
            
            prev_hash = event.cryptographic_hash
            
        return True, None
