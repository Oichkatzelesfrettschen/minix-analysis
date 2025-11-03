# Claude Code MCP Integration Prompts

A collection of tested Claude Code prompts for interacting with the MINIX MCP framework.

---

## Docker MCP Prompts

### List and Inspect Containers

```
List all Docker containers and show their current status.
Show CPU and memory usage for each.
```

**Expected Output:**
- Container ID, names, images, status
- Resource usage (CPU %, memory usage)
- Port mappings, volume mounts

---

### Monitor Container Health

```
Check the health status of all MCP service containers.
Show any recent errors or warnings in logs.
Which containers are running and which are stopped?
```

**Expected Output:**
- Health status for each service
- Recent log entries for failed containers
- Recommendation for failed services

---

### Get Boot Measurement Data

```
Show me the contents of the measurements database.
How many boot logs are stored?
Which errors appear most frequently?
```

**Expected Output:**
- Database statistics
- Boot log counts by date
- Error frequency analysis
- Storage usage

---

## Docker Hub MCP Prompts

### Search MINIX Images

```
Search Docker Hub for MINIX-related images.
Show me available versions and their sizes.
Which are recommended for testing?
```

**Expected Output:**
- Image names and versions
- Image sizes and pull counts
- Recommendations by MINIX version

---

### Find Analysis Tools

```
Search for Docker images containing analysis tools.
What's available for system call tracing?
Are there pre-built MINIX analysis environments?
```

**Expected Output:**
- Available analysis tool images
- Feature comparison table
- Installation instructions

---

## GitHub MCP Prompts

### Create Boot Failure Issue

```
Create a GitHub issue for MINIX boot failure.
Title: "Boot failure: E003 CD9660 module load error"
Include:
- Error code: E003
- Boot log excerpt
- Suggested recovery steps (use RC6+ ISO)
- Assign to analysis team
```

**Expected Output:**
- Issue created with complete details
- Automatically assigned
- Link to issue page

---

### Search Issues for E006 Solutions

```
Search GitHub issues for "IRQ hook assignment" errors.
Show closed issues with solutions.
What workarounds exist for E006 network IRQ conflicts?
```

**Expected Output:**
- Related issues with solutions
- Workaround descriptions
- Links to resolved PRs

---

### Create Performance Report

```
Create a GitHub discussion about MINIX boot performance.
Title: "Performance Benchmark Results - Boot Time Analysis"
Include:
- Average boot time: 1.6 seconds
- Peak memory usage: 256 MB
- 5 samples averaged
- Recommendations for optimization
```

**Expected Output:**
- Discussion created
- Formatted with markdown
- Ready for team collaboration

---

## SQLite MCP Prompts

### Query Boot Performance Metrics

```
From the boot-profiling database, show:
1. Average boot time by MINIX version
2. Trend over last 30 days
3. Fastest and slowest boots
4. Correlation with error patterns
```

**Expected Output:**
- Performance statistics table
- Trend analysis
- Slowest boot scenarios with causes

---

### Find Error Correlations

```
Query the measurements database for error patterns.
Which errors appear together most frequently?
What's the success rate after each error type is fixed?
Show confidence levels for each correlation.
```

**Expected Output:**
- Error co-occurrence matrix
- Success rates post-fix
- Statistical significance

---

### Generate Performance Report

```
Create a comprehensive boot performance analysis:
- Weekly statistics (min, max, avg, stddev)
- Error impact on performance
- Resource utilization trends
- Export as CSV for spreadsheet analysis
```

**Expected Output:**
- Formatted report table
- CSV data
- Interpretation and insights

---

## Combined Workflow Prompts

### Complete Boot Analysis

```
I'm getting a MINIX boot failure. Here's the log:
[paste boot log]

Please:
1. Analyze the log using triage tool
2. Identify error patterns
3. Check GitHub for similar issues
4. Suggest recovery steps
5. Show boot performance metrics
6. Create an issue if appropriate
```

**Expected Output:**
- Error analysis report
- GitHub issue links
- Recovery script
- Performance comparison

---

### Performance Optimization

```
Optimize MINIX boot performance:
1. Analyze current boot metrics in database
2. Compare with other configurations
3. Identify bottlenecks
4. Search for related Docker images/tools
5. Create optimization plan
6. Generate before/after comparison
```

**Expected Output:**
- Performance analysis
- Configuration recommendations
- Step-by-step optimization guide
- Expected improvement estimates

---

### Automated Daily Report

```
Generate daily MINIX health report:
1. Check Docker service status
2. Verify database integrity
3. Summarize recent boot attempts
4. List any errors from yesterday
5. Show performance trends
6. Recommend actions if needed
7. Create GitHub issue if critical errors found
```

**Expected Output:**
- Comprehensive daily report
- Service status table
- Error summary
- Trend analysis
- Action items

---

### Error Recovery Chain

```
Recover from this MINIX boot failure:
1. Analyze the error log
2. Find recovery steps in Error Registry
3. Generate recovery script
4. Check database for similar cases
5. Show success rate of fix
6. Monitor recovery progress
7. Report results to GitHub
```

**Expected Output:**
- Error diagnosis
- Recovery script
- Expected success rate
- Monitoring checklist

---

## Advanced Prompts (Multi-Step Analysis)

### Research MINIX Architecture

```
Research MINIX 3.4 architecture:
1. Analyze source code structure (from diagrams)
2. Show system call patterns
3. Visualize process architecture
4. Compare with other OSes (from GitHub discussions)
5. Generate white paper content
6. Create publication-ready diagrams
```

