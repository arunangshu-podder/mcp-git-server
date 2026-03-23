# MCP Git Server — Copilot Prompt Instructions

A collection of ready-to-use prompts for common git workflows using the MCP Git Server.
Before running a prompt, replace all placeholder values (marked with `< >`) with your actual values.

---

## Useful Prompts

---

## Prompt 1 — Push Latest Code to Remote

```
Using the git MCP server, perform the following steps in order:

Variables (replace before running):
- BRANCH_NAME   : <enter-branch-name>
- FILES_TO_STAGE: <file1.ext, file2.ext, file3.ext>
- COMMIT_MESSAGE: <enter-commit-message>

Steps:
1. Stash the current working changes.
2. Pull the latest code from the remote branch BRANCH_NAME.
3. Apply the stashed changes back onto the working tree.
4. Stage only the following files: FILES_TO_STAGE
5. Commit the staged changes with the message: COMMIT_MESSAGE
6. Push the committed changes to the remote branch BRANCH_NAME.
7. If the push is rejected because the local branch is behind the remote,
   perform a git pull with rebase on BRANCH_NAME, then retry the push.

Constraints:
- Use only the tools available in the MCP git server. Do not invoke any terminal commands.
- If a required git operation has no corresponding MCP tool, notify me immediately and stop — do not proceed with that step.
- Do not hallucinate commands or invent tool calls that do not exist.
```

---

## Prompt 2 — Checkout to New Feature Branch

```
Using the git MCP server, perform the following steps in order:

Variables (replace before running):
- BRANCH_NAME: <enter-new-branch-name>

Steps:
1. Fetch the remote branch BRANCH_NAME to make it available locally.
2. Checkout to the local branch BRANCH_NAME.

Constraints:
- Use only the tools available in the MCP git server. Do not invoke any terminal commands.
- If a required git operation has no corresponding MCP tool, notify me immediately and stop — do not proceed with that step.
- Do not hallucinate commands or invent tool calls that do not exist.
```

---

---

## Simple Prompts

---

## Prompt 3 — Check Repository Status

```
Using the git MCP server, perform the following steps in order:

Variables (replace before running):
- REPO_PATH: <absolute-path-to-local-repo>

Steps:
1. Get the current status of the repository at REPO_PATH, showing staged,
   unstaged, and untracked files.
2. Show the current active branch name.
3. Show the last 10 commits on this branch.

Constraints:
- Use only the tools available in the MCP git server. Do not invoke any terminal commands.
- If a required git operation has no corresponding MCP tool, notify me immediately and stop — do not proceed with that step.
- Do not hallucinate commands or invent tool calls that do not exist.
```

---

## Prompt 4 — Discard Local Changes to Specific Files

```
Using the git MCP server, perform the following steps in order:

Variables (replace before running):
- REPO_PATH        : <absolute-path-to-local-repo>
- FILES_TO_DISCARD : <file1.ext, file2.ext>

Steps:
1. Get the current status of the repository so I can confirm the files
   listed below have local changes before discarding.
2. Restore FILES_TO_DISCARD in the working tree to their last committed state,
   discarding all unstaged changes to those files.

Constraints:
- Only discard changes to the specific FILES_TO_DISCARD listed — do not touch any other files.
- Use only the tools available in the MCP git server. Do not invoke any terminal commands.
- If a required git operation has no corresponding MCP tool, notify me immediately and stop — do not proceed with that step.
- Do not hallucinate commands or invent tool calls that do not exist.
```

---

## Prompt 5 — Create and Switch to a New Local Branch

```
Using the git MCP server, perform the following steps in order:

Variables (replace before running):
- REPO_PATH  : <absolute-path-to-local-repo>
- BRANCH_NAME: <new-branch-name>

Steps:
1. Check the current status of the repository to ensure there are no
   uncommitted changes that could interfere.
2. Create a new local branch named BRANCH_NAME and switch to it immediately.
3. Confirm the active branch is now BRANCH_NAME.

Constraints:
- Use only the tools available in the MCP git server. Do not invoke any terminal commands.
- If a required git operation has no corresponding MCP tool, notify me immediately and stop — do not proceed with that step.
- Do not hallucinate commands or invent tool calls that do not exist.
```

