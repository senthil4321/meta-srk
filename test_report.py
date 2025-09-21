#!/usr/bin/env python3
"""
Test Report Generation Module
Provides utilities for generating formatted test reports with colored output.
"""

__version__ = "1.2.0"
__author__ = "SRK Development Team"
__copyright__ = "Copyright (c) 2025 SRK. All rights reserved."
__license__ = "MIT"

class TestReportGenerator:
    """Generates formatted test reports with colored output and statistics."""

    def __init__(self):
        # Define colored icons
        self.green_check = "\033[92m✅\033[0m"
        self.red_x = "\033[91m❌\033[0m"
        self.yellow_warn = "\033[93m⚠️\033[0m"
        self.blue_skip = "\033[94m⏭️\033[0m"

    def generate_report(self, results, non_blocking=None):
        """
        Generate a formatted test report.

        Args:
            results: List of tuples (name, passed, message)
            non_blocking: List of test names that are non-blocking (optional)

        Returns:
            str: Formatted report string
        """
        if non_blocking is None:
            non_blocking = []

        report_lines = []

        # Header
        report_lines.append("\n" + "="*80)
        report_lines.append("TEST SUMMARY")
        report_lines.append("="*80)

        # Table header
        report_lines.append(f"{'#':<3} | {'Test Name':<30} | {'Status':<20} | {'Message':<40}")
        report_lines.append("-" * 97)

        # Table rows
        counter = 1
        for name, passed, msg in results:
            status = self._get_status_icon(msg, passed, name, non_blocking)

            # Truncate name and msg if too long
            name_display = name[:28] + "..." if len(name) > 28 else name
            msg_display = msg[:38] + "..." if len(msg) > 38 else msg

            report_lines.append(f"{counter:<3} | {name_display:<30} | {status:<20} | {msg_display:<40}")
            counter += 1

        report_lines.append("-" * 97)

        # Statistics
        stats = self._calculate_statistics(results, non_blocking)
        report_lines.append(f"\nTotal: {stats['total']}, Passed: {stats['passed']}, Failed: {stats['failed']}, Warnings: {stats['warnings']}")

        return "\n".join(report_lines)

    def _get_status_icon(self, msg, passed, name, non_blocking):
        """Get the appropriate status icon for a test result."""
        if msg == "SKIPPED":
            return f"{self.blue_skip} SKIP"
        elif passed:
            return f"{self.green_check} PASS"
        else:
            if name in non_blocking:
                return f"{self.yellow_warn} NON-BLOCK FAIL"
            else:
                return f"{self.red_x} FAIL"

    def _calculate_statistics(self, results, non_blocking):
        """Calculate test statistics."""
        total = len(results)
        passed_count = sum(1 for _, p, _ in results if p)
        failed_count = sum(1 for name, p, _ in results if not p and name not in non_blocking)
        warning_count = sum(1 for name, p, _ in results if not p and name in non_blocking)

        return {
            'total': total,
            'passed': passed_count,
            'failed': failed_count,
            'warnings': warning_count
        }

    def print_report(self, results, non_blocking=None):
        """Print the report directly to stdout."""
        print(self.generate_report(results, non_blocking))

    def save_report_to_file(self, results, filename, non_blocking=None):
        """Save the report to a file."""
        report = self.generate_report(results, non_blocking)
        try:
            with open(filename, 'w') as f:
                f.write(report)
            print(f"Report saved to {filename}")
        except Exception as e:
            print(f"Failed to save report: {e}")

def create_test_report(results, non_blocking=None, save_to_file=None):
    """
    Convenience function to create and optionally save a test report.

    Args:
        results: List of tuples (name, passed, message)
        non_blocking: List of test names that are non-blocking (optional)
        save_to_file: Filename to save report to (optional)

    Returns:
        TestReportGenerator: The report generator instance
    """
    generator = TestReportGenerator()
    generator.print_report(results, non_blocking)

    if save_to_file:
        generator.save_report_to_file(results, save_to_file, non_blocking)

    return generator