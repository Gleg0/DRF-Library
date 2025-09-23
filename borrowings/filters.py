import django_filters

from borrowings.models import Borrowing


class BorrowingFilter(django_filters.FilterSet):
    is_active = django_filters.BooleanFilter(
        field_name="actual_return_date",
        lookup_expr="isnull",
        label="is_active",
        help_text="Search by active status (Example: ?is_active=true|false)",
    )

    class Meta:
        model = Borrowing
        fields = ("is_active",)


class BorrowingAdminFilter(BorrowingFilter):
    user = django_filters.NumberFilter(
        field_name="user",
        help_text="Search by user id",
    )

    class Meta(BorrowingFilter.Meta):
        model = Borrowing
        fields = BorrowingFilter.Meta.fields + ("user",)
