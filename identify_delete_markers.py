#!/usr/bin/env python3
"""
S3 Delete Marker Analysis Script

This script identifies versioned S3 buckets with high delete marker counts
and excludes Object Lock buckets. It can also propose enabling the
"Remove expired delete markers" lifecycle rule.

Usage:
    python identify_delete_markers.py --profile <aws-profile> [--threshold <count>] [--propose-lifecycle]
    python identify_delete_markers.py --profile absec-test-usa0 --threshold 1000
    python identify_delete_markers.py --profile absec-test-usa0 --propose-lifecycle --output results.csv
"""

import argparse
import boto3
import csv
import json
import sys
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional, Tuple, List, Dict
from botocore.exceptions import ClientError, NoCredentialsError, ProfileNotFound


@dataclass
class BucketAnalysis:
    """Analysis results for a single bucket"""
    bucket_name: str
    account_id: str
    profile_name: str
    is_versioned: bool
    has_object_lock: bool
    delete_marker_count: int
    has_lifecycle_delete_marker_rule: bool
    lifecycle_rules: list
    status: str  # 'needs_attention', 'excluded', 'ok'


def get_account_id(session: boto3.Session) -> str:
    """Get AWS account ID"""
    try:
        sts = session.client("sts")
        return sts.get_caller_identity()["Account"]
    except Exception as e:
        print(f"Warning: Could not get account ID: {e}", file=sys.stderr)
        return "unknown"


