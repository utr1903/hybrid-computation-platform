from dataclasses import dataclass


@dataclass
class TaskDataObject:
    organizationId: str
    jobId: str
    jobVersion: int
    timestampSubmitted: float
    taskId: str
    taskStatus: str

    def toDict(
        self,
    ):
        return {
            "organizationId": self.organizationId,
            "jobId": self.jobId,
            "jobVersion": self.jobVersion,
            "timestampSubmitted": self.timestampSubmitted,
            "taskId": self.taskId,
            "taskStatus": self.taskStatus,
        }


@dataclass
class TaskCreateRequestDto:
    organizationId: str
    jobId: str
    jobVersion: int
    timestampSubmitted: float

    def toDict(
        self,
    ):
        return {
            "organizationId": self.organizationId,
            "jobId": self.jobId,
            "jobVersion": self.jobVersion,
            "timestampSubmitted": self.timestampSubmitted,
        }
