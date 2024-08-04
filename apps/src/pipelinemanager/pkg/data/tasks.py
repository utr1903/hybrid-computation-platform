from dataclasses import dataclass


@dataclass
class TaskDataObject:
    organizationId: str
    jobId: str
    jobVersion: int
    timestampCreated: float
    taskId: str
    taskStatus: str

    def toDict(
        self,
    ):
        return {
            "organizationId": self.organizationId,
            "jobId": self.jobId,
            "jobVersion": self.jobVersion,
            "timestampCreated": self.timestampCreated,
            "taskId": self.taskId,
            "taskStatus": self.taskStatus,
        }


@dataclass
class TaskCreateRequestDto:
    organizationId: str
    jobId: str
    jobVersion: int
    timestampCreated: float

    def toDict(
        self,
    ):
        return {
            "organizationId": self.organizationId,
            "jobId": self.jobId,
            "jobVersion": self.jobVersion,
            "timestampCreated": self.timestampCreated,
        }
