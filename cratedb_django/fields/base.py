from django.db.models import Field


class CrateDBBaseField(Field):
    """
    Base field for CrateDB columns, it implements crate specific
    column options.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
