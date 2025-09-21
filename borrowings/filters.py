import django_filters

from borrowings.models import Borrowing


class BorrowingFilter(django_filters.FilterSet):
    actual_return_date = django_filters.BooleanFilter(
        field_name="actual_return_date",
        lookup_expr="isnull",
        label="is_active"

    )

    class Meta:
        model = Borrowing
        fields = ("actual_return_date", )
