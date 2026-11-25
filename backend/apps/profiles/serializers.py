"""
ClauseLens – Profile serializers.
"""
from rest_framework import serializers
from .models import UserProfile

VALID_INTENDED_USE = {'personal', 'student', 'freelancer', 'business', 'parent_of_minor'}


class UserProfileSerializer(serializers.ModelSerializer):
    """Full serializer for creating and updating a user profile."""
    intended_use = serializers.ListField(
        child=serializers.ChoiceField(choices=list(VALID_INTENDED_USE)),
        min_length=1,
        help_text='List of intended use tags.',
    )

    class Meta:
        model = UserProfile
        fields = ['age_group', 'intended_use', 'jurisdiction', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def validate_intended_use(self, value):
        invalid = set(value) - VALID_INTENDED_USE
        if invalid:
            raise serializers.ValidationError(
                f'Invalid intended use values: {invalid}. '
                f'Valid choices are: {VALID_INTENDED_USE}'
            )
        return value

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        # Always return intended_use as a list
        rep['intended_use'] = instance.get_intended_use_list()
        return rep

    def to_internal_value(self, data):
        internal = super().to_internal_value(data)
        # Convert list → stored string
        if 'intended_use' in internal:
            internal['intended_use'] = ','.join(internal['intended_use'])
        return internal
