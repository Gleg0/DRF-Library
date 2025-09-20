from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext as _
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
        style={"input_type": "password"},
        label=_("Password"),
    )

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "password",
            "is_staff",
        )
        read_only_fields = ("id", "is_staff")

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class ManageUserSerializer(UserSerializer):
    current_password = serializers.CharField(
        write_only=True,
        required=False,
        style={"input_type": "password"},
        label=_("Current password"),
    )
    new_password = serializers.CharField(
        write_only=True,
        required=False,
        validators=[validate_password],
        style={"input_type": "password"},
        label=_("New password"),
    )

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "current_password",
            "new_password",
        )
        read_only_fields = ("id", "is_staff")

    def validate(self, attrs):
        """
        Confirm old password when user want to change it.
        """
        user = self.instance
        current_password = attrs.get("current_password")
        new_password = attrs.get("new_password")

        if new_password and not current_password:
            raise serializers.ValidationError(
                {"current_password": "You must provide the current password."}
            )

        if current_password and not user.check_password(current_password):
            raise serializers.ValidationError(
                {"current_password": "Current password is not correct."}
            )

        return attrs

    def update(self, instance, validated_data):
        email = validated_data.pop("email", instance.email)
        first_name = validated_data.pop("first_name", instance.first_name)
        last_name = validated_data.pop("last_name", instance.last_name)
        new_password = validated_data.pop("new_password", None)

        instance.email = email
        instance.first_name = first_name
        instance.last_name = last_name

        if new_password:
            instance.set_password(new_password)

        instance.save()

        return instance
