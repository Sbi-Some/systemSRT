from rest_framework import serializers
from .models import ThreatAssessment, TrendAnalysis, Alert, AlertAcknowledgment

class ThreatAssessmentSerializer(serializers.ModelSerializer):
    analyst_name = serializers.CharField(source='analyst.get_full_name', read_only=True)
    reviewed_by_name = serializers.CharField(source='reviewed_by.get_full_name', read_only=True)
    risk_score = serializers.ReadOnlyField()
    
    class Meta:
        model = ThreatAssessment
        fields = [
            'id', 'title', 'assessment_type', 'executive_summary', 'detailed_analysis',
            'key_findings', 'recommendations', 'probability_score', 'impact_score',
            'risk_score', 'analyst_name', 'reviewed_by_name', 'status',
            'classification_level', 'valid_from', 'valid_until', 'created_at'
        ]
        read_only_fields = ['risk_score', 'analyst_name', 'reviewed_by_name', 'created_at']

class TrendAnalysisSerializer(serializers.ModelSerializer):
    analyst_name = serializers.CharField(source='analyst.get_full_name', read_only=True)
    
    class Meta:
        model = TrendAnalysis
        fields = [
            'id', 'title', 'trend_type', 'description', 'date_range_start',
            'date_range_end', 'key_metrics', 'visualization_data',
            'confidence_level', 'analyst_name', 'created_at'
        ]
        read_only_fields = ['analyst_name', 'created_at']

class AlertSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    acknowledgment_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Alert
        fields = [
            'id', 'title', 'message', 'alert_level', 'alert_type',
            'is_active', 'auto_expire', 'created_by_name',
            'acknowledgment_count', 'created_at'
        ]
        read_only_fields = ['created_by_name', 'acknowledgment_count', 'created_at']
    
    def get_acknowledgment_count(self, obj):
        return obj.acknowledgments.count()

class AlertAcknowledgmentSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = AlertAcknowledgment
        fields = ['id', 'user_name', 'acknowledged_at', 'notes']
        read_only_fields = ['user_name', 'acknowledged_at']