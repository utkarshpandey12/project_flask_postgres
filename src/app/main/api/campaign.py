from ...utils import response
from ..dao import campaign as campaign_dao
from ..schemas import campaign as campaign_schemas


def search_campaigns(org_id, query, current_user):
    campaigns = campaign_dao.get_campaigns_with_criteria(org_id, query, current_user)
    res = campaign_schemas.campaign_schema.dump(campaigns, many=True)
    return response.success(res)
