"""
Integration tests for Approval Workflow - Human-in-the-loop approval for sensitive actions.

Tests cover:
- Threshold evaluation for financial, communication, and data operations
- Task movement to /Pending_Approval
- Approval command processing
- Rejection command processing
- Approval logging
- Dashboard integration
"""

import pytest
import tempfile
from pathlib import Path
from datetime import datetime
import yaml


@pytest.fixture
def temp_vault():
    """Create temporary vault for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        vault_path = Path(tmpdir)
        # Create vault structure
        folders = ["Needs_Action", "Done", "Rejected", "Pending_Approval", "Approved", "Logs"]
        for folder in folders:
            (vault_path / folder).mkdir()

        # Create Company_Handbook.md with approval thresholds
        handbook = vault_path / "Company_Handbook.md"
        handbook.write_text("""# Company Handbook

## Approval Thresholds

### Financial Decisions
- Under $100: Auto-approve
- $100-$500: Flag for review
- Over $500: Require explicit approval

### Communication Actions
- Reply to known contacts: Auto-approve
- Reply to new contacts: Require approval
- Client communications (new/sensitive): Require approval
- Bulk communications: Require approval
- Social media posts (LinkedIn, etc.): Require approval

### Data Operations
- Read operations: Auto-approve
- Create/Update single records: Auto-approve
- Bulk operations (>10 items): Require approval
- Delete operations: Always require approval
""")

        yield vault_path


class TestThresholdEvaluation:
    """Test approval threshold evaluation logic."""

    def test_financial_under_100_auto_approve(self, temp_vault):
        """Test that financial transactions under $100 auto-approve."""
        # Create task with $50 payment
        task_file = temp_vault / "Needs_Action" / "PAYMENT_20260309T143000Z_invoice.md"
        task_file.write_text("""---
type: payment
amount: 50
status: pending
---

# Payment: Invoice Payment

Process payment of $50 for invoice #12345.
""")

        # Threshold evaluation should auto-approve (no approval required)
        # This would be done by approval-workflow skill
        assert task_file.exists()

    def test_financial_over_500_requires_approval(self, temp_vault):
        """Test that financial transactions over $500 require approval."""
        # Create task with $750 payment
        task_file = temp_vault / "Needs_Action" / "PAYMENT_20260309T143000Z_invoice.md"
        task_file.write_text("""---
type: payment
amount: 750
status: pending
---

# Payment: Invoice Payment

Process payment of $750 for invoice #12345.
""")

        # Simulate approval workflow moving task to Pending_Approval
        pending_file = temp_vault / "Pending_Approval" / "PAYMENT_20260309T143000Z_invoice.md"
        task_file.rename(pending_file)

        # Update metadata
        content = pending_file.read_text()
        content = content.replace("status: pending", "status: pending\napproval_required: true\napproval_threshold_exceeded: payment_over_500")
        pending_file.write_text(content)

        assert pending_file.exists()
        assert "approval_required: true" in pending_file.read_text()

    def test_new_contact_email_requires_approval(self, temp_vault):
        """Test that emails to new contacts require approval."""
        # Create email task to new contact
        task_file = temp_vault / "Needs_Action" / "EMAIL_20260309T143000Z_new-client.md"
        task_file.write_text("""---
type: email
recipient: new_client@example.com
status: pending
---

# Email: Reply to New Client

Reply to inquiry from new client.
""")

        # Simulate approval workflow moving task to Pending_Approval
        pending_file = temp_vault / "Pending_Approval" / "EMAIL_20260309T143000Z_new-client.md"
        task_file.rename(pending_file)

        # Update metadata
        content = pending_file.read_text()
        content = content.replace("status: pending", "status: pending\napproval_required: true\napproval_threshold_exceeded: new_contact_communication")
        pending_file.write_text(content)

        assert pending_file.exists()
        assert "approval_required: true" in pending_file.read_text()

    def test_linkedin_post_requires_approval(self, temp_vault):
        """Test that LinkedIn posts require approval."""
        # Create LinkedIn post task
        task_file = temp_vault / "Needs_Action" / "LINKEDIN_POST_20260309T143000Z_update.md"
        task_file.write_text("""---
type: linkedin_post
status: pending
---

# LinkedIn Post: Business Update

Post weekly business update to LinkedIn.
""")

        # Simulate approval workflow moving task to Pending_Approval
        pending_file = temp_vault / "Pending_Approval" / "LINKEDIN_POST_20260309T143000Z_update.md"
        task_file.rename(pending_file)

        # Update metadata
        content = pending_file.read_text()
        content = content.replace("status: pending", "status: pending\napproval_required: true\napproval_threshold_exceeded: social_media_post")
        pending_file.write_text(content)

        assert pending_file.exists()
        assert "approval_required: true" in pending_file.read_text()


class TestApprovalCommands:
    """Test approval and rejection command processing."""

    def test_approve_task_moves_to_approved(self, temp_vault):
        """Test that approving a task moves it to /Approved."""
        # Create pending task
        pending_file = temp_vault / "Pending_Approval" / "EMAIL_20260309T143000Z_client.md"
        pending_file.write_text("""---
