"""
ClauseLens – Analysis serializers.
"""
from rest_framework import serializers
from .models import Clause, AnalysisResult


class ClauseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clause
        fields = [
            'id', 'document', 'clause_title', 'original_text',
            'category', 'severity', 'simple_explanation', 'created_at',
        ]
        read_only_fields = fields


class AnalysisResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalysisResult
        fields = [
            'id', 'document', 'total_clauses',
            'high_risk_count', 'medium_risk_count', 'low_risk_count',
            'overall_risk_score', 'analysis_status', 'created_at',
        ]
        read_only_fields = fields


# ─── Internal / NLP callback serializers ──────────────────────────

class NLPClauseInputSerializer(serializers.Serializer):
    """Shape of a single clause as returned by the NLP service."""
    clause_title = serializers.CharField(max_length=500)
    original_text = serializers.CharField()
    category = serializers.ChoiceField(choices=[c[0] for c in Clause.Category.choices])
    severity = serializers.FloatField(min_value=0.0, max_value=1.0)
    simple_explanation = serializers.CharField()


class NLPResponseSerializer(serializers.Serializer):
    """Full response envelope expected from the NLP service."""
    document_id = serializers.IntegerField()
    total_clauses = serializers.IntegerField()
    clauses = NLPClauseInputSerializer(many=True)
