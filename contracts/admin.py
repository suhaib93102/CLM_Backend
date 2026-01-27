from django.contrib import admin
from . import models

# Register models only if they exist (avoids import issues)
if hasattr(models, 'ContractTemplate'):
    @admin.register(models.ContractTemplate)
    class ContractTemplateAdmin(admin.ModelAdmin):
        list_display = ('name', 'contract_type', 'version', 'status')
        list_filter = ('contract_type', 'status')
        search_fields = ('name', 'contract_type')

if hasattr(models, 'Clause'):
    @admin.register(models.Clause)
    class ClauseAdmin(admin.ModelAdmin):
        list_display = ('clause_id', 'name', 'contract_type', 'version', 'status')
        list_filter = ('contract_type', 'status', 'is_mandatory')
        search_fields = ('clause_id', 'name')

if hasattr(models, 'Contract'):
    @admin.register(models.Contract)
    class ContractAdmin(admin.ModelAdmin):
        list_display = ('title', 'contract_type', 'status')
        list_filter = ('status', 'contract_type')
        search_fields = ('title', 'contract_type')

if hasattr(models, 'BusinessRule'):
    @admin.register(models.BusinessRule)
    class BusinessRuleAdmin(admin.ModelAdmin):
        pass
    list_display = ('name', 'rule_type', 'is_active')
    list_filter = ('rule_type', 'is_active')
    search_fields = ('name', 'description')