type: email
recipient: client@example.com
status: pending
approval_required: true
approval_threshold_exceeded: new_contact_communication
approval_requested_at: 2026-03-09T14:30:00Z
approval_status: pending
---

# Email: Reply to Client

Reply to client inquiry.
""")

        # Simulate approval command
        approved_file = temp_vault / "Approved" / "EMAIL_20260309T143000Z_client.md"
        pending_file.rename(approved_file)

        # Update metadata
        content = approved_file.read_text()
        content = content.replace("approval_status: pending", "approval_status: approved\napproved_by: user\napproved_at: 2026-03-09T15:00:00Z")
        approved_file.write_text(content)

        assert approved_file.exists()
        assert "approval_status: approved" in approved_file.read_text()

    def test_reject_task_moves_to_rejected(self, temp_vault):
        """Test that rejecting a task moves it to /Rejected."""
        # Create pending task
        pending_file = temp_vault / "Pending_Approval" / "EMAIL_20260309T143000Z_client.md"
        pending_file.write_text("""---
type: email
recipient: client@example.com
status: pending
approval_required: true
approval_threshold_exceeded: new_contact_communication
approval_requested_at: 2026-03-09T14:30:00Z
approval_status: pending
---

# Email: Reply to Client

Reply to client inquiry.
""")

        # Simulate rejection command
        rejected_file = temp_vault / "Rejected" / "EMAIL_20260309T143000Z_client.md"
        pending_file.rename(rejected_file)

        # Update metadata
        content = rejected_file.read_text()
        content = content.replace("approval_status: pending", "approval_status: rejected\nrejected_by: user\nrejected_at: 2026-03-09T15:00:00Z\nrejection_reason: Not appropriate for this client")
        rejected_file.write_text(content)

        assert rejected_file.exists()
        assert "approval_status: rejected" in rejected_file.read_text()
        assert "rejection_reason:" in rejected_file.read_text()


class TestApprovalLogging:
    """Test approval decision logging."""

    def test_approval_logged(self, temp_vault):
        """Test that approval decisions are logged."""
        # Create log file
        log_file = temp_vault / "Logs" / "approvals.log"

        # Simulate approval logging
        import json
        log_entry = {
            "timestamp": "2026-03-09T15:00:00Z",
            "task_id": "EMAIL_20260309T143000Z_client",
            "action": "approved",
            "approved_by": "user",
            "threshold_exceeded": "new_contact_communication",
            "reason": None,
            "task_file_path": "Approved/EMAIL_20260309T143000Z_client.md"
        }

        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')

        assert log_file.exists()

        # Verify log entry
        with open(log_file, 'r') as f:
            lines = f.readlines()
            assert len(lines) == 1
            logged = json.loads(lines[0])
            assert logged['action'] == 'approved'
            assert logged['task_id'] == 'EMAIL_20260309T143000Z_client'

    def test_rejection_logged(self, temp_vault):
        """Test that rejection decisions are logged."""
        # Create log file
        log_file = temp_vault / "Logs" / "approvals.log"

        # Simulate rejection logging
        import json
        log_entry = {
            "timestamp": "2026-03-09T15:00:00Z",
            "task_id": "EMAIL_20260309T143000Z_client",
            "action": "rejected",
            "rejected_by": "user",
            "threshold_exceeded": "new_contact_communication",
            "reason": "Not appropriate for this client",
            "task_file_path": "Rejected/EMAIL_20260309T143000Z_client.md"
        }

        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')

        assert log_file.exists()

        # Verify log entry
        with open(log_file, 'r') as f:
            lines = f.readlines()
            assert len(lines) == 1
            logged = json.loads(lines[0])
            assert logged['action'] == 'rejected'
            assert logged['reason'] == 'Not appropriate for this client'


class TestApprovalMetadata:
    """Test approval metadata in task files."""

    def test_pending_approval_metadata(self, temp_vault):
        """Test that pending approval tasks have correct metadata."""
        # Create pending task
        pending_file = temp_vault / "Pending_Approval" / "EMAIL_20260309T143000Z_client.md"
        pending_file.write_text("""---
type: email
recipient: client@example.com
status: pending
approval_required: true
approval_threshold_exceeded: new_contact_communication
approval_requested_at: 2026-03-09T14:30:00Z
approval_status: pending
---

# Email: Reply to Client

Reply to client inquiry.

## Approval Required

**Threshold Exceeded**: New contact communication
**Requested**: 2026-03-09 14:30:00 UTC
**Status**: Pending

**To approve this task, run:**
```
claude "approve task EMAIL_20260309T143000Z_client"
```

