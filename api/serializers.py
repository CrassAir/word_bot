from rest_framework import serializers


class RecursiveField(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data


# class AccountSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Account
#         # fields = '__all__'
#         fields = ('pk', 'email', 'username', 'first_name', 'last_name', 'avatar', 'date_joined', 'last_login',
#                   'position', 'group', 'is_admin', 'is_active', 'is_staff', 'is_superuser', 'can_edit_data',
#                   'change_password', 'phone_number')
#         depth = 2
