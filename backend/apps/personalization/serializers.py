"""
ClauseLens – Personalization serializers.
"""
from rest_framework import serializers
from .models import PersonalizedRisk


class PersonalizedRiskSerializer(serializers.ModelSerializer):
    clause_title = serializers.CharField(source='clause.clause_title', read_only=True)
    clause_category = serializers.CharField(source='clause.category', read_only=True)
    clause_severity = serializers.FloatField(source='clause.severity', read_only=True)
    document_id = serializers.IntegerField(source='clause.document_id', read_only=True)

    class Meta:
        model = PersonalizedRisk
        fields = [
            'id', 'clause', 'clause_title', 'clause_category', 'clause_severity',
            'document_id', 'relevance_score', 'risk_level', 'why_it_matters', 'created_at',
        ]
        read_only_fields = fields