---

## Prompt 6 — Unstage Files (Keep Changes in Working Tree)

```
Using the git MCP server, perform the following steps in order:

Variables (replace before running):
- REPO_PATH        : <absolute-path-to-local-repo>
- FILES_TO_UNSTAGE : <file1.ext, file2.ext>

Steps:
1. Get the current status of the repository to confirm FILES_TO_UNSTAGE
   are currently staged.
2. Unstage FILES_TO_UNSTAGE using a mixed reset, so their changes are
   preserved in the working tree but removed from the staging area.
3. Get the status again to confirm the files are now unstaged.

Constraints:
- Use only the tools available in the MCP git server. Do not invoke any terminal commands.
- If a required git operation has no corresponding MCP tool, notify me immediately and stop — do not proceed with that step.
- Do not hallucinate commands or invent tool calls that do not exist.
```

---

## Prompt 7 — Clone a Repository

```
Using the git MCP server, perform the following steps in order:

Variables (replace before running):
- REPO_URL  : <https://github.com/owner/repo.git>
- DEST_PATH : <absolute-path-to-destination-folder>

Steps:
1. Clone the repository at REPO_URL into the directory DEST_PATH.
2. Once cloned, show the current status and active branch of the
   newly cloned repository to confirm it is ready.

Constraints:
- Use only the tools available in the MCP git server. Do not invoke any terminal commands.
- If a required git operation has no corresponding MCP tool, notify me immediately and stop — do not proceed with that step.
- Do not hallucinate commands or invent tool calls that do not exist.
```

---

## Prompt 8 — Save and Clear Work in Progress (Stash)

```
Using the git MCP server, perform the following steps in order:

Variables (replace before running):
- REPO_PATH    : <absolute-path-to-local-repo>
- STASH_MESSAGE: <describe-what-you-are-stashing>

Steps:
1. Show the current repository status so I can see what will be stashed.
2. Stash all current working changes with the description STASH_MESSAGE.
3. Show the stash list to confirm the stash was created successfully.
4. Show the repository status again to confirm the working tree is clean.

Constraints:
- Use only the tools available in the MCP git server. Do not invoke any terminal commands.
- If a required git operation has no corresponding MCP tool, notify me immediately and stop — do not proceed with that step.
- Do not hallucinate commands or invent tool calls that do not exist.
```

---

---

## Complex Prompts

---

## Prompt 9 — Merge Feature Branch into Main with Conflict Handling

```
Using the git MCP server, perform the following steps in order:

Variables (replace before running):
- REPO_PATH     : <absolute-path-to-local-repo>
- TARGET_BRANCH : <main or develop>
- FEATURE_BRANCH: <feature-branch-name>
- COMMIT_MESSAGE: <e.g. "Merge feature-x into main">

Steps:
1. Check the current status of the repository — abort if there are any
   uncommitted changes.
2. Checkout TARGET_BRANCH.
3. Pull the latest changes from the remote TARGET_BRANCH to ensure it is
   up to date.
4. Merge FEATURE_BRANCH into TARGET_BRANCH using a no-fast-forward merge.
5. Check the conflict status of the repository after the merge.
6. If conflicts are detected:
   a. List all conflicting files.
   b. Show the conflict markers for each conflicting file one by one.
   c. Pause and ask me what resolution to apply for each file before continuing.
   d. Once I confirm all conflicts are resolved and the files are staged,
      continue the merge with the commit message COMMIT_MESSAGE.
7. If no conflicts are detected, the merge commit is created automatically —
   confirm success and show the latest log entry.

Constraints:
- Do NOT push to remote automatically — stop after a successful local merge.
- Use only the tools available in the MCP git server. Do not invoke any terminal commands.
- If a required git operation has no corresponding MCP tool, notify me immediately and stop — do not proceed with that step.
- Do not hallucinate commands or invent tool calls that do not exist.
```