def check_versioning(s3_client, bucket_name: str) -> bool:
    """Check if bucket has versioning enabled"""
    try:
        response = s3_client.get_bucket_versioning(Bucket=bucket_name)
        return response.get("Status") == "Enabled"
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        if error_code == "AccessDenied":
            print(f"  Warning: Access denied checking versioning for {bucket_name}", file=sys.stderr)
        else:
            print(f"  Warning: Error checking versioning for {bucket_name}: {e}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"  Warning: Unexpected error checking versioning for {bucket_name}: {e}", file=sys.stderr)
        return False


def check_object_lock(s3_client, bucket_name: str) -> bool:
    """Check if bucket has Object Lock enabled"""
    try:
        response = s3_client.get_object_lock_configuration(Bucket=bucket_name)
        config = response.get("ObjectLockConfiguration", {})
        return config.get("ObjectLockEnabled") == "Enabled"
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        if error_code == "NoSuchObjectLockConfiguration":
            return False
        elif error_code == "AccessDenied":
            print(f"  Warning: Access denied checking Object Lock for {bucket_name}", file=sys.stderr)
            return False
        else:
            # Assume no Object Lock if we can't check
            return False
    except Exception as e:
        # Assume no Object Lock if we can't check
        return False


def count_delete_markers(s3_client, bucket_name: str, max_markers: Optional[int] = None) -> int:
    """Count delete markers in a versioned bucket"""
    delete_marker_count = 0
    
    try:
        paginator = s3_client.get_paginator("list_object_versions")
        page_iterator = paginator.paginate(Bucket=bucket_name)
        
        for page in page_iterator:
            delete_markers = page.get("DeleteMarkers", [])
            delete_marker_count += len(delete_markers)
            
            # Early exit if we've exceeded threshold
            if max_markers and delete_marker_count > max_markers:
                return delete_marker_count
                
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        if error_code == "AccessDenied":
            print(f"  Warning: Access denied counting delete markers for {bucket_name}", file=sys.stderr)
        else:
            print(f"  Warning: Error counting delete markers for {bucket_name}: {e}", file=sys.stderr)
        return -1  # Indicate error
    except Exception as e:
        print(f"  Warning: Unexpected error counting delete markers for {bucket_name}: {e}", file=sys.stderr)
        return -1
    
    return delete_marker_count


def check_lifecycle_delete_marker_rule(s3_client, bucket_name: str) -> Tuple[bool, List]:
    """Check if bucket has lifecycle rule to remove expired delete markers"""
    try:
        response = s3_client.get_bucket_lifecycle_configuration(Bucket=bucket_name)
        rules = response.get("Rules", [])
        
        has_delete_marker_rule = False
        rule_details = []
        
        for rule in rules:
            if rule.get("Status") != "Enabled":
                continue
                
            expiration = rule.get("Expiration", {})
            if expiration.get("ExpiredObjectDeleteMarker") == True:
                has_delete_marker_rule = True
                rule_details.append({
                    "id": rule.get("Id", "unknown"),
                    "status": rule.get("Status"),
                    "expired_object_delete_marker": True
                })
        
        return has_delete_marker_rule, rule_details
        
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        if error_code == "NoSuchLifecycleConfiguration":
            return False, []
        elif error_code == "AccessDenied":
            print(f"  Warning: Access denied checking lifecycle for {bucket_name}", file=sys.stderr)
            return False, []
        else:
            return False, []
    except Exception as e:
        return False, []


def analyze_bucket(
    s3_client,
    bucket_name: str,
    account_id: str,
    profile_name: str,
    threshold: int,
    max_markers: Optional[int] = None
) -> BucketAnalysis:
    """Analyze a single bucket for delete markers"""
    
    print(f"Analyzing bucket: {bucket_name}")
    
    # Check versioning
    is_versioned = check_versioning(s3_client, bucket_name)
    
    if not is_versioned:
        return BucketAnalysis(
            bucket_name=bucket_name,
            account_id=account_id,
            profile_name=profile_name,
            is_versioned=False,
            has_object_lock=False,
            delete_marker_count=0,
            has_lifecycle_delete_marker_rule=False,
            lifecycle_rules=[],
            status="ok"
        )
    
    # Check Object Lock
    has_object_lock = check_object_lock(s3_client, bucket_name)
    
    if has_object_lock:
        return BucketAnalysis(
            bucket_name=bucket_name,
            account_id=account_id,
            profile_name=profile_name,
            is_versioned=True,
            has_object_lock=True,
            delete_marker_count=0,
            has_lifecycle_delete_marker_rule=False,
            lifecycle_rules=[],
            status="excluded"
        )
    
    # Count delete markers
    delete_marker_count = count_delete_markers(s3_client, bucket_name, max_markers)
    
    # Check lifecycle rules
    has_lifecycle_rule, lifecycle_rules = check_lifecycle_delete_marker_rule(s3_client, bucket_name)
    
    # Determine status
    if delete_marker_count == -1:
        status = "ok"  # Error counting, skip
    elif delete_marker_count >= threshold:
        status = "needs_attention"
    else:
        status = "ok"
    
    return BucketAnalysis(
        bucket_name=bucket_name,
        account_id=account_id,
        profile_name=profile_name,
        is_versioned=True,
        has_object_lock=False,
        delete_marker_count=delete_marker_count,
        has_lifecycle_delete_marker_rule=has_lifecycle_rule,
        lifecycle_rules=lifecycle_rules,
        status=status
    )


def get_buckets(s3_client) -> list[str]:
    """Get list of all S3 buckets"""
    try:
        response = s3_client.list_buckets()
        return [bucket["Name"] for bucket in response.get("Buckets", [])]
    except Exception as e:
        print(f"Error listing buckets: {e}", file=sys.stderr)
        return []


def write_csv(results: list[BucketAnalysis], filename: str):
    """Write results to CSV file"""
    if not results:
        return
    
    fieldnames = [
        "bucket_name",
        "account_id",
        "profile_name",
        "is_versioned",
        "has_object_lock",
        "delete_marker_count",
        "has_lifecycle_delete_marker_rule",
        "status"
    ]
    
    with open(filename, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for result in results:
            row = asdict(result)
            # Flatten lifecycle_rules to JSON string
            row["lifecycle_rules"] = json.dumps(row["lifecycle_rules"])
            writer.writerow(row)


def print_summary(results: list[BucketAnalysis], threshold: int):
    """Print summary of analysis"""
    total_buckets = len(results)
    versioned_buckets = [r for r in results if r.is_versioned]
    object_lock_buckets = [r for r in results if r.has_object_lock]
    needs_attention = [r for r in results if r.status == "needs_attention"]
    has_lifecycle_rule = [r for r in results if r.has_lifecycle_delete_marker_rule and r.is_versioned]
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total buckets analyzed: {total_buckets}")
    print(f"Versioned buckets: {len(versioned_buckets)}")
    print(f"Object Lock buckets (excluded): {len(object_lock_buckets)}")
    print(f"Buckets with delete markers >= {threshold}: {len(needs_attention)}")
    print(f"Buckets with lifecycle delete marker rule: {len(has_lifecycle_rule)}")
    print()
    
    if needs_attention:
        print("BUCKETS NEEDING ATTENTION:")
        print("-" * 80)
        for result in sorted(needs_attention, key=lambda x: x.delete_marker_count, reverse=True):
            lifecycle_status = "✓" if result.has_lifecycle_delete_marker_rule else "✗"
            print(f"  {result.bucket_name}")
            print(f"    Delete markers: {result.delete_marker_count:,}")
            print(f"    Lifecycle rule: {lifecycle_status}")
            print()


def main():
    parser = argparse.ArgumentParser(
        description="Identify versioned S3 buckets with high delete marker counts"
    )
    parser.add_argument(
        "--profile",
        required=True,
        help="AWS profile to use"
    )
    parser.add_argument(
        "--threshold",
        type=int,
        default=1000,
        help="Threshold for 'high' delete marker count (default: 1000)"
    )
    parser.add_argument(
        "--max-markers",
        type=int,
        help="Maximum delete markers to count per bucket (for performance, stops counting after this)"
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Output CSV filename (optional)"
    )
    parser.add_argument(
        "--region",
        help="AWS region (optional, uses default if not specified)"
    )
    
    args = parser.parse_args()
    
    # Create AWS session
    try:
        session = boto3.Session(profile_name=args.profile, region_name=args.region)
        s3_client = session.client("s3")
    except ProfileNotFound:
        print(f"Error: Profile '{args.profile}' not found", file=sys.stderr)
        sys.exit(1)
    except NoCredentialsError:
        print(f"Error: No credentials found for profile '{args.profile}'", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error creating AWS session: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Get account ID
    account_id = get_account_id(session)
    
    print("=" * 80)
    print("S3 DELETE MARKER ANALYSIS")
    print("=" * 80)
    print(f"Profile: {args.profile}")
    print(f"Account ID: {account_id}")
    print(f"Threshold: {args.threshold:,} delete markers")
    print()
    
    # Get all buckets
    print("Listing buckets...")
    buckets = get_buckets(s3_client)
    print(f"Found {len(buckets)} buckets")
    print()
    
    # Analyze each bucket
    results = []
    for i, bucket_name in enumerate(buckets, 1):
        print(f"[{i}/{len(buckets)}] ", end="")
        result = analyze_bucket(
            s3_client,
            bucket_name,
            account_id,
            args.profile,
            args.threshold,
            args.max_markers
        )
        results.append(result)
    
    # Write CSV if requested
    if args.output:
        write_csv(results, args.output)
        print(f"\nResults written to: {args.output}")
    
    # Print summary
    print_summary(results, args.threshold)
    
    # Exit with error code if buckets need attention
    needs_attention = [r for r in results if r.status == "needs_attention"]
    if needs_attention:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()

