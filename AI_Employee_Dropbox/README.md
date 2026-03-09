# AI Employee Dropbox

This is the **drop zone** for the File System Watcher.

## Purpose

Place files here that you want the AI Employee to process:
- PDFs (contracts, invoices, reports)
- Documents (DOCX, XLSX, TXT)
- Any file type you configure in `.env`

## How It Works

1. **Drop a file** into this folder
2. **File System Watcher detects it** (within 5 seconds)
3. **Task file created** in `AI_Employee_Vault/Needs_Action/`
4. **Claude processes** the task and creates a plan

## Example

```bash
# Drop a contract
cp ~/Downloads/vendor-contract.pdf ./AI_Employee_Dropbox/

# Watcher creates task file
# AI_Employee_Vault/Needs_Action/FILE_DROP_20260309_vendor-contract.md

# Process with Claude
cd AI_Employee_Vault
claude "Process new file drop task"
```

## Configuration

Set in `.env`:
```bash
WATCH_DIRECTORY=/absolute/path/to/personal-ai-employee/AI_Employee_Dropbox
FILE_EXTENSIONS=*  # Or: .pdf,.docx,.xlsx
WATCHER_TYPE=filesystem
```

## Note

This folder is monitored by the File System Watcher when `WATCHER_TYPE=filesystem` in `.env`.
