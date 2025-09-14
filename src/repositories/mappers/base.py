


class DataMapper:
    db_model: None
    schema: None

    @classmethod
    def map_to_domain_entity(cls, data) -> None:
        if data is None:
            return None
        return cls.schema.model_validate(data, from_attributes=True)
    
    @classmethod
    def map_to_persistence_entity(cls, data) -> None:
        if data is None:
            return None
        return cls.db_model(**data.model_dump(exclude_unset=True))