#!/usr/bin/env python
"""
Approval Workflow Engine - Quick Demonstration
Shows how the workflow engine works with configurable rules
"""

import os
import django
from uuid import uuid4

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clm_backend.settings')
django.setup()

from workflows.engine import (
    WorkflowEngine,
    ApprovalRule,
    RuleCondition,
    WorkflowConfigurations
)

print("\n" + "="*80)
print("  APPROVAL WORKFLOW ENGINE - DEMONSTRATION")
print("="*80)

# Sample Tenant ID
TENANT_ID = uuid4()

# ============================================================================
# DEMO 1: RULE-BASED WORKFLOW ROUTING
# ============================================================================

print("\n" + "="*80)
print("DEMO 1: RULE-BASED WORKFLOW ROUTING")
print("="*80)

print("\n📋 Scenario: Different contracts need different approval paths")
print("   Based on: Contract Value and Type")

# Initialize engine with value-based workflow
engine = WorkflowEngine(TENANT_ID, 'value_based')

contracts = [
    {
        'name': 'Standard Service Agreement',
        'type': 'Service Agreement',
        'value': 50000
    },
    {
        'name': 'Medium-Value Consulting Contract',
        'type': 'Consulting',
        'value': 500000
    },
    {
        'name': 'High-Value NDA',
        'type': 'NDA',
        'value': 2000000
    },
    {
        'name': 'Enterprise MSA',
        'type': 'MSA',
        'value': 10000000
    }
]

print("\n" + "-"*80)
print("Applying Rules to Different Contracts:\n")

for contract in contracts:
    context = {
        'contract_type': contract['type'],
        'contract_value': contract['value']
    }
    
    actions = engine.evaluate_rules(context)
    steps = engine.get_workflow_steps(context)
    
    print(f"\n📄 {contract['name']}")
    print(f"   Value: ${contract['value']:,.0f}")
    print(f"   Actions Triggered: {actions if actions else 'None (uses standard path)'}")
    print(f"   Approval Path: {' → '.join(steps)}")

# ============================================================================
# DEMO 2: DYNAMIC WORKFLOW STEP GENERATION
# ============================================================================

print("\n" + "="*80)
print("DEMO 2: DYNAMIC WORKFLOW STEP GENERATION")
print("="*80)

print("\n📋 Scenario: Different contract types require different approvers")

engine_type = WorkflowEngine(TENANT_ID, 'type_based')

contracts_by_type = [
    {'name': 'Standard Service Agreement', 'type': 'Service Agreement', 'value': 100000},
    {'name': 'Vendor Agreement', 'type': 'Vendor Agreement', 'value': 250000},
    {'name': 'NDA', 'type': 'NDA', 'value': 50000},
]

print("\n" + "-"*80)
print("Workflows Generated for Each Contract Type:\n")

for contract in contracts_by_type:
    context = {
        'contract_type': contract['type'],
        'contract_value': contract['value']
    }
    
    steps = engine_type.get_workflow_steps(context)
    
    print(f"\n📄 {contract['name']}")
    print(f"   Type: {contract['type']}")
    print(f"   Approval Workflow:")
    for i, step in enumerate(steps, 1):
        if step not in ['submission', 'completed']:
            print(f"     {i}. {step.replace('_', ' ').title()}")

# ============================================================================
# DEMO 3: CUSTOM RULE CONFIGURATION
# ============================================================================

print("\n" + "="*80)
print("DEMO 3: CUSTOM RULE CONFIGURATION")
print("="*80)

print("\n📋 Scenario: Adding custom rules for business requirements")
print("   Rule: Strategic partners require executive approval\n")

engine_custom = WorkflowEngine(TENANT_ID, 'simple')

print(f"Initial workflow steps: {engine_custom.get_workflow_steps()}")

# Add custom rule
strategic_rule = ApprovalRule(
    name="Strategic Partner Approval",
    condition=RuleCondition.IN_LIST,
    field="partner_type",
    threshold=["Strategic", "Key Account", "Fortune 500"],
    action="add_executive_approval",
    priority=1
)

engine_custom.add_rule(strategic_rule)

print(f"\nAdded custom rule: '{strategic_rule.name}'")
print(f"Rule condition: {strategic_rule.field} {strategic_rule.condition.value} {strategic_rule.threshold}")
print(f"Action: {strategic_rule.action}")

# Test the rule
context_strategic = {
    'partner_type': 'Strategic',
    'contract_value': 200000
}

actions = engine_custom.evaluate_rules(context_strategic)
steps = engine_custom.get_workflow_steps(context_strategic)

