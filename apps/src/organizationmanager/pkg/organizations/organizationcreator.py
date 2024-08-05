import json
import logging
import uuid

from commons.database.database import Database
from commons.broker.producer import BrokerProducer
from commons.broker.consumer import BrokerConsumer
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
        self.establishConnections()

        self.brokerConsumer.consume(self.processOrganizationCreateRequest)

    def establishConnections(
        self,
    ) -> None:
        self.database.connect()
        self.brokerProducer.connect()
        self.brokerConsumer.connect()

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
        logger.info(
            f"Publishing created organization [{organizationDataObject.organizationName}] to [organizationcreated] topic..."
        )
        self.brokerProducer.produce(
            "organizationcreated",
            json.dumps(organizationDataObject.toDict()).encode("ascii"),
        )
        logger.info(
            f"Publishing created organization [{organizationDataObject.organizationName}] to [organizationcreated] topic succeeded."
        )
