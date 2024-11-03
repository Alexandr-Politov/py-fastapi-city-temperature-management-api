from typing import Optional

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.engine import SessionLocal
import schemas, crud


app = FastAPI()


def get_session() -> Session:
    db_session = SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()


@app.get("/")
def welcome_screen() -> dict:
    return {"message": "Welcome"}


@app.get("/cities/", response_model=list[schemas.CityInfo])
def read_cities(db_session: Session = Depends(get_session)):
    return crud.get_all_cities(db_session=db_session)


@app.post("/cities/", response_model=schemas.CityInfo)
def create_city(
        city: schemas.CityCreate,
        db_session: Session = Depends(get_session)
):
    db_city = crud.get_city_by_name(name=city.name, db_session=db_session)
    if db_city:
        raise HTTPException(status_code=400, detail="City already exists")

    return crud.create_city(city=city, db_session=db_session)


@app.get("/cities/{city_id}", response_model=schemas.CityInfo)
def read_city(
        city_id: int,
        db_session: Session = Depends(get_session)
) -> schemas.CityInfo:
    city = crud.get_city_by_id(city_id=city_id, db_session=db_session)
    if not city:
        raise HTTPException(status_code=404, detail="City not found")
    return city


@app.put("/cities/{city_id}", response_model=schemas.CityInfo)
def update_city(
        city_id: int,
        city: schemas.CityCreate,
        db_session: Session = Depends(get_session)
) -> schemas.CityInfo:
    return crud.update_city(city_id=city_id, city=city, db_session=db_session)


@app.delete("/cities/{city_id}", status_code=status.HTTP_200_OK)
def delete_city(city_id: int, db_session: Session = Depends(get_session)):
    crud.delete_city(city_id=city_id, db_session=db_session)
    return {"message": "City deleted successfully"}


@app.get("/temperatures/", response_model=list[schemas.TemperatureInfo])
def read_all_temperatures(
        city_id: Optional[int] = None,
        db_session: Session = Depends(get_session)):
    return crud.get_all_temperatures(db_session=db_session, city_id=city_id)


@app.post("/temperatures/", response_model=schemas.TemperatureInfo)
def create_temperature(
        temperature: schemas.TemperatureCreate,
        db_session: Session = Depends(get_session)
):
    db_city = crud.get_city_by_id(
        city_id=temperature.city_id, db_session=db_session
    )
    if not db_city:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="City with the specified ID does not exist"
        )

    return crud.create_temperature(
        temperature=temperature, db_session=db_session
    )


@app.get("/temperatures/{temp_id}", response_model=schemas.TemperatureInfo)
def read_single_temperature(
        temp_id: int,
        db_session: Session = Depends(get_session)
) -> schemas.TemperatureInfo:
    db_temperature = crud.get_temperature_by_id(
        temperature_id=temp_id, db_session=db_session
    )
    if not db_temperature:
        raise HTTPException(status_code=404, detail="Temperature not found")
    return db_temperature