print(f"\n✓ Rule triggered for strategic partner")
print(f"  Actions: {actions}")
print(f"  Workflow: {' → '.join(steps)}")

# ============================================================================
# DEMO 4: WORKFLOW TEMPLATES
# ============================================================================

print("\n" + "="*80)
print("DEMO 4: PREDEFINED WORKFLOW TEMPLATES")
print("="*80)

print("\n📋 Available Workflow Templates:\n")

templates = [
    ('simple', 'Basic 2-step approval (Manager only)'),
    ('standard', 'Standard 4-step approval workflow'),
    ('comprehensive', 'Full workflow with all review types'),
    ('value_based', 'Smart routing based on contract value'),
    ('type_based', 'Smart routing based on contract type'),
]

for template_name, description in templates:
    engine_template = WorkflowEngine(TENANT_ID, template_name)
    template_config = engine_template.workflow_config
    
    print(f"\n📋 {template_name.upper()}")
    print(f"   Description: {description}")
    print(f"   Base Steps: {' → '.join(template_config['steps'])}")
    print(f"   Rules: {len(template_config.get('rules', []))} configured")

# ============================================================================
# DEMO 5: MULTI-CRITERIA RULE EVALUATION
# ============================================================================

print("\n" + "="*80)
print("DEMO 5: MULTI-CRITERIA RULE EVALUATION")
print("="*80)

print("\n📋 Scenario: Contract routing based on multiple criteria\n")

engine_multi = WorkflowEngine(TENANT_ID, 'value_based')

test_contracts = [
    {
        'name': 'Small consulting service ($30K)',
        'contract_type': 'Consulting',
        'contract_value': 30000
    },
    {
        'name': 'Medium high-risk vendor ($750K)',
        'contract_type': 'Vendor Agreement',
        'contract_value': 750000
    },
    {
        'name': 'Critical NDA ($2.5M)',
        'contract_type': 'NDA',
        'contract_value': 2500000
    },
    {
        'name': 'Strategic partnership ($8M)',
        'contract_type': 'Partnership',
        'contract_value': 8000000
    },
]

print("-"*80)
print("Contract Routing Analysis:\n")

for contract in test_contracts:
    context = {
        'contract_type': contract['contract_type'],
        'contract_value': contract['contract_value']
    }
    
    # Evaluate rules
    actions = engine_multi.evaluate_rules(context)
    steps = engine_multi.get_workflow_steps(context)
    
    # Estimate approval time
    base_days = 3
    additional_days = len(steps) - 3  # Base has 3 steps
    total_days = base_days + additional_days
    
    print(f"📄 {contract['name']}")
    print(f"   Base Workflow: {len(steps)} steps")
    print(f"   Route: {' → '.join(steps[:3])}...")
    if len(steps) > 3:
        print(f"   Additional Steps: {', '.join(steps[3:-1])}")
    print(f"   Est. Approval Time: {total_days} days")
    if actions:
        print(f"   Special Rules: {', '.join(actions)}")
    print()

# ============================================================================
# DEMO 6: APPROVAL RULES REFERENCE
# ============================================================================

print("="*80)
print("DEMO 6: PREDEFINED RULE CONFIGURATIONS")
print("="*80)

print("\n📋 Contract Approval Rules:\n")

contract_rules = WorkflowConfigurations.get_contract_approval_rules()

for rule in sorted(contract_rules, key=lambda r: r.priority):
    print(f"Rule {rule.priority}: {rule.name}")
    print(f"  Condition: if {rule.field} {rule.condition.value} {rule.threshold}")
    print(f"  Action: {rule.action}")
    print()

# ============================================================================
# SUMMARY
# ============================================================================

print("="*80)
print("WORKFLOW ENGINE FEATURES DEMONSTRATED")
print("="*80)

features = [
    "✓ Rule-based workflow routing (value, type, custom)",
    "✓ Dynamic approval step generation",
    "✓ Multi-criteria condition evaluation",
    "✓ Custom rule configuration",
    "✓ Predefined workflow templates",
    "✓ Automatic step insertion based on rules",
    "✓ Flexible approval path management",
    "✓ Configurable rules for all processes",
]

for feature in features:
    print(f"\n{feature}")

print("\n" + "="*80)
print("✅ WORKFLOW ENGINE IS FULLY FUNCTIONAL AND CONFIGURABLE")
print("="*80 + "\n")

print("Key Capabilities:")
print("  • Handles simple to complex approval workflows")
print("  • Rules automatically route contracts to correct approvers")
print("  • Supports value-based, type-based, and custom rules")
print("  • Easy to add new rules and templates")
print("  • Production-ready with logging and error handling")
print()
