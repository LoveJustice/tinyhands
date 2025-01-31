# models.py

from typing import List, Optional
from pydantic import BaseModel, Field


class IncidentResponse(BaseModel):
    answer: str  # "yes" or "no"
    evidence: Optional[List[str]] = None


class CrimeResponse(BaseModel):
    answer: str  # "yes" or "no"
    evidence: Optional[List[str]] = None


class SuspectResponse(BaseModel):
    answer: str  # "yes" or "no"
    evidence: Optional[List[str]] = None


class VictimResponse(BaseModel):
    answer: str  # "yes" or "no"
    evidence: Optional[List[str]] = None


class CrimeDateResponse(BaseModel):
    answer: str  # "yes" or "no"
    evidence: Optional[List[str]] = None  # ["YYYY-MM-DD"]


class PublishedDateResponse(BaseModel):
    answer: str  # "yes" or "no"
    evidence: Optional[List[str]] = None  # ["YYYY-MM-DD"]


class LocationResponse(BaseModel):
    answer: str  # "yes" or "no"
    evidence: Optional[str] = None  # "location"


class PersonResponse(BaseModel):
    persons_mentioned: str  # "yes" or "no"
    evidence: Optional[List[str]] = None


class PlacenameResponse(BaseModel):
    place_names_mentioned: str  # "yes" or "no"
    evidence: Optional[List[str]] = None


class VictimOriginResponse(BaseModel):
    answer: str  # "yes" or "no"
    evidence: Optional[List[str]] = None


class SuspectOriginResponse(BaseModel):
    answer: str  # "yes" or "no"
    evidence: Optional[List[str]] = None


class VictimDestinationResponse(BaseModel):
    answer: str  # "yes" or "no"
    evidence: Optional[List[str]] = None


class CaseNotesResponse(BaseModel):
    answer: str  # "yes" or "no"
    evidence: Optional[List[str]] = None


class CountryResponse(BaseModel):
    answer: str  # "yes" or "no"
    evidence: Optional[List[str]] = None

class Gender(BaseModel):
    answer: str  # "yes" or "no"
    evidence: Optional[List[str]] = None

class Age(BaseModel):
    answer: str  # "yes" or "no"
    evidence: Optional[List[int]] = None

class ArticleMetaData(BaseModel):
    authors: Optional[List[str]] = None
    date_of_publication: Optional[str] = None   # "YYYY-MM-DD" or null

class ConfirmResponse(BaseModel):
    answer: str  # "yes" or "no"
    evidence: Optional[List[str]] = None


class SuspectFormResponse(BaseModel):
    name: str  # The suspect's name
    gender: Optional[str] = None
    date_of_birth: Optional[str] = None  # "YYYY-MM-DD" or null
    age: Optional[int] = None
    address_notes: Optional[str] = None
    phone_number: Optional[str] = None
    nationality: Optional[str] = None
    occupation: Optional[str] = None
    role: Optional[str] = None
    appearance: Optional[str] = None
    vehicle_description: Optional[str] = None
    vehicle_plate_number: Optional[str] = None
    evidence: Optional[str] = None
    arrested_status: Optional[str] = None
    arrest_date: Optional[str] = None   # "YYYY-MM-DD" or null
    crimes_person_charged_with: Optional[str] = None
    willing_pv_names: Optional[str] = None
    suspect_in_police_custody: Optional[str] = None
    suspect_current_location: Optional[str] = None
    suspect_last_known_location: Optional[str] = None
    suspect_last_known_location_date: Optional[str] = None  # "YYYY-MM-DD" or null

class VictimFormResponse(BaseModel):
    name: str  # The suspect's name
    gender: Optional[str] = None
    date_of_birth: Optional[str] = None  # "YYYY-MM-DD" or null
    age: Optional[int] = None
    address_notes: Optional[str] = None
    phone_number: Optional[str] = None
    nationality: Optional[str] = None
    occupation: Optional[str] = None
    appearance: Optional[str] = None
    vehicle_description: Optional[str] = None
    vehicle_plate_number: Optional[str] = None
    destination: Optional[str] = None
    job_offered: Optional[str] = None

