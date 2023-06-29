from dagger.models.partner import Partner
from dagger.schemas.partner import PartnerCreate, PartnerUpdate
from dagger.services.base import ServiceBase


class PartnerService(ServiceBase[Partner, PartnerCreate, PartnerUpdate]):
    ...


partner = PartnerService(Partner)
