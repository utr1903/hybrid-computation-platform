import json
import logging
import uuid

from pkg.database.database import Database
from pkg.broker.producer import BrokerProducer
from pkg.broker.consumer import BrokerConsumer
from pkg.data.organizations import (
    OrganizationDataObject,
    OrganizationCreateRequestDto,
)

logger = logging.getLogger(__name__)


class OrganizationCreator:
    def __init__(
        self,
        database: Database,
        brokerProducer: BrokerProducer,
        brokerConsumer: BrokerConsumer,
    ):
        self.database = database
        self.brokerProducer = brokerProducer
        self.brokerConsumer = brokerConsumer

    def run(
        self,
    ) -> None:

        self.brokerConsumer.consume(self.processOrganizationCreateRequest)

    def processOrganizationCreateRequest(
        self,
        message: dict,
    ) -> None:

        try:
            logger.info(message)

            # Extract organization create request DTO
            organizationCreateRequestDto = self.extractOrganizationCreateRequestDto(
                message
            )

            # Create organization data object
            organizationDataObject = self.createOrganizationDataObject(
                organizationCreateRequestDto
            )

            # Add organization to organizations collection
            self.addOrganizationToOrganizationsCollection(organizationDataObject)

            # Publish new organization to broker
            self.publishOrganizationCreated(organizationDataObject)

        except Exception as e:
            logger.error(e)

    def extractOrganizationCreateRequestDto(
        self,
        message: dict,
    ) -> OrganizationCreateRequestDto:

        return OrganizationCreateRequestDto(
            organizationName=message.get("organizationName"),
        )

    def createOrganizationDataObject(
        self,
        organizationCreateRequestDto: OrganizationCreateRequestDto,
    ) -> OrganizationDataObject:
        return OrganizationDataObject(
            organizationId=str(uuid.uuid4()),
            organizationName=organizationCreateRequestDto.organizationName,
        )

    def addOrganizationToOrganizationsCollection(
        self,
        organizationDataObject: OrganizationDataObject,
    ) -> None:

        logger.info(f"Inserting job [{organizationDataObject.organizationId}]...")
        self.database.insert(
            databaseName="organizations",
            collectionName="organizations",
            request=organizationDataObject.toDict(),
        )
        logger.info(
            f"Inserting job [{organizationDataObject.organizationId}] succeeded."
        )

    def publishOrganizationCreated(
        self,
        organizationDataObject: OrganizationDataObject,
    ) -> None:
        logger.info(f"Publishing created organization to  [organizationcreated] topic...")
        # Publish to broker
        self.brokerProducer.produce(
            "organizationcreated",
            json.dumps(organizationDataObject),
        )
        logger.info(f"Publishing created organization to  [organizationcreated] topic succeeded.")