---

## Prompt 10 — Undo Last Commit (Keep Changes Staged)

```
Using the git MCP server, perform the following steps in order:

Variables (replace before running):
- REPO_PATH: <absolute-path-to-local-repo>

Steps:
1. Show the last 5 commits on the current branch so I can confirm which
   commit will be undone.
2. Undo the most recent commit using a soft reset, so the changes from
   that commit remain staged and ready to re-commit.
3. Show the repository status to confirm the changes are now staged.

Constraints:
- Use a SOFT reset only — do not discard any changes.
- Use only the tools available in the MCP git server. Do not invoke any terminal commands.
- If a required git operation has no corresponding MCP tool, notify me immediately and stop — do not proceed with that step.
- Do not hallucinate commands or invent tool calls that do not exist.
```

---

## Prompt 11 — Reset Branch to a Specific Commit (Hard Reset)

```
Using the git MCP server, perform the following steps in order:

Variables (replace before running):
- REPO_PATH  : <absolute-path-to-local-repo>
- COMMIT_HASH: <full-or-short-commit-hash-to-reset-to>

Steps:
1. Show the last 20 commits on the current branch so I can verify
   COMMIT_HASH exists in the history.
2. Show the current repository status — if there are any uncommitted
   changes, stash them first and notify me before proceeding.
3. Perform a hard reset to COMMIT_HASH, discarding all commits and
   changes after that point.
4. Show the repository status and the last 5 commits to confirm the
   reset was applied correctly.

Constraints:
- This is destructive — confirm the target COMMIT_HASH with me before
  executing the hard reset.
- Use only the tools available in the MCP git server. Do not invoke any terminal commands.
- If a required git operation has no corresponding MCP tool, notify me immediately and stop — do not proceed with that step.
- Do not hallucinate commands or invent tool calls that do not exist.
```

---

## Prompt 12 — Sync Feature Branch with Upstream

```
Using the git MCP server, perform the following steps in order:

Variables (replace before running):
- REPO_PATH      : <absolute-path-to-local-repo>
- UPSTREAM_BRANCH: <main or master>
- MY_BRANCH      : <your-current-feature-branch>

Steps:
1. Check the current status of the repository — stash any uncommitted
   changes and notify me if stashing was necessary.
2. Fetch the latest changes from the remote for UPSTREAM_BRANCH.
3. Checkout UPSTREAM_BRANCH locally.
4. Pull the latest changes on UPSTREAM_BRANCH.
5. Checkout back to MY_BRANCH.
6. Merge UPSTREAM_BRANCH into MY_BRANCH to bring it up to date.
7. If merge conflicts arise:
   a. Show the conflict status and list all conflicting files.
   b. Show the conflict markers for each file.
   c. Pause and ask me to resolve each conflict before continuing.
   d. After I confirm resolution, continue the merge.
8. If a stash was created in step 1, pop it back onto the working tree.
9. Show the final repository status and last 5 commits to confirm success.

Constraints:
- Do NOT push to remote automatically — stop after a successful local sync.
- Use only the tools available in the MCP git server. Do not invoke any terminal commands.
- If a required git operation has no corresponding MCP tool, notify me immediately and stop — do not proceed with that step.
- Do not hallucinate commands or invent tool calls that do not exist.
```

---

## Prompt 13 — Full Conflict Resolution Walkthrough

