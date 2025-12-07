#!/usr/bin/env python3
"""
Comprehensive testing suite for CT-1166 workflows and composite actions.
Tests all components without relying on GitHub Actions runtime.
"""

import os
import sys
import json
import yaml
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class TestResult(Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    WARN = "WARN"
    SKIP = "SKIP"


@dataclass
class ComponentTest:
    name: str
    category: str
    description: str
    filepath: Optional[str] = None
    result: TestResult = TestResult.SKIP
    details: List[str] = None
    errors: List[str] = None

    def __post_init__(self):
        if self.details is None:
            self.details = []
        if self.errors is None:
            self.errors = []


class WorkflowValidator:
    """Validates GitHub Actions workflows."""

    def __init__(self, repo_root: str):
        self.repo_root = Path(repo_root)
        self.workflows_dir = self.repo_root / ".github" / "workflows"
        self.actions_dir = self.repo_root / ".github" / "actions"
        self.tests = []

    def validate_yaml_syntax(self, filepath: Path) -> Tuple[bool, Optional[str]]:
        """Validate YAML file syntax."""
        try:
            with open(filepath, 'r') as f:
                yaml.safe_load(f)
            return True, None
        except yaml.YAMLError as e:
            return False, str(e)
        except Exception as e:
            return False, str(e)

    def validate_workflow_yaml(self, filepath: Path) -> ComponentTest:
        """Validate workflow YAML structure and content."""
        test = ComponentTest(
            name=filepath.stem,
            category="YAML Validation",
            description=f"Validate {filepath.name} YAML syntax",
            filepath=str(filepath)
        )

        # Check syntax
        is_valid, error = self.validate_yaml_syntax(filepath)
        if not is_valid:
            test.result = TestResult.FAIL
            test.errors.append(f"YAML Syntax Error: {error}")
            return test

        test.details.append("YAML syntax valid")

        # Parse and validate structure
        try:
            with open(filepath, 'r') as f:
                workflow = yaml.safe_load(f)

            # Check required fields
            if not workflow.get('name'):
                test.errors.append("Missing 'name' field")
            else:
                test.details.append(f"Name: {workflow['name']}")

            # Check for 'on' trigger - YAML parses 'on:' as True
            # Check both 'on' and True (YAML parses 'on' as boolean True)
            has_trigger = 'on' in workflow or True in workflow
            if not has_trigger:
                test.errors.append("Missing 'on' trigger")
            else:
                # Handle both cases: 'on' key or True (YAML boolean)
                on_config = workflow.get('on') or workflow.get(True)
                if isinstance(on_config, dict):
                    triggers = ', '.join(on_config.keys())
                    test.details.append(f"Triggers: {triggers}")
                    if 'workflow_call' in on_config:
                        test.details.append("✓ Callable workflow (workflow_call)")
                elif on_config is True or on_config is None:
                    test.details.append("✓ Trigger configured (on:)")
                else:
                    test.details.append(f"Trigger: {on_config}")

            if 'jobs' not in workflow:
                test.errors.append("Missing 'jobs' section")
            else:
                test.details.append(f"Jobs: {', '.join(workflow['jobs'].keys())}")

            test.result = TestResult.PASS if not test.errors else TestResult.FAIL

        except Exception as e:
            test.result = TestResult.FAIL
            test.errors.append(f"Parsing Error: {str(e)}")

        return test

    def validate_composite_action(self, filepath: Path) -> ComponentTest:
        """Validate composite action structure."""
        test = ComponentTest(
            name=filepath.parent.name,
            category="Composite Actions",
            description=f"Validate {filepath.parent.name} action",
            filepath=str(filepath)
        )

        # Check syntax
        is_valid, error = self.validate_yaml_syntax(filepath)
        if not is_valid:
            test.result = TestResult.FAIL
            test.errors.append(f"YAML Syntax Error: {error}")
            return test

        test.details.append("YAML syntax valid")

        try:
            with open(filepath, 'r') as f:
                action = yaml.safe_load(f)

            # Check required fields
            if not action.get('name'):
                test.errors.append("Missing 'name' field")
            else:
                test.details.append(f"Name: {action['name']}")

            if not action.get('description'):
                test.errors.append("Missing 'description' field")
            else:
                test.details.append(f"Description: {action['description']}")

            if action.get('runs', {}).get('using') != 'composite':
                test.errors.append("Not a composite action")
            else:
                test.details.append("✓ Composite action")

            # Check for inputs/outputs
            if 'inputs' in action:
                test.details.append(f"Inputs: {', '.join(action['inputs'].keys())}")

            if 'outputs' in action:
                test.details.append(f"Outputs: {', '.join(action['outputs'].keys())}")

            test.result = TestResult.PASS if not test.errors else TestResult.FAIL

        except Exception as e:
            test.result = TestResult.FAIL
            test.errors.append(f"Parsing Error: {str(e)}")

        return test

    def validate_permissions(self, filepath: Path) -> ComponentTest:
        """Validate permissions configuration."""
        test = ComponentTest(
            name=f"{filepath.stem} (Permissions)",
            category="Security",
            description=f"Validate permissions in {filepath.name}",
            filepath=str(filepath)
        )

        try:
            with open(filepath, 'r') as f:
                content = f.read()
                workflow = yaml.safe_load(content)

            permissions = workflow.get('permissions', {})

            if not permissions:
                test.details.append("No explicit permissions block")
            else:
                test.details.append(f"Permissions: {permissions}")

            # Check for overly permissive settings
            if permissions.get('contents') == 'write' and 'pull_request' not in str(workflow.get('on', {})):
                test.details.append("Note: contents: write configured")

            if permissions.get('write-all') or permissions.get('write_all'):
                test.errors.append("Overly permissive 'write-all' setting found")

            test.result = TestResult.PASS if not test.errors else TestResult.FAIL

        except Exception as e:
            test.result = TestResult.FAIL
            test.errors.append(f"Error: {str(e)}")

        return test

    def validate_secrets(self, filepath: Path) -> ComponentTest:
        """Validate secret handling."""
        test = ComponentTest(
            name=f"{filepath.stem} (Secrets)",
            category="Security",
            description=f"Validate secret usage in {filepath.name}",
            filepath=str(filepath)
        )

        try:
            with open(filepath, 'r') as f:
                content = f.read()

            # Check for secret declarations
            if 'secrets:' in content:
                # Extract secret names
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if 'secrets:' in line and (i == 0 or lines[i-1].strip().endswith(':')):
                        secrets = []
                        j = i + 1
                        while j < len(lines) and lines[j].startswith('  ') and not lines[j].strip().startswith('#'):
                            if ':' in lines[j] and not lines[j].strip().startswith('-'):
                                secret_name = lines[j].split(':')[0].strip()
                                secrets.append(secret_name)
                            j += 1
                        if secrets:
                            test.details.append(f"Declared secrets: {', '.join(secrets)}")

            # Check for hardcoded credentials
            hardcoded_patterns = ['password=', 'api_key=', 'apikey=', 'token=']
            for pattern in hardcoded_patterns:
                if pattern in content.lower() and 'secrets' not in content.split(pattern)[0][-50:]:
                    test.errors.append(f"Potential hardcoded credential: {pattern}")

            test.result = TestResult.PASS if not test.errors else TestResult.FAIL

        except Exception as e:
            test.result = TestResult.FAIL
            test.errors.append(f"Error: {str(e)}")

        return test

    def validate_actions_references(self, filepath: Path) -> ComponentTest:
        """Validate action references."""
        test = ComponentTest(
            name=f"{filepath.stem} (Actions)",
            category="Integration",
            description=f"Validate action references in {filepath.name}",
            filepath=str(filepath)
        )

        try:
            with open(filepath, 'r') as f:
                content = f.read()

            actions_found = []
            lines = content.split('\n')
            for line in lines:
                if 'uses:' in line:
                    uses_value = line.split('uses:')[1].strip()
                    actions_found.append(uses_value)

            if actions_found:
                test.details.append(f"Actions referenced: {len(actions_found)}")
                for action in actions_found:
                    test.details.append(f"  - {action}")

            test.result = TestResult.PASS

        except Exception as e:
            test.result = TestResult.FAIL
            test.errors.append(f"Error: {str(e)}")

        return test

    def validate_callable_interface(self, filepath: Path) -> ComponentTest:
        """Validate workflow callable interface."""
        test = ComponentTest(
            name=f"{filepath.stem} (Interface)",
            category="Workflow Structure",
            description=f"Validate callable interface in {filepath.name}",
            filepath=str(filepath)
        )

        try:
            with open(filepath, 'r') as f:
                workflow = yaml.safe_load(f)

            # Handle YAML parsing of 'on' keyword (becomes True in dict)
            on_config = workflow.get('on') or workflow.get(True, {})

            if isinstance(on_config, dict) and 'workflow_call' in on_config:
                test.details.append("✓ Workflow is callable")

                workflow_call = on_config['workflow_call']

                if workflow_call is not None and isinstance(workflow_call, dict):
                    # Check inputs
                    if 'inputs' in workflow_call and workflow_call['inputs']:
                        inputs = workflow_call['inputs']
                        test.details.append(f"Inputs ({len(inputs)}): {', '.join(inputs.keys())}")
                    else:
                        test.details.append("Inputs: (none)")

                    # Check secrets
                    if 'secrets' in workflow_call and workflow_call['secrets']:
                        secrets = workflow_call['secrets']
                        test.details.append(f"Secrets ({len(secrets)}): {', '.join(secrets.keys())}")
                    else:
                        test.details.append("Secrets: (none)")
                else:
                    test.details.append("Workflow is callable (empty workflow_call)")

            elif isinstance(on_config, dict):
                test.details.append("Workflow is NOT callable (no workflow_call)")
            else:
                test.details.append("Workflow trigger configuration present")

            test.result = TestResult.PASS

        except Exception as e:
            test.result = TestResult.FAIL
            test.errors.append(f"Error: {str(e)}")

        return test

    def run_all_tests(self) -> List[ComponentTest]:
        """Run all validation tests."""
        all_tests = []

        # Find all YAML files
        yaml_files = []
        for root, dirs, files in os.walk(str(self.repo_root / ".github")):
            for file in files:
                if file.endswith(('.yml', '.yaml')):
                    yaml_files.append(Path(root) / file)

        yaml_files.sort()

        print("=" * 80)
        print("CT-1166 Comprehensive Testing Suite")
        print("=" * 80)
        print(f"\nScanning {len(yaml_files)} YAML files...\n")

        # Test each file
        for filepath in yaml_files:
            rel_path = filepath.relative_to(self.repo_root)

            # Determine file type and run appropriate tests
            if '/actions/' in str(filepath) and 'action.yml' in str(filepath):
                # Composite action
                all_tests.append(self.validate_composite_action(filepath))
            else:
                # Workflow file
                all_tests.append(self.validate_workflow_yaml(filepath))

            # Run additional validation tests
            all_tests.append(self.validate_permissions(filepath))
            all_tests.append(self.validate_secrets(filepath))
            all_tests.append(self.validate_actions_references(filepath))

            if 'workflow_call' in open(filepath).read():
                all_tests.append(self.validate_callable_interface(filepath))

        return all_tests

    def print_report(self, tests: List[ComponentTest]):
        """Print formatted test report."""
        print("\n" + "=" * 80)
        print("Test Results")
        print("=" * 80 + "\n")

        # Group by category
        by_category = {}
        for test in tests:
            if test.category not in by_category:
                by_category[test.category] = []
            by_category[test.category].append(test)

        # Print by category
        total_pass = 0
        total_fail = 0
        total_warn = 0

        for category in sorted(by_category.keys()):
            tests_in_cat = by_category[category]
            print(f"\n{category}:")
            print("-" * 80)

            for test in tests_in_cat:
                status_icon = {
                    TestResult.PASS: "✓",
                    TestResult.FAIL: "✗",
                    TestResult.WARN: "⚠",
                    TestResult.SKIP: "○"
                }[test.result]

                print(f"{status_icon} {test.name}: {test.result.value}")
                print(f"  Description: {test.description}")

                if test.details:
                    for detail in test.details:
                        print(f"  - {detail}")

                if test.errors:
                    for error in test.errors:
                        print(f"  ERROR: {error}")

                if test.result == TestResult.PASS:
                    total_pass += 1
                elif test.result == TestResult.FAIL:
                    total_fail += 1
                elif test.result == TestResult.WARN:
                    total_warn += 1

        # Summary
        print("\n" + "=" * 80)
        print("Summary")
        print("=" * 80)
        print(f"Total Tests: {len(tests)}")
        print(f"  Passed:  {total_pass}")
        print(f"  Failed:  {total_fail}")
        print(f"  Warned:  {total_warn}")
        print(f"  Skipped: {len(tests) - total_pass - total_fail - total_warn}")

        # Overall status
        if total_fail == 0:
            print("\n✓ All tests PASSED!")
            return 0
        else:
            print(f"\n✗ {total_fail} test(s) FAILED!")
            return 1


def main():
    repo_root = os.getcwd()

    validator = WorkflowValidator(repo_root)
    tests = validator.run_all_tests()
    exit_code = validator.print_report(tests)

    return exit_code


if __name__ == '__main__':
    sys.exit(main())
