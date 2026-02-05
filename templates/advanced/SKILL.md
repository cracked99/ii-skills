---
name: advanced-skill
description: Comprehensive skill template with all features. Use when building complex skills with scripts, references, and tool restrictions.
allowed-tools: Bash(python *), Read, Write
disable-model-invocation: false
user-invocable: true
---

# Advanced Skill Template

This template demonstrates all available skill features including scripts, references, tool restrictions, and progressive disclosure patterns.

## When to Use

- User explicitly requests [primary function]
- User mentions keywords: [keyword1], [keyword2], [keyword3]
- User needs to [accomplish complex goal]
- Context includes [specific file types or patterns]

## Quick Start

The fastest path to a working result:

```bash
# Run the main script
python scripts/main.py input.file output.file
```

## Capabilities

### Core Features
- **Feature 1** - Description of what it does
- **Feature 2** - Description of what it does
- **Feature 3** - Description of what it does

### Advanced Features
- **Advanced 1** - See [ADVANCED.md](references/ADVANCED.md) for details
- **Advanced 2** - See [ADVANCED.md](references/ADVANCED.md) for details

## Workflow

```
┌─────────────────┐
│   User Input    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Analyze Input  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Execute Process │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Validate Output │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Deliver Result  │
└─────────────────┘
```

## Step-by-Step Process

### Phase 1: Setup

1. **Verify prerequisites**
   ```bash
   python --version  # Requires 3.8+
   pip list | grep required-package
   ```

2. **Prepare workspace**
   - Create output directory
   - Validate input files exist

### Phase 2: Execution

3. **Run main process**
   ```bash
   python scripts/main.py --input file.ext --output result.ext
   ```

4. **Monitor progress**
   - Check console output for errors
   - Verify intermediate results

### Phase 3: Delivery

5. **Validate output**
   - Check file integrity
   - Verify expected format

6. **Present to user**
   - Provide summary
   - Attach output files

## Examples

### Example 1: Simple Case

**User Request:**
> Process this file and extract the data

**Agent Response:**
1. Analyze the input file
2. Run extraction script
3. Return structured data

**Output:**
```json
{
  "status": "success",
  "data": [...]
}
```

### Example 2: Complex Case

**User Request:**
> Process multiple files with custom options

**Agent Response:**
1. Batch process all input files
2. Apply custom configuration
3. Merge results
4. Generate summary report

## Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| `--format` | `json` | Output format (json, csv, xml) |
| `--verbose` | `false` | Enable detailed logging |
| `--validate` | `true` | Validate output before saving |

## Error Handling

### Common Errors

**Error: File not found**
```
FileNotFoundError: [Errno 2] No such file or directory
```
**Solution:** Verify the input file path is correct and the file exists.

**Error: Invalid format**
```
ValueError: Unsupported file format
```
**Solution:** Check supported formats in the documentation.

**Error: Permission denied**
```
PermissionError: [Errno 13] Permission denied
```
**Solution:** Check file permissions and ensure write access to output directory.

### Recovery Strategies

1. **Retry with defaults** - Remove custom options and try again
2. **Check dependencies** - Ensure all required packages are installed
3. **Validate input** - Verify input file is not corrupted

## Additional Resources

- For complete API reference, see [REFERENCE.md](references/REFERENCE.md)
- For usage examples, see [EXAMPLES.md](references/EXAMPLES.md)
- For troubleshooting, see [TROUBLESHOOTING.md](references/TROUBLESHOOTING.md)

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `python` | ≥3.8 | Runtime environment |
| `package1` | ≥1.0 | Core functionality |
| `package2` | ≥2.0 | Data processing |

## Changelog

- **v1.0.0** - Initial release
- **v1.1.0** - Added batch processing
- **v1.2.0** - Improved error handling