from rest_framework import serializers
from .models import (
    IntelligenceReport, ThreatCategory, HostileGroup,
    GeographicZone, ReportAttachment, ReportComment
)

class ThreatCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ThreatCategory
        fields = ['id', 'name', 'category_type', 'description', 'color_code', 'priority_weight']

class HostileGroupSerializer(serializers.ModelSerializer):
    threat_categories = ThreatCategorySerializer(many=True, read_only=True)
    
    class Meta:
        model = HostileGroup
        fields = [
            'id', 'name', 'aliases', 'description', 'threat_categories',
            'estimated_members', 'activity_status', 'threat_level'
        ]

class ReportAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportAttachment
        fields = ['id', 'filename', 'file_type', 'file_size', 'description', 'is_evidence']

class ReportCommentSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    
    class Meta:
        model = ReportComment
        fields = ['id', 'content', 'author_name', 'created_at', 'is_internal']

class IntelligenceReportSerializer(serializers.ModelSerializer):
    source_agent_name = serializers.CharField(source='source_agent.get_full_name', read_only=True)
    assigned_analyst_name = serializers.CharField(source='assigned_analyst.get_full_name', read_only=True)
    threat_categories = ThreatCategorySerializer(many=True, read_only=True)
    hostile_groups = HostileGroupSerializer(many=True, read_only=True)
    attachment_files = ReportAttachmentSerializer(many=True, read_only=True)
    comments = ReportCommentSerializer(many=True, read_only=True)
    
    class Meta:
        model = IntelligenceReport
        fields = [
            'id', 'title', 'description', 'report_type', 'classification_level',
            'source_agent_name', 'source_type', 'latitude', 'longitude', 'location_description',
            'threat_categories', 'hostile_groups', 'threat_level', 'confidence_level',
            'status', 'assigned_analyst_name', 'priority', 'report_date', 'created_at',
            'attachment_files', 'comments', 'tags'
        ]
        read_only_fields = ['id', 'created_at', 'source_agent_name']

class GeographicZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeographicZone
        fields = ['id', 'name', 'zone_type', 'description', 'coordinates', 'risk_level']