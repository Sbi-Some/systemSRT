from rest_framework import serializers
from .models import Dashboard, Widget, SystemMetric

class WidgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Widget
        fields = [
            'id', 'widget_type', 'title', 'position_x', 'position_y', 
            'width', 'height', 'config', 'is_visible'
        ]

class DashboardSerializer(serializers.ModelSerializer):
    widgets = WidgetSerializer(many=True, read_only=True)
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    
    class Meta:
        model = Dashboard
        fields = [
            'id', 'name', 'description', 'owner_name', 'is_public', 
            'layout_config', 'widgets', 'created_at', 'updated_at'
        ]
        read_only_fields = ['owner_name', 'created_at', 'updated_at']

class SystemMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemMetric
        fields = ['id', 'metric_name', 'metric_value', 'metric_unit', 'timestamp', 'metadata']