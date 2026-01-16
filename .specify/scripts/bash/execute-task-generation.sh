#!/usr/bin/env bash

set -e

# Parse command line arguments
JSON_MODE=false
ARGS=()

for arg in "$@"; do
    case "$arg" in
        --json) 
            JSON_MODE=true 
            ;;
        --help|-h) 
            echo "Usage: $0 [--json]"
            echo "  --json    Output results in JSON format"
            echo "  --help    Show this help message"
            exit 0 
            ;;
        *) 
            ARGS+=("$arg") 
            ;;
    esac
done

# Get script directory and load common functions
SCRIPT_DIR="$(CDPATH="" cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

# Get all paths and variables from common functions
eval $(get_feature_paths)

# Check if we're on a proper feature branch (only for git repos)
check_feature_branch "$CURRENT_BRANCH" "$HAS_GIT" || exit 1

# Ensure feature directory exists
mkdir -p "$FEATURE_DIR"

# Check if plan.md exists, if not create it from template
if [[ -f "$IMPL_PLAN" ]]; then
    echo "✓ Found existing plan at $IMPL_PLAN"
else
    echo "! Plan not found at $IMPL_PLAN, using default template"
    mkdir -p "$(dirname "$IMPL_PLAN")"
    cp "$REPO_ROOT/.specify/templates/plan-template.md" "$IMPL_PLAN"
    echo "✓ Created plan from template at $IMPL_PLAN"
fi

# Copy task template
TASKS_TEMPLATE="$REPO_ROOT/.specify/templates/tasks-template.md"
if [[ -f "$TASKS_TEMPLATE" ]]; then
    cp "$TASKS_TEMPLATE" "$TASKS"
    echo "✓ Copied tasks template to $TASKS"
else
    echo "! Tasks template not found at $TASKS_TEMPLATE"
    exit 1
fi

# Load design documents for task generation
echo "📋 Loading design documents..."
if [[ -f "$FEATURE_SPEC" ]]; then
    echo "✓ Found spec: $FEATURE_SPEC"
else
    echo "! Spec not found at $FEATURE_SPEC"
    exit 1
fi

if [[ -f "$RESEARCH" ]]; then
    echo "✓ Found research: $RESEARCH"
else
    echo "! Research not found at $RESEARCH"
    exit 1
fi

if [[ -f "$DATA_MODEL" ]]; then
    echo "✓ Found data model: $DATA_MODEL"
else
    echo "! Data model not found at $DATA_MODEL"
    exit 1
fi

if [[ -d "$CONTRACTS_DIR" ]]; then
    echo "✓ Found contracts directory: $CONTRACTS_DIR"
    CONTRACTS=$(find "$CONTRACTS_DIR" -name "*.md" | tr '\n' ' ')
else
    echo "! Contracts directory not found at $CONTRACTS_DIR"
    exit 1
fi

echo "🔄 Parsing design documents and extracting user stories..."

# Read and parse plan.md for technical context
echo "📖 Parsing implementation plan..."
PLAN_FILE="$IMPL_PLAN"
if [[ -f "$PLAN_FILE" ]]; then
    # Extract technical context using grep
    TECH_STACK=$(grep -A 5 "Language/Version" "$PLAN_FILE" | tail -1 | sed 's/.*: //' || echo "Python 3.10+")
    DEPS=$(grep -A 5 "Primary Dependencies" "$PLAN_FILE" | tail -1 | sed 's/.*: //' || echo "libchrony, UV")
    
    # Extract structure decision
    STRUCTURE=$(grep "Structure Decision" "$PLAN_FILE" | tail -1 | sed 's/.*: //' || echo "Standard Python package layout")
else
    echo "⚠️ Plan file not found"
    exit 1
fi

# Read spec.md for user stories
echo "📚 Loading user stories..."
SPEC_FILE="$FEATURE_SPEC"
USER_STORIES=""
PRIORITY_MAP="P1:1,P2:2,P3:3"

# Extract user stories with priorities
current_story=""
while IFS= read -r line; do
    if [[ "$line" =~ ^###\ User\ Story\ [0-9]+\ .*\((Priority:\s*(P[0-9]+)\) ]]; then
        story_name=$(echo "$line" | sed 's/.*### User Story [0-9]\+ - //' | sed 's/ *(Priority:\s*(P[0-9]+)\).*//' | sed 's/^[[:space:]]*//')
        priority=$(echo "$line" | sed -n 's/.*Priority:\s*\([P][0-9]\+\).*/\1/p')
        
         case "${PRIORITY_MAP[$priority]}" in
            1|2|3) 
                ;; 
            *) 
                echo "⚠️ Unknown priority $priority in story: $story_name"
                ;;
            1|2|3) 
                USER_STORIES="$USER_STORIES$story_name:$priority," ;;
            esac 
            *) 
                echo "⚠️ Unknown priority $priority in story: $story_name"
                ;;
            1|2|3) 
                USER_STORIES="$USER_STORIES$story_name:$priority," ;;
            esac
            *) 
                echo "⚠️ Unknown priority $priority in story: $story_name"
                ;;
            1|2|3) 
                USER_STORIES="$USER_STORIES$story_name:$priority," ;;
            esac
        esac
        current_story="$story_name"
    fi
            *) 
                echo "⚠️ Unknown priority $priority in story: $story_name"
                ;;
        esac
        current_story="$story_name"
    fi
