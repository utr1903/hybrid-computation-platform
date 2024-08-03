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
class OrganizationCreateRequestDto:
    organizationName: str

    def toDict(
        self,
    ):
        return {
            "organizationName": self.organizationName,
        }
