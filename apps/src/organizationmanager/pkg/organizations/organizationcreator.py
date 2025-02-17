import json
import logging
import uuid

from commons.logger.logger import Logger
from commons.database.database import Database
from commons.broker.producer import BrokerProducer
from commons.broker.consumer import BrokerConsumer
from pkg.data.organizations import (
    OrganizationDataObject,
    OrganizationCreateRequestDto,
)


class OrganizationCreator:
    def __init__(
        self,
        logger: Logger,
        database: Database,
        brokerProducer: BrokerProducer,
        brokerConsumer: BrokerConsumer,
    ):
        self.logger = logger
        self.database = database
        self.brokerProducer = brokerProducer
        self.brokerConsumer = brokerConsumer

    def run(
        self,
    ) -> None:
        # Establish connections
        self.establishConnections()

        # Consume messages
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
            # Parse message
            messageParsed = self.parseMessage(message)

            # Extract organization create request DTO
            organizationCreateRequestDto = self.extractOrganizationCreateRequestDto(
                messageParsed
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
            self.logger.log(
                logging.ERROR,
                "Error processing organization create request.",
                attrs={
                    "error": str(e),
                },
            )

    def parseMessage(
        self,
        message,
    ) -> dict:

        self.logger.log(
            logging.INFO,
            "Parsing message...",
        )

        try:
            messageParsed = json.loads(message)
        except Exception as e:
            self.logger.log(
                logging.ERROR,
                f"Message parsing failed.",
                attrs={"error": str(e)},
            )
            raise Exception("Message parsing failed: {e}")

        self.validateMessage(messageParsed)

        return messageParsed

    def validateMessage(
        self,
        messageParsed,
    ) -> None:

        self.logger.log(
            logging.INFO,
            "Validating message...",
        )

        missingFields = []
        if "organizationName" not in messageParsed:
            missingFields.append("organizationName")

        if len(missingFields) > 0:
            msg = f"There are missing fields which have to be defined: {missingFields}"
            self.logger.log(
                logging.ERROR,
                msg,
            )
            raise Exception(msg)

        self.logger.log(
            logging.INFO,
            "Message validation succeeded.",
        )

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

        self.logger.log(
            logging.INFO,
            f"Inserting job [{organizationDataObject.organizationId}]...",
        )
        self.database.insert(
            databaseName="organizations",
            collectionName="organizations",
            request=organizationDataObject.toDict(),
        )
        self.logger.log(
            logging.INFO,
            f"Inserting job [{organizationDataObject.organizationId}] succeeded.",
        )

    def publishOrganizationCreated(
        self,
        organizationDataObject: OrganizationDataObject,
    ) -> None:
        self.logger.log(
            logging.INFO,
            f"Publishing created organization [{organizationDataObject.organizationName}] to [organizationcreated] topic...",
        )
        self.brokerProducer.produce(
            "organizationcreated",
            json.dumps(organizationDataObject.toDict()).encode("ascii"),
        )
        self.logger.log(
            logging.INFO,
            f"Publishing created organization [{organizationDataObject.organizationName}] to [organizationcreated] topic succeeded.",
        )
