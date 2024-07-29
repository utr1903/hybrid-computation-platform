import json
from dataclasses import dataclass


@dataclass
class JobRequestDto:
    customerOrganizationId: str
    customerUserId: str
    jobName: str
    jobVersion: float
    jobRequestTimestamp: float

    def toDict(
        self,
    ):
        return {
            "customerOrganizationId": self.customerOrganizationId,
            "customerUserId": self.customerUserId,
            "jobName": self.jobName,
            "jobVersion": self.jobVersion,
            "jobRequestTimestamp": self.jobRequestTimestamp,
        }


@dataclass
class JobCreationDto:
    customerOrganizationId: str
    customerUserId: str
    jobId: str
    jobName: str
    jobStatus: str
    jobVersion: float
    jobRequestTimestamp: float
    jobCreationTimestamp: float

    def toDict(
        self,
    ):
        return {
            "customerOrganizationId": self.customerOrganizationId,
            "customerUserId": self.customerUserId,
            "jobId": self.jobId,
            "jobName": self.jobName,
            "jobStatus": self.jobStatus,
            "jobVersion": self.jobVersion,
            "jobRequestTimestamp": self.jobRequestTimestamp,
            "jobCreationTimestamp": self.jobCreationTimestamp,
        }