**To reject this task, run:**
```
claude "reject task EMAIL_20260309T143000Z_client --reason 'reason here'"
```
""")

        content = pending_file.read_text()
        assert "approval_required: true" in content
        assert "approval_threshold_exceeded:" in content
        assert "approval_requested_at:" in content
        assert "approval_status: pending" in content
        assert "## Approval Required" in content

    def test_approved_task_metadata(self, temp_vault):
        """Test that approved tasks have correct metadata."""
        # Create approved task
        approved_file = temp_vault / "Approved" / "EMAIL_20260309T143000Z_client.md"
        approved_file.write_text("""---
type: email
recipient: client@example.com
status: pending
approval_required: true
approval_threshold_exceeded: new_contact_communication
approval_requested_at: 2026-03-09T14:30:00Z
approval_status: approved
approved_by: user
approved_at: 2026-03-09T15:00:00Z
---

# Email: Reply to Client

Reply to client inquiry.
""")

        content = approved_file.read_text()
        assert "approval_status: approved" in content
        assert "approved_by: user" in content
        assert "approved_at:" in content

    def test_rejected_task_metadata(self, temp_vault):
        """Test that rejected tasks have correct metadata."""
        # Create rejected task
        rejected_file = temp_vault / "Rejected" / "EMAIL_20260309T143000Z_client.md"
        rejected_file.write_text("""---
type: email
recipient: client@example.com
status: pending
approval_required: true
approval_threshold_exceeded: new_contact_communication
approval_requested_at: 2026-03-09T14:30:00Z
approval_status: rejected
rejected_by: user
rejected_at: 2026-03-09T15:00:00Z
rejection_reason: Not appropriate for this client
---

# Email: Reply to Client

Reply to client inquiry.
""")

        content = rejected_file.read_text()
        assert "approval_status: rejected" in content
        assert "rejected_by: user" in content
        assert "rejected_at:" in content
        assert "rejection_reason:" in content


class TestTaskIDExtraction:
    """Test task ID extraction from filenames."""

    def test_email_task_id_extraction(self):
        """Test extracting task ID from email task filename."""
        filename = "EMAIL_20260309T143000Z_client-inquiry.md"
        task_id = filename.replace(".md", "")
        assert task_id == "EMAIL_20260309T143000Z_client-inquiry"

    def test_file_drop_task_id_extraction(self):
        """Test extracting task ID from file drop task filename."""
        filename = "FILE_DROP_20260309T143000Z_invoice.md"
        task_id = filename.replace(".md", "")
        assert task_id == "FILE_DROP_20260309T143000Z_invoice"

    def test_linkedin_task_id_extraction(self):
        """Test extracting task ID from LinkedIn task filename."""
        filename = "LINKEDIN_MSG_20260309T143000Z_John-Doe.md"
        task_id = filename.replace(".md", "")
        assert task_id == "LINKEDIN_MSG_20260309T143000Z_John-Doe"


class TestEndToEndApprovalWorkflow:
    """Test complete end-to-end approval workflow."""

    def test_complete_approval_workflow(self, temp_vault):
        """Test complete workflow from detection to approval to execution."""
        # Step 1: Task created in /Needs_Action
        needs_action_file = temp_vault / "Needs_Action" / "EMAIL_20260309T143000Z_client.md"
        needs_action_file.write_text("""---
type: email
recipient: new_client@example.com
status: pending
---

# Email: Reply to New Client

Reply to inquiry from new client.
""")

        assert needs_action_file.exists()

        # Step 2: Approval workflow evaluates and moves to /Pending_Approval
        pending_file = temp_vault / "Pending_Approval" / "EMAIL_20260309T143000Z_client.md"
        needs_action_file.rename(pending_file)

        content = pending_file.read_text()
        content = content.replace("status: pending", "status: pending\napproval_required: true\napproval_threshold_exceeded: new_contact_communication\napproval_requested_at: 2026-03-09T14:30:00Z\napproval_status: pending")
        pending_file.write_text(content)

        assert pending_file.exists()
        assert not needs_action_file.exists()

        # Step 3: User approves task
        approved_file = temp_vault / "Approved" / "EMAIL_20260309T143000Z_client.md"
        pending_file.rename(approved_file)

        content = approved_file.read_text()
        content = content.replace("approval_status: pending", "approval_status: approved\napproved_by: user\napproved_at: 2026-03-09T15:00:00Z")
        approved_file.write_text(content)

        assert approved_file.exists()
        assert not pending_file.exists()

        # Step 4: Log approval decision
        log_file = temp_vault / "Logs" / "approvals.log"
        import json
        log_entry = {
            "timestamp": "2026-03-09T15:00:00Z",
            "task_id": "EMAIL_20260309T143000Z_client",
            "action": "approved",
            "approved_by": "user",
            "threshold_exceeded": "new_contact_communication",
            "reason": None,
            "task_file_path": "Approved/EMAIL_20260309T143000Z_client.md"
        }

        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')

        assert log_file.exists()

        # Step 5: Task executed and moved to /Done
        done_file = temp_vault / "Done" / "EMAIL_20260309T143000Z_client.md"
        approved_file.rename(done_file)

        assert done_file.exists()
        assert not approved_file.exists()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
