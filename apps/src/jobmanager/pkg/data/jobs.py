from dataclasses import dataclass


@dataclass
class OrganizationDataObject:
    organizationName: str
    organizationId: str

    def toDict(
        self,
    ):
        return {
            "organizationId": self.organizationId,
            "organizationName": self.organizationName,
        }


@dataclass
class JobRequestDto:
    customerOrganizationId: str
    customerUserId: str
    jobId: str
    jobName: str
    jobVersion: float
    jobRequestTimestamp: float

    def toDict(
        self,
    ):
        return {
            "customerOrganizationId": self.customerOrganizationId,
            "customerUserId": self.customerUserId,
            "jobId": self.jobId,
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