**Expected Output:**
- Architecture analysis
- System call taxonomy
- Comparison tables
- LaTeX/TikZ diagrams

---

### Benchmark Suite Development

```
Develop comprehensive MINIX benchmark suite:
1. Review current benchmark results in database
2. Identify missing test cases
3. Design new benchmarks for identified gaps
4. Create benchmark scripts
5. Document expected performance ranges
6. Set up CI/CD pipeline (GitHub Actions)
7. Monitor trends over time
```

**Expected Output:**
- Benchmark design document
- Test scripts
- Expected baselines
- CI/CD configuration

---

### Build Automated Testing Pipeline

```
Create automated MINIX testing pipeline:
1. Check current boot test coverage (from CI/CD)
2. Identify untested scenarios
3. Design test cases
4. Create Docker containers for testing
5. Setup GitHub Actions workflow
6. Configure result reporting
7. Create dashboard for visualization
```

**Expected Output:**
- Test plan document
- Docker configurations
- GitHub Actions workflow
- Dashboard setup instructions

---

## Prompt Templates

### Template 1: Error Analysis

```
Analyze this MINIX error:
[paste error details]

Provide:
1. Error classification (E001-E015)
2. Severity assessment
3. Root cause analysis
4. Recovery recommendations
5. Success rate from historical data
6. Similar cases from GitHub
```

---

### Template 2: Performance Analysis

```
Analyze MINIX boot performance:
[paste boot log or metrics]

Show:
1. Execution timeline
2. Performance bottlenecks
3. Resource usage patterns
4. Comparison with baseline
5. Optimization opportunities
6. Implementation difficulty
```

---

### Template 3: Troubleshooting

```
Troubleshoot MINIX boot issue:
[describe problem]

Follow this process:
1. Check system health (health-check.sh)
2. Analyze boot logs (triage tool)
3. Search GitHub for similar issues
4. Review error registry
5. Generate recovery script
6. Test recovery steps
7. Document results
```

---

## Best Practices for MCP Prompts

### 1. Be Specific
- Name the error code (E001, E003, etc.)
- Provide boot log excerpts
- Include system configuration details

### 2. Ask for Structured Output
```
Provide results as:
- A markdown table
- A JSON report
- A step-by-step script
- A CSV for data analysis
```

### 3. Request Sources
```
Show your work:
- Database query used
- GitHub issues referenced
- Error registry entries matched
- Confidence level for each finding
```

### 4. Enable Automation
```
Make results actionable:
- Generate shell scripts
- Create GitHub issues
- Provide CSV exports
- Create configuration files
```

### 5. Build on Previous Results
```
Reference earlier analysis:
- Use previous boot log analysis
- Reference historical performance data
- Build on earlier GitHub issues
- Continue optimization from last report
```

---

## Common Queries Quick Reference

| Goal | Prompt |
|------|--------|
| Boot Status | "Check Docker status of all MINIX services" |
| Error Help | "Analyze this boot error: [log excerpt]" |
| Performance | "Show boot metrics from last week" |
| Recovery | "How do I fix E003 CD9660 error?" |
| Diagnostics | "What's the health status of the system?" |
| History | "Show me similar boot failures from GitHub" |
| Optimization | "What's slowing down my MINIX boot?" |
| Reporting | "Generate a daily status report" |
| Automation | "Create a recovery script for E006" |
| Research | "Compare MINIX boot with other OSes" |

---

## Tips for Best Results

### Structure Your Prompts
1. **Context:** What you're working on
2. **Problem:** What's not working
3. **Data:** Boot logs, metrics, or errors
4. **Request:** What you want to know
5. **Format:** How you want results

### Example Well-Structured Prompt

```
Context: Testing MINIX 3.4 boot via QEMU
Problem: Boot hangs at module loading
Data: [paste boot log]
Request: 
  1. Identify the error pattern
  2. Find recovery steps
  3. Show success rate
Format: Markdown report with recovery script
```

### Avoid These Common Issues
- Don't paste entire logs (excerpt relevant lines)
- Do specify MINIX version (3.3 vs 3.4)
- Do include QEMU parameters used
- Don't assume MCP has context from previous session
- Do ask for confidence scores on detections

---

## Integration with Workflows

### Daily Routine
```
1. Morning: "Generate today's health report"
2. During: "Analyze any boot failures encountered"
3. Evening: "Summary of boot metrics for the day"
4. Weekly: "Performance trends and recommendations"
```

### Research Workflow
```
1. "Analyze architecture from source code"
2. "Search GitHub for related research"
3. "Compare performance benchmarks"
4. "Generate publication-ready diagrams"
5. "Create white paper outline"
```

### Debugging Workflow
```
1. "Boot MINIX and capture log"
2. "Analyze log for errors"
3. "Find recovery steps"
4. "Generate recovery script"
5. "Test and monitor recovery"
6. "Report results"
```

---

## Examples by Use Case

### New User Setup
- "What's the quickest way to start using this?"
- "Show me example boot logs"
- "How do I interpret boot errors?"
- "What's the recommended QEMU configuration?"

### Daily Testing
- "Boot MINIX and save the log"
- "Analyze today's boot results"
- "Compare performance to baseline"
- "Report any anomalies"

### Research & Publication
- "Generate MINIX architecture diagrams"
- "Create performance comparison charts"
- "Build statistical analysis of boot times"
- "Help write paper methodology section"

### Troubleshooting
- "My boot is failing"
- "Performance has degraded"
- "Errors increased in frequency"
- "Need diagnostic recommendations"