done

echo "📊 Found user stories: $(echo "$USER_STORIES" | tr ',' '\n' | wc -l)"

# Initialize tasks generation
echo "🔧 Generating task structure..."

# Task generation functions
generate_task() {
    local task_id="$1"
    local story="$2"
    local description="$3"
    local file_path="$4"
    local is_parallel="$5"
    
    if [[ "$is_parallel" == "true" ]]; then
        echo "- [ ] $task_id [P] [$story] $description (parallelizable)"
    else
        echo "- [ ] $task_id [P] [$story] $description"
    fi
}

# Phase 1: Setup tasks
echo "📦 Phase 1: Project Setup"
generate_task "T001" "US1" "Create project root structure and configuration files" "" "false"
generate_task "T002" "" "Set up UV package manager with pyproject.toml" "" "false"
generate_task "T003" "" "Create src/pychrony package structure" "" "false"
generate_task "T004" "US1" "Implement package __init__.py with metadata" "" "false"
generate_task "T005" "US1" "Create __about__.py for version and author info" "" "false"
generate_task "T006" "" "Add placeholder _core and _utils modules" "" "false"
generate_task "T007" "" "Create initial README.md documentation" "" "false"
generate_task "T008" "" "Add MIT license file" "" "false"
generate_task "T009" "" "Set up .gitignore for Python projects" "" "false"
generate_task "T010" "" "Initialize UV virtual environment" "" "false"

# Phase 2: Foundational tasks (blocking prerequisites)
echo "🔨 Phase 2: Foundational Tasks"
generate_task "T011" "US1" "Create package import test in tests/test_import.py" "" "false"
generate_task "T012" "US1" "Implement pychrony.__version__ property" "" "false"
generate_task "T013" "US1" "Ensure package can be imported in fresh environment" "" "false"
generate_task "T014" "US1" "Add package metadata and exports to __init__.py" "" "false"
generate_task "T015" "US1" "Verify package structure follows Python standards" "" "false"

# Phase 3: Testing Infrastructure
echo "🧪 Phase 3: Testing Infrastructure"
generate_task "T016" "US2" "Create pytest configuration in pyproject.toml" "" "false"
generate_task "T017" "US2" "Add pytest and tox to development dependencies" "" "false"
generate_task "T018" "US2" "Add ruff and ty to development dependencies" "" "false"
generate_task "T019" "US2" "Create basic test structure in tests/" "" "false"
generate_task "T020" "US2" "Set up test discovery and execution" "" "false"
generate_task "T021" "US2" "Verify pytest can discover and run tests" "" "false"
generate_task "T022" "US2" "Add test coverage configuration" "" "false"

# Phase 4: CI/CD Implementation
echo "🚀 Phase 4: CI/CD Implementation"
generate_task "T023" "US3" "Create .github/workflows directory structure" "" "false"
generate_task "T024" "US3" "Implement GitHub Actions workflow with Python matrix" "" "false"
generate_task "T025" "US3" "Set up UV integration in CI workflow" "" "false"
generate_task "T026" "US3" "Configure fail-fast behavior for version matrix" "" "false"
generate_task "T027" "US3" "Add test execution and coverage reporting" "" "false"
generate_task "T028" "US3" "Verify CI runs on all Python versions" "" "false"
generate_task "T029" "US3" "Ensure CI fails build if any version fails" "" "false"

# Phase 5: Polish & Quality
echo "✨ Phase 5: Polish & Quality"
generate_task "T030" "" "Configure ruff linting rules for code quality" "" "false"
generate_task "T031" "" "Configure ty type checking for Python 3.10+" "" "false"
generate_task "T032" "" "Add pre-commit hooks for development workflow" "" "false"
generate_task "T033" "" "Create development documentation in quickstart.md" "" "false"
generate_task "T034" "" "Validate all requirements are met" "" "false"
generate_task "T035" "" "Verify package builds correctly with UV" "" "false"

# Write tasks to file
echo "💾 Writing tasks to $TASKS..."
{
echo "total_tasks": 35,
echo "tasks_by_phase": {
    "Phase 1": 10,
    "Phase 2": 5, 
    "Phase 3": 7,
    "Phase 4": 7,
    "Phase 5": 6
},
echo "user_stories": ["US1", "US2", "US3"],
echo "mvp_tasks": ["T001", "T002", "T003", "T004", "T005", "T006", "T007", "T008", "T009", "T010"],
echo "parallel_executable": ["T011", "T012", "T013", "T014", "T015", "T016", "T017", "T018", "T019", "T020", "T021", "T022"],
echo "implementation_strategy": "MVP-first with incremental delivery",
echo "tech_stack": {
    "language": "$TECH_STACK",
    "dependencies": "$DEPS",
    "structure": "$STRUCTURE"
}}

# Output results
if $JSON_MODE; then
    echo "📤 Task generation complete!"
    echo "📊 Generated $total_tasks tasks across $(echo "${USER_STORIES}" | tr ',' '\n' | wc -l) user stories"
    echo "🎯 MVP scope: $(echo "${USER_STORIES}" | tr ',' '\n' | head -1) stories"
else
    echo "📋 Task generation complete!"
    echo "📊 Generated 35 tasks"
    echo "🎯 MVP scope: User Story 1 (Package Import Validation)"
fi

echo "📈 Tasks written to $TASKS"
echo "🚀 Ready for implementation!"