```
Using the git MCP server, perform the following steps in order:

Variables (replace before running):
- REPO_PATH: <absolute-path-to-local-repo>

Steps:
1. Check the conflict status of the repository to determine what type of
   operation is in progress (merge, rebase, or cherry-pick) and list all
   conflicting files.
2. For each conflicting file:
   a. Show the raw conflict markers in the file.
   b. Show the diff for that file.
   c. Pause and ask me which version to keep or how to resolve it.
3. Once I confirm all files are resolved and manually edited:
   a. Stage all the resolved files.
   b. If the operation in progress is a merge, continue the merge with an
      appropriate commit message.
   c. If the operation in progress is a rebase, continue the rebase.
4. Show the final log to confirm the operation completed successfully.

Fallback:
- If at any point I decide not to proceed, abort the in-progress merge or
  rebase cleanly so the repository returns to a stable state.

Constraints:
- Never auto-resolve conflicts — always ask me for each conflicting file.
- Use only the tools available in the MCP git server. Do not invoke any terminal commands.
- If a required git operation has no corresponding MCP tool, notify me immediately and stop — do not proceed with that step.
- Do not hallucinate commands or invent tool calls that do not exist.
```

---

## Prompt 14 — Configure Git Identity for a Repository

```
Using the git MCP server, perform the following steps in order:

Variables (replace before running):
- REPO_PATH : <absolute-path-to-local-repo>
- USER_NAME : <Your Full Name>
- USER_EMAIL: <your@email.com>
- SCOPE     : <local or global>

Steps:
1. Read the current git config for user.name and user.email at the SCOPE
   level to see what is currently set.
2. Set user.name to USER_NAME at the SCOPE level.
3. Set user.email to USER_EMAIL at the SCOPE level.
4. Read back user.name and user.email to confirm the values were applied
   correctly.

Constraints:
- Use only the tools available in the MCP git server. Do not invoke any terminal commands.
- If a required git operation has no corresponding MCP tool, notify me immediately and stop — do not proceed with that step.
- Do not hallucinate commands or invent tool calls that do not exist.
```

---

---

## Code Review Prompts

---

## Prompt 15 — Automated Code Review for a Commit

```
You are a code review assistant. Your task is to review a git commit and provide
detailed feedback on code quality, best practices, and potential improvements.

I have a file called Code_Review_Instructions.md in the repository that contains
a comprehensive code review guide with best coding practices and standards.

Variables (replace before running):
- REPO_PATH : <absolute-path-to-local-repo>
- COMMIT_SHA: <full-commit-sha-to-review>

Steps:
1. Read the Code_Review_Instructions.md file to understand the coding standards
   and best practices that code should adhere to.
2. Retrieve the full commit details and changes using the commit SHA COMMIT_SHA.
3. Analyze the commit to identify:
   a. What files were changed and how many lines were added/removed
   b. The commit message and metadata (author, date)
   c. All changes made in the diff
4. Compare the changes against all the best practices in Code_Review_Instructions.md.
5. For each category in the checklist (Project Structure, Cucumber/BDD, POM, etc.),
   identify if the code adheres to or violates the practices.
6. Provide a structured code review report with:
   a. Summary of changes
   b. Checklist violations or concerns (organized by category)
   c. Specific suggestions for improvement with line references where applicable
   d. Positive aspects: any practices that were followed well
7. Once the review is complete, ask me if I would like to export the review report
   to a PDF file.
8. If I confirm YES, export the report to REPO_PATH/code-review-COMMIT_SHA.pdf
   with an appropriate title.
9. If I confirm NO, skip the PDF export.

Constraints:
- Base your review strictly on Code_Review_Instructions.md — do not invent rules.
- Use only the tools available in the MCP git server. Do not invoke any terminal commands.
- If a required git operation has no corresponding MCP tool, notify me immediately and stop — do not proceed with that step.
- Do not hallucinate commands or invent tool calls that do not exist.
```

---

## Prompt 16 — Compare Two Commits for Code Quality Changes

```
Using the git MCP server, perform the following steps in order:

Variables (replace before running):
- REPO_PATH     : <absolute-path-to-local-repo>
- OLDER_COMMIT  : <older-commit-sha>
- NEWER_COMMIT  : <newer-commit-sha>
- CODE_REVIEW_GUIDE: Code_Review_Instructions.md

Steps:
1. Read Code_Review_Instructions.md to understand the coding standards.
2. Retrieve the diff between OLDER_COMMIT and NEWER_COMMIT to see what changed
   between these two commits.
3. Analyze the delta to understand:
   a. Which files were modified, added, or removed
   b. What specific lines of code changed
   c. Whether improvements or regressions were introduced
4. Check both the old version and new version of key modified files to compare
   side-by-side quality improvements.
5. Generate a comparative analysis report:
   a. Files that improved in code quality
   b. Files that may have regressed
   c. Adherence to Code_Review_Instructions.md practices in the changes
   d. Overall assessment of whether this is a forward step in code quality
6. Once the analysis is complete, ask me if I would like to export the comparison
   report to a PDF file.
7. If I confirm YES, export the report to REPO_PATH/comparison-OLDER_COMMIT-to-NEWER_COMMIT.pdf
   with an appropriate title.
8. If I confirm NO, skip the PDF export.

Constraints:
- Use only the tools available in the MCP git server. Do not invoke any terminal commands.
- If a required git operation has no corresponding MCP tool, notify me immediately and stop — do not proceed with that step.
- Do not hallucinate commands or invent tool calls that do not exist.
```

---

## Prompt 17 — Review a Single File Across Commits

```
Using the git MCP server, perform the following steps in order:

Variables (replace before running):
- REPO_PATH   : <absolute-path-to-local-repo>
- FILE_PATH   : <path-to-file-in-repo, e.g., src/main.py>
- COMMIT_1    : <first-commit-sha-or-branch>
- COMMIT_2    : <second-commit-sha-or-branch>

Steps:
1. Show the content of FILE_PATH as it existed in COMMIT_1.
2. Show the content of FILE_PATH as it exists in COMMIT_2.
3. Show the diff for FILE_PATH between COMMIT_1 and COMMIT_2.
4. Provide a detailed analysis of how the file evolved:
   a. What logic changed or improved
   b. Any refactoring that occurred
   c. Whether the changes align with best practices
   d. Any potential code quality concerns introduced
5. Once the analysis is complete, ask me if I would like to export the review
   to a PDF file.
6. If I confirm YES, export the report to REPO_PATH/file-review-FILE_PATH.pdf
   with an appropriate title.
7. If I confirm NO, skip the PDF export.

Constraints:
- Use only the tools available in the MCP git server. Do not invoke any terminal commands.
- If a required git operation has no corresponding MCP tool, notify me immediately and stop — do not proceed with that step.
- Do not hallucinate commands or invent tool calls that do not exist.
```

---

## Prompt 18 — Export Code Review Report to PDF

```
You have just completed a code review analysis and have the full review report
text ready. Now export this report to a PDF file for documentation and sharing.

Variables (replace before running):
- REPORT_CONTENT: <the-complete-code-review-report-text>
- OUTPUT_PATH   : <absolute-path-where-pdf-will-be-saved, e.g., /path/to/review_report.pdf>
- REPORT_TITLE  : <title-for-the-pdf, e.g., "Code Review - Feature X">

Steps:
1. Take the complete code review report text (REPORT_CONTENT) that you have generated.
2. Export it to a PDF file at OUTPUT_PATH with the title REPORT_TITLE.
3. Confirm the PDF was created successfully and provide the file path where it was saved.

Notes on formatting:
- The PDF exporter automatically formats markdown-style headers (#, ##, ### for different heading levels)
- Bullet points (- or *) are automatically indented and formatted
- Numbered lists are preserved and formatted appropriately
- The PDF includes generated timestamp and page numbers

Constraints:
- Use only the tools available in the MCP git server. Do not invoke any terminal commands.
- If a required git operation has no corresponding MCP tool, notify me immediately and stop — do not proceed with that step.
- Do not hallucinate commands or invent tool calls that do not exist.
```

---
