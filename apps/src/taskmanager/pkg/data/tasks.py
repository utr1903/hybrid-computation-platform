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

@dataclass
class TaskUpdateRequestDto:
    organizationId: str
    taskId: str
    taskStatus: str
    timestampUpdated: float

    def toDict(
        self,
    ):
        return {
            "organizationId": self.organizationId,
            "taskId": self.taskId,
            "taskStatus": self.taskStatus,
            "timestampUpdated": self.timestampUpdated,
        }
