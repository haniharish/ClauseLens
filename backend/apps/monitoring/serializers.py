"""
ClauseLens – Monitoring serializers.
"""
from rest_framework import serializers
from .models import MonitoredPolicy, PolicyVersion, PolicyChange


class MonitoredPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = MonitoredPolicy
        fields = [
            'id', 'policy_url', 'policy_name', 'monitoring_status',
            'check_interval_hours', 'added_at', 'last_checked_at',
        ]
        read_only_fields = ['id', 'added_at', 'last_checked_at']


class PolicyVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PolicyVersion
        fields = ['id', 'document', 'version_number', 'content_hash', 'fetched_at']
        read_only_fields = fields


class PolicyChangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PolicyChange
        fields = [
            'id', 'document', 'old_clause', 'new_clause',
            'change_type', 'change_direction', 'magnitude', 'alert_score', 'detected_at',
        ]
        read_only_fields = fields


# ─── Internal – used by version_client callback ─────────────────

class VersionUpdateClauseSerializer(serializers.Serializer):
    """Shape of a single clause change in an incoming version update."""
    clause_id = serializers.IntegerField(required=False)
    new_clause_title = serializers.CharField(required=False)
    new_clause_text = serializers.CharField(required=False)
    change_type = serializers.ChoiceField(choices=[c[0] for c in PolicyChange.ChangeType.choices])
    change_direction = serializers.ChoiceField(choices=[c[0] for c in PolicyChange.ChangeDirection.choices])
    magnitude = serializers.FloatField(min_value=0.0, max_value=1.0)


class VersionUpdateSerializer(serializers.Serializer):
    """Full payload sent by the version tracking module."""
    document_id = serializers.IntegerField()
    version_number = serializers.IntegerField()
    version_text = serializers.CharField()
    content_hash = serializers.CharField(max_length=64)
    changes = VersionUpdateClauseSerializer(many=True)
