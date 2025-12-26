#!/bin/bash
# Example usage script for S3 Lifecycle Guardrails

set -e

PROFILE="${AWS_PROFILE:-absec-test-usa0}"
THRESHOLD="${THRESHOLD:-1000}"
OUTPUT_DIR="${OUTPUT_DIR:-./output}"

echo "S3 Lifecycle Guardrails - Example Usage"
echo "========================================"
echo ""

# Create output directory
mkdir -p "$OUTPUT_DIR"

echo "Step 1: Identifying buckets with high delete marker counts..."
echo "Profile: $PROFILE"
echo "Threshold: $THRESHOLD"
echo ""

python identify_delete_markers.py \
  --profile "$PROFILE" \
  --threshold "$THRESHOLD" \
  --output "$OUTPUT_DIR/analysis_results.csv"

echo ""
echo "Step 2: Generating lifecycle rule proposals..."
echo ""

if [ -f "$OUTPUT_DIR/analysis_results.csv" ]; then
  python propose_lifecycle_rule.py \
    --input "$OUTPUT_DIR/analysis_results.csv" \
    --terraform \
    --output "$OUTPUT_DIR/lifecycle_proposals.tf"
  
  echo ""
  echo "Analysis complete!"
  echo "Results saved to: $OUTPUT_DIR/"
  echo "  - analysis_results.csv"
  echo "  - lifecycle_proposals.tf"
else
  echo "Error: analysis_results.csv not found"
  exit 1
fi

