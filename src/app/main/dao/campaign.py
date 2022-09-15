from ... import db
from ..models.main import Campaign


def get_campaign_with_id(campaign_id):
    return Campaign.query.get(campaign_id)


def get_campaigns_with_criteria(org_id, query_text, current_user, limit=25):
    query = Campaign.query
    if org_id:
        query = query.filter(Campaign.org_id == org_id)
    if query:
        query = query.filter(
            db.func.lower(Campaign.name).ilike(f"%{query_text.lower()}%")
        )
    return query.order_by(Campaign.name).limit(limit).all()
