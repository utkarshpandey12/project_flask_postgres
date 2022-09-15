import datetime

from sqlalchemy.exc import IntegrityError

from ... import db
from ..models.main import Country


def get_country_with_id(country_id):
    return Country.query.get(country_id)


def get_all_countries():
    return Country.query.all()


def get_countries_with_ids(country_ids):
    return Country.query.filter(Country.id.in_(country_ids)).all()


def get_country_by_name(name):
    country = Country.query.filter(
        db.func.lower(Country.name) == name.strip().lower()
    ).first()
    return country


def get_country_by_country_code(country_code):
    country = Country.query.filter(Country.country_code == country_code).first()
    return country


def create_country(name, country_code):
    now = datetime.datetime.now()
    country = Country(
        name=name,
        country_code=country_code,
        created_at=now,
    )
    db.session.add(country)
    db.session.flush()
    return country


def delete_country(country):
    try:
        db.session.delete(country)
        db.session.flush()
        return True
    except IntegrityError:
        db.session.rollback()
        return False


def update_country(country, name, country_code, current_user):
    country.name = name
    country.country_code = country_code
    return country
