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
class JobCreateRequestDto:
    organizationId: str
    jobName: str
    timestampRequest: float

    def toDict(
        self,
    ):
        return {
            "organizationId": self.organizationId,
            "jobName": self.jobName,
            "timestampRequest": self.timestampRequest,
        }


@dataclass
class JobUpdateRequestDto:
    organizationId: str
    jobId: str
    jobName: str
    jobStatus: str

    def toDict(
        self,
    ):
        return {
            "organizationId": self.organizationId,
            "jobId": self.jobId,
            "jobName": self.jobName,
            "jobStatus": self.jobStatus,
        }


@dataclass
class JobDataObject:
    organizationId: str
    jobId: str
    jobName: str
    jobStatus: str
    jobVersion: float
    timestampRequest: float
    timestampCreate: float
    timestampUpdate: float

    def toDict(
        self,
    ):
        return {
            "organizationId": self.organizationId,
            "jobId": self.jobId,
            "jobName": self.jobName,
            "jobStatus": self.jobStatus,
            "jobVersion": self.jobVersion,
            "timestampRequest": self.timestampRequest,
            "timestampCreate": self.timestampCreate,
            "timestampUpdate": self.timestampUpdate,
        }
