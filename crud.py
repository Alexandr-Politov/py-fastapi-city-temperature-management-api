from typing import List

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

import schemas
from database import models


def get_all_cities(db_session: Session) -> List[schemas.CityInfo]:
    cities = db_session.query(models.DBCity)
    return [schemas.CityInfo.from_orm(city) for city in cities]


def get_city_by_name(name: str, db_session: Session) -> schemas.CityInfo | None:
    return (db_session.query(models.DBCity)
            .filter(models.DBCity.name == name).first())


def get_city_by_id(city_id: int, db_session: Session) -> schemas.CityInfo | None:
    return (db_session.query(models.DBCity)
            .filter(models.DBCity.id == city_id).first())


def create_city(
        city: schemas.CityCreate, db_session: Session
) -> schemas.CityInfo:
    db_new_city = models.DBCity(**city.model_dump())
    db_session.add(db_new_city)
    db_session.commit()
    db_session.refresh(db_new_city)
    return schemas.CityInfo.from_orm(db_new_city)


def update_city(
        city_id: int, city: schemas.CityCreate, db_session: Session
) -> schemas.CityInfo:
    db_city = get_city_by_id(city_id=city_id, db_session=db_session)
    if not db_city:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="City not found"
        )

    city_data = city.model_dump(exclude_unset=True)
    for key, value in city_data.items():
        setattr(db_city, key, value)

    db_session.commit()
    db_session.refresh(db_city)
    return schemas.CityInfo.from_orm(db_city)


def delete_city(city_id: int, db_session: Session) -> None:
    db_city = (db_session.query(models.DBCity)
               .filter(models.DBCity.id == city_id)).first()

    if not db_city:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="City not found"
        )

    db_session.delete(db_city)
    db_session.commit()